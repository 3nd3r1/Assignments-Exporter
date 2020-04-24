import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
import msal
import app_config
import json

app = Flask(__name__)
Session(app)

#Viljamin refercances
#session['user'].get("oid") -> id   

@app.template_filter("datetime")
def datetime(datestr):
    return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S%z")
@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("logged"))
    return render_template('index.html', app_version=app_config.APP_VERSION, msal_version=msal.__version__)

@app.route("/logged")
def logged():
    if not session.get("user"):
        return redirect(url_for("index"))
    return render_template('logged.html', session=session._get_current_object(), tokens=session.get("token_cache"), user=session.get("user"))

@app.route("/launch")
def launch():
    return render_template("launch.html", msal_version=msal.__version__)

@app.route("/auth", methods=['POST'])
def auth():
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    session["exportto"] = request.form.get('exportto')
    session["update"] = request.form.get('update')
    return redirect(auth_url,code=302)

@app.route(app_config.REDIRECT_PATH) 
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("index"))  
    if "error" in request.args: 
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,  
            redirect_uri=url_for("authorized", _external=True))
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect(url_for("launched"))

def logout():
    session.clear()  
    return redirect(  
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

@app.route("/launched")
def launched():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("index"))
    class_data = requests.get("https://graph.microsoft.com/beta/education/classes",
        headers={'Authorization': 'Bearer ' + token['access_token'], 'Accept':'application/json'}
        ).json()
    skips=0
    sent=0
    #for every class
    for a in class_data["value"]:
        #get assignments
        assignment_data = requests.get("https://graph.microsoft.com/beta/education/classes/"+a["id"]+"/assignments", 
               headers = {'Authorization': 'Bearer ' + token['access_token'], 'Accept':'application/json'}).json()

        #Todo add
        if(session.get("exportto")=="todo"):
            tasks_data = requests.get("https://graph.microsoft.com/beta/me/outlook/tasks",
                                    headers = {'Authorization': 'Bearer ' + token['access_token'], 'Accept':'application/json'}).json()
            tasks = [i["subject"] for i in tasks_data["value"]]

            #for every assignment
            for b in assignment_data["value"]:
                #If in tasks or submitted
                if(b['displayName'] in tasks or len(b['submissions'])):
                    taskskips += 1
                    continue
                data = {
                        "subject": b['displayName'],
                        "startDateTime": 
                            {
                            "dateTime": b['assignedDateTime'],
                            "timeZone": "Eastern European Summer Time"
                            },
                        "dueDateTime":  
                            {
                            "dateTime": b['dueDateTime'],
                            "timeZone": "Eastern European Summer Time"
                            }
                        } 
                #add task
                requests.post("https://graph.microsoft.com/beta/me/outlook/tasks",data=json.dumps(data),
                              headers = {'Authorization': 'Bearer ' + token['access_token'],'Content-type': 'application/json','Prefer': 'outlook.timezone="Pacific Standard Time"', 'Content-length': '276'}).json();
                tasksent +=1
                result_data=[{"skips":skips,"tasksent":tasksent}]
                return render_template('launched.html', result=result_data, update=session.get("update"), exportto=session.get("exportto"), user=session.get("user"))

        #calender add
        if(session.get("exportto")=="calender"):
            return render_template('launched.html', result="moro", update=session.get("update"), exportto=session.get("exportto"), user=session.get("user"))

        #text
        if(session.get("exportto")=="text"):
            return render_template('launched.html', result=assignment_data["value"], update=session.get("update"), exportto=session.get("exportto"), user=session.get("user"))
    


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache() 
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_url=_build_auth_url)  

if __name__ == "__main__":
    app.secret_key = app_config.CLIENT_SECRET
    app.config['SESSION_TYPE'] = app_config.SESSION_TYPE
    app.run()

