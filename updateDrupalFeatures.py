from array import *
import os, sys, subprocess, re

#Description
#Checks through your Drupal installation and automatically updates/resets overridden features.
#This script is a useful deploy tool and will aid in automatic deployments using Jenkins, Phing, etc.

#Notes
#1. To ensure readability, do not use drush command aliases.
#2. Needs to be run within the drupal installation
#3. Is automated. To ensure that you want to update only selective features, remove the -y flag on line 25.

#Generic settings
devnull = open(os.devnull,"w")
env = os.environ["VDNA_ENVIRONMENT"]

#Simple function to run commands using subprocess
def runCom(command):
  proc = subprocess.Popen(command, shell=True, stdin=devnull, stdout=None, stderr=None, executable="/bin/bash")
	proc.wait()
	return proc.returncode

#Run drush commands
def runDrushCom(command):
	return runCom('drush -y ' + command)

#Function to print out status text
def status(string, status):
	colors={"default":"",
		"yellow": "\x1b[01;33m",
        "blue":   "\x1b[01;34m",
        "cyan":   "\x1b[01;36m",
        "green":  "\x1b[01;32m",
        "red":    "\x1b[01;05;37;41m"}

	if status == "info":
		color = "green"
		msg = "ok"
	elif status == "warning":
		color = "cyan"
		msg = "warning"
	elif status == "error":
		color = "red"
		msg = "error"
	elif status == "heading":
		return colors["yellow"] + string.upper() + "\x1b[00m";

	return colors[color] + "[" + msg.upper() + "]" + "\x1b[00m" + " " + string;

#Create an array of features with attributes
def getFeatures():
	cmd = "drush features"
	proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	proc.wait()
	output=proc.communicate()[0].splitlines()
	
	headerString = output.pop(0)
	headers = re.findall('([a-zA-z]+[ ]*)', headerString)

	attributes = {}
	for header in headers:
		attributes[header.strip().lower()] = {
			'offset' : headerString.index(header),
			'len' : len(header)
		}

	features = []
	for feature in output:
		newFeature = {}
		for attr, values in attributes.iteritems():
			start = values['offset']
			stop = values['offset'] + values['len']
			newFeature[attr] = feature[start:stop].strip()
		features.append(newFeature)

	return features

#Checks all attributes of a drush-returned feature row and updates if necessary
def shouldUpdate(feature):
	if feature['name'] == '':
		return False

	if feature['status'] != 'Enabled':
		print status(feature['name'] + ' is disabled!', 'info')
		return False

	if feature['status'] == 'Enabled' and feature['state'] == '':
		print status(feature['name'] + ' is up-to-date!', 'info')
		return False

	if feature['status'] == 'Enabled' and feature['state'] == 'Overridden':
		print status(feature['name'] + ' requires update!', 'warning')
		return True

#Update a single feature
def updateFeature(feature):
	runDrushCom('features-update ' + feature['feature'])

#Put it all together
print status('Checking for features that require update', 'heading')

toUpdate = []
for feature in getFeatures():
	if shouldUpdate(feature):
		toUpdate.append(feature)

if len(toUpdate) == 0:
	print status('No features require update. Exiting...', 'heading')
	sys.exit()

print status('Found ' + str(len(toUpdate)) + ' feature(s) to update. Updating now...', 'heading')
for feature in toUpdate:
	updateFeature(feature)
