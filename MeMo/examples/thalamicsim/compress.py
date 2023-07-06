filenamein = 'output-spont-drv-%d.nwb'
filenameout = 'test-drv.nwb'
filedict = 'test_firing_rate_drv.npy'
import MeMo.nwbio as nwbio
import numpy as np

info = str(np.load(filedict, allow_pickle=True).tolist())

n = 7700

import os

fo = nwbio.FileWriter(filenameout, info, 'thal')

for i in range(n):
  fi = nwbio.FileReader(filenamein % i)
  for k in fi.keys():
    fo.add(k, *fi.read(k))
  fi.close()
  os.system('rm %s' % (filenamein % i))


fo.close()
