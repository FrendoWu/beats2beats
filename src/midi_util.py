import midi
import sys

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
            if isinstance(event, midi.ProgramChangeEvent):
                try:
                    program = event.data
                    channel = event.channel
                    _sub_pattern.append(track)
                    sub_pattern = {
                        'pattern': _sub_pattern,
                        'program': program,
                        'channel': channel}
                    sub_patterns.append(sub_pattern)
                    break
                except AttributeError:
                    pass
    return sub_patterns

def save_multitracks(multitracks, root="../track/", name="untitled"):
    """
    将multitracks保存
    """
    idx, program = read_general_midi()
    for track in multitracks:
        p = idx.index(track["program"][0])
        filename = root + name + "_" + str(track["channel"])\
                        + "_" + program[p] + ".mid"    
        midi.write_midifile(filename, track["pattern"])
    
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

def demo_multitracks(song):
    midiname = "../midi/" + song + ".mid"
    test_pattern = read_midifile(midiname)
    test_multitracks = gen_multitracks(test_pattern)
    save_multitracks(test_multitracks, name=song)

if __name__ == '__main__':
    song = sys.argv[1]
    demo_multitracks(song)