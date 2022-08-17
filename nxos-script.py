
'''

********************************************************
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
*********************************************************

 * Author:                  Ozair Saiyad
 *                          Technical Solutions Specialist
 *                          Cisco Systems
 * 
 * Special Thanks:          Muhammad Akbar (Systems Engineer - Cisco)

 * 
 * Released: 17 August, 2022
 * 
 * Version: 1.0

 '''






from pyats.topology import loader
import pprint, os
import datetime
import csv
import yaml
from send_email import *
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler





from lxml import etree





 

# GLOBAL VARIABLES TO CONFIGURE
CLEAR_FREQUENCY = datetime.timedelta(minutes=2)

TASK_FREQUENCY = datetime.timedelta(seconds=60)


USER_INPUT_FILE = 'user-port-input.yaml'

TESTBED_FILE = 'nxos-jakartalab.yaml'


# LOAD TESTBED
testbed = loader.load(f'{TESTBED_FILE}')


#Schedule for a determined interval
task_scheduler = BlockingScheduler()

mail_prev_time =  float(0)



#Dictionary global variable- will be written to power report
tx_rx_status_dict = {}

# access the devices
testbed.devices

fake_nxos = testbed.devices['fake-nxos']

month_counter = 1


# CSV Operations 
csvfile = open('sfp_txrx_power_report.csv', 'w+')
fieldnames = ['Date Time', 'Device Name', 'Serial Number', 'Switch Interface Name', 'RX Power', 'RX Power Status', 'TX Power', 'TX Power Status' ]
writer = csv.DictWriter(csvfile, fieldnames= fieldnames)
writer.writeheader()

csvfile2 = open('sfp_txrx_power_summary.csv', 'w+')
fieldnames2 = ['Date Time', 'High Alarm Count', 'Low Alarm Count', 'High Warning Count', 'Low Warning Count' ]
writer2 = csv.DictWriter(csvfile2, fieldnames= fieldnames2)
writer2.writeheader()



# Reads user-port-input file and parses YAML data to a Python Dictionary
def user_sfp_port_input_handler() :
    global USER_INPUT_FILE
    global devices
    global device_port_mapping

    with open(f"{USER_INPUT_FILE}", "r") as stream:
        try:
            device_port_mapping = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

# Helper function which classifies the TX and RX power into either a warning or alarm or normal status
def get_txrx_status(power_dict):
    global high_warning_count, low_warning_count, high_alarm_count, low_alarm_count

        
    try:
        current_power = float(power_dict['current'])

    except ValueError:
        current_power = 0

    high_warning = float(power_dict['high_warning'])
    low_warning = float(power_dict['low_warning'])
    high_alarm = float(power_dict['high_alarm'])
    low_alarm = float(power_dict['low_alarm'])

    print(current_power)
    status = ''

    #Within warning stages
    if current_power <= high_warning and current_power >= low_warning :
        status = 'normal'

    #Exceeds warning threshold but lower than alarm measures    
    elif current_power <= high_alarm and current_power >= low_alarm :
 
            direction = 'low' if current_power<= low_warning else 'high'
            if direction == 'low':
                low_warning_count+=1
            else:
                high_warning_count+=1

            status = direction+ ' warning'
    
    #Exceeds warning threshold but lower than alarm measures    
    else:
        direction = 'low' if current_power<= low_alarm else 'high'

        if direction == 'low':
                low_alarm_count+=1
        else:
                high_alarm_count+=1

        status =  direction+ ' alarm'

    return current_power, status
        




# Reads parsed JSON output from CLI command, creates a dictionary to write to CSV
def get_information_from_data(data, device) :
    port_name = list(data.keys())[0]

    rx_power_dict = data[port_name]['lane_number']['0 SFP Detail Diagnostics Information']['Rx Power']
    [rx_power, rx_status] = get_txrx_status(rx_power_dict)

    tx_power_dict = data[port_name]['lane_number']['0 SFP Detail Diagnostics Information']['Tx Power']
    [tx_power, tx_status] = get_txrx_status(tx_power_dict)

    serial_number = data[port_name]['serial_number']

    epoch_time = datetime.datetime.now()
    date_time = epoch_time.strftime("%d/%m/%Y %H:%M")

    if device in list(tx_rx_status_dict.keys()) :
        tx_rx_status_dict[device][port_name]= {'RX Power': rx_power, 'RX Power Status': rx_status,'TX Power': tx_power, 'TX Power Status': tx_status, 'Serial Number': serial_number, 'Date Time': date_time } 
    else:
        tx_rx_status_dict[device] = {}
        tx_rx_status_dict[device][port_name]= {'RX Power': rx_power, 'RX Power Status': rx_status,'TX Power': tx_power, 'TX Power Status': tx_status, 'Serial Number': serial_number, 'Date Time': date_time } 



    pprint.pprint(tx_rx_status_dict)


# Takes Python Dictionary, and writes to the CSV files(s)
def write_to_csv(status_dict):
    global high_warning_count, low_warning_count, high_alarm_count, low_alarm_count, fieldnames
    
    csvfile_email_attachment = open(f'email_sfp_txrx_power_report.csv', 'w+')
    writer3 = csv.DictWriter(csvfile_email_attachment, fieldnames= fieldnames)

    writer3.writeheader()


    for device in list(status_dict.keys()) :
        for interface in list(status_dict[device].keys()) :
            status_dict[device][interface].update({'Switch Interface Name': interface})
            status_dict[device][interface].update({'Device Name': device})

            writer.writerow(status_dict[device][interface] )
            
            writer3.writerow(status_dict[device][interface])
    
    writer2.writerow({ 'Date Time': status_dict[device][interface]['Date Time'] , 'Low Warning Count': low_warning_count, 'High Warning Count': high_warning_count, 'Low Alarm Count': low_alarm_count, 'High Alarm Count': high_alarm_count})

    

    csvfile_email_attachment.close()
        
# Closes the CSV files at 'CLEAR_FREQUENCY' interval, and opens new ones with a name appended with the iteration number
def clear_csv_handler():
    global start_time, CLEAR_FREQUENCY, csvfile, csvfile2, writer, writer2, fieldnames, fieldnames2
    

    current_time = time.time()

    print("TRUNCATION CHECK", current_time - start_time, CLEAR_FREQUENCY.seconds)
    if current_time - start_time >= CLEAR_FREQUENCY.seconds :
        global month_counter
        month_counter += 1
        csvfile.close()
        csvfile2.close()


        csvfile = open(f'sfp_txrx_power_report_{month_counter}.csv', 'w+')
        csvfile2 = open(f'sfp_txrx_power_summary_{month_counter}.csv', 'w+')

        writer = csv.DictWriter(csvfile, fieldnames= fieldnames)
        writer.writeheader()

        writer2 = csv.DictWriter(csvfile2, fieldnames= fieldnames2)
        writer2.writeheader()



        start_time = time.time()




# Main task- run every 'TRIGGER_INTERVAL'
def start() :

    clear_csv_handler()

            
    global high_warning_count, low_warning_count, high_alarm_count, low_alarm_count

    high_warning_count = 0
    low_warning_count = 0
    high_alarm_count  = 0
    low_alarm_count   = 0


    print(testbed.devices)

    for device in testbed.devices:
        if device != 'fake-nxos' :

                fi_device = testbed.devices[device]

                #connect to the device
                fi_device.connect(init_exec_commands=[],
                            init_config_commands=[], 
                            log_stdout=True)

                fi_device.execute.timeout = 60
                fi_device.sendline('connect nxos')


                ports = device_port_mapping[device]
                print(ports)


                for port in ports :
                    print(f'show interface {port} transceiver details')
                    raw_output = fi_device.execute(f'show interface {port} transceiver details')

                    parsed_output = fake_nxos.parse('show interface transceiver details', output = raw_output)
                    pprint.pprint(parsed_output)


                    get_information_from_data(parsed_output, device)



    write_to_csv(tx_rx_status_dict)

    #Writing CSV data to storage, instead of waiting for the file to close
    csvfile.flush()
    csvfile2.flush()
    
    email_handler()


    

# Sends the notification email
def email_handler():

    global high_warning_count, low_warning_count, high_alarm_count, low_alarm_count

    current_time = time.time()


        

    elapsed_time = current_time - mail_prev_time

    print("ELAPSED TIME:", mail_prev_time ,elapsed_time)




    print("SENDING EMAIL", current_time- mail_prev_time)
    current_info = f"Devices with \n\n Low Power Warning:{low_warning_count}, High Power Warning:{high_warning_count}, Low Power Alarm:{low_alarm_count}, High Power Alarm:{high_alarm_count}"

    send_email('email_sfp_txrx_power_report.csv', current_info)




#Run first and only once
if '__name__ == __main__' :
    try :

        user_sfp_port_input_handler()
        print(device_port_mapping)

        global start_time
        start_time = time.time()

        #Run the main task once before starting a schedule for it
        start()

    
        #starts the scheduler
        task_scheduler.add_job(start, args=[], trigger='interval', seconds= TASK_FREQUENCY.seconds)

        task_scheduler.start()

    except KeyboardInterrupt :
        csvfile.close()
        csvfile2.close()
        



