from threading import Thread
from subs import run
from util import makeFragmentDir, deleteFragmentDir
from reconstruction import Merge
from video import fetch

def translate(url, lang):
  try:
    threads = []

    try:
      makeFragmentDir(url, lang)
    except:
      return

    m = Merge(url)

    # start subtitle thread
    subThread = Thread(target = run, args = (url, lang, m))
    subThread.start()
    threads.append(subThread)
    
    # download thread
    dThread = Thread(target = fetch, args = (url, lang))
    dThread.start()
    threads.append(dThread)

    for t in threads:
        t.join()
  finally:
    None