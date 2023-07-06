import preprocessing.celltree as gd
from neuron import h
import numpy
import misc.sec2array as sec2array

Diameter_min_constant = 0.473
Diameter_NoChild_factor = 0.004
Diameter_WithChild_factor = 0.515
Diameter_WithChild_constant = 0.182

Diameter_primary_max_factor = 0.861
Diameter_primary_constant = 0.858
Diameter_primary_min = 1
Diameter_primary_tapering_factor = 0.045
  

def diameter_rectification(sec):
  for child in gd.get_descendant(sec, children_flag=True):
    diameter_rectification(child)
    
  for i in range(sec.n3d()):
    #if sec.diam3d(i) < 1.0:
    h.pt3dchange(i, sec.x3d(i), sec.y3d(i), sec.z3d(i), sec.diam3d(i), sec=sec)


    
def set_diameter(sec):
  if gd.get_nchildren(sec) == 0:
    diam =   Diameter_min_constant - Diameter_NoChild_factor * gd.get_depth(sec) 
  else:
    diam = 0.0
    for child in gd.get_descendant(sec, children_flag=True):
      diam += child.diam3d(0) ** 1.5
    diam = ( Diameter_WithChild_constant  + Diameter_WithChild_factor * diam ) ** (1/1.5)
  for i in range(sec.n3d()):
    h.pt3dchange(i, sec.x3d(i), sec.y3d(i), sec.z3d(i), diam, sec=sec)


def _diameter_preprocessing(sec):
  sref = h.SectionRef(sec=sec)
  for child in sref.child:
    if gd.get_section_type(sec) == "dend":
      _diameter_preprocessing(child)
  set_diameter(sec)


def _first_order_branch_preprocessing(sec):
  pts = sec2array.sec2array(sec)
  if len(pts) > 1:
    dx = numpy.linalg.norm(pts[1,:-1]-pts[0,:-1])
    for i in range(sec.n3d()):
      # don't reduce the diameter size
      diam_new = sec.diam3d(i) * max([ Diameter_primary_min, Diameter_primary_constant + Diameter_primary_max_factor * numpy.exp(-Diameter_primary_tapering_factor * dx * i) ])
      h.pt3dchange(i, sec.x3d(i), sec.y3d(i), sec.z3d(i), diam_new, sec=sec)


def histogram(sec):
  small = []
  medium = []
  large = []
  
  for child in gd.get_descendant(sec, children_flag=True):
    _small, _medium, _large = histogram(child)
    small += _small
    medium += _medium
    large += _large

  if "dend" in h.secname(sec=sec):
    import numpy
    for i in range(1, sec.n3d()):
      L = numpy.linalg.norm(numpy.array([sec.x3d(i), sec.y3d(i), sec.z3d(i)])-numpy.array([sec.x3d(i-1), sec.y3d(i-1), sec.z3d(i-1)]))
      j = (sec.diam3d(i)+sec.diam3d(i-1))/2.0
      
      if j >= 0 and j < 0.5:
        small.append(L)
        #small.append(j)
        #print (sec.diam3d(i), sec.diam3d(i-1), L)
      elif j >= 0.5 and j < 1.0:
        medium.append(L)
        #medium.append(j)
        #print (sec.diam3d(i), sec.diam3d(i-1), L)
      elif j >= 1.0:
        large.append(L)
        #large.append(j)
        #print (sec.diam3d(i), sec.diam3d(i-1), L)
  
  return small, medium, large

def preprocess(sec):
  # set all leaves
##  d=0
  for _sec in h.SectionRef(sec=sec).child:
    if gd.get_section_type(_sec) == "dend":
      _diameter_preprocessing(_sec)
      _first_order_branch_preprocessing(_sec)
      #diameter_rectification(_sec)
      
##      d += _sec.diam3d(0)
##      print (_sec.diam3d(0))
##  print ('diam', d)
##  s,m,l=histogram(sec)
##  print (numpy.min(s), numpy.max(s), numpy.min(m), numpy.max(m), numpy.min(l), numpy.max(l) )
##  
##  y = numpy.array([numpy.sum(s),numpy.sum(m),numpy.sum(l)])
##  y /= numpy.sum(y)
##  import matplotlib.pyplot as plt
##  #plt.hist(s)
##  #plt.hist(m,color='red')
##  #plt.hist(l,color='green')
##  plt.plot([0,1,2], y)
##  plt.show()
