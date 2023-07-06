NEURON {
	POINT_PROCESS MeMo_ExpSyn
	RANGE tau, e, i, g_max
	NONSPECIFIC_CURRENT i

	RANGE g
}

UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(umho) = (micromho)
}

PARAMETER {
	tau = 0.1 (ms) <1e-9,1e9>
	e = 0	(mV)
        g_max = 0 (umho)
}

ASSIGNED {
	v (mV)
	i (nA)
}

STATE {
	g (umho)
}

INITIAL {
	g=0
}

BREAKPOINT {
	SOLVE state METHOD cnexp
	i = g*(v - e)
}

DERIVATIVE state {
	g' = -g/tau
}

NET_RECEIVE(weight) {
	g = g + g_max
}
