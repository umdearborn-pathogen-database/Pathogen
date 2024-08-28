import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def snip_baseline_correction(signal, iterations=150):
    n = len(signal)
    baseline = np.copy(signal)
    
    for i in range(iterations):
        for j in range(1, n - 1):
            baseline[j] = min(baseline[j], (baseline[j - 1] + baseline[j + 1]) / 2)
    
    return baseline