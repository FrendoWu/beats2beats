import midi
import numpy as np

def _cal_var(l):
    """
    list = [...]
    计算直到第i位list[:i]方差大于1
    """
    for i in range(1,len(l)):
        if np.var(l[:i]) / i > 0.1:
            return i - 1
    return 0

def _read_general_midi():
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
