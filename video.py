from pytube import YouTube
from util import getFragmentDir
import os
import subprocess

def fetch(url, lang):
  yt = YouTube(url)

  d = getFragmentDir(url, lang)
  file = os.path.join(d, "bg")

  stream = yt.streams.filter(file_extension='mp4', res="360p").first()
  stream.download(output_path=d, filename="bg") 
  subprocess.call("ffmpeg -i " + file + ".mp4 -b:a 192K -vn " + file + ".temp.mp3 && mv " + file + ".temp.mp3 " + file + ".mp3", shell=True)