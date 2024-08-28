import numpy as np

def is_regular(df, column_name):
    intervals = np.diff(df[column_name].values)
    return np.allclose(intervals, intervals[0])