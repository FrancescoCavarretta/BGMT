
if __name__ == '__main__':
    from parameters import Parameters
    import numpy as np
    gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
    amod = 0.15
    adrv = 0.15
    print('driver', (adrv * gsyn['CN_VL'] + (1 - adrv) * gsyn['CN_VM']) )
    print('modulator', amod*gsyn['CX'] )


    par = Parameters(np.load('mkcell/hof_3sd_good.npy', allow_pickle=True).tolist(), 'test_control.npy')
    par.add(ntrial=1, g_mod=amod*gsyn['CX'], g_drv=(adrv * gsyn['CN_VL'] + (1 - adrv) * gsyn['CN_VM']), tstop=15000)
    par.close()

    par = Parameters(np.load('mkcell/hof_3sd_good.npy', allow_pickle=True).tolist(), 'test_control_0.npy')
    par.add(seed_start=1, ntrial=1, g_mod=amod*gsyn['CX'], g_drv=(adrv * gsyn['CN_VL'] + (1 - adrv) * gsyn['CN_VM']), tstop=15000)
    par.close()
