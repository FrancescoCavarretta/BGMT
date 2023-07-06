
if __name__ == '__main__':
    import pandas as pd
    from parameters import Parameters
    import numpy as np
    gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
    
    par = Parameters(np.load('vmcell/hof_chk3.npy', allow_pickle=True).tolist(), 'test_sensitivity.npy', fmt='output-sense-%d')

    percents = [-0.1, -0.05, 0.0, 0.05, 0.1]

    params = {
        "mod":{
                "n":1450,
                "g":float(gsyn['CX']),
                "mean_rate":1.1,
            },
        "drv":{
                "n":350,
                "g":float(gsyn['CN_VM']),
                "mean_rate":30,
            },
        "rtn":{
                "n":400,
                "g":float(gsyn['RTN']),
                "mean_rate":10,
            },
        "snr":{
                "n":100,
                "g":float(gsyn['SNR']),
                "mean_rate":50,
            },
    }

    for k1 in params:
        for k2 in params[k1]:
            val_name = '%s__%s' % (k1, k2)
            
            for p in percents:
                val = (1 + p) * params[k1][k2]
                if k2 == 'n':
                    val = int(val)
                else:
                    val = float(val)
                print(val_name, val)
                par.add(tstop=20000, ntrial=10, **{val_name:val})
    print(len(par.params))
    par.close()
