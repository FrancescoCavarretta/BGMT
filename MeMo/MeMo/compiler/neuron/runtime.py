# initialize coreneuron
from neuron import h, coreneuron
import time

def _mech_list(obj, flag):
    # object name
    mech_name = str(obj).split('[')[0]

    # check whether in the list
    mt = h.MechanimType()
    mnames = []
    for i in range(mt.count()):
        mt.select(i)
        mname = h.ref('')[0]
        if mech_name == mname:
            return True
    return False
        
    
def is_mech_density(obj):
    return _mech_list(obj, 0)


def is_mech_point(obj):
    return _mech_list(obj, 1)


def forall():
    """
    iterator for all the sections
    """
    from neuron import h
    allsecs = h.SectionList()
    roots = h.SectionList()
    roots.allroots()
    for s in roots:
        allsecs.wholetree(sec=s)
    return [s for s in allsecs]


def init():
    """
    Initialize coreneuron
    """
    h.load_file("stdgui.hoc")

    # set for eventual recordings of total membrane current
    h.cvode.use_fast_imem(1)
    h.cvode.cache_efficient(1)
    h.cvode_active(0)
    coreneuron.enable = True
    coreneuron.verbose = 0
    print('dt=', h.dt)

def setup(**kwargs):
    """
    Set environmental variables
    """
    # apply a channel blocker
    if 'ion_channel_blocker' in kwargs:
        for blocker in kwargs['ion_channel_blocker']:
            if blocker == 'TTX':
                attrs = [ 'gna_max_TC_HH', 'gnap_max_TC_HH''gna_max_extra_TC_HH', 'gnap_max_extra_TC_HH']
            elif blocker == 'Cs':
                attrs = [ 'gk_max_TC_HH', 'gk_max_TC_iD', 'gk_max_TC_iA',
                          'gSK_E2bar_SK_E2', 'gbar_BK', 'gmax_iM', 'gmax_extra_iM', 'gk_max_extra_TC_HH'  ]
            elif blocker == 'AP5':
                attrs = [ 'gk_max_TC_iD', 'gk_max_TC_iA' ]
            else:
                print (blocker, 'channel blocker is unknown')
            for s in forall():
                for k in attrs:
                    if hasattr(s, k):
                        setattr(s, k, 1e-20)
        del kwargs['ion_channel_blocker']

    # set simulation parameters
    for k, v in kwargs.items():
        try:
            setattr(h, k, v)
        except:
            for s in forall():
                if hasattr(s, k):
                    setattr(s, k, v)


def run(tstop, tcheckpoint=1000.0, vinit=-78.0, recordings=None, **kwargs):
    """
    Run a simulation
    """
    # reinit neuron
    init()

    # set simulation parameters
    setup(**kwargs)

    pc = h.ParallelContext(1)
    h.finitialize(vinit)
    h.stdinit()
    h.t = 0.

    # verbose
    if tcheckpoint:
        print('Simulation started!')
        print('\tSimulation time %f ms' % tstop)
        print('\tCheckpoint every %f ms' % tcheckpoint)
        print ('\tend\tinit\tcheckp.\tsolve\tflush')    

    ttotal = 0.0
    t = 0.0
    while t < tstop:
        if tcheckpoint and (t + tcheckpoint) < tstop:
            tnext = t + tcheckpoint
        else:
            tnext = tstop      

        tstart = time.time()
        # solve and profile
        pc.psolve(tnext)
        tsolve = time.time() - tstart

        tstart = time.time()
        # flush recordings
        if recordings:
            for rec in recordings.values():
                rec._flush()
        tflush = time.time() - tstart

        # total run time
        ttotal += tsolve + tflush

        if tcheckpoint:
            info = (h.t, t, tnext, tsolve, tflush)
            print (('\t%.1f' * len(info)) % info )

        t = tnext

    pc.done()
    pc = None
    if tcheckpoint:
        print('total run time %.1f s' % ttotal)


init()
