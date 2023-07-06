import numpy
from neuron import h

def sec2array(sec):
  vec = []
  for i in range(sec.n3d()):
    vec.append(numpy.array([sec.x3d(i), sec.y3d(i),sec.z3d(i),sec.diam3d(i)]))
  return numpy.array(vec)


def array2sec(lst, sec=None):
  if sec is None:
    sec = h.Section()

  sec.pt3dclear()
  for p in lst:
    sec.pt3dadd(p[0], p[1], p[2], p[3])
  return sec


def length(sec):
  sec = sec2array(sec)
  L = numpy.sum(numpy.linalg.norm(sec[:-1,:-1]-sec[1:,:-1], axis=1))
  return L


def _interpolate(sec, dx=5.0):
  sec = sec2array(sec)
  seglen = numpy.linalg.norm(sec[:-1,:-1]-sec[1:,:-1], axis=1)
  L = numpy.sum(seglen)
  t = numpy.concatenate(([0.0], numpy.cumsum(seglen)))

  pt3dlist = [sec[0,:]]
  
  l = dx
  while l <= L:
    i_max = numpy.argwhere(l <= t)[0][0]
    pt3dlist.append( (l-t[i_max-1])/(t[i_max]-t[i_max-1]) * (sec[i_max,:]-sec[i_max-1,:]) + sec[i_max-1,:] )
    l += dx
    
  return pt3dlist




def interpolate(sec, dx=5.0):
  array2sec(_interpolate(sec, dx=dx), sec)



def cut(sec_ref, max_len):
  sec = sec2array(sec_ref)
  idx = numpy.argwhere(numpy.concatenate(([0.0], numpy.cumsum(numpy.linalg.norm(sec[:-1,:-1]-sec[1:,:-1], axis=1)))) >= max_len)[0][0]
  for i in range(sec_ref.n3d()-1, idx-1, -1):
    h.pt3dremove(i, sec=sec_ref)
    
