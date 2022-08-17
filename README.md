# Pyats UCS-FI Power Monitoring
This sample code represents a solution where you can monitor the power levels in interfaces with Fibre SFPs in a FI by using PyATS, with reports appended/generated each iteration and a notification with data of the latest run report sent in an email. 

## Contacts
* Ozair Saiyad (osaiyad@cisco.com)


## Solution Components
* PyATS: Open-source software made by Cisco for automated testing, used to send commands to FI via SSH, and parse the output 
* SMTP: Role for Ansible which is responsible for parsing the text output from the network (IOSXE) devices to JSON
* Background Scheduler: Runs the task at the scheduled interval

* Input files: 
  * user-port-input.yaml :  File should define the interfaces which may have
  relevant Fiber SFPs and require monitoring. [Example file](user-port-input.yaml)
  * nxos-jakartalab.yaml: This is the **testbed** file. You should define the connections to the devices you want, the connection method and credentials 
   to access it. [Example file](nxos-jakartalab.yaml)

  

#### Set up a Python venv
First make sure that you have Python 3 installed on your machine. We will then be using venv to create
an isolated environment with only the necessary packages.

##### Install virtualenv via pip
```
$ pip install virtualenv
```
##### Create a new venv
```
Change to your project folder
$ cd Pyats_monitoring_project
Create the venv
$ python3 -m venv venv
Activate your venv
$ source venv/bin/activate
```
#### Install dependencies
In the target folder: 
```
$ pip install -r requirements.txt
```

#### API Secrets
Create a ```env_vars.py``` file where you will fill in your token and other sensitive variables

## Setup:

In ```nxos-script.py```, the following variables should be configured by the user according to their preference:
* TASK_FREQUENCY
* CLEAR_FREQUENCY
* TESTBED_FILE

Note: If you change TASK_FREQUENCY to different unites, eg minutes or hours, please reflect this change on line 310 as well. 


Import the env_vars file in ```send_email.py```, put it in the authorization section, which should have the token for your DB. 


In the TESTBED file define all the hosts you wish to, and methods to connect to them, preferably SSH. For FIs, leave the OS to be **Linux**  since as of 17th August 2022, unicon does not work with them natively. Please read the PyATS documentation regarding the correct format for inventory files : https://pubhub.devnetcloud.com/media/pyats/docs/topology/index.html 


Set-up the correct interval for your tasks to run in the background scheduler in main.py, with the variable 'TASK_FREQUENCY'. For Background Scheduler reference, you may read the following: https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/background.html 

For the SMTP library used in ```send_email.py``` , you may reference the following link to see what the methods called represent, and other actions you can take with the help of the library: https://docs.python.org/3/library/smtplib.html 


## Running:

Enter the following command to run the script:

```
$ source venv/bin/activate

$ python3 nxos-script.py
```



## Output :

There are 3 CSV files generated:
* sfp_txrx_power_report.csv : An **aggregate** report with timeseries info, and TX RX power levels, their status, and SFP Serial number for each defined interface in ```user-port-input.yaml```. Stored locally.
* sfp_power_summary.csv: A **aggregate** report which summarises the number of devices that meet each warning/alarm status. Stored locally.
* email_sfp_txrx_power_report.csv : A report concerning the **latest run**, format is the same as ```sfp_txrx_power_report.csv``` with the only difference being that it's not an aggregate. It is stored locally AND sent via email. Note that there aren't new instances of this file created every run, this file is simply overwritten as you can access previous data from the ```sfp_txrx_power_report.csv``` as well as email records. 


## Screenshots: 
   
### sfp_txrx_power_report : 
![SFP Power Report](/Images/power_report.png)

### sfp_power_summary.csv :
![SFP Summary report](/Images/summary_report.png)
![Email notification report](/Images/email_notification_report.jpg)


## email_sfp_txrx_power_report.csv


## Additional info:

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](/LICENSES/LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](/LICENSES/CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](/LICENSES/CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
