import numpy as np

def cal_var(l):
    """
    list = [...]
    计算直到第i位list[:i]方差大于1
    """
    for i in range(1,len(l)):
        if np.var(l[:i]) / i > 0.1:
            return i - 1
    return 0
