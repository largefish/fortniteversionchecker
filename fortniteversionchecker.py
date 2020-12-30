import smtplib
import requests
import time
from datetime import datetime
from requests.exceptions import ConnectionError
import json
import ast

def emailnotify(subject, body):
    fromaddress = "youremail@email.com" 
    toaddresses  = ["addresses@mail.com", "to@mail.com", "notify@mail.com"]

    #The From: and To: below is used to have the from and to show up in the email message headers
    #msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (fromaddress, toaddress, subject,  body)
    msg = "Subject: %s\n\n%s" % (subject, body)

    username = "username"
    password = "password"

    #Settings to log into Yahoo server to send notification email
    server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddress, toaddresses, msg)
    server.quit()    

def getversion():
    r = requests.get("https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/version")
    jsonresponse = r.json()

    build = jsonresponse["build"]
    version = jsonresponse["version"]
    branch = jsonresponse["branch"]
    
    
    version = {
            "build": build,
            "version": version,
            "branch": branch
            }
    return version

def log(currentversion):
    logfile = "/home/username/fortnitechecker/versionlog.txt"

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    f = open(logfile, "a")
    f.write(now + " EST    " + currentversion + "\n")
    f.close()

    with open(logfile, "r") as f:
        rows = f.readlines()
    f.close()

    #Cron runs this script every 24 hours. 7 lines is 7 days of logs
    if len(rows) > 7:
        rows = rows[-7:]
        f = open(logfile, "w")
        for r in rows:
            f.write(r)
        f.close()

versionfile = open("/home/username/fortnitechecker/mostrecentversion.txt", "r")

contents = versionfile.read().strip()
versionfile.close()

previousversion = ast.literal_eval(contents)

currentversion = getversion()

if currentversion["branch"] != previousversion["branch"]:
    subject = "Fortnite Branch Changed"
    body = "Previous Version: " + str(previousversion) + "\nCurrent Version: " + str(currentversion)
    emailnotify(subject, body)
elif currentversion["version"] != previousversion["version"]:
    subject = "Fortnite Version Changed"
    body = "There is a new update available for Fortnite. See details below\n\n\nPrevious Version: " + str(previousversion) + "\nCurrent Version: " + str(currentversion)
    emailnotify(subject, body)
elif currentversion["build"] != previousversion["build"]:
    subject = "Fortnite Build Changed"
    body = "There is a new update available for Fortnite. See details below\n\n\nPrevious Version: " + str(previousversion) + "\nCurrent Version: " + str(currentversion)
    #Disabled build notify since updated build number != new update
    #emailnotify(subject, body)
else:
    subject = "All good"
    body = "The reported Fortnite version matches last checked"
    #Disabled so we don't get spammed
    #emailnotify(subject, body)

versionstring = "{\"build\": \"" + currentversion["build"] + "\", \"version\": \"" + currentversion["version"] + "\", \"branch\": \"" + currentversion["branch"] + "\"}"
versionfile = open("/home/pi/fortnitechecker/mostrecentversion.txt", "w")
versionfile.write(versionstring)
versionfile.close()

log(versionstring)
