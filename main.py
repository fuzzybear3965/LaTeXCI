from flask import Flask, request
# from flask import json, g
import requests
import threading
import traceback
from cryptography.fernet import Fernet
import ConfigParser
import base64
import session, repository
import os,tarfile,errno

app = Flask(__name__)
app.config.from_envvar('LCICONFIG')

def writeToFile(filename, data):
    with open(filename,'w') as f:
        json.dump(data,f)
    return

def printToLog(message,PRINT_STACK):
    print("\n"+"!"*40)
    print message
    if PRINT_STACK == 1:
        traceback.print_exc()
    print("!"*40+"\n")
    return

def extract_archive(relpath):
    fileroot = os.path.splitext(os.path.basename(relpath))[0] # ignore extension
    subdir = os.path.split(relpath)[0] # ignore tail
    tar = tarfile.open("relpath")
    extractpath = os.path.join(subdir,fileroot)
    # Make the directory if it doesn't exist
    if not os.path.exists(extractpath):
        try:
            os.makedirs(os.path.dirname(extractpath))
        except OSError as exc: # protects against races
            if exc.errno != errno.EEXIST:
                raise
    try:
        tar.extractall(extractpath)
        printToLog("Successfully extracted archive to: " + extractpath, 0)
    except:
        printToLog("Failed to extract archive.",1)
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
            # from:
            # http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
            filename = os.path.join("builds",\
                    repository.json["project"]["name"],\
                    repository.json["project"]["default_branch"],\
                    repository.json["after"]+".tar")
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # protects against race conds
                    if exc.errno != errno.EEXIST:
                        printToLog("Failed to make the directory!",1)
                        raise
            printToLog("Made the directory.",0)
            with open(filename,"w") as f:
                for chunk in res.iter_content(2**20):
                    f.write(chunk)
            printToLog("Downloaded something.",0)
        printToLog("Downloaded repository archive just fine.",0)
        extract_archive(filename)
    except:
        printToLog("Failed to download the file.",1)
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
