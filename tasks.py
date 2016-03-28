# Celery tasks
import celery
import session, repository
import os,tarfile,errno
from main import *
import requests

celery = celery.Celery('tasks',broker='amqp://user:password@localhost//')

@celery.task(name='tasks.download_repo')
def grab_git_repo(repository):
    try:
#        printToLog("I'm grabbing the repo.",0)
        s = session.Session()
#        printToLog("I've made a session object with token " + s.token,0)
        url = 'https://gitlab.com/api/v3/projects/' + \
                str(repository.json["project_id"]) + \
                '/repository/archive' + '?private_token=' + s.token
#        printToLog("The url is: " + url,0)
        res = requests.get(url,stream=True)
        printToLog("I have the HTTP response.",0)
        # below taken from:
        # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
        if int(res.status_code) == 200:
            # from:
            # http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output
            printToLog("We're good to grab the repository.",0)
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
            with open(filename,"w") as f:
                for chunk in res.iter_content(2**20):
                    f.write(chunk)
        printToLog("Downloaded repository archive just fine.",0)
        return filename
    except:
        printToLog("Failed to download the file.",1)
        return
    
@celery.task(name='tasks.extract_repo')
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

