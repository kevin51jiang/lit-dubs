from pytube import YouTube
import hashlib
import os
import re
import shutil

mainLanguages = ['en', 'es', 'fr', 'jp', 'zh-TW']

def getCaptions(url):
  #captions
  yt = YouTube(url)

  for language in mainLanguages:
    caption = yt.captions.get_by_language_code(language)
    if caption != None:
      break
  if caption == None:
    caption = yt.captions.all()[0]
  caption = caption.generate_srt_captions() 
  caption = re.sub('<[^<]+?>', '', caption)
  caption = ''.join([i if ord(i) < 128 else '' for i in caption])
  return caption

def getFragmentDir(url, lang):
  dirname = os.path.split(os.path.abspath(__file__))
  return os.path.join(os.path.sep, dirname[0], "fragments", hashlib.md5((lang + "://" + url).encode()).hexdigest())

def makeFragmentDir(url, lang):
  os.makedirs(getFragmentDir(url, lang))
  os.makedirs(os.path.join(getFragmentDir(url, lang), 'fg'))
 
def deleteFragmentDir(url):
  None
  # shutil.rmtree(getFragmentDir(url))