from jaeger_diameter_fitting import *
    

if __name__ == '__main__':
  for filename in os.listdir('./'):
    if filename.endswith('.swc'):
      print (filename)
      try:
        c = neuron.h.MorphologyLoader('./' + filename)
        visit(c.soma[0])
      except: pass
  diameter_leaves = np.array(diameter_leaves)
  diameter_2_3_rule = np.array(diameter_2_3_rule)
  import matplotlib.pyplot as plt
  ax = plt.subplots(1, 2)[1]


  slope, intercept = stats.linregress(diameter_leaves[:,0], diameter_leaves[:,1])[:2]
  print('slope: %g\tintercept: %g' % (slope, intercept))
  ax[0].scatter(diameter_leaves[:,0],diameter_leaves[:,1], color='black')
  ax[0].plot([0, max(diameter_leaves[:,0])], [0 * slope + intercept, max(diameter_leaves[:,0]) * slope + intercept], color='red')
  ax[0].set_title('Leaves diameters')
  ax[0].set_xlabel('branch order')
  ax[0].set_ylabel('diameter')
  slope, intercept = stats.linregress(diameter_2_3_rule[:,0], diameter_2_3_rule[:,1])[:2]
  print('slope: %g\tintercept: %g' % (slope, intercept))
  ax[1].scatter(diameter_2_3_rule[:,0],diameter_2_3_rule[:,1], color='black')
  ax[1].plot([0, max(diameter_2_3_rule[:,0])], [0 * slope + intercept, max(diameter_2_3_rule[:,0]) * slope + intercept], color='red')
  ax[1].set_title('2/3 Power rule')
  ax[1].set_xlabel('sum. children diameters ^ 1.5')
  ax[1].set_ylabel('sum. soma diameters ^ 1.5')
  plt.show()
