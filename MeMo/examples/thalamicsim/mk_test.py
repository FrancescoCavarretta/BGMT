
if __name__ == '__main__':
    from parameters import Parameters
    import numpy as np
    g = np.load('gsyn.npy', allow_pickle=True).tolist()

    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_4.npy')
    par.add(ntrial=1)
    par.close()
    print(len(par.params))

    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_1.npy')
    par.add(ntrial=10)
    par.close()
    print(len(par.params))


    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_2.npy')
    par.add(ntrial=10, tstop=21000, snr__n=25)
    par.close()
    print(len(par.params))

    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_3.npy', lesioned_flags=[True], fmt='output-test-snr-%d')
    par.add(ntrial=10, tstop=21000, snr__g=1.15 * g['SNR'])
    par.close()
    print(len(par.params))

