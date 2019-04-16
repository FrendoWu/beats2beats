import sys
import midi
import numpy as np
import pandas as pd 
from util import cal_var
from midi_util import save_midfile, read_midifile

def track_to_matrix(track):
    """
    把single track变为一个[[time,frequence,intensity],[...]...]的矩阵
    """
    if isinstance(track, midi.Track):
        pass
    else:
        print("Input not a midi.Track!")
        exit
  
    outputs = []
    time = 0
    for event in track:
        output = []
        if isinstance(event, midi.NoteOnEvent) and event.data[1] > 0:
            # True NoteOn Event
            time = time + event.tick
            output = [time, event.data[0], event.data[1]]
            outputs.append(output)
        elif isinstance(event, midi.NoteOffEvent) or \
            (isinstance(event, midi.NoteOnEvent) and event.data[1] == 0):
            # True NoteOff Event
            # ! -- 这里也可能要改动 -- !
            time = time + event.tick
            output = [time, event.data[0], 0]
            outputs.append(output)
           
    return outputs

def matrix_to_track(matrix, program=0):
    """
    把上述matrix变为一段track
    """

    #
    # ! -- 需要处理,音色和速度的信息还没弄进来 -- !
    # 

    track = midi.Track()

    program_change = \
        midi.ProgramChangeEvent(tick=0, channel=1, data=[program])
    track.append(program_change)

    time = 0
    for term in matrix:
        event = midi.NoteOnEvent(tick=int(term[0]-time), channel=1, data=[int(term[1]),int(term[2])])
        track.append(event)
        time = term[0]
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    return track

def sort_matrix(matrix):
    """
    整理Track_Matrix
    将同一时间的频率按大小排序
    """
    dt = pd.DataFrame(matrix)
    dt = dt.sort_values(by=[0,1], ascending=(True, True))
    matrix = dt.values
    return matrix

def find_pattern(matrix): 
    """
    在一段track中找到重复模式
    这里的pattern是模式的意思
    """

# ! -- 我个人觉得这个方法有点垃圾,是否沿用这个思路有待商榷 -- !

    matrix = np.array(matrix)
    freq = matrix[:,1] # 第二列为频率, 通过频率来找重复模式
    tmp = 0
    for i in range(1,len(freq)):
        res = freq[i:] - freq[:-i] # 位移
        idx = cal_var(res)
        if idx > tmp and idx % 2 == 0:
            tmp = idx
    return matrix[:tmp]

def change_program(track, value):
    """
    修改一个Track的音色
    """

    # ! -- 可能有问题 -- !

    for idx, event in enumerate(track):
        if isinstance(event, midi.ProgramChangeEvent):
            channel = track[idx+1].channel
            track[idx] = midi.ProgramChangeEvent(tick=0, channel=channel, data=[value])
    return track

def get_program(pattern):
    """
    得到仅包含一个Track的midi.Pattern的ProgramChangeEvent
    """
    for track in pattern:
        for event in track:
            if isinstance(event, midi.ProgramChangeEvent):
                return event.data

def demo_pattern(song):
    midiname = "../track/" + song + ".mid"
    pattern = read_midifile(midiname)
    program = get_program(pattern)
    
    matrix = track_to_matrix(pattern[1])
    matrix = sort_matrix(matrix)
    beat = find_pattern(matrix)
    track = matrix_to_track(beat, program[0])

    fragement = midi.Pattern(resolution=pattern.resolution, format=pattern.format)
    fragement.append(pattern[0])
    fragement.append(track)
    save_midfile(fragement, "../data/"+song+".mid")

if __name__ == '__main__':
    song = sys.argv[1]
    demo_pattern(song)