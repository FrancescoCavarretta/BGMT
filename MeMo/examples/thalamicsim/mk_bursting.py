
if __name__ == '__main__':
    import pandas as pd
    from parameters import Parameters
    import numpy as np
    gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_cur.npy', fmt='output-burst-cur-%d', lesioned_flags=[True, False])

    for percsync in [1.0]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000 })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

        b = dict({ 'snr__burst__Tdur':150.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000, 'snr_async_no_burst':True })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

    print(len(par.params))
    par.close()

    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_cur_test.npy', fmt='output-burst-cur-%d', lesioned_flags=[True, False])

    for percsync in [1.0]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000 })
        par.add(tstop=2000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

        b = dict({ 'snr__burst__Tdur':150.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000, 'snr_async_no_burst':True })
        par.add(tstop=2000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

    print(len(par.params))
    par.close()



    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting.npy', fmt='output-burst-%d', lesioned_flags=[True, False])
    for percsync in [0.125, 0.375, 0.625, 0.875]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000 })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

        b = dict({ 'snr__burst__Tdur':150.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000, 'snr_async_no_burst':True })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

    print(len(par.params))
    par.close()

    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_strongsnr.npy', fmt='output-burst-%d', lesioned_flags=[True])
    for percsync in [0, 0.25, 0.5, 0.75, 1.0]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000 })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, snr__g=1.15 * gsyn['SNR'], **b)

        b = dict({ 'snr__burst__Tdur':150.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000, 'snr_async_no_burst':True })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, snr__g=1.15 * gsyn['SNR'], **b)

    print(len(par.params))
    par.close()


    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_psth_bursting.npy', fmt='output-burst-%d')
    for percsync in [1, 0.75, 0.5, 0.25]:

        b = dict({ 'snr__burst__Tdur':150.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':400.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':150.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':31000, 'snr__burst__tinit':10000, 'snr_async_no_burst':True })
        par.add(tstop=31000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)

    print(len(par.params))
    par.close()

    '''par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_off_reduced.npy', fmt='output-burst-off-%d')
    for percsync in [1]:

#      for mod__g, drv__n in [((0.002134+0.002246) / 2, 5), (0.002134, 10), (0.002021, 15), (0.001909, 20)]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        #par.add(tstop=30000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50, **b)
        par.add(tstop=31000, ntrial=10, mod__g=float(0.05 * 13.5 * 0.2 * gsyn['CX']), drv__g=float(0.05 * 13.5 * gsyn['CN_VM']), **b)
    print(len(par.params))
    par.close()


    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_on_reduced.npy', fmt='output-burst-on-%d')
    for percsync in [1]:
 #     for mod__g, drv__n in [((0.002134+0.002246) / 2, 5), (0.002134, 10), (0.002021, 15), (0.001909, 20)]:
        b = dict({ 'snr__burst__Tdur':100.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        #par.add(tstop=30000, snr__mean_rate=35.0, snr__regularity=50, **b)
        par.add(tstop=31000, ntrial=10, mod__g=float(0.05 * 13.5 * 0.2 * gsyn['CX']), drv__g=float(0.05 * 13.5 * gsyn['CN_VM']), **b)
    print(len(par.params))
    par.close()

    par = Parameters(np.load('vmcell/hof_chk2.npy', allow_pickle=True).tolist(), 'test_bursting_off.npy', fmt='output-burst-off-%d')
    for percsync in [1]:

#      for mod__g, drv__n in [((0.002134+0.002246) / 2, 5), (0.002134, 10), (0.002021, 15), (0.001909, 20)]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        par.add(tstop=30000, ntrial=10, snr__mean_rate=35.0, snr__regularity=50,  mod__g=0.9 * gsyn['CX'], **b)
        #par.add(ntrial=5, tstop=21000, **b)
    print(len(par.params))
    par.close()


    par = Parameters(np.load('vmcell/hof_chk2.npy', allow_pickle=True).tolist(), 'test_bursting_on_2.npy', fmt='output-burst-on-2-%d')
    for percsync in [1]:
 #     for mod__g, drv__n in [((0.002134+0.002246) / 2, 5), (0.002134, 10), (0.002021, 15), (0.001909, 20)]:
        b = dict({ 'snr__burst__Tdur':100.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        par.add(tstop=30000, snr__mean_rate=35.0, snr__regularity=50, mod__g=0.9 * gsyn['CX'], **b)
        #par.add(ntrial=5, tstop=21000, **b)
    print(len(par.params))
    par.close()


    par = Parameters(np.load('vmcell/hof_136_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_off_2.npy', fmt='output-burst-off-2-%d')
    for percsync in [1]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        #par.add(tstop=30000, snr__mean_rate=35.0, snr__regularity=50, **b)
        par.add(tstop=30000, **b)
    print(len(par.params))
    par.close()


    par = Parameters(np.load('vmcell/hof_136_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_on_2.npy', fmt='output-burst-on-2-%d')
    for percsync in [1]:
        b = dict({ 'snr__burst__Tdur':100.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        #par.add(tstop=30000, snr__mean_rate=35.0, snr__regularity=50, **b)
        par.add(tstop=30000, **b)
    print(len(par.params))
    par.close()


    a = 7 * 0.05 + 0.5
    gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
    gmod, gdrv = 0.5 * gsyn['CX'], 0.05 * gsyn['CN_VL'] + (1 - 0.05) * gsyn['CN_VM']

    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_off_2.npy', fmt='output-burst-off-%d')
    for percsync in [1]:
        b = dict({ 'snr__burst__Tdur':0.0, 'snr__burst__Tpeak':0.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        par.add(tstop=30000, drv__g=float(a*gdrv), mod__g=float(a*gmod), snr__mean_rate=35.0, snr__regularity=50, **b)
    print(len(par.params))
    par.close()


    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_bursting_on_2.npy', fmt='output-burst-on-%d')
    for percsync in [1]:
        b = dict({ 'snr__burst__Tdur':100.0, 'snr__burst__Tpeak':20.0, 'snr__burst__max_rate':320.0, 'snr__burst__min_rate':35.0,
                   'snr__burst__burst_mean_rate':1.0, 'snr__burst__min_inter_period':100.0, 'snr__burst__regularity_sync':5000000, 
                   'snr__burst__regularity_async':5, 'snr__burst__percent_sync':percsync, 'snr__burst__tstop':30000, 'snr__burst__tinit':10000 })
        par.add(tstop=30000, drv__g=float(a*gdrv), mod__g=float(a*gmod), snr__mean_rate=35.0, snr__regularity=50, **b)
    print(len(par.params))
    par.close()'''
