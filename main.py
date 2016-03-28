import flask
import celery
import traceback
import repository
import tasks

app = flask.Flask(__name__)
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

@app.route('/',methods=['POST'])
def request_compilation():
    try:
        # Thanks to @AKX via #uwsgi (freenode) for helping confirm the below was
        # right
        repo = repository.Repository(flask.request)
#        t = threading.Thread(target=grab_git_repo, args=(repo,))
#        t.start()
        res = celery.chain(tasks.grab_git_repo(repo),tasks.extractarchive())
        res.get()
    except:
        printToLog("Failed to start the downloading thread.",1)
    return ""

@app.route('/',methods=['GET'])
def view_page():
    return "GET request (hey john)"

if __name__ == '__main__':
    app.run(host='127.0.0.1')
