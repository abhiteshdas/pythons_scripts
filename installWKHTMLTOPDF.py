from array import *
import os, sys, subprocess

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

#Check if the command is being run as SUDO
if not os.geteuid() == 0:
	print status("You need to run this command as root", "error")
	sys.exit();

#Make sure that the present-working-dir is the one where all the processing has to be done
cwdOK = raw_input("Your current working directory is " + os.getcwd() + ". I'll be using this to download WKHTMLTOPDF into. Is this ok? [y/n]: ")
if cwdOK.lower() == 'n':
	print status("Please change the DIR and run this command from there", "error")
	sys.exit()

#Check if the necessary dpkg packages are installed
deps = ['xvfb','xorg','openssl','build-essential','xorg','libssl-dev','libxrender-dev','git']
devnull = open(os.devnull,"w")
for dep in deps[:]:
	retval = subprocess.call(["dpkg","-s",dep],stdout=devnull,stderr=subprocess.STDOUT)
	if retval == 0:
		deps.remove(dep)

#Install the ones that do no exist
if len(deps) == 0:
	print status("All required dependencies installed!","info")
else:
	print status("The following packages are required and will be installed: " + (', '.join(deps)), "warning")
	runCom('apt-get install -y ' + (' '.join(deps)))
	print status("All dependencies installed: Check above for any errors!", "info")

#Housekeeping: Install all dependencies for QT4 so that we can build it later
proc = subprocess.Popen("sudo apt-get build-dep qt4-x11", shell=True, stdin=devnull, stdout=None, stderr=None, executable="/bin/bash")
proc.wait()
print status("Dependencies for QT4 built!", "info")

#checkout wkhtmltopdf and wkhtmltopf-qt into cwd
runCom("git clone git://github.com/antialize/wkhtmltopdf.git wkhtmltopdf")
print status("WKHTMLTOPDF checked out!", "info")
runCom("git clone git://gitorious.org/+wkhtml2pdf/qt/wkhtmltopdf-qt.git wkhtmltopdf-qt")
print status("WKHTMLTOPDF-QT checked out!", "info")

#start the patching
os.chdir("wkhtmltopdf-qt")
runCom("git checkout staging")
runCom("cat ../wkhtmltopdf/static_qt_conf_base ../wkhtmltopdf/static_qt_conf_linux | sed -re 's/#.*//'")
runCom("./configure -nomake tools,examples,demos,docs,translations -opensource -prefix '../wkqt'")
runCom("make -j3 && make install")
os.chdir("..")
os.chdir("wkhtmltopdf")
runCom("../wkqt/bin/qmake")
runCom("make && make install")
print status("QT patched successfully! Check above for errors if any.", "info")

#Install actual WKHTMLTOPDF
runCom("wget http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.9.9-static-amd64.tar.bz2")
runCom("tar xvjf wkhtmltopdf-0.9.9-static-amd64.tar.bz2")
runCom("mv wkhtmltopdf-amd64 /usr/local/bin/wkhtmltopdf")
runCom("chmod +x /usr/local/bin/wkhtmltopdf")
print status("WKHTMLTOPDF installed!", "info")

