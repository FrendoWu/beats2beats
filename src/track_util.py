import sys
import midi
import numpy as np
import pandas as pd 
from util import _cal_var, _read_general_midi

lowerBound = 21
upperBound = 108

def track_to_matrix(track, resolution):

    step = resolution / 8
    track = get_note(track)
    statematrix = []
    span = upperBound - lowerBound + 1 # 似乎是音高?
    state = [0 for x in range(span)]
    state[track[0].pitch-lowerBound] = 1

    time = 0
    for evt in track[1:]:
        tick = evt.tick
        while time + tick >= step:
            statematrix.append(state.copy())
            time = 0
            tick = tick - step + time 
        if isinstance(evt, midi.NoteEvent):
            if (evt.pitch < lowerBound) or (evt.pitch >= upperBound):
                pass
                # print "Note {} at time {} out of bounds (ignoring)".format(evt.pitch, time)
            else:
                if isinstance(evt, midi.NoteOffEvent) or evt.velocity == 0:
                    state[evt.pitch-lowerBound] = 0
                else:
                    state[evt.pitch-lowerBound] = 1
            time = time + tick
    return statematrix

def get_program_drum(track):
    '''
    从打击乐track中提取乐器表
    '''
    program = set()
    for event in track:
        if isinstance(event, midi.NoteOnEvent) or isinstance(event, midi.NoteOffEvent):
            try:
                program.add(event.data[0])
            except AttributeError:
                pass
    return list(program)

def get_channel_program(track):
    """
    得到Track的ProgramChangeEvent中的channel和program
    """
    idx, program = _read_general_midi()
    for event in track:
        if isinstance(event, midi.ProgramChangeEvent):
            if event.channel == 9:
                print("Channel - 9(not in GM): Percussion")
                # print(get_program_drum(track))
            else:
                print("Channel - " + str(event.channel) + \
                    ": " + program[idx.index(event.data[0])])
            return [event.channel, event.data[0]]

# def track_to_matrix(track):
#     """
#     把single track变为一个[[time,frequence,intensity],[...]...]的矩阵
#     #添加了tempo,channel,program => [time,frequence,intensity, tempo, channel, program]
#     """
#     if isinstance(track, midi.Track):
#         pass
#     else:
#         print("Input not a midi.Track!")
#         exit
    
#     channel, program = get_channel_program(track)
#     tempo = _get_tempo(track)
#     outputs = []
#     time = 0
#     for event in track:
#         output = []
#         #channel==9时，frequency无效。
#         if isinstance(event, midi.NoteOnEvent) and event.data[1] > 0:
#             # True NoteOn Event
#             time = time + event.tick
#             output = [time, event.data[0], event.data[1], tempo, channel, program]
#             if channel == 9: output[-1] = event.data[0]
#             outputs.append(output)

#         elif isinstance(event, midi.NoteOffEvent) or \
#             (isinstance(event, midi.NoteOnEvent) and event.data[1] == 0):
#             # True NoteOff Event
#             time = time + event.tick
#             output = [time, event.data[0], 0, tempo, channel, program]
#             if channel == 9: output[-1] = event.data[0]
#             outputs.append(output)
            
#     return outputs

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
        idx = _cal_var(res)
        if idx > tmp and idx % 2 == 0:
            tmp = idx
    return matrix[:tmp]


def set_program(track, channel=0, value=0):
    """
    设置一个自己写的Track的音色
    value是音色
    对于Percussion, value没有意义, 随便输
    """

    if channel != 9:
        # is not drum
        ProgramChangeEvent = \
            midi.ProgramChangeEvent(channel=channel, data=[value])
        track.insert(0, ProgramChangeEvent)   
        return track
    else:
        # is drum
        ProgramChangeEvent = \
            midi.ProgramChangeEvent(channel=9)
        track.insert(0, ProgramChangeEvent)
        for idx, event in enumerate(track):
            if isinstance(event, midi.NoteEvent):
                track[idx].channel = 9
    return track

def get_note(track):
    """
    截取Note开始的Events
    返回一段Track
    """
    start_idx = len(track)
    for idx, event in enumerate(track):
        if isinstance(event, midi.NoteEvent):
            start_idx = idx
            break
    sub_track = midi.Track()
    sub_track = track[start_idx:]
    return sub_track

def set_note(track, notes):
    """
    调用这个方法的track本身应该没有Note
    """
    track = track + notes
    return track

# ------------------------Private Method Here------------------ #

def _get_tempo(track):
    '''
    遍历track, 通过midi.SetTempoEvent得到tempo
    '''
    for event in track:
        if isinstance(event, midi.SetTempoEvent): 
            return event.get_bpm()
    return 0 # 当前Track没有SetTempoEvent

def _get_time_signature(track):
    """
    遍历track, 通过midi.TimeSignatureEvent得到time signature
    """
    for event in track:
        if isinstance(event, midi.TimeSignatureEvent):
            return event.data
    return 0 # 当前Track没有TimeSignatureEvent

def _set_tempo(track, value):
    """
    设置一个自己写的Track的Tempo
    """
    SetTempoEvent = midi.SetTempoEvent(bpm=value)
    track.insert(0, SetTempoEvent)
    return track

def _set_time_signature(track, data):
    """
    设置一个自己写的Track的time signature
    """
    TimeSignatureEvent = midi.TimeSignatureEvent(data=data)
    track.insert(0, TimeSignatureEvent)
    return track

def demo_pattern():
    pat = midi.read_midifile("../track/Stan_1_Violin.mid")
    resolution = pat.resolution
    track = pat[1]
    mat = track_to_matrix(track, resolution)
    print(len(mat[0]))
    np.savetxt("./state_matrix.txt", np.array(mat))
    return "sbpp"

if __name__ == '__main__':
    demo_pattern()