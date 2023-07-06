TITLE Hippocampal HH channels

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX TC_HH
	USEION na READ ena WRITE ina
	USEION k READ ek WRITE ik
	RANGE gna_max, gk_max, gnap_max, gna_max_extra, gnap_max_extra, gk_max_extra
	RANGE m_inf, h_inf, n_inf, mp_inf, hp_inf
	RANGE tau_m, tau_h, tau_n, tau_mp, tau_hp
	RANGE ina, ik

        : ------ analysis ------
        RANGE output_nat, output_nap, output_k, i_output_nat, i_output_nap, i_output_na, i_output_k
        GLOBAL m_factor, n_factor, h_factor
        GLOBAL vtraubna, vtraubk
        
        GLOBAL shift
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(S)  = (siemens)
}

PARAMETER {
	gna_max	= 1.0e-1 	(S/cm2) 
	gnap_max	= 1.0e-1 	(S/cm2) 
	gk_max	= 1.0e-1 	(S/cm2)
        
	gna_max_extra	= 0 	(S/cm2) 
	gnap_max_extra	= 0 	(S/cm2) 
	gk_max_extra	= 0 	(S/cm2) 

	celsius         (degC)
	dt              (ms)
	v               (mV)
	vtraubna = -55.5   : Average of original value and Amarillo et al., J Neurophysiol 112:393-410, 2014
        vtraubk  = -55.5   : Average of original value and Amarillo et al., J Neurophysiol 112:393-410, 2014
        shift    = 0
        m_factor = 1
        n_factor = 1
        h_factor = 1
}

STATE {
	m h n mp hp
}

ASSIGNED {
	ina	(mA/cm2)
	ik	(mA/cm2)
	ena	(mV)
	ek	(mV)
	m_inf
	h_inf
	mp_inf
	hp_inf
	n_inf
	tau_m
	tau_h
	tau_n
	tau_mp
	tau_hp
	tcorr




        output_nat
        output_nap
        output_k
        i_output_nat
        i_output_nap
        i_output_na
        i_output_k
}


BREAKPOINT {
	SOLVE states METHOD cnexp

        output_nat = (gna_max + gna_max_extra) * m*m*m*h
        output_nap = (gnap_max + gnap_max_extra) * mp*mp*mp*hp 
        output_k   = (gk_max + gk_max_extra) * n*n*n*n
        
        i_output_nat  = output_nat*(v - ena)
        i_output_nap  = output_nap*(v - ena)
        i_output_na   = i_output_nat + i_output_nap
        i_output_k    = output_k * (v - ek)
        
	ina   =  i_output_na 
	ik    = i_output_k   
}


DERIVATIVE states {   : exact Hodgkin-Huxley equations
	evaluate_fct(v)
	m' = (m_inf - m) / tau_m
	h' = (h_inf - h) / tau_h
	mp' = (mp_inf - mp) / tau_mp
	hp' = (hp_inf - hp) / tau_hp
	n' = (n_inf - n) / tau_n
}



UNITSOFF
INITIAL {
	tcorr = 3.0 ^ ((celsius-36)/ 10 )
        evaluate_fct(v)
	m = m_inf
	h = h_inf
	mp = mp_inf
	hp = hp_inf
	n = n_inf

        output_nat = (gna_max + gna_max_extra) * m*m*m*h
        output_nap = (gnap_max + gnap_max_extra) * mp*mp*mp*hp 
        output_k   = (gk_max + gk_max_extra) * n*n*n*n
        
        i_output_nat  = output_nat *(v - ena)
        i_output_nap  = output_nap *(v - ena)
        i_output_na   = i_output_nat + i_output_nap
        i_output_k    = output_k * (v - ek)
        
	ina   =  i_output_na  :gna_max * m*m*m*h * (v - ena) + gnap_max * (mp*mp*mp*hp) * (v - ena) 
	ik    =  i_output_k   :gk_max  * n*n*n*n * (v - ek)
}

PROCEDURE evaluate_fct(v(mV)) { LOCAL a,b,v2, v3, v4

	v2 = v - vtraubna + shift : convert to traub convention
	v3 = v - vtraubk + shift  : EI: shift only K
	v4 = v - vtraubna + 15 + shift: convert to traub convention
                                
	if(v2 == 13 || v2 == 40 || v3 == 15 || v4 == 13 || v4 == 40){
    	v = v+0.0001
        }

	a = 0.32 * (13-v2) / ( exp((13-v2)/4) - 1)
	b = 0.28 * (v2-40) / ( exp((v2-40)/5) - 1)
	tau_m = 1 / (a + b) / tcorr * m_factor
	m_inf = a / (a + b)

	a = 0.128 * exp((17-v2)/18)
	b = 4 / ( 1 + exp((40-v2)/5) )
	tau_h = 1 / (a + b) / tcorr * h_factor
	h_inf = a / (a + b)


	a = 0.032 * (15-v3) / ( exp((15-v3)/5) - 1)
	b = 0.5 * exp((10-v3)/40)
	tau_n = 1 / (a + b) / tcorr * n_factor
	n_inf = a / (a + b)




	if(v4 == 13 || v4 == 40 || v4 == 15 ){
          v = v+0.0001
        }

	a = 0.32 * (13-v4) / ( exp((13-v4)/(1.5*4)) - 1) 
	b = 0.28 * (v4-40) / ( exp((v4-40)/(1.5*5)) - 1) 
	tau_mp = 1 / (a + b) / tcorr
	mp_inf = a / (a + b)

                                
        a = 0.128 * exp((17-v4)/18) 
        b = 4 / ( 1 + exp((40-v4)/5) )
	tau_hp = 1 / (a + b) / tcorr
        hp_inf = a / (a + b)

                              
                                
}

UNITSON






