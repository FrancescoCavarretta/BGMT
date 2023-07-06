import numpy as np

import sim as ts
import MeMo.compiler as compiler
import MeMo.compiler.precompiler as precompiler
import MeMo.compiler.neuron as base
import MeMo.compiler.neuron.util.recorder as recorder
import MeMo.memo.spiketrain as stn

import vmcell

from neuron import h
from neuron import coreneuron

def mk_default_inputs():
    bgST_sync = stn.SpikeTrain("regular", tstart=5000, number=1, mean_rate=10.0, time_unit="ms")
    bgST_async = stn.SpikeTrain("regular", tstart=5000, number=1, mean_rate=10.0, time_unit="ms")
    rtnST = stn.SpikeTrain("regular", tstart=5000, number=1, mean_rate=10.0, time_unit="ms")
    drvST = stn.SpikeTrain("regular", tstart=5000, number=1, mean_rate=10.0, time_unit="ms")
    modST = stn.SpikeTrain("regular", tstart=5000, number=1, mean_rate=10.0, time_unit="ms")
    return bgST_sync, bgST_async, rtnST, drvST, modST


def clean(r):
    for _r in list( r.values() ):
        for __r in list( _r.values() ):
            if "real_simobj" in __r:
                del __r["real_simobj"]


def _test(cellid, input_name, gsyn, nsyn, seed, vclamp, tstim, tstop, kwargs):
    circ, conn = ts.mk_vm_model(cellid, False, *mk_default_inputs())
    conn.n_reticular = 0
    conn.n_snr = 0
    conn.n_modulator = 0
    conn.n_driver = 0    

    setattr(conn, "n_" + input_name, nsyn)

    setattr(list(circ.models)[0], "gsyn_" + input_name, gsyn)

    retsim = precompiler.precompile(circ, seed)
    compiler.compile(retsim, base)

    soma = retsim["models"][list(circ.models)[0].cell]["real_simobj"].section["somatic"][0]

    seclamp = h.SEClamp(soma(0.5))
    seclamp.amp1 = vclamp
    seclamp.dur1 = tstop
    
    # record current
    rri = ts.recorder.Recorder(seclamp._ref_i, seg=soma(0.5))

    # run simulation and get the output
    #ts.nrn_run(retsim, circ, conn, tstop, seed, [], tcheckpoint=None, **kwargs)
    coreneuron.active = False
    h.CVode().active(1)
    ts.base.runtime.setup(**kwargs)
    h.v_init = vclamp
    h.CVode().atol(1e-4)
    h.tstop = tstop
    h.run()

    # estimate the peak
    data = rri.get()
    data = data[np.logical_and(data[:, 0] >= tstim, data[:,0] <= tstop), :]
    data[:, 1] = np.abs(data[:, 1] - data[0, 1])
    Di = np.max(data[:, 1])

    clean(retsim)

    del seclamp
    return Di

if __name__ == '__main__':
    import sys

    if '--n-trial' in sys.argv:
        ntrial = int(sys.argv[sys.argv.index('--n-trial')+1])
    else:
        ntrial = 10

    param_file = sys.argv[sys.argv.index('--param_file')+1]
    conductance_file = sys.argv[sys.argv.index('--output')+1]
    ts._MODEL_CONFIG_FILENAME = param_file

    nmodel = len([k for k in np.load(param_file, allow_pickle=True).tolist().keys() if k[0].startswith('control')])
    print ('nmodel', nmodel)

    def test(input_name, gsyn, vclamp, nsyn, tstim=5000, tstop=5500.0, **kwargs):
        import multiprocessing
        from multiprocessing import Pool

        params = []
        for cellid in range(nmodel):
            for iseed in range(ntrial):
                params.append((cellid, input_name, gsyn, nsyn, (iseed, iseed), vclamp, tstim, tstop, kwargs))
        
        with Pool(multiprocessing.cpu_count()) as p:    
            return p.starmap(_test, params )

    def search_gsyn(input_name, peak_target, vclamp, n=1, tstop=5500.0, gmin=0.0, gmax=0.05, err=0.0001, **kwargs):
        while abs(gmin - gmax) > err:
            g = (gmin+gmax) / 2

            peak = test(input_name, g, vclamp, n, tstop=tstop, **kwargs)

            peak_mean = np.mean(peak)

            if peak_mean < peak_target:
                gmin = g
            elif peak_mean > peak_target:
                gmax = g
            else:
                print (np.mean(peak), '+/-', np.std(peak), ' pA   ', peak_target, ' pA')
                break
        print (np.mean(peak), '+/-', np.std(peak), ' pA   ', peak_target, ' pA')

        return g


    g_mean_snr = search_gsyn("snr",  2.7 * 4.1 / 1000.0, -64.0, ena=60.4, ek=-105.8, celsius=32) 
    print ("snr", g_mean_snr)

    g_mean_rtn =  search_gsyn("reticular",  24.43 / 1000.0,     -9.3,  gmax=0.0015, ena=145.2, ek=-272.0, celsius=24, ion_channel_blocker=['TTX', 'Cs'])
    print ("rtn", g_mean_rtn)

    g_mean_cx = search_gsyn("modulator",  28.4 / 1000.0,       -79.3, ena=145.2, ek=-272.0, celsius=24, ion_channel_blocker=['TTX', 'Cs'])
    print ("cx", g_mean_cx)

    #g_mean_cx = search_gsyn("modulator",  165.0 / 3.66 / 3.06 / 1000.0,   -68.4, ena=64.8, n=1, ek=-107.1, celsius=34, ion_channel_blocker=['TTX'])
    #print ("cx", g_mean_cx)

    g_mean_cn_vm = search_gsyn("driver",  165.0 / 1000.0,   -68.4, ena=64.8, n=4, ek=-106.9, celsius=34, ion_channel_blocker=['TTX'])
    print ("vm", g_mean_cn_vm)

#    g_mean_cn_vl = search_gsyn("driver",  847.7 / 1000.0,   -68.4, ena=64.8, n=4, ek=-107.1, celsius=34, ion_channel_blocker=['TTX'])
#    print ("vl", g_mean_cn_vl)


    g = {"SNR":g_mean_snr,
    "CX":g_mean_cx,
    "CN_VM":g_mean_cn_vm,
    "RTN": g_mean_rtn}

    np.save(conductance_file, g, allow_pickle=True)

    for k in g:
	    print (k, np.mean(g[k]))

    g  = np.load('gsyn.npy', allow_pickle=True).tolist()
    g_mean_cx = g['CX']
    g_mean_cn_vm = g['CN_VM']
    peak = test("modulator", g_mean_cx, -79.3, 1, tstop=5500, ena=145.2, ek=-209.5, celsius=24, ion_channel_blocker=['TTX', 'Cs', 'AP5'])
    print(np.mean(peak), np.std(peak))
    peak = test("driver", g_mean_cn_vm, -68.4, 4, tstop=5500, ena=64.8, ek=-107.1, celsius=34, ion_channel_blocker=['TTX'])
    print(np.mean(peak), np.std(peak))
