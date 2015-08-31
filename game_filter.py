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

def interp_playback_nfb(game, nfb_points):
    tr = game.tr

    time_points = tr*np.arange(len(nfb_points)) + 0.5*tr
    time_points = np.append(0, time_points)
    time_points = np.append(time_points, time_points[-1] + 0.5*tr)

    nfb_points = np.append(nfb_points[0], nfb_points)
    nfb_points = np.append(nfb_points, nfb_points[-1])

    nfb_interp_func = interp1d(time_points, nfb_points, kind='cubic')

    # add game.playback_time_buffer and game.move_counter
    return nfb_interp_func(game.playback_time_buffer[0:game.move_counter+1]/1000.0)
