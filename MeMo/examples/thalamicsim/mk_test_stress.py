
if __name__ == '__main__':
    from parameters import Parameters
    import numpy as np
    g = np.load('gsyn.npy', allow_pickle=True).tolist()

    par = Parameters(np.load('vmcell/hof_chk2.npy', allow_pickle=True).tolist(), 'test_stress_1.npy')
    par.add(ntrial=10)
    par.close()
    print(len(par.params))


    par = Parameters(np.load('vmcell/hof_chk2.npy', allow_pickle=True).tolist(), 'test_stress_2.npy')
    par.add(ntrial=10, tstop=21000, snr__n=25)
    par.close()
    print(len(par.params))


