import sys
import MeMo.nwbio as nwbio
#import MPI_Pool
import multiprocessing
import numpy as np
import warnings
warnings.simplefilter("ignore")

import spiketrain

import eFELExt
eFELExt.efel.setThreshold(-40)

filenamein = sys.argv[sys.argv.index('--filenamein')+1]
filenameout = sys.argv[sys.argv.index('--filenameout')+1]

def get_spike_times(t, v, tinit=10000, tend=20000, threshold=-30):
    """
    Extract the spike time
    t:time array of the trace
    v:voltage array of the trace
    tinit:(default 2000) lower bound of time
    tend:(default 10000) upper bound of time
    threshold:(default 0) spike threshold
    """
    idx = np.logical_and(t >= tinit, t <= tend)
    t = t[idx]
    v = v[idx]
    idx = np.argwhere(v > threshold)[:, 0]
    idx = np.delete(idx, np.argwhere( (idx[1:] - idx[:-1]) == 1)[:, 0] + 1)
    return t[idx]


def firing_rate(filenamein, idx, file_key, tinit=10000, tstop=20000, threshold=-30):
    # read
    f = nwbio.FileReader(filenamein)
    t, v = f.read(file_key)
    f.close()

    tspk = get_spike_times(t, v, tinit=tinit, tend=tstop, threshold=threshold)
    freq = len(tspk) / (tstop - tinit) * 1000

    try:
        isi = tspk[1:] - tspk[:-1]
        cv = np.std(isi) / np.mean(isi)
    except:
        cv = np.nan

    vm = spiketrain.get_baseline_voltage(t, v)

    return idx, freq, cv, vm

if __name__ == '__main__': 
  f = nwbio.FileReader(filenamein)
  tab = f.session_description.copy()
  f.close()

  args = []
  for i, file_key in enumerate(f.keys()):
    idx = file_key.split('.')[0]
    
    # add arguments
    args.append((filenamein, idx, file_key))

  # extract firing rate
  pool = multiprocessing.Pool() #MPI_Pool.Pool()
  for idx, freq, cv, vm in pool.starmap(firing_rate, args): #pool.map(firing_rate, args):
    # get firing rate
    tab.loc[idx, 'firing rate (hz)'] = freq
    tab.loc[idx, 'CV ISI'] = cv
    tab.loc[idx, 'baseline'] = vm
    print(idx, 'elaborated')

  # output
  tab.to_csv(filenameout)
  
  # exit
  sys.exit(0)
