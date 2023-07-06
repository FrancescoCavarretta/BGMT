
def _check_nchildren(sec):
  import neuron
  sref = neuron.h.SectionRef(sec=sec)
  assert sref.nchild < 1 or sref.nchild > 2


def _check_parent_child_relation(sec):
  import neuron
  import preprocessing.celltree as celltree
  
  sref = neuron.h.SectionRef(sec=sec)
  if sref.has_parent():
    parent_name = celltree.get_section_type(sref.parent)
    my_name = celltree.get_section_type(sec)
    if parent_name != my_name:
      assert parent_name == "soma" and (my_name == "dend" or my_name == "axon")


def _check_soma(sec):
  import neuron
  
  sref = neuron.h.SectionRef(sec=sec)
  assert sref.has_parent() < 1


def check(cell):
  import preprocessing.celltree as celltree
  import misc.sec2array as sec2array
  
  _check_soma(cell.soma[0])
  for sec in celltree.get_descendant(cell.soma[0]):
    sec2array.interpolate(sec)
    _check_nchildren(sec)
    _check_parent_child_relation(sec)
    
