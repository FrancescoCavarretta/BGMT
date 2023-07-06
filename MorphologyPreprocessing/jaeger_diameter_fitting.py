import neuron
import numpy as np
import os
import scipy.stats as stats

neuron.h.load_file('MorphologyLoader.hoc')



diameter_leaves = []
diameter_2_3_rule = []

def depth(sec):
  depth = -1
  secname = neuron.h.secname(sec=sec)
  while 'soma' not in secname:
    depth += 1
    sec = neuron.h.SectionRef(sec=sec).parent
    secname = neuron.h.secname(sec=sec)
  return depth


def diameter(sec):
  return np.mean([s.diam for s in sec.allseg()])



def visit(sec):
  sref = neuron.h.SectionRef(sec=sec)
  diam = diameter(sec)
  if sref.nchild() == 0 and 'axon' not in neuron.h.secname(sec=sec) and 'soma' not in neuron.h.secname(sec=sec):
    diameter_leaves.append((depth(sec), diam))
  else:
    diam_ch = 0.
    for ch in sref.child:
      if 'axon' not in neuron.h.secname(sec=ch) and 'soma' not in neuron.h.secname(sec=ch):
        diam_ch += visit(ch) ** 1.5
    if 'axon' not in neuron.h.secname(sec=sec) and 'soma' not in neuron.h.secname(sec=sec):
      diameter_2_3_rule.append((diam_ch, diam ** 1.5))
  return diam
      
    

if __name__ == '__main__':
  for filename in os.listdir('./jaeger'):
    if filename.endswith('.my.swc'):
      print (filename)
      try:
        c = neuron.h.MorphologyLoader('./jaeger/' + filename)
        visit(c.soma[0])
      except: pass
  diameter_leaves = np.array(diameter_leaves)
  diameter_2_3_rule = np.array(diameter_2_3_rule)
  import matplotlib.pyplot as plt
  ax = plt.subplots(1, 2)[1]


  slope, intercept = stats.linregress(diameter_leaves[:,0], diameter_leaves[:,1])[:2]
  print('slope: %.3g \tintercept: %.3g' % (round(slope, 3), intercept))
  ax[0].scatter(diameter_leaves[:,0],diameter_leaves[:,1], color='black')
  ax[0].plot([0, max(diameter_leaves[:,0])], [0 * slope + intercept, max(diameter_leaves[:,0]) * slope + intercept], color='red')
  ax[0].set_title('Leaves diameters')
  ax[0].set_xlabel('branch order')
  
  ax[0].set_ylabel('diameter')
  slope, intercept = stats.linregress(diameter_2_3_rule[:,0], diameter_2_3_rule[:,1])[:2]
  print('slope: %.3g \tintercept: %.3g' % (slope, intercept))
  ax[1].scatter(diameter_2_3_rule[:,0],diameter_2_3_rule[:,1], color='black')
  ax[1].plot([0, max(diameter_2_3_rule[:,0])], [0 * slope + intercept, max(diameter_2_3_rule[:,0]) * slope + intercept], color='red')
  ax[1].set_title('2/3 Power rule')
  ax[1].set_xlabel('sum. children diameters ^ 1.5')
  ax[1].set_ylabel('sum. soma diameters ^ 1.5')
  plt.show()
