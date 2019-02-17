from flask import Flask, request, send_file, render_template
from stream import translate
from util import getFragmentDir
import os
import time
app = Flask(__name__, static_folder='public/build/static', template_folder="public")

@app.route('/')
def index():
    return render_template('build/index.html')

@app.route('/download')
def download():
  video_id = request.args.get('id', '')
  lang = request.args.get('lang', '')
  url = "https://www.youtube.com/watch?v=" + video_id
  translate(url, lang)
  file = os.path.join(getFragmentDir(url, lang), "bg.complete.mp4")
  while not os.path.exists(file):
    time.sleep(0.01)
  return send_file(file, conditional=True, attachment_filename=(video_id + ".mp4"))
  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
