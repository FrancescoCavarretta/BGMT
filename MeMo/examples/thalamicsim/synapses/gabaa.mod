NEURON {
	POINT_PROCESS MeMo_GABAA
	RANGE tau, e, i, g_max
	NONSPECIFIC_CURRENT i
        RANGE tadj, tau_in, q10, temp0

	RANGE g
}

UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(umho) = (micromho)
}

PARAMETER {
	tau = 14 (ms) <1e-9,1e9>
	e = -75	(mV)
        g_max = 0 (umho)
        q10 = 2.1
        temp0 = 32
}

ASSIGNED {
	v (mV)
	i (nA)
        celsius
        tadj
        tau_in
}

STATE {
	g (umho)
}

INITIAL {
	g=0
        tadj=q10^((celsius-temp0)/10)
        tau_in = tau / tadj
}

BREAKPOINT {
	SOLVE state METHOD cnexp
	i = g*(v - e)
}

DERIVATIVE state {
	g' = -g/tau_in
}

NET_RECEIVE(weight) {
	g = g + g_max
}
