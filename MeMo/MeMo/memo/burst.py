import numpy as np
#import seaborn as sns
#import matplotlib.pyplot as plt



def _get_param(xv, yv, xother):
    """
    Calculates the parameters a, b, c of a 
    parabola given vertex and another point
    xv, yv : vertex coordinates
    xother : additional points
    ------------------------------------------
    a, b, c parameters
    """
    assert yv == 0 or yv == 1
    
    if yv == 0:
        x0 = xv
        x1 = xother
    elif yv == 1:
        x0 = xother
        x1 = xv
    else:
        raise Exception("yv should be equal to either 1 or 0")
    
    
    # a * x * x + b * x + c = y
    a = 1.0 / ((x1 * x1 - x0 * x0) - 2 * xv * (x1 - x0))
    b = - 2 * a * xv
    c = - a * x0 * x0 - b * x0
    
    return a, b, c
    
def _get_param_template(Tpeak, Ttotal, fast_rise, fast_decay):
    """
    Time of peak firing rate and average total duration of burst
    are used to calculate the parameters for the burst template.
    Rise and Decay can be either fast or slow
    Tpeak: Time of peak firing rate
    Ttotal: Total duration of burst
    fast_rise:boolean defining whether the course to peak is concave or convex
    fast_decay:boolean defining whether the course from peak is concave or convex
    ---------------------------------------------------------------------
    a0, b0, c0, a1, b1, c1 parameters for the template
    """
    
    assert Tpeak < Ttotal
    
    if fast_rise:
        a0, b0, c0 = _get_param(0, 0, Tpeak)
    else:
        a0, b0, c0 = _get_param(Tpeak, 1, 0)
        
    if fast_decay:
        a1, b1, c1 = _get_param(Ttotal, 0, Tpeak)
    else:
        a1, b1, c1 = _get_param(Tpeak, 1, Ttotal)
        
    return a0, b0, c0, a1, b1, c1
    
    
def mk_burst_template(Tpeak, Tdur, max_rate, fast_rise, fast_decay, min_rate=0, dt=0.01):
    """
    This function generate a template for burst generation.    Tpeak: Time of peak firing rate
    Ttotal: Total duration of burst
    fast_rise:boolean defining whether the course to peak is concave or convex
    fast_decay:boolean defining whether the course from peak is concave or convex
    max_rate: intra-burst maximum firing rate
    min_rate: intra-burst minimum firing rate
    dt: (default 0.1) time bin of the template
    """
    
    a0, b0, c0, a1, b1, c1 = _get_param_template(Tpeak, Tdur, fast_rise, fast_decay)
    t = np.arange(0, Tdur, dt)
    rate = min_rate + (max_rate - min_rate)* np.concatenate((
            a0 * t[t <= Tpeak] * t[t <= Tpeak] + b0 * t[t <= Tpeak] + c0, 
            a1 * t[t > Tpeak] * t[t > Tpeak] + b1 * t[t > Tpeak] + c1
            ))
    return t, rate


