import numpy as np

etypes = ["control_BK_short_AP", \
        "control_BK_short_AP_AA0137", \
        "control_BK_short_AP_AA0176", \
        "control_BK_short_AP_AA0226", \
        "control_BK_short_AP_AA0448", \
        "control_BK_short_AP_AA0451", \
        "control_BK_short_AP_AA0612", \
        "control_BK_short_AP_AA0675", \
        "control_BK_short_AP_AA0718", \
        "control_BK_short_AP_AA0719", \
        "control_BK_short_AP_AA0809" ]


def branch_order(sec, soma_sec):
  from neuron import h
  order = 0
  sref = h.SectionRef(sec=sec)
  while sref.sec != soma_sec:
    sref = h.SectionRef(sec=sref.parent)
    order += 1
  return order

  
def mk_cell_model(etype_id):
  def load_params(filename):
    import numpy as np
    return sorted(np.load(filename, allow_pickle=True).tolist().items())

  import mkcell
  import os
  
  filename = "test_model_control_edyta_test_good.npy"
  param = load_params(os.path.join(os.path.dirname(__file__), 'mkcell', filename))[0][1][0]
  etype = etypes[etype_id]
  return mkcell.mk_cell_model(param, etype=etype)


def get_n_synapse(etype_id, dens):
  nsyn = 0
  for sec in mk_cell_model(etype_id).icell.basal:
    for seg in sec.allseg():
      ibin = int(round(seg.diam / 0.5))
      if ibin > 2:
        ibin = 2
      nsyn += seg.area() * dens[ibin]
  return nsyn


dens = { "AS":{0:0.0696, 1:0.0275, 2:0.0005},
         "S1":{0:0.0003, 1:0.00025, 2:0.0004},
         "S2":{0:0.0, 1:0.0003, 2:0.0014}}

res = {}
for k in dens.keys():
  vec = np.array([get_n_synapse(i, dens[k]) for i in range(len(etypes)) ])
  print (k, vec.mean(), vec.std())
  res[k] = (vec.mean(), vec.std())

  
