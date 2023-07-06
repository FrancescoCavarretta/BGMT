def preprocess(sec, length=70.0, diam=1.5):
  import misc.sec2array as sec2array
  import preprocessing.celltree as celltree
  from neuron import h

  # cut the axon
  sec2array.cut(sec, length)

  # set diameter
  for i in range(sec.n3d()):
    h.pt3dchange(i, sec.x3d(i), sec.y3d(i), sec.z3d(i), diam, sec=sec)

  # eliminate descendants, keep axon initial segment only
  seclist = celltree.get_descendant(sec)
  for s in seclist:
    h.disconnect(sec=s)
    
  for s in seclist:
    h.delete_section(sec=s)
  
