TITLE Thalamic KD channels

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX TC_iD
	USEION k READ ek WRITE ik
        RANGE gk_max
	RANGE m_inf, h_inf
	RANGE ik
        RANGE q10
        GLOBAL shift


        
        RANGE output, i_output
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
}

PARAMETER {
	gk_max	= 1.0e-1 	(S/cm2) 

	celsius         (degC)
	dt              (ms)
	v               (mV)
        q10=3.0
	shift=0               (mV)

}

STATE {
  m h
}

ASSIGNED {
	ik	(mA/cm2)
	ek	(mV)
	m_inf
	h_inf
	tcorr
	tau_m
	tau_h


        
        i_output
        output
}


BREAKPOINT {
	SOLVE states METHOD cnexp

        
        output   =  gk_max*m*h
        i_output = output*(v - ek)

        
	ik   = i_output
}


DERIVATIVE states {   : exact Hodgkin-Huxley equations
	evaluate_fct(v)
	m' = (m_inf - m) / tau_m
	h' = (h_inf - h) / tau_h
}


UNITSOFF
INITIAL {
  	tcorr = q10 ^ ((celsius-23)/ 10 )
        evaluate_fct(v)
	m = m_inf
	h = h_inf


        
        output   =  gk_max*m*h
        i_output = output*(v - ek)

        
	ik   = i_output
      
}

PROCEDURE evaluate_fct(v(mV)) {
  m_inf = 1/(1+exp(-(v+22+shift)/7.4))
  h_inf = 1-1/(1+exp(-(v+44+shift)/4.3))
  tau_m = 2.8+37.1*exp(-((v+22+shift)/3.1)^2)/tcorr
  tau_h = 0.5+exp(-((v + 44+shift)/1.0)^2)/tcorr
}

UNITSON






