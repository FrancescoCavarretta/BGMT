class FileWriter:
    def __init__(self, filename, session_description, identifier, \
                 experimenter='', lab='Jaeger Lab', institution='Emory University', \
                 experiment_description='', session_id='happiness_in_silico', \
                 max_size=240000000):
        """
          Create a NWB handle for output
        """
        
        from datetime import datetime
        from dateutil.tz import tzlocal
        from pynwb import NWBFile, NWBHDF5IO     
    
        self.filename = filename
        self.session_description = str(session_description)
        self.identifier = identifier
        self.experimenter = experimenter
        self.lab = lab
        self.institution = institution
        self.experiment_description = experiment_description
        self.session_id = session_id
       
        # file handle
        nwbfile = NWBFile(
            self.session_description,
            self.identifier,
            datetime.now(tzlocal()),
            experimenter=self.experimenter,
            lab=self.lab,
            institution=self.institution,
            experiment_description=self.experiment_description,
            session_id=self.session_id
            )

        with NWBHDF5IO(self.filename, 'w') as io:
            io.write(nwbfile)

        self._size = 0
        self.max_size = max_size
        
        self._open()


    def _open(self):
        from pynwb import NWBHDF5IO
        self.io = NWBHDF5IO(self.filename, 'a')
        self.nwbfile = self.io.read()
        self._size = 0
        

    def add(self, key, t, y, unit='milliseconds', compression='gzip', compression_opts=9):
        from pynwb import TimeSeries
        from hdmf.backends.hdf5.h5_utils import H5DataIO

        if self.io is None or self.nwbfile is None:
            self._open()
        
        self.nwbfile.add_acquisition(TimeSeries(name=key,
                                           data=H5DataIO(data=y.reshape(y.shape[0], 1), chunks=True, maxshape=(None, 1), compression=compression, compression_opts=compression_opts),
                                           starting_time=t[0], rate=(1.0 / (t[1] - t[0])) * 1000, unit=unit))

        # if the number of unstored entry has overcame the maximum count
        self._size += y.shape[0]
        if self.max_size and self._size >= self.max_size:
            self.close()
            self._open()
            
        

    def close(self):
        if self._size > 0:
            self.io.write(self.nwbfile)
            self._size = 0
        self.io.close()
        self.nwbfile = None
        self.io = None
        



class FileReader:
    def __init__(self, filename):
        import pandas as pd
        from pynwb import NWBHDF5IO
        self.filename = filename
        self.io = NWBHDF5IO(self.filename, 'r')
        self.nwbfile = self.io.read()

        try:
            exec('self.session_description = ' + self.nwbfile.session_description)
        except:
            self.session_description = None

        if self.session_description:
            # turn all the attributes from none to true
            for entry in self.session_description:
                for name, val in entry.items():
                    if val is None:
                        entry[name] = True
                    
            # replace None with False
            self.session_description = pd.DataFrame(self.session_description).replace({None:False}).set_index('key')
        
        # access keys
        self.keys = self.nwbfile.acquisition.keys
        
    def read(self, key):
        from pynwb import NWBHDF5IO

        self._size = 0

        self.io.close()

        self.nwbfile = None
        self.io = None

        self.io = NWBHDF5IO(self.filename, 'r')
        self.nwbfile = self.io.read()
            
        
        import numpy as np
        data = self.nwbfile.acquisition[key]
        y = np.array(data.data).flatten()
        
        return data.starting_time + np.arange(0, y.size, 1) / data.rate * 1000.0, y
               
    
    def close(self):
        self.nwbfile = None
        self.io.close()
    
    
        







