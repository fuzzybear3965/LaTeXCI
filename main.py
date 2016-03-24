from flask import Flask, request
# from flask import json, g
import requests
import threading
import traceback
from cryptography.fernet import Fernet
import ConfigParser
import base64
import session, repository

app = Flask(__name__)
app.config.from_envvar('LCICONFIG')

def writeToFile(filename, data):
    with open(filename,'w') as f:
        json.dump(data,f)
    return

def printToLog(message,PRINT_STACK):
    print("!"*40)
    print message
    if PRINT_STACK == 1:
        traceback.print_exc()
    print("!"*40)
    return

def grab_git_repo(repository):
    try:
        s = session.Session()
        url = 'http://gitlab.com/api/v3/projects/' + \
                str(repository.json["project_id"]) + \
                '/repository/archive' + '?private_token=' + s.token
        res = requests.get(url,stream=True)
        # below taken from:
        # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
        if int(res.status_code) == 200:
            with open("builds/" + "archive" + ".tar", 'wb') as f:
                for chunk in res.iter_content(2**20):
                    f.write(chunk)
        printToLog("Downloaded repository archive just fine.",0)
    except:
        printToLog("Failed to launch the downloadToFile() function.",1)
    return

@app.route('/',methods=['POST'])
def request_compilation():
    try:
        # Thanks to @AKX via #uwsgi (freenode) for helping confirm the below was
        # right
        repo = repository.Repository(request)
        t = threading.Thread(target=grab_git_repo, args=(repo,))
        t.start()
    except:
        printToLog("Failed to start the downloading thread.",1)
    return ""

@app.route('/',methods=['GET'])
def view_page():
    return "GET request (hey john)"

if __name__ == '__main__':
    # Initialize cryptographic key
    app.run(host='127.0.0.1')
