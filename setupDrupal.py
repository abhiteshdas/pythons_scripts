from array import *
import os, sys, subprocess

#Notes
#1. To ensure readability, do not use drush command aliases.

#Generic settings
devnull = open(os.devnull,"w")

#Function to print out status text
def status(string, status):
  colors={"default":"",
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

	return colors[color] + "[" + msg.upper() + "]" + "\x1b[00m" + " " + string;

#Simple function to run commands using subprocess
def runCom(command):
	proc = subprocess.Popen(command, shell=True, stdin=devnull, stdout=None, stderr=None, executable="/bin/bash")
	proc.wait()
	return proc.returncode

#Install a module
def installModule(moduleName, isCore=True):
	if(not isCore):
		runDrushCom("pm-download " + moduleName)
	runDrushCom("pm-enable -y " + moduleName)

#Run drush commands
def runDrushCom(command):
	return runCom('drush ' + alias + command)

#Setup Drupal afresh
def installDrupal():
	askedOnce = False
	accountPassword = ''
	accountMail = ''
	notice = "We cannot proceed without this info. "
	emailNotice = "Enter admin e-mail (NB: This will be used for logging in): "
	passNotice = "Enter admin password (NB: This will be used for logging in): "
	mysqlSUUsernameNotice = "Enter MySQL SU username: "
	mysqlSUPassNotice = "Enter MySQL SU password: "

	while((not accountMail) or (not accountPassword)):
		if(not accountMail):
			q = notice + emailNotice if askedOnce else emailNotice
			accountMail = raw_input(q)
		if(not accountPassword):
			q = notice + passNotice if askedOnce else passNotice
			accountPassword = raw_input(q)
		askedOnce = True

	installCommand = "site-install -y minimal --account-mail=" + accountMail + " --account-pass=" + accountPassword + " --account-name=admin --site-name=DealsCMS --clean-url --db-url=mysql://dealscms:coldcold@localhost/dealscms"
	runDrushCom(installCommand)

#Check if the command is being run as SUDO
if os.geteuid() == 0:
	print status("Do not run this command as SUDO.", "error")
	sys.exit();

#Check if drush aliases are setup. And if yes, use them
alias = raw_input("If you have drush aliases setup, please specify the alias to use along without the @ sign. Otherwise, I will assume that the current working directory is where Drupal is installed:  " + os.getcwd() + ". Example ['local'/'dev'/'']: ")
if alias.lower() == '':
	print status("No alias will be used. Instead, the current directory(" + os.getcwd() + ") will be used.", "info")
else:
	alias = '@' + alias
	print status("Alias to be used: " + alias, "info")

#Check if Drupal is installed. If not, do it.
isNotInstalled = runDrushCom('core-requirements')
if isNotInstalled:
	print status("Drupal is not installed! Installing now.", "warning")
	installDrupal()
else:
	print status("Drupal is already installed!", "info")

#Install necessary core modules
reqModules = ['path','options','number','list','image','field_ui','taxonomy','toolbar','menu','locale','php','syslog']
for module in reqModules:
	installModule(module)

#Install necessary contrib modules
reqModules = ['views','views_ui','term_reference_tree','taxonomy_image','date','date_popup','date_views','libraries','jquery_update','link','services','rest_server','taxonomy_manager','views_bulk_operations']
for module in reqModules:
	installModule(module, False)

#Uninstall dblog
runDrushCom("-y pm-disable dblog")
runDrushCom("-y pm-uninstall dblog")

#Clear all caches
runDrushCom("cache-clear all")
