from vmcell import Cell
import neurom
from neurom import viewer
import pandas as pd
import matplotlib.pyplot as plt
import random
import sys

def section_index(x):
  x = x[x.index('.')+1:]
  return int(x[x.index('[')+1:x.index(']')])


def section_type(x):
  x = x[x.index('.')+1:]
  x = x[:x.index('[')]
  return x

  
def section_arc(x):
  return float(x[x.index('(')+1:x.index(')')])


def arc2xyz(m, sectype, index, arc):
    import numpy as np
    sec = m.cell.dend[index]

    points = np.array([[sec.x3d(i), sec.y3d(i), sec.z3d(i), sec.diam3d(i)] for i in range(sec.n3d())])
    
    d = np.cumsum(np.linalg.norm(points[1:, :-1] - points[:-1, :-1], axis=1))
    ds = arc * d[-1]
    index = np.argwhere(ds <= d).T[0, 0]
    if index == 0:
      dmin = 0
    else:
      dmin = d[index-1]
    dmax = d[index]
    
    a = points[index, :-1]
    b = points[index + 1, :-1]
    return (b - a) * (ds - dmin) / (dmax - dmin) + a



mt = pd.read_csv('morph.csv')
mt['segment'] = mt['segment'].astype(float)
mt['number'] = mt['number'].astype(int)

distr = pd.read_csv('allsyns.csv') # load experimental data
for c in distr.columns:
    distr.drop(distr[distr[c] == c].index, inplace=True)
distr['path distance'] = distr['path distance'].apply(lambda x:float(x))
distr['target diam'] = distr['target diam'].apply(lambda x:float(x))
distr['type'] = distr['section name'].apply(lambda x : x.split('.')[1].split('[')[0])
distr['number'] = distr['section name'].apply(lambda x : int(x.split('.')[1].split('[')[1].split(']')[0]))
distr['section arc'] = distr['section arc'].astype(float)
distr.replace({'dend':'basal', 'soma':'somatic'}, inplace=True)
distr.rename(columns={'section arc':'segment'}, inplace=True)

print(
    100 * distr[distr['section name'].str.contains('soma')].shape[0] / distr[distr['input name'].str.contains('snr')].shape[0]
)

distr.drop(distr[distr['section name'].str.contains('soma')].index, inplace=True)

distr = distr.merge(mt, on=['segment', 'type', 'number'], how='left')

distr = distr[distr.seed == 0]

c = Cell('Test')
c.make()
m = neurom.load_morphology('vmcell/morphologies/AA0719.swc')
fig, ax = viewer.draw(m, mode='3d', color='black')
fig.set_size_inches(20, 20)
ax.set_xlim([-350, 350])
ax.set_ylim([-250, 450])
ax.set_zlim([-275, 425])
ax.set_xlabel('x ($\mu$m)')
ax.set_ylabel('y ($\mu$m)')
ax.set_zlabel('z ($\mu$m)')
ax.set_axis_off()

def plot_synapses(ax, c, data, input_name, sz, color):
  x = []
  y = []
  z = []
  for _, r in data[data['input name'] == input_name].iterrows():
    #print(, , r.path_distance)
    _x, _y, _z = arc2xyz(c, r['type'], r['number'], r['segment'])
    x.append(_x)
    y.append(_y)
    z.append(_z)
  ax.scatter(x, y, z, color=color, s=sz)

if '--excitatory' in sys.argv:
  distr = distr[distr['input name'].isin(['driver', 'modulator'])]
  distr.drop_duplicates(subset=['type', 'number', 'segment'], keep='last', inplace=True)
  plot_synapses(ax, c, distr, 'driver', 8, 'orange')
  plot_synapses(ax, c, distr, 'modulator', 3, 'magenta')
elif '--inhibitory' in sys.argv:
  distr = distr[distr['input name'].isin(['reticular', 'snr'])]
  distr.drop_duplicates(subset=['type', 'number', 'segment'], keep='last', inplace=True)
  plot_synapses(ax, c, distr, 'reticular', 3, 'cyan')
  plot_synapses(ax, c, distr, 'snr', 8, 'blue')
else:
  pass

plt.show() 
