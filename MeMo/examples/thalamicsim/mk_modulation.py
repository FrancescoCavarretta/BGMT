if __name__ == '__main__':
    import pandas as pd
    from parameters import Parameters
    import numpy as np
    gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_mod_realistic.npy', fmt='output-mod-realistic-%d')
    for rate in [12.5, 25.0, 31.25]:
      for amp in [ 0.1 ]:
          
        m1 = dict({ 'snr__modulation__tinit':10000.0, 'snr__modulation__tstop':20000.0,
                   'snr__modulation__regularity':1e+20, 'snr__modulation__phase':0.0,
                   'snr__modulation__rate':rate, 'snr__modulation__amplitude':amp })
        
        par.add(tstop=20000, ntrial=10, **m1) #, snr__g=gsyn['SNR']*1.15, **m1)

        
        for phase in [np.pi * 80.0 / 180.0, np.pi * 245.0 / 180.0]:
          m2 = dict({ 'mod__modulation__tinit':10000.0, 'mod__modulation__tstop':20000.0,
           'mod__modulation__regularity':1e+20, 'mod__modulation__phase':phase,
           'mod__modulation__rate':rate, 'mod__modulation__amplitude':amp,
	   'drv__modulation__tinit':10000.0, 'drv__modulation__tstop':20000.0,
           'drv__modulation__regularity':1e+20, 'drv__modulation__phase':phase,
           'drv__modulation__rate':rate, 'drv__modulation__amplitude':amp })

          m12 = m1.copy()
          m12.update(m2)

          par.add(tstop=20000, ntrial=10, **m12) #, snr__g=gsyn['SNR']*1.15, **m12)
          
          
          m3 = dict({ 'mod__modulation__tinit':10000.0, 'mod__modulation__tstop':20000.0,
           'mod__modulation__regularity':1e+20, 'mod__modulation__phase':phase,
           'mod__modulation__rate':rate, 'mod__modulation__amplitude':amp})

          m13 = m1.copy()
          m13.update(m3)

          par.add(tstop=20000, ntrial=10, **m13) #, snr__g=gsyn['SNR']*1.15, **m13)

    par.close()
    print(len(par.params))



    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_mod.npy', fmt='output-mod-%d')
    for rate in [12.5, 25.0]:
      for amp in [ 0.1 ]:
          
        m1 = dict({ 'snr__modulation__tinit':10000.0, 'snr__modulation__tstop':20000.0,
                   'snr__modulation__regularity':1e+20, 'snr__modulation__phase':0.0,
                   'snr__modulation__rate':rate, 'snr__modulation__amplitude':amp })
        
        par.add(tstop=20000, ntrial=10, **m1)

        
        for phase in [np.pi]:
          m2 = dict({ 'mod__modulation__tinit':10000.0, 'mod__modulation__tstop':20000.0,
           'mod__modulation__regularity':1e+20, 'mod__modulation__phase':phase,
           'mod__modulation__rate':rate, 'mod__modulation__amplitude':amp,
	   'drv__modulation__tinit':10000.0, 'drv__modulation__tstop':20000.0,
           'drv__modulation__regularity':1e+20, 'drv__modulation__phase':phase,
           'drv__modulation__rate':rate, 'drv__modulation__amplitude':amp })

          m12 = m1.copy()
          m12.update(m2)

          par.add(tstop=20000, ntrial=10, **m12)
          
          
          m3 = dict({ 'mod__modulation__tinit':10000.0, 'mod__modulation__tstop':20000.0,
           'mod__modulation__regularity':1e+20, 'mod__modulation__phase':phase,
           'mod__modulation__rate':rate, 'mod__modulation__amplitude':amp})

          m13 = m1.copy()
          m13.update(m3)

          par.add(tstop=20000, ntrial=10, **m13)

    par.close()
    print(len(par.params))
