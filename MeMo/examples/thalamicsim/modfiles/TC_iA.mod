TITLE Fast Transient Potassium Current IA

:   Huguenard and Prince, 1991
:   The junction potential was considered


UNITS {
    (mV) = (millivolt)
    (mA) = (milliamp)
    (S)  = (siemens)
}

NEURON {
    SUFFIX TC_iA
    USEION k READ ek WRITE ik
    RANGE gk_max, ik, taom, taoh1, taoh2
    RANGE shift



    
    RANGE output, i_output
}

PARAMETER {
    gk_max  = 5.5e-3 (S/cm2)	: Default maximum conductance
    celsius
    shift   = 0 (mV)
}

ASSIGNED { 
    v     (mV)
    ek    (mV)
    ik    (mA/cm2)
    m1inf 
    m2inf
    hinf
    taoh1 (ms)
    taoh2 (ms)
    taom  (ms)
    tadj




    
    output
    i_output
}

STATE {
    m1 m2 h1 h2
}

BREAKPOINT {
    SOLVE states METHOD cnexp


    
    
    output   = gk_max * (0.6*h1*m1^4+0.4*h2*m2^4)
    i_output = output*(v-ek)




    ik = i_output
}

INITIAL {
    tadj = 2.8 ^ ((celsius-23)/10)
    settables(v)
    m1 = m1inf
    m2 = m2inf
    h1 = hinf
    h2 = hinf


    
    output   = gk_max * (0.6*h1*m1^4+0.4*h2*m2^4)
    i_output = output*(v-ek)




    ik = i_output
}

DERIVATIVE states {  
    settables(v)      
    m1' = (m1inf-m1)/taom
    m2' = (m2inf-m2)/taom
    h1' = (hinf-h1)/taoh1
    h2' = (hinf-h2)/taoh2
}

UNITSOFF

PROCEDURE settables(v (mV)) { 
    LOCAL taodef

    m1inf = 1/(1+exp(-(v+60+shift)/8.5))
    m2inf = 1/(1+exp(-(v+36+shift)/20))
    hinf  = 1/(1+exp((v+78+shift)/6))

    taom  = (0.37 + 1/(exp((v+35.8+shift)/19.7)+exp(-(v+79.7+shift)/12.7))) / tadj
    
    taodef = (1/(exp((v+46+shift)/5)+exp(-(v+238+shift)/37.5))) / tadj
    if (v<(-63-shift)) {taoh1 = taodef} else {taoh1 = (19 / tadj)}
    if (v<(-73-shift)) {taoh2 = taodef} else {taoh2 = (60 / tadj)}

}

UNITSON
