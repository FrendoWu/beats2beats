import midi
import sys
'''
    Tempo - 一个拍的时间，比如120BPM表示1min120beats，所以是500,000ms一个beat
    Resolution - 一个beat含有的tick数，tick是midi中最小的时间单位（相对的，由Tempo和Resolution定出绝对值）。如Resolution为1,000，则一个tick500ms
    Time Signature - 拍号，在midi中不会影响到Tempo
'''
def read_general_midi():
    """
    获取general_midi
    """
    with open("./general_midi") as f:
        lines = f.readlines()
        idx, program = [], []
        for line in lines:
            if line:
                line = line.split()
                idx.append(int(line[0]))
                program.append('_'.join(line[1:]))
    return idx, program

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
                    program = event.data if channel != 9 else get_program_drum(track)
                    sub_pattern = {
                        'pattern': _sub_pattern,
                        'channel': channel,
                        'program':program  
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
    idx, program = read_general_midi()
    for track in multitracks:
        p = idx.index(track["program"][0])
        program_name = program[p] if track["channel"] != 9 else "Drum"
        filename = root + name + "_" + str(track["channel"])\
                        + "_" + program_name + ".mid"    
        midi.write_midifile(filename, track["pattern"])
        
def demo_multitracks(song):
    midiname = "../midi/" + song + ".mid"
    test_pattern = read_midifile(midiname)
    test_multitracks = gen_multitracks(test_pattern)
    save_multitracks(test_multitracks, name=song)

def get_tempo(pattern):
    '''
    遍历pattern,通过midi.SetTempoEvent得到tempo
    '''
    for track in pattern:
        for event in track:
            if isinstance(event, midi.SetTempoEvent): 
                return event.get_bpm()

if __name__ == '__main__':
    song = 'Stan'
    demo_multitracks(song)
    