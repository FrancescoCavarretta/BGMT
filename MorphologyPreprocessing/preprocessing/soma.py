def preprocess(sec, S=293.0, ecc=0.76):
  import numpy
  from neuron import h

  # get soma radius
  dmin = 2 * numpy.sqrt(S/numpy.pi/numpy.sqrt(1-ecc*ecc))
  dmax = dmin/numpy.sqrt(1-ecc*ecc)

  # set somatic size
  h.pt3dclear(sec=sec)
  h.pt3dadd(0.0, 0.0, 0.0, dmin, sec=sec)
  h.pt3dadd(0.0, 0.0, dmax, dmin, sec=sec)

  

