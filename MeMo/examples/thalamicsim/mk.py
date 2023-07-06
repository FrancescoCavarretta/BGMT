>>> import numpy as np
>>> data = {}
>>> for i in range(2):
...   if 'session_description' in data:
...     data['session_description'] += tmp['session_description']
...     del tmp['session_description']
...   data.update(tmp)
... 
Traceback (most recent call last):
  File "<stdin>", line 5, in <module>
NameError: name 'tmp' is not defined
>>> for i in range(2):
...   tmp=np.load('test_bursting_ih_%d.npy' % i, allow_pickle=True).tolist()
...   if 'session_description' in data:
...     data['session_description'] += tmp['session_description']
...     del tmp['session_description']
...   data.update(tmp)
... 
>>> np.save('burst_spike_times_ih.npy', data, allow_pickle=True)
>>> 


