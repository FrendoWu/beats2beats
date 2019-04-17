import midi
import sys
from util import _read_general_midi
from track_util import _get_tempo, _get_time_signature, \
    _set_tempo, _set_time_signature

# 只是为了demo使用
from track_util import get_note, get_channel_program, \
    set_note, set_program

'''
    Tempo - 一个拍的时间，比如120BPM表示1min120beats，所以是500,000ms一个beat
    Resolution - 一个beat含有的tick数，tick是midi中最小的时间单位（相对的，由Tempo和Resolution定出绝对值）。如Resolution为1,000，则一个tick500ms
    Time Signature - 拍号，在midi中不会影响到Tempo
'''

def gen_multitracks(pattern):
    """
    将一个midi.Pattern类分成各个音轨
    """
    sub_patterns = []
    for track in pattern:
        _sub_pattern = midi.Pattern(
            format=pattern.format, 
            resolution=pattern.resolution)
        _sub_pattern.append(pattern[0]) # basic info, usage not sure
        for idx, event in enumerate(track):
            #分离track
            if isinstance(event, midi.ProgramChangeEvent):
                try:
                    channel = event.channel
                    _sub_pattern.append(track)
                    #判断是旋律音色还是打击乐
                    program = event.data if channel != 9 else "Percusiion"
                    sub_pattern = {
                        'pattern': _sub_pattern,
                        'channel': channel,
                        'program': program  
                    }
                    #分离track
                    sub_patterns.append(sub_pattern)
                    break
                except AttributeError:
                    pass
    return sub_patterns
    
def read_midifile(midiname):
    """
    读取一个mid文件
    返回一个midi.Pattern类
    """
    return midi.read_midifile(midiname)

def save_midfile(pattern, midiname):
    """
    保存一个mid文件
    """
    midi.write_midifile(midiname, pattern)

def save_multitracks(multitracks, root="../track/", name="untitled"):
    """
    将multitracks保存
    """
    idx, program = _read_general_midi()
    for track in multitracks:
        p = idx.index(track["program"][0])
        program_name = program[p] if track["channel"] != 9 else "Drum"
        filename = root + name + "_" + str(track["channel"])\
                        + "_" + program_name + ".mid"    
        midi.write_midifile(filename, track["pattern"])

def get_tempo(pattern):
    '''
    遍历pattern,通过midi.SetTempoEvent得到tempo
    '''
    for track in pattern:
        bpm = _get_tempo(track)
        if bpm == 0:
            continue
        else:
            return bpm
    
    print("! : No tempo INFO!")
    return 0

def get_time_signature(pattern):
    """
    遍历pattern,通过midi.TimeSignatureEvent得到time signature
    """
    for track in pattern:
        data = _get_time_signature(track)
        if data == 0:
            continue
        else:
            return data

    print("! : No time signature INFO!")
    return 0

def get_resolution(pattern):
    """
    返回resolution
    """
    return pattern.resolution

def set_tempo(pattern, bpm):
    """
    设置一个Pattern的tempo
    放在第一个Track中(第一个Track只记录信息)
    """
    track = _set_tempo(pattern[0], bpm)
    pattern[0] = track
    return pattern

def set_time_signature(pattern, data):
    """
    设置一个Pattern的time signature
    放在第一个Track中(第一个Track只记录信息)
    """
    track = _set_time_signature(pattern[0], data)
    pattern[0] = track
    return pattern

def set_resolution(pattern, resolution):
    """
    设置一个Pattern的resolution
    """
    pattern.resolution = resolution
    return pattern
    
def demo_multitracks(song):
    midiname = "../midi/" + song + ".mid"
    test_pattern = read_midifile(midiname)
    test_multitracks = gen_multitracks(test_pattern)
    save_multitracks(test_multitracks, name=song)

def demo():
    # 这个demo是把我们分出的单音色的Pattern标准化
    # 这样的Pattern有两个Track
    # Track0 仅有一些基本信息
    # Track1 包含了音乐本身
    midifile = "../track/Stan_1_Violin.mid"
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

    pat[1] = set_program(pat[1], channel=program[0], value=40)
    pat[1] = set_note(pat[1], note)

    save_midfile(pat, "../test_std_Stan.mid")

if __name__ == '__main__':
    # song = 'Stan'
    # demo_multitracks(song)
    demo()
    