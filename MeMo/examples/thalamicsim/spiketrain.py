import numpy as np
import efel

def get_spike_times(t, v, threshold=-30):
    """
    Extract the spike time
    t:time array of the trace
    v:voltage array of the trace
    threshold:(default -30) spike threshold
    """
    idx = np.argwhere(v > threshold)[:, 0]
    idx = np.delete(idx, np.argwhere( (idx[1:] - idx[:-1]) == 1)[:, 0] + 1)
    return t[idx]


def cut_spikes(t, v, tinit, tend, dt, threshold=-30): #, efel_flag=True):
    """
    Remove spikes
    t:time array of the trace
    v:voltage array of the trace
    threshold:(default -30) spike threshold
    """

    
    # retain only portion of trace of interest
    #idx = np.logical_and(t >= tinit, t <= tend)
    #t = t[idx]
    #v = v[idx]
    
#    if efel_flag:    
    efel.setThreshold(threshold)
    trace = {
        'T':t,
        'V':v,
        'stim_start':[tinit],
        'stim_end':[tend]
    }
    
    try:
        ef = efel.getFeatureValues([trace], ['AP_begin_indices', 'AP_end_indices'])

        del_indices = np.array([])
        a = ef[0]['AP_begin_indices']
        b = ef[0]['AP_end_indices']
        j = min([a.size, b.size])
        a = a[:j]
        b = b[:j]

        for init_index, end_index in np.concatenate(([a], [b])).T:
            del_indices = np.concatenate((del_indices, np.arange(init_index, end_index)))

        del_indices = del_indices.astype(int)
        
        
        t = np.delete(t, del_indices)
        v = np.delete(v, del_indices)
    except:
        pass
        
  

 #   else:
 #       del_indices = v > threshold
        

    tp = np.arange(tinit, tend+dt, dt)
    vp = np.interp(tp, t, v)    
    return tp, vp


def get_baseline_voltage(t, v):
    """
    return the average value of baseline membrane potential
    t:time array of the trace (in ms)
    v:voltage array of the trace
    cutoff: (default 10 Hz) cutoff frequency in Hertz
    """
#    idx = np.logical_and(t >= tinit, t <= tend)
#    t = t[idx]
#    v = v[idx]    
    return np.mean(cut_spikes(t, v, 10000, 20000, 0.1)[1])

