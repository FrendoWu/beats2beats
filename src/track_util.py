import sys
import midi
import numpy as np
import pandas as pd 
from util import cal_var
from midi_util import save_midfile, read_midifile

def get_channel_program(track):
    """
    得到Track的ProgramChangeEvent中的channel和program
    """
    for event in track:
        if isinstance(event, midi.ProgramChangeEvent):
            return [event.channel, event.data[0]]

def get_tempo(track):
    '''
    遍历track, 通过midi.SetTempoEvent得到tempo
    '''
    for event in track:
        if isinstance(event, midi.SetTempoEvent): 
            return event.get_bpm()

def track_to_matrix(track):
    """
    把single track变为一个[[time,frequence,intensity],[...]...]的矩阵
    #添加了tempo,channel,program => [time,frequence,intensity, tempo, channel, program]
    """
    if isinstance(track, midi.Track):
        pass
    else:
        print("Input not a midi.Track!")
        exit
    
    channel, program = get_channel_program(track)
    tempo = get_tempo(track)
    outputs = []
    time = 0
    for event in track:
        output = []
        #channel==9时，frequency无效。
        if isinstance(event, midi.NoteOnEvent) and event.data[1] > 0:
            # True NoteOn Event
            time = time + event.tick
            output = [time, event.data[0], event.data[1], tempo, channel, program]
            if channel == 9: output[-1] = event.data[0]
            outputs.append(output)

        elif isinstance(event, midi.NoteOffEvent) or \
            (isinstance(event, midi.NoteOnEvent) and event.data[1] == 0):
            # True NoteOff Event
            time = time + event.tick
            output = [time, event.data[0], 0, tempo, channel, program]
            if channel == 9: output[-1] = event.data[0]
            outputs.append(output)
            
    return outputs

def matrix_to_track(matrix):
    """
    把上述matrix变为一段track
    matrix每一行的信息[time,frequence,intensity, tempo, channel, program]
    """

    if(len(matrix) <= 0):
        print('size error')
        exit

    track = midi.Track()
    #从matrix中提取channel和program
    channel = matrix[0][4]
    program = matrix[0][5]

    program_change = \
        midi.ProgramChangeEvent(tick=0, channel=channel, data=[program])
    track.append(program_change)

    time = 0
    for term in matrix:
        # ! -- 如果需要进行计算的话,打击乐的乐器可能会出错 -- !
        tmp_data = [int(term[1]),int(term[2])] if channel != 9 else [int(term[5]), int(term[2])]
        event = midi.NoteOnEvent(tick=int(term[0]-time), channel=channel, data=tmp_data)
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
    value是一个二元组[isDrum, program]
    """

    #添加了打击乐的情况
    if not value[0]:
        for idx, event in enumerate(track):
            if isinstance(event, midi.ProgramChangeEvent):
                track[idx].data[0] = value[1]
                break
    else:
        for idx, event in enumerate(track):
            if isinstance(event, midi.ProgramChangeEvent):
                track[idx].channel = 9
            elif isinstance(event, midi.NoteOnEvent) or isinstance(event, midi.NoteOffEvent):
                track[idx].channel = 9
                track[idx].data[0] = value[1]

    return track
    
def demo_pattern(song):
    midiname = "../track/" + song + ".mid"
    pattern = read_midifile(midiname)
    matrix = track_to_matrix(pattern[1])
    matrix = sort_matrix(matrix)
    beat = find_pattern(matrix)
    track = matrix_to_track(beat)
    
    fragement = midi.Pattern(resolution=pattern.resolution, format=pattern.format)
    fragement.append(pattern[0])
    fragement.append(track)
    save_midfile(fragement, "../data/"+song+".mid")

if __name__ == '__main__':
    #song = sys.argv[1]
    song = 'Stan_9_drum'
    demo_pattern(song)