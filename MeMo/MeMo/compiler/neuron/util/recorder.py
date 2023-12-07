class Recorder:
  def __init__(self, ref, seg=None, dt=0.05, density_variable=False):
    from neuron import h, nrn
    import numpy as np
      
    self.y = h.Vector()
    self.t = h.Vector()
    
    self._data = None
    
    if seg:
        self.t.record(h._ref_t, sec=seg.sec)
        self.y.record(ref, sec=seg.sec)
    else:
        self.t.record(h._ref_t)
        self.y.record(ref)

    self.density_variable = density_variable
    self.seg = seg
    self.dt = dt

    # it raise an exception if, with the density variable, there is no area
    assert (density_variable and seg is not None) or not density_variable

  def _get(self, dt=None):
    from neuron import h
    if dt:
        tp = h.Vector()
        yp = h.Vector()
        tp.indgen(self.t[0], self.t[-1], dt)
        yp.interpolate(tp, self.t, self.y)
#        print('interpolation dt=', dt)
#        print(self.t.size(), tp.size(), self.y.size(), yp.size())
        return tp, yp
    return self.t, self.y

    '''import numpy as np
    r = np.array([ [self.t.x[i], self.y.x[i]] for i in range(self.t.size()) ])

    if self._data is not None:
      # it is the second or above interpolation
      # add last point
      r = np.concatenate(([self._data[-1, :]], r), axis=0)
      
    # interpolation
    tp = np.arange(r[0, 0], r[-1, 0], self.dt)
    yp = np.interp(tp, r[:, 0], r[:, 1])
    r = np.array([ tp, yp ]).T

    if self._data is not None:
      # remove the first point
      r = np.delete(r, [0], axis=0)
    
    return r'''


  def _flush(self): pass


  def get(self, dt=None):
    import numpy as np
    tp, yp = self._get(dt=dt)
    if self.density_variable:
        yp.mul(self.seg.area() * 1e-8)
    return np.array([ tp.as_numpy(), yp.as_numpy() ]).T
    

  

class GroupRecorder:
  def __init__(self, recorders, mean_flag=False):
    self.recorders = recorders
    self.t = []
    self.y = []
    self.mean_flag = mean_flag

    
  def _flush(self):
    import numpy as np
    t, y = None, []
    for r in self.recorders:
      
      # get the data
      data = r.get()

      if t is None:
        t, y = data[:, 0], [data[:, 1]]
      else:
        y.append(data[:, 1])    

      # clear the recorders
      r.t.resize(0)
      r.y.resize(0)

    # concatenate the data
    self.t.append(t)
    self.y.append((np.mean if self.mean_flag else np.sum)(y, axis=0))



  def get(self, dt=None):
    import numpy as np
    t = np.concatenate(tuple(self.t))
    y = np.concatenate(tuple(self.y))
    if dt:
      tp = np.arange(t[0], t[-1], dt)
      y = np.interp(tp, t, y)
      t = tp
    return np.array([ t, y ]).T   


if __name__ == '__main__':
  c = Recorder(None)
  c.y.append(0.1)
  c.t.append(0.0)
  c.y.append(0.1)
  c.t.append(0.3)
  c.y.append(0.1)
  c.t.append(0.7)
  c._flush()
  print (c._data)
  print ('second round')
  c.y.append(0.9)
  c.t.append(0.9)
  c._flush()
  print (c._data)
  print ('third round')
  c.y.append(0.9)
  c.t.append(1.2)
  c._flush()
  print (c._data)
  print ('fourth round')
  try:
    c._flush()
  except ValueError:
    pass
  print (c._data)
  
    
  print ('fourth round')
  print (c.get(dt=0.2))
