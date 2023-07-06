      
''' Implement a Neuro SAGE Reader in Python '''
class FileReader:
  def __init__(self, filename, stim_start=800.0, bias_end=500.0, tstop=5000.0, stim_duration=[200.0, 500.0, 1000.0, 1500.0, 2000.0], interp_dt=0.1, junction_potential=14.2, filter_flag=True, filter_width_factor=2):
    import numpy
    import h5py
    
    self.filename = filename

    self.handle = h5py.File(filename, 'r')
    self.keys   = list(self.handle['/Trials'].keys())
    self.ntrial = len(self.keys)
    self.stim_start = stim_start
    self.stim_duration = stim_duration
    self.tstop = 5000.0
    self.interp_dt = interp_dt
    self.junction_potential = junction_potential
    self.bias_end = bias_end
    self.filter_flag = filter_flag
    self.filter_width_factor = filter_width_factor

  def close(self):
    self.handle.close()


  def _filter_trace(self, t, v):
    import scipy.signal as signal
    import numpy
    
    # apply a 3-pole lowpass filter at 0.1x Nyquist frequency
    sampleRate = 1.0/(t[1]-t[0])
    b, a = signal.butter(3, self.filter_width_factor*1.0/sampleRate)
    filtered = signal.filtfilt(b, a, v)

    return numpy.arange(0.0,len(filtered))/sampleRate+t[0], filtered

    
  ''' read the a trial:
    if current_flag is true, it read the current trace
    otherwise it reads the voltage traces '''
  def _read_trace(self, itrial, current_flag):
    assert itrial < self.ntrial
    
    import numpy

    
    def _get_voltage_key(path):
      for key in self.handle[path]:
        if 'voltage' in key.lower():
          return path + '/' + key
      return None

    
    def _get_current_key(path):
      #return path + '/' + list(self.handle[path].keys())[0]
      for key in self.handle[path]:
        if 'current' in key.lower():
          return path + '/' + key
      return None
    

    if current_flag:
      key = _get_current_key('/Trials/' + self.keys[itrial] + '/Data/Acquisition Data')
      
      ## --------------------------------------------------------------------------------------------------------
      #print (self.keys[itrial])
      #tk = ''
      #for xx in self.keys[itrial].split()[1:]:
      #  tk += xx + ' '
      #key = '/Trials/' + self.keys[itrial] + '/Data/Stimulation Data/' + tk + '(NI PCI-6733 AO 00)'
      ## ---------------------------------------------------------------------------------------------------------
      y_shift = 0.
    else:
      key = _get_voltage_key('/Trials/' + self.keys[itrial] + '/Data/Acquisition Data')
      y_shift = self.junction_potential

    entry = self.handle[key]

    assert entry.attrs['Transform.Type'] == b'Linear'
    
    if not current_flag:
      assert entry.attrs['Transform.Offset'] == 0
    #else:
    #  print (entry.attrs['Transform.Offset'])
      
    y = entry.attrs['Transform.Scale'] * entry + entry.attrs['Transform.Offset'] - y_shift
    t = numpy.arange(0, len(y), 1.0) / entry.attrs['Sampling Rate'] * 1000.0
    tp = numpy.arange(0.0, self.tstop + self.interp_dt, self.interp_dt)
    yp = numpy.interp(tp, t, y)
    #print(self.filter_flag)
    if self.filter_flag:
        tp, yp = self._filter_trace(tp, yp)
    
    return numpy.array([ tp, yp ]).T


  """ number of entries or records """
  def size(self):
    return self.ntrial

  
  def _trace_cut(self, entry, tinit, tend):
    import numpy
    return entry[numpy.logical_and(entry[:, 0] >= tinit, entry[:, 0] < tend), :]
  
  
  '''
    read the voltage trace
  '''
  def read_voltage_trace(self, itrial):
    return self._read_trace(itrial, False)
  

  '''
    read the current trace associated to a trial
  '''
  def read_current_trace(self, itrial):
    return self._read_trace(itrial, True)


  def _step_length(self, itrial, tinit, tend, stim_duration, cc_bin=None, plot=False):
    import numpy
    entry = self.read_current_trace(itrial)
    entry[:,1] -= self.bias_amplitude(itrial)
    
    if cc_bin is not None:
      entry[:,1] = numpy.round(entry[:,1] / cc_bin) * cc_bin
    entry = self._trace_cut(entry, tinit, tend)
    cum_diff_curve = numpy.abs(numpy.cumsum( entry[:, 1] ))
    i_max = numpy.argmax(cum_diff_curve)
    
    if plot:
      import matplotlib.pyplot as plt
      plt.plot(range(len(cum_diff_curve)), cum_diff_curve)
      #print ("tmax:", entry[i_max, 0])
      plt.show()
      
    
    
    # search the most coincident time
    i_dur = numpy.argmin( numpy.abs(  (entry[i_max, 0] - tinit) / numpy.array(stim_duration)  - 1 ) )

    return stim_duration[i_dur]    
    

  
  '''
    time stamp
  '''
  def time_stamp(self, itrial):
    return self.handle[ '/Trials/' + self.keys[itrial] ].attrs['Time Stamp']
      

    
  
  '''
    current duration
  '''
  def step_length(self, itrial, cc_bin=None, plot=False):
    return self._step_length(itrial, self.stim_start, self.tstop, self.stim_duration, cc_bin=cc_bin, plot=plot)
      

  '''
    bias current amplitude
  '''
  def bias_amplitude(self, itrial):
    import numpy
    return numpy.mean(self._trace_cut(self.read_current_trace(itrial), 0.0, self.bias_end)[:,1])


  '''
    stimulus current amplitude
  '''
  def step_amplitude(self, itrial, cc_bin=None):
    import numpy
    cc = numpy.mean( self._trace_cut(self.read_current_trace(itrial), self.stim_start, self.stim_start + self.step_length(itrial, cc_bin=cc_bin))[:,1] ) - self.bias_amplitude(itrial)

    if cc_bin is not None:
      cc = numpy.round(cc/cc_bin)*cc_bin

    return cc
    
  

  ''' return holding voltage '''
  def holding_voltage(self, itrial):
    import numpy
    return numpy.mean(self._trace_cut(self.read_voltage_trace(itrial), 0.0, self.stim_start)[:,1])
                      
                      
  ''' plot a trace '''
  def plot_voltage_trace(self, i):
    try:
      import matplotlib.pyplot as plt
      data = self.read_voltage_trace(i)
      plt.plot(data[:, 0], data[:, 1])
      plt.xlabel('t (ms)')
      plt.ylabel('v (mV)')
      #plt.show()
    except:
      pass  



  ''' plot a trace '''
  def plot_current_trace(self, i):
    try:
      import matplotlib.pyplot as plt
      data = self.read_current_trace(i)
      plt.plot(data[:, 0], data[:, 1])
      plt.xlabel('t (ms)')
      plt.ylabel('i (pA)')
      #plt.show()
    except:
      pass  

"""
  read all the files related to an experiment
"""
class DatasetReader:
  
  def __init__(self, filename, stim_start=800.0, tstop=5000.0, stim_duration=[200.0, 500.0, 1000.0, 1500.0, 2000.0], interp_dt=0.1, junction_potential=14.2, open_error_ignore=True, filter_flag=True, filter_width_factor=2):
    from collections import OrderedDict
    
    if type(filename) != list:
      filename = [ filename ]

    self.filename = filename

    self._file_reader = OrderedDict() # file reader ordered by offset

    offset = 0
    for _filename in filename:
      if open_error_ignore:
        try:
          fr = FileReader(_filename, stim_start=stim_start, tstop=tstop, stim_duration=stim_duration, interp_dt=interp_dt, junction_potential=junction_potential, filter_flag=filter_flag, filter_width_factor=filter_width_factor)
        except KeyError:
          print('Warning (KeyError): ', _filename, 'will not be considered')
          continue
      else:
        fr = FileReader(_filename, stim_start=stim_start, tstop=tstop, stim_duration=stim_duration, interp_dt=interp_dt, junction_potential=junction_potential, filter_flag=filter_flag, filter_width_factor=filter_width_factor)
      self._file_reader[offset] = fr
      offset += fr.size()
  

  ''' return all the suffixes '''
  def _get_key_types(self):
    keys = {}
    for fr in self._file_reader.values():
      for k in fr.keys:
        k = k[k.index(' ')+1:].lower()
        if k not in keys:
          keys[k] = 0
        keys[k] += 1
    return keys


  def _get_key(self, i):
    # get the file reader
    fr, j = self._get_file_reader(i)
    return fr.keys[j]

  ''' size, ie, number of records '''
  def size(self):
    sz = 0
    for fr in self._file_reader.values():
      sz += fr.size()
    return sz
  

  def close(self):
    for fr in self._file_reader.values():
      fr.close()


  def _get_file_reader(self, itrial):
    import numpy
    _keys = numpy.array(list( self._file_reader.keys() ))

    try:
      offset_key = _keys[ numpy.where(itrial < _keys)[0][0] - 1]
    except IndexError:
      offset_key = _keys[-1]

    return self._file_reader[offset_key], itrial - offset_key

      
  ''' read the a trial:
    if current_flag is true, it read the current trace
    otherwise it reads the voltage traces '''
  def _read_trace(self, itrial, current_flag):
    file_reader, offset_key = self._get_file_reader(itrial)
    itrial = int(itrial - offset_key)
    trace = file_reader._read_trace(itrial, current_flag)
    if not current_flag:
      trace[:, 1] -= self.junction_potential
    return trace
  
  '''
    read the voltage trace
  '''
  def read_voltage_trace(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    return fr.read_voltage_trace(itrial)

  '''
    read the current trace associated to a trial
  '''
  def read_current_trace(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    return fr.read_current_trace(itrial) 

  
  def __union_of_string(self, s):
    r = ''
    for _s in s:
      r += _s
    return r
  
          
  ''' return all the traces obtained with the same intensity '''
  def trial_by_current(self, cur_bin=None, total_current_flag=False, suffix=None):
    ret = {}

    
    for i in range(self.size()):
      # check whether the suffix is considered
      # it is case insensitive
      if suffix:
        _key_low = self._get_key(i).lower()
        _flag_continue = True
        if type(suffix) == str:
          _flag_continue = suffix.lower() not in _key_low
        elif type(suffix) == list or type(suffix) == set:
          for _suffix in suffix:
            _flag_continue = _flag_continue and _suffix.lower() not in _key_low

        # let's check again
        if _flag_continue:
          continue
            
      if total_current_flag:
        cc = self.step_amplitude(i, cc_bin=None) + self.bias_amplitude(i)
        if cur_bin:
          cc = int(cc/cur_bin)*cur_bin
      else:
        cc = self.step_amplitude(i, cc_bin=cur_bin)
        
      stim_key = (cc, self.step_length(i, cc_bin=cur_bin))
      
      if stim_key not in ret:
        ret[stim_key] = []
      ret[stim_key].append(i)

    return ret
  

  def _step_length(self, itrial, tinit, tend, stim_duration, cc_bin=None, plot=False):
    fr, itrial = self._get_file_reader(itrial)
    return fr._step_length(itrial, tinit, tend, stim_duration, cc_bin=cc_bin, plot=plot)
    
  '''
    current duration
  '''
  def step_length(self, itrial, cc_bin=None, plot=False):
    fr, itrial = self._get_file_reader(itrial)
    return fr.step_length(itrial, cc_bin=cc_bin, plot=plot) 
      

  '''
    bias current amplitude
  '''
  def bias_amplitude(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    return fr.bias_amplitude(itrial) 
  

  '''
    stimulus current amplitude
  '''
  def time_stamp(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    return fr.time_stamp(itrial) 

  '''
    stimulus current amplitude
  '''
  def step_amplitude(self, itrial, cc_bin=None):
    fr, itrial = self._get_file_reader(itrial)
    return fr.step_amplitude(itrial, cc_bin=cc_bin) 
    

  ''' return holding voltage '''
  def holding_voltage(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    return fr.holding_voltage(itrial)

  ''' plot a trace '''
  def plot_voltage_trace(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    fr.plot_voltage_trace(itrial)

    
  ''' plot a trace '''
  def plot_current_trace(self, itrial):
    fr, itrial = self._get_file_reader(itrial)
    fr.plot_current_trace(itrial)
    
if __name__ == '__main__':
  import matplotlib.pyplot as plt
  import efel
  import eFELExt as efel_ext
  import numpy as np
  
  thresh = 0
  def init():
    import efel
    efel.setThreshold(thresh)
  init()
  
  fr = FileReader("dataset/2018-08-03_NS/2018-08-03 Slice1c2 fI.hdf5", filter_flag=True)
  i = fr.keys.index('000011 f-I curve +20~+300')
  fr.plot_voltage_trace(i)
  
  data = fr.read_voltage_trace(i)
  pack = {
    'T':data[:,0],
    'V':data[:,1],
    'stim_start':[800.0],
    'stim_end':[2800.0]
  }
  
  x = efel.getFeatureValues([pack], ['Spikecount', 'all_ISI_values', 'time_to_first_spike'])
  t = np.cumsum(np.concatenate(([0.0], x[0]['all_ISI_values']))) + x[0]['time_to_first_spike']
  t = t[t>=50]+800.0
  plt.scatter(t, [.00]*len(t))

  print ('3-Pole filtered Spikcount:', x[0]['Spikecount'][0])
  #print (efel_ext.SpikeCountEdyta(pack))

  fr_no_filt = FileReader("dataset/2018-08-03_NS/2018-08-03 Slice1c2 fI.hdf5", filter_flag=False)
  i = fr_no_filt.keys.index('000011 f-I curve +20~+300')
  fr_no_filt.plot_voltage_trace(i)
  
  data = fr_no_filt.read_voltage_trace(i)
  pack = {
    'T':data[:,0],
    'V':data[:,1],
    'stim_start':[800.0],
    'stim_end':[2800.0]
  }
  x = efel.getFeatureValues([pack], ['peak_time', 'peak_voltage', 'time_to_first_spike'])
  #t = np.cumsum(np.concatenate(([0.0], x[0]['all_ISI_values']))) + x[0]['time_to_first_spike']
  #t = t[t>=50]+800.0
  #5plt.scatter(t, [5.00]*len(t))
  print ('No 3-Pole filtered Spikcount:', x[0]['peak_time'][0])
  #print (efel_ext.SpikeCountEdyta(pack))
  
  plt.show()

