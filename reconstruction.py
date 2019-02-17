from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
from pydub.utils import ratio_to_db

import os
import util
import time
import subprocess

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
  trim_ms = 0 # ms
  assert chunk_size > 0 # to avoid infinite loop
  while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
      trim_ms += chunk_size
  return trim_ms

def trim(sound):
  start_trim = detect_leading_silence(sound)
  end_trim = detect_leading_silence(sound.reverse())
  duration = len(sound)    
  return sound[start_trim:duration-end_trim]

def removeVocal(sound_stereo):
  sound_monoL = sound_stereo.split_to_mono()[0]
  sound_monoR = sound_stereo.split_to_mono()[1]
  sound_monoR_inv = sound_monoR.invert_phase()
  sound_CentersOut = sound_monoL.overlay(sound_monoR_inv)
  return sound_CentersOut.low_pass_filter(1300)


def speed_change(sound, speed=1.0):
  # Manually override the frame_rate. This tells the computer how many
  # samples to play per second
  sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
      "frame_rate": int(sound.frame_rate * speed)
  })
  # convert the sound with altered frame rate to a standard frame rate
  # so that regular playback programs will work right. They often only
  # know how to play audio at standard frame rate (like 44.1k)
  return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)


def build(base, source, start, length):
  l = len(source)
  ratio = l/length 
  # speed it up if necessary
  speech = source.speedup(ratio * 1.05) if ratio > 1 else source
  # set volume to max possible volume
  speech = speech.apply_gain(ratio_to_db(source.max_possible_amplitude / source.max))
  gain = min(0, ratio_to_db(speech.max/base[start:(start+l)].max))
  return base.overlay(speech, start, gain_during_overlay=gain)


class Merge:
  url = None
  base = None
  def __init__(self, url):
    self.url = url
    return
  def init(self, parts, lang):
    fragmentRoot = util.getFragmentDir(self.url, lang)
    fragDir = os.path.join(fragmentRoot, 'fg')
    lastEnd = 0
    sourceFile = os.path.join(fragmentRoot, 'bg.mp3')
    while not os.path.exists(sourceFile):
      time.sleep(0.01)
    self.base = AudioSegment.from_mp3(sourceFile)
    self.base = self.base.overlay(removeVocal(self.base), 0, gain_during_overlay = -20)
    for p in parts:
      try:
        print(p)
        splitted = p.split("-")
        start = int(splitted[0])
        end = int(splitted[1])
        f = os.path.join(fragDir, p + '.mp3')
        # wait for file to be saved
        while not os.path.exists(f):
          time.sleep(0.01)
        start = max(start, lastEnd)
        length = end - start
        source = trim(AudioSegment.from_file(f, format="mp3"))
        l = len(source)
        if l <= length:
          length = l
        else:
          maxSpeedup = min(1.75, l/length)
          length = l/maxSpeedup
        self.base = build(self.base, source, start, length)
        lastEnd = start + length
      except:
        None
    outputFile = sourceFile.replace(".mp3", ".wav")
    self.base.export(outputFile, format="wav")
    subprocess.call("ffmpeg -i " + sourceFile.replace(".mp3", ".mp4") + " -i " + outputFile + " -c:v copy -map 0:v:0 -map 1:a:0 " + sourceFile.replace(".mp3", ".complete.mp4"), shell=True)
