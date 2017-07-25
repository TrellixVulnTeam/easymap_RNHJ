#!/usr/bin/python

import subprocess
import os

# Get amount of data currently in user_projects directory
proc = subprocess.Popen("du -s ../user_projects", shell=True, stdout=subprocess.PIPE)
folder_size_output = proc.stdout.read()
user_projects_size_gb = float(float(folder_size_output.split("	")[0]) / 1048576)


# Get number of projects currently running
proc = subprocess.Popen("ls ../user_projects", shell=True, stdout=subprocess.PIPE)
list_projects = proc.stdout.read().split()
number_running_files = 0

for project in list_projects:
	try:
		with open("../user_projects/"+project+"/2_logs/status") as status:
			for lines in status:
				if lines[:6] =="status":
					lines = lines.rstrip()
					stat = lines.split(":")[1] 
			if stat == "running":
				number_running_files += 1				
	except:
		continue

# Get configuration information from file /config/config
n = 0
with open("./config") as con_file:
	for lines in con_file:
		n += 1
		if lines[:5] == "user_":#################################################################################################################################################
			size_limit = lines.rstrip().split(":")[1]
		if lines[:3] == "max":#########################################################################################################################################################
			simultaneous_limit = lines.rstrip().split(":")[1]

# Check whether it is possible to keep running the project

try:
	if float(size_limit) > 0:
			percentage_size = (float(user_projects_size_gb)/float(size_limit))*100
			percentage_size = str(int(percentage_size))	
	else:
		percentage_size = 0
except:
	percentage_size = "Error during maximum size allowed reading. Please check config file." ########## Si esta excepcion ocurre, luego easymap.py peta

try:
	if float(simultaneous_limit) > 0:
		percentage_running = (float(number_running_files)/float(simultaneous_limit))*100
		percentage_running = str(int(percentage_running))
	else:
		percentage_running = 0
except:
	percentage_running = "Error during maximum simultaneous running allowed reading. Please check config file."###################################

print str(percentage_size)+","+str(percentage_running)+","+str(size_limit)+","+str(simultaneous_limit)