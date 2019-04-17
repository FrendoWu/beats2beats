import midi
import sys

from midi_util import get_resolution, get_tempo, get_time_signature, \
    read_midifile, save_midfile, set_resolution, set_tempo, set_time_signature
from track_util import get_note, get_channel_program, \
    set_note, set_program

"""
标准化单音轨的文件,格式如下

track(0):
 - 设置tempo
 - 设置time_signature

track(1):
 - 设置音色
 - 加入音乐
"""
filename = sys.argv[1]
midifile = "../track/" + filename
pattern = read_midifile(midifile)

resolution = get_resolution(pattern)
bpm = get_tempo(pattern)
time_signature = get_time_signature(pattern)
note = get_note(pattern[1])
program = get_channel_program(pattern[1]) # [channel, program]

# 输出Pattern的初始化
pat = midi.Pattern(tracks=[[],[]])

pat = set_resolution(pat, resolution)
pat = set_tempo(pat, bpm)
pat = set_time_signature(pat, time_signature)
pat[0].append(midi.EndOfTrackEvent(tick=0, data=[]))

pat[1] = set_program(pat[1], channel=program[0], value=program[1])
pat[1] = set_note(pat[1], note)

save_midfile(pat, "../std_track/std_"+filename)