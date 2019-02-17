#coding=utf-8
from gtts import gTTS
from google.cloud import translate, texttospeech
from pydub import AudioSegment
import html
import srt, sys, os.path
import util
import urllib3
from threading import Thread
from queue import Queue

client = texttospeech.TextToSpeechClient()

def timeCheck(a):
  millis = 0
  millis += a.seconds * 1000
  millis += a.microseconds / 1000
  return str(int(millis))

def makeFiles(url, a, lang):
  timeStamp = timeCheck(a.start) + "-" + timeCheck(a.end)
  tmpName = os.path.join(util.getFragmentDir(url, lang), "fg", timeStamp + ".mp3.tmp")
  try:
    translate_client = translate.Client()
    myPhrase = a.content.replace(".", "")
    #smh
    urllib3.disable_warnings()
    txt = html.unescape(translate_client.translate(myPhrase, target_language=lang)['translatedText'])
    synthesis_input = texttospeech.types.SynthesisInput(text=txt)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=lang,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    with open(tmpName, 'wb') as out:
      out.write(response.audio_content)
    # tts = gTTS(text = html.unescape(
    #                       translate_client.translate(
    #                           myPhrase,
    #                           target_language=lang)['translatedText']), lang = lang)
    # tts.save(tmpName)
  except:
    AudioSegment.silent(1000).export(tmpName, format="mp3")
  os.rename(tmpName, tmpName[0:-4])

  return timeStamp

class ThreadRunner:
  def __init__(self, url, subs, lang):
    while not subs.empty():
      sub = subs.get()
      makeFiles(url, sub, lang)

def runThread(url, subs, lang):
  ThreadRunner(url, subs, lang)

def run(url, lang, merge):
  mySubs = list(srt.parse(util.getCaptions(url)))
  timestamps = []
  threads = []
  subs = Queue()
  for i in mySubs:
    timestamps.append(timeCheck(i.start) + "-" + timeCheck(i.end))
    subs.put(i)
  for i in range(0, 6):
    t = Thread(target = runThread, args = (url, subs, lang))
    t.start()
    threads.append(t)
  merge.init(timestamps, lang)
  for t in threads:
      t.join()
