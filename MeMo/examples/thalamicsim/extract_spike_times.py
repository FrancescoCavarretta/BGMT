import MeMo.nwbio as nwbio
import numpy as np
import sys
def get_spike_times(t, v, threshold=-30):
    """
    Extract the spike time
    t:time array of the trace
    v:voltage array of the trace
    tinit:(default 2000) lower bound of time
    tend:(default 10000) upper bound of time
    threshold:(default 0) spike threshold
    """
#    idx = np.logical_and(t >= tinit, t <= tend)
#    t = t[idx]
#    v = v[idx]
    idx = np.argwhere(v > threshold)[:, 0]
    idx = np.delete(idx, np.argwhere( (idx[1:] - idx[:-1]) == 1)[:, 0] + 1)
    return t[idx]


def exfunc(filename, file_key):
  fi = nwbio.FileReader(filename)
  t, v = fi.read(file_key)
  fi.close()
  tspk = get_spike_times(t, v)
  return file_key.split('.')[0], tspk

if __name__ == '__main__':

  import sys
  filenamein = sys.argv[sys.argv.index('--filenamein')+1]
  filenameout = sys.argv[sys.argv.index('--filenameout')+1]

  import multiprocessing
  fi = nwbio.FileReader(filenamein)
  sd = fi.session_description.copy()
  for file_key in fi.keys():
   key = file_key.split('.')[0]
   sd.loc[key, 'file_key'] = file_key
  fi.close()
  print(sd.dropna(subset=['file_key'], inplace=True))
  args = [ (filenamein, file_key) for file_key in sd['file_key'] ]
  pool = multiprocessing.Pool()

  output = {}
  for k, r in pool.starmap(exfunc, args):
    output[k] = r
  output['session_description'] = list(sd.reset_index().T.to_dict().values())

  np.save(filenameout, output, allow_pickle=True)
