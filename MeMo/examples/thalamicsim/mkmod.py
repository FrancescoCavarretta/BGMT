if __name__ == '__main__':
    import pandas as pd
    from parameters import Parameters
    import numpy as np
    gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'st.npy', fmt='output-mod-%d', lesioned_flags=[True])
    for rate in [12.5, 25.0]:
      for amp in [ 0.5 ]:
        m1 = dict({ 'snr__modulation__tinit':10000.0, 'snr__modulation__tstop':20000.0,
                   'snr__modulation__regularity':1e+20, 'snr__modulation__phase':0.0,
                   'snr__modulation__rate':rate, 'snr__modulation__amplitude':amp })
        par.add(tstop=20000, ntrial=10, cellids=[0], **m1)
        for phase in [np.pi]:
          m2 = dict({ 'mod__modulation__tinit':10000.0, 'mod__modulation__tstop':20000.0,
           'mod__modulation__regularity':1e+20, 'mod__modulation__phase':phase,
           'mod__modulation__rate':rate, 'mod__modulation__amplitude':amp })
          m12 = m1.copy()
          m12.update(m2)
          par.add(tstop=20000, ntrial=10, cellids=[0], **m12)
    par.close()
    print(len(par.params))


    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_modulation_brazhnik.npy', fmt='output-mod-%d')
    for rate in [33]:
      for amp in [ 0.5, 0.75 ]:
        m1 = dict({ 'snr__modulation__tinit':10000.0, 'snr__modulation__tstop':20000.0,
                   'snr__modulation__regularity':1e+20, 'snr__modulation__phase':0.0,
                   'snr__modulation__rate':rate, 'snr__modulation__amplitude':amp })
        par.add(tstop=20000, ntrial=10, **m1)
        for phase in [ np.pi, (1+1/3) * np.pi, (1+2/3) * np.pi]:
          m2 = dict({ 'mod__modulation__tinit':10000.0, 'mod__modulation__tstop':20000.0,
           'mod__modulation__regularity':1e+20, 'mod__modulation__phase':phase,
           'mod__modulation__rate':rate, 'mod__modulation__amplitude':amp })
          m12 = m1.copy()
          m12.update(m2)
          par.add(tstop=20000, ntrial=10, **m12)
    par.close()
    print(len(par.params))

