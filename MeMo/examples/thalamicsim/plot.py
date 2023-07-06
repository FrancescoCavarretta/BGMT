import sys
import matplotlib.pyplot as plt
import MeMo.nwbio as nwbio
f1 = nwbio.FileReader('output-burst-off-'+sys.argv[-1]+'.nwb')
plt.plot(*f1.read(list(f1.keys())[0]))
f2 = nwbio.FileReader('output-burst-on-'+sys.argv[-1]+'.nwb')
plt.plot(*f2.read(list(f2.keys())[0]))
plt.show()
