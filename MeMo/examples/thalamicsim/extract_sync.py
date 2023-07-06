import MeMo.nwbio as nwbio

def func(file_key):
  fi = nwbio.FileReader('test_bursting_0.nwb')
  data = fi.read(file_key)
  fi.close()
  return file_key, data

if __name__ == '__main__':

 import MPI_Pool

 fi = nwbio.FileReader('test_bursting_0.nwb')
 sd = fi.session_description.copy()
 for file_key in fi.keys():
  key = file_key.split('.')[0]
  sd.loc[key, 'file_key'] = file_key
 sd = sd[sd.snr__burst__percent_sync.isin([0, 1])]
 fi.close()

 pool = MPI_Pool.Pool()

 args = [ (file_key, ) for file_key in sd.file_key ]

 fw = nwbio.FileWriter('test_bursting_sel_0.nwb', list(sd.drop('file_key', axis=1).reset_index().T.to_dict().values()), 'thalamicdata')

 for file_key, data in pool.map(func, args):
  fw.add(file_key, *data)

 fw.close()

