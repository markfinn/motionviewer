import os
from flask import Flask, render_template, request, redirect, current_app, abort
import ConfigParser
from functools import wraps
from urlparse import urlparse
import json
import re

def secure_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if request.is_secure or urlparse(request.url).netloc.startswith('localhost:'):
                return fn(*args, **kwargs)
        else:
                return redirect(request.url.replace("http://", "https://"))
        
        abort(500)
            
    return decorated_view



config = ConfigParser.SafeConfigParser()
config.read('settings.conf')

videoPath = config.get('config', 'video_path')

assert os.path.isdir(videoPath), 'bad video path'
        
app = Flask(__name__)


def groupFiles(path, interval=1000000, minimum=None, maximum=None):
  r=re.compile(r'motion-(\d)-(\d{14})-\d+.avi')
  f = []
  for (dirpath, dirnames, filenames) in os.walk(path):
    f.extend(filenames)
    break

  periods = {}
  for n in f:
    m=r.match(n)
    if m:
      t,w,nn = (long(m.group(2)), int(m.group(1)), os.path.join(path, n))
      if (minimum==None or t >= minimum) and (maximum==None or t <= maximum):
        i=str(t//interval)
        if i not in periods:
          p=[]
          periods[i]=p
        else:
          p=periods[i]
          
        p.append((t,w,nn))
  return periods

@app.route('/')
#@secure_required
def index():

  files = groupFiles(videoPath)
  
  return render_template('index.html', periods=files.keys())

@app.route('/interval/<interval>')
#@secure_required
def interval(interval):

  files = groupFiles(videoPath)
  return render_template('timeline.html', interval=interval, files=sorted(files[interval]))

if __name__ == '__main__':
    app.run(debug=True)
