import os

#Assigments Exporter config

#A client secret (change this)
CLIENT_SECRET = "39fd2j893f8j823dj82j38dj283d33"

#Auth page common for non all accounts
AUTHORITY = "https://login.microsoftonline.com/common" 

#Your application client id
CLIENT_ID = ""

#Assignments-Exporter app version
APP_VERSION = "v0.1"

#Redirect path
REDIRECT_PATH = "/getAToken"  

#Microsoft endpoint
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'

#Permissions for the client
SCOPE = ["EduAssignments.ReadBasic Tasks.readWrite EduRoster.ReadBasic"]

#Flask session types
SESSION_TYPE = "filesystem"  

