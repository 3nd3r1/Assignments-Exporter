import os

#Assigments Exporter config

#A client secret (change this)
CLIENT_SECRET = "8dsua883m39d9m3i9mfm93m9fasd"

#Auth page common for non all accounts
AUTHORITY = "https://login.microsoftonline.com/common" 

#Your application client id
CLIENT_ID = "aa93cfb0-41f1-47d3-b93a-8e04a43da5bc"

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

