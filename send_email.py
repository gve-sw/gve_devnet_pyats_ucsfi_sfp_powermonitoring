
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




from env_vars import *


HOST_ADDRESS = 'smtp.gmail.com'
HOST_PORT = 587


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import ssl
from email.mime.text import MIMEText


#Called in the main function to send attachment with body text to the specified emails
def send_email(filepath, body_text):


    #Connection with the server
    context = ssl._create_unverified_context()



    with smtplib.SMTP(HOST_ADDRESS, HOST_PORT) as server:

        server.starttls(context= context)
        server.ehlo()
        server.login(MY_ADDRESS, MY_PASSWORD)

        #Creating a MIMEMultippart Object
        message = MIMEMultipart()

        #Setting up the MIMEmultipart object header
        message['FROM'] = MY_ADDRESS
        message['TO'] = RECIPIENT_ADDRESS
        message['Subject'] = 'Mandiri SFP Status Notification'

        #Creating a MIMEText Object
        textPart = MIMEText(f"{body_text}")

        #Creating a MIMEApplication Object
        # filename = "/Users/ltyagi/Desktop/Projects/devnetCases/Case03837529/data.json"
        filePart = MIMEApplication(open(filepath, 'rb').read(), Name = filepath)
        filePart['Content-Disposition'] = 'attachment'; filename = "%s" % filepath

        #Parts attachment
        message.attach(textPart)
        message.attach(filePart)

        #Send email and close connection
        server.send_message(message)
