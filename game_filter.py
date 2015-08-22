import numpy as np
from scipy.signal import butter, lfilter, filtfilt
from scipy.interpolate import interp1d
from scipy.stats import logistic
from scipy.special import gamma

def gen_hrf(frame_rate=120, tf=30,
            c=1/6.0, a1=6, a2=16, A=1/0.833657):
    ts = 1/float(frame_rate)
    A = A*ts
    t = np.arange(0,tf,ts)
    h = A*np.exp(-t)*(t**(a1-1)/gamma(a1) - c*t**(a2-1)/gamma(a2))
    return(h[::-1])

def gen_impulse(frame_rate=120, tf=30):
    ts = 1/float(frame_rate)
    h = np.zeros(0,tf,ts)
    h[-1] = 1

def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_lowpass(lowcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    b, a = butter(order, low, btype='lowpass')
    return b, a

def filter_data(data, b, a):
    y = filtfilt(b, a, data)
    return y

def filter_data_rt(data, b, a):
    y = lfilter(b, a, data)
    return y[-1]
