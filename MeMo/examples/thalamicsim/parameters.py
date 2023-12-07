import numpy as np
import os
import MeMo.nwbio as nwbio
import sys
# (585+20+60+5)*(2+1*3)

class Parameters:
    def __init__(self, models, filename, fmt='output-test-%d', lesioned_flags=[True,False], seed_inc=3500):
        self.params = []
        self.models = models
        self.filename = filename
        self.fmt = fmt
        self.lesioned_flags = lesioned_flags
        self.seed_inc = seed_inc


    def close(self):
        np.save(self.filename, self.params, allow_pickle=True)

        
    def add(self, tstop=21000, ntrial=10, seed_start=0, **kwargs):
        
        for lesioned_flag in self.lesioned_flags:
            
            if lesioned_flag:
                cellids = [i for i in range(len([ k for k in sorted(self.models.keys()) if k[0].startswith('lesioned') ]))]
            else:
                cellids = [i for i in range(len([ k for k in sorted(self.models.keys()) if k[0].startswith('control')  ]))]
                
            if 'cellids' in kwargs:
              cellids = kwargs['cellids']

            for cellid in cellids:
                for seed in range(ntrial):
                    key = self.fmt % len(self.params)
                    self.params.append({})
                            
                    self.params[-1].update(kwargs)
                    self.params[-1].update({'cellid':cellid, 'seed':((seed_start + seed) * self.seed_inc), 'tstop':tstop, 'key':key})
                    if lesioned_flag:
                        self.params[-1].update({'lesioned':None})
