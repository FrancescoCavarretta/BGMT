TITLE simple NMDA receptors

: Hines combined AMPA and NMDA and spike dependent plasticity

: Modified from the original AMPA.mod, M.Migliore Jan 2003
: A weight of 0.0035 gives a peak conductance of 1nS in 0Mg

COMMENT
-----------------------------------------------------------------------------

	Simple model for glutamate AMPA receptors
	=========================================

  - FIRST-ORDER KINETICS, FIT TO WHOLE-CELL RECORDINGS

    Whole-cell recorded postsynaptic currents mediated by AMPA/Kainate
    receptors (Xiang et al., J. Neurophysiol. 71: 2552-2556, 1994) were used
    to estimate the parameters of the present model; the fit was performed
    using a simplex algorithm (see Destexhe et al., J. Computational Neurosci.
    1: 195-230, 1994).

  - SHORT PULSES OF TRANSMITTER (0.3 ms, 0.5 mM)

    The simplified model was obtained from a detailed synaptic model that 
    included the release of transmitter in adjacent terminals, its lateral 
    diffusion and uptake, and its binding on postsynaptic receptors (Destexhe
    and Sejnowski, 1995).  Short pulses of transmitter with first-order
    kinetics were found to be the best fast alternative to represent the more
    detailed models.

  - ANALYTIC EXPRESSION

    The first-order model can be solved analytically, leading to a very fast
    mechanism for simulating synapses, since no differential equation must be
    solved (see references below).



References

   Destexhe, A., Mainen, Z.F. and Sejnowski, T.J.  An efficient method for
   computing synaptic conductances based on a kinetic model of receptor binding
   Neural Computation 6: 10-14, 1994.  

   Destexhe, A., Mainen, Z.F. and Sejnowski, T.J. Synthesis of models for
   excitable membranes, synaptic transmission and neuromodulation using a 
   common kinetic formalism, Journal of Computational Neuroscience 1: 
   195-230, 1994.


-----------------------------------------------------------------------------
ENDCOMMENT



NEURON {
	POINT_PROCESS MeMo_AmpaNmda
        
	NONSPECIFIC_CURRENT i
        
        RANGE gnmda, gampa, i, inmda, iampa, mg, e, gnmda_max, gampa_max, ampatau

        THREADSAFE
}

UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(umho) = (micromho)
	(mM) = (milli/liter)
}

PARAMETER {

        
	Cdur	= 1		(ms)	: transmitter duration (rising phase)
        
	Alpha	= 0.35		(/ms)	: forward (binding) rate
	Beta	= 0.035		(/ms)	: backward (unbinding) rate
        
	e	= 0	(mV)		: reversal potential
	mg	= 1    (mM)		: external magnesium concentration

        
        gnmda_max = 0.0 (umho)
        
        gampa_max = 0.0 (umho)
	ampatau = 3 (ms)
     

}


ASSIGNED {
	v		(mV)		: postsynaptic voltage
	i 		(nA)		: total current = iampa+inmda
        
	inmda 		(nA)		: current = gnmda*(v - E)
	iampa 		(nA)		: current = gampa*(v - E)

        
	Rinf				: steady state channels open
	Rtau		(ms)		: time constant of channel binding
	synon
        
        gnmda
        
        r0

        R_Max
}

STATE {
       Ron
       Roff
       gampa
}

INITIAL {
	Rinf = Alpha / (Alpha + Beta)
	Rtau = 1 / (Alpha + Beta)
        r0 = 0
	synon = 0
	gampa = 0
        gnmda = 0
        R_Max = exp(-3 * Cdur / Rtau) * Rinf
}

BREAKPOINT {
	SOLVE release METHOD cnexp
        gnmda = mgblock(v)*(Ron + Roff) / R_Max  *  gnmda_max        
	inmda = gnmda * (v - e)
	iampa = gampa * (v - e)
	i = iampa + inmda
}

DERIVATIVE release {
	Ron' = (synon*Rinf - Ron) / Rtau
	Roff' = -Beta*Roff
	gampa' = -gampa/ampatau
}

: following supports both saturation from single input and
: summation from multiple inputs
: if spike occurs during CDur then new off time is t + CDur
: ie. transmitter concatenates but does not summate
: Note: automatic initialization of all reference args to 0 except first


FUNCTION mgblock(v(mV)) {
	mgblock = 1 / (1 + exp(0.062 (/mV) * -v) * (mg / 3.57 (mM)))
}


NET_RECEIVE(weight, s, w, tlast (ms), r0, t0 (ms)) {

	INITIAL {
		r0 = 0
		t0 = -1e9 (ms)
	}
        
	: flag is an implicit argument of NET_RECEIVE and  normally 0
        if (flag == 0) { : a spike, so turn on if not already in a Cdur pulse

                         
                
                         
		r0 = r0*exp(-Beta*(t - t0))
		t0 = t
                         
		synon = synon + 1
		Ron = Ron + r0
		Roff = Roff - r0
                         
		: come again in Cdur with flag = current value of w+1
		net_send(Cdur, 1)

                gampa = gampa + gampa_max       : ampa conductance         
        } else { : turn off what was added Cdur ago
		r0 = Rinf + (r0 - Rinf) * exp(-(t - t0)/Rtau)
		t0 = t
               
		synon = synon - 1
		Ron = Ron - r0
		Roff = Roff + r0
	}
}







