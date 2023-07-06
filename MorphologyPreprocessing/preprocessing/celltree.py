from neuron import h

def get_depth(sec):
  depth = -1
  sref = h.SectionRef(sec=sec)
  while sref.has_parent():
    depth += 1
    sref = h.SectionRef(sec=sref.parent)
  return depth
    



def get_descendant(sec, children_flag=False):
  seclist = []
  
  sref = h.SectionRef(sec=sec)
  for child in sref.child:
    seclist.append(child)

  if children_flag:
    return seclist

  i = 0
  while i < len(seclist):
    sref = h.SectionRef(sec=seclist[i])
    for child in sref.child:
      seclist.append(child)
    i += 1
  return seclist



def get_section_type(sec, names=["dend","soma","axon"]):
  for name in names:
    if name in h.secname(sec=sec):
      return name



def get_nchildren(sec):
  return h.SectionRef(sec=sec).nchild()
