from flask import Flask, request
from flask import json, g
import requests
import threading
#import gevent
#from gevent import monkey

#import grequests

app = Flask(__name__)
app.config.from_envvar('LCICONFIG')

def writeToFile(filename, data):
    with open(filename,'w') as f:
        json.dump(data,f)
    return

def downloadToFile(url):
    # grequests
#    res = grequests.get(url,stream=True,hooks={'response' : downloadToFile})
#    grequests.send(res,grequests.Pool(1))
    # Requests
    try:
        res = requests.get(url,stream=True)

        # Taken from:
        # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
        print "Status code: " + str(res.status_code)
        if int(res.status_code) == 200:
            with open("builds/archive.tar", 'wb') as f:
                for chunk in res.iter_content(2**20):
                    f.write(chunk)
    except:
        import traceback
        print("downloading failed")
        traceback.print_exc()
        print("="*40)
    return

def grab_git_repo(projectID):
    print "words"
    try:
        pt = '3Xt92RbNewkomrp8GsBb'
        url = 'http://gitlab.com/api/v3/projects/' + str(projectID) + \
                '/repository/archive' + '?private_token=' + pt
        print "URL is: " + url
        print "Downloading the Repo......."
        downloadToFile(url)
    #    subprocess.Popen('wget',url)
        print "Done downloading the repo...."
    except:
        import traceback
        print("Printing or something lame failed.")
        traceback.print_exc()
        print("="*40)
    return

#@app.after_request
#def after_post(response):
#    print "------- grabbing repo -------"
#    grab_git_repo(123)
#    print "------ done grabbing repo -------"
#    return response

@app.route('/',methods=['POST'])
def request_compilation():
    # Use gevent
#    g = gevent.spawn(grab_git_repo,requestJSON["project_id"])
    # Use threading
    try:
        # Thanks to @AKX via #uwsgi (freenode) for helping confirm the below was
        # right
        requestJSON = request.get_json()
        t = threading.Thread(target=grab_git_repo, args=(requestJSON["project_id"],))
        t.start()
#        import time
#        time.sleep(5)
        #    t.join()
        #    g.join()
    except:
        import traceback
        print("starting thread failed.")
        traceback.print_exc()
        print("="*40)
    return ""

@app.route('/',methods=['GET'])
def view_page():
    return "GET request"

if __name__ == '__main__':
    #    monkey.patch_all()
    app.run(host='127.0.0.1')
