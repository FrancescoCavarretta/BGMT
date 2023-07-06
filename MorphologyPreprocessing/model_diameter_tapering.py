from jaeger_diameter_fitting import *


def distance(seg):
  return neuron.h.distance(seg.x, sec=seg.sec)


def visit(sec):
  data = []
  
  sref = neuron.h.SectionRef(sec=sec)
  for ch in sref.child:
    data += visit(ch)
    
  if 'soma' not in neuron.h.secname(sec=sec) and 'axon' not in neuron.h.secname(sec=sec):
    for seg in sec:
      data.append((distance(seg), seg.diam))
  
  return data


def visit_primary(sec):
  data = []
  
  if 'soma' not in neuron.h.secname(sec=sec) and 'axon' not in neuron.h.secname(sec=sec) and depth(sec) == 0:
    for seg in sec:
      data.append((distance(seg), seg.diam))

    # normalize
    data = np.array(data)
    data[:, 1] = data[:, 1] / np.mean(data[:, 1])
    data[:, 0] = data[:, 0] - data[0, 0] + 45.93
    data = data.tolist()
    
  sref = neuron.h.SectionRef(sec=sec)
  for ch in sref.child:
    data += visit_primary(ch)

  
  return data


if __name__ == '__main__':
  import matplotlib.pyplot as plt
  import numpy as np

  def plot(ax, dirname, ext='.swc', visit_func=visit):
    all_data = None
    print(visit_func)
    for filename in os.listdir(dirname):
      if filename.endswith(ext):
        c = neuron.h.MorphologyLoader(os.path.join(dirname, filename))
        neuron.h.distance(sec=c.soma[0])
        data = np.array(visit_func(c.soma[0]))
        data = np.concatenate((data, np.array([[1.0 / data.shape[0]]] * data.shape[0])), axis=1)
        ax.scatter(data[:, 0], data[:, 1])
        if all_data is None:
          all_data = data
        else:
          all_data = np.concatenate((all_data, data))
    ax.set_xlabel('distance from soma ($\mu$)')
    ax.set_ylabel('diameter ($\mu$)')
    return all_data

  plt.figure(figsize=(15, 5))
  ax = plt.subplot(3, 3, 1)
  plt.title('Jaeger')
  plot(ax, 'jaeger', ext='.my.swc')
  ax.set_ylim([0, 4])
  ax.set_xlim([0, 600])
  
  ax = plt.subplot(3, 3, 2)
  plt.title('Jaeger Primary Dendrites')
  all_data = plot(ax, 'jaeger', ext='.my.swc', visit_func=visit_primary)
  ax.set_ylim([0, 4])
  ax.set_xlim([0, 250])


  # fitting
  ax = plt.subplot(3, 3, 3)
  ax.scatter(all_data[:, 0], all_data[:, 1])
  
  from scipy.optimize import curve_fit
  def expfunc(x, a, b, c):
    return a * np.exp(-b * (x - 20)) + c
  
  pars = curve_fit(expfunc, all_data[:, 0], all_data[:, 1], sigma=all_data[:, 2], maxfev=10000, bounds=([0, 0, -10], [5, 1, 10]))[0]
  print('%.3f %.3f %.3f' % tuple(pars.tolist()))
  x = np.linspace(0, 300, 100)
  plt.plot(x, expfunc(x, *pars), linewidth=2, color='red')
  ax.set_ylim([0, 4])
  ax.set_xlim([0, 250])
  print( 'Error', np.sum(np.power(expfunc(all_data[:, 0], *pars) - all_data[:, 1], 2) * all_data[:, 2]) / np.sum(all_data[:, 2]) )


##  ax = plt.subplot(3, 3, 4)
##  plt.title('Markram')
##  plot(ax, 'markram')
##  ax.set_ylim([0, 10])
##  ax.set_xlim([0, 600])
##  
##  ax = plt.subplot(3, 3, 5)
##  plt.title('Markram Primary Dendrites')
##  all_data = plot(ax, 'markram', visit_func=visit_primary)
##  ax.set_ylim([0, 10])
##  ax.set_xlim([0, 250])
##  
##  # fitting
##  ax = plt.subplot(3, 3, 6)
##  ax.scatter(all_data[:, 0], all_data[:, 1])
##  
##
##  pars = pars = curve_fit(expfunc, all_data[:, 0], all_data[:, 1], sigma=all_data[:, 2], maxfev=10000, bounds=([0, 0, -10, -50], [5, 1, 10, 50]))[0]
##  print(pars)
##  x = np.linspace(0, 300, 100)
##  plt.plot(x, expfunc(x, *pars), linewidth=2, color='red')
##  print( 'Error', np.sum(np.power(expfunc(all_data[:, 0], *pars) - all_data[:, 1], 2) * all_data[:, 2]) / np.sum(all_data[:, 2]) )
##  ax.set_ylim([0, 10])
##  ax.set_xlim([0, 250])
##
##  ax = plt.subplot(3, 3, 7)
##  plt.title('Custom')
##  plot(ax, '.')
##  ax.set_ylim([0, 4])
##  ax.set_xlim([0, 600])
##  
##  ax = plt.subplot(3, 3, 8)
##  plt.title('Custom Primary Dendrites')
##  all_data = plot(ax, '.', visit_func=visit_primary)
##  ax.set_ylim([0, 4])
##  ax.set_xlim([0, 250])
##  
##  # fitting
##  ax = plt.subplot(3, 3, 9)
##  ax.scatter(all_data[:, 0], all_data[:, 1])
##  
##
##  pars = curve_fit(expfunc, all_data[:, 0], all_data[:, 1], sigma=all_data[:, 2], maxfev=10000, bounds=([0, 0, -10], [5, 1, 10]))[0]
##  print(pars)
##  x = np.linspace(0, 300, 100)
##  plt.plot(x, expfunc(x, *pars), linewidth=2, color='red')
##  print( 'Error', np.sum(np.power(expfunc(all_data[:, 0], *pars) - all_data[:, 1], 2) * all_data[:, 2]) / np.sum(all_data[:, 2]) )
##  ax.set_ylim([0, 4])
##  ax.set_xlim([0, 250])
  
  plt.tight_layout(pad=1)
  plt.show()
