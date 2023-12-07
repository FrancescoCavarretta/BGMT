#!/usr/bin/env python
# coding: utf-8
import MeMo.compiler.neuron.modules as modules
import os

# register model mechanisms
modules.register_modules(os.path.join(os.path.dirname(__file__), './mechanisms'))
_MODEL_CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'hof_chk3.npy')

class Cell:
  
  def __del__(self):
      del self.bpo_cell
      del self.cell
      del self.section
      del self.product 
      
      self.bpo_cell = self.cell = self.section = self.product = None
    
  
  def load_params(self, filename):
    import numpy as np
    return sorted(np.load(filename, allow_pickle=True).tolist().items())


  def _mk_cell_model(self, params, recipes=None, etype="control", cvode_active=True, altmorph=None):
    import os
    import json
    
    from . import CellEvalSetup
    from bluepyopt.ephys.simulators import NrnSimulator
    from bluepyopt.ephys import models

    if recipes is None:
      with open(os.path.join(os.path.dirname(__file__), '.', 'config/recipes.json')) as f:
        recipe = json.load(f)
    c = CellEvalSetup.template.create(recipe, etype, altmorph=altmorph)
    c.freeze(params)
    c.instantiate(sim=NrnSimulator(cvode_active=cvode_active))
    return c


  def mk_cell_model(self, cellid=0, control=True, altmorph=None):
    import os

    param = self.load_params(os.path.join(os.path.dirname(__file__), _MODEL_CONFIG_FILENAME))

    # select etype
    etype = "control" if control else "lesioned"

    # filter the etypes
    model_cfg = [ p for p in param if p[0][0].startswith(etype) ][cellid]
    model_etype = model_cfg[0][0]
    param = model_cfg[1]['parameter']

    return self._mk_cell_model(param, etype=model_etype, altmorph=altmorph)
  

  def __init__(self, name, cellid=0, lesioned_flag=False):      
      self.name = name
      self.cellid = cellid
      self.product = None
      self.lesioned_flag = lesioned_flag
      
      

  def make(self):
    import numpy as np
    import pandas as pd

    if self.product is None:
      self.bpo_cell = self.mk_cell_model(self.cellid, control=not self.lesioned_flag)
      self.cell = self.bpo_cell.icell
      self.morph_table, self.section = Cell.bpo2memo_cell(self.bpo_cell)
      self.product = { "Cell":self.section, "MorphologyTable":self.morph_table }
                
    return self.product
      

  def branch_order(sec, soma_sec):
    from neuron import h
    order = 0
    sref = h.SectionRef(sec=sec)
    while sref.sec != soma_sec:
      sref = h.SectionRef(sec=sref.parent)
      order += 1
    return order

  def bpo2memo_cell(bpo_cell):

    from neuron import h
    import pandas as pd
    import numpy as np

    
    def soma_pos():
      sec = bpo_cell.icell.soma[0]
      points = np.array([[sec.x3d(i), sec.y3d(i), sec.z3d(i)] for i in range(sec.n3d())])
      return np.mean(points, axis=0)

    
    def arc2xyz(sec, arc):
        points = np.array([[sec.x3d(i), sec.y3d(i), sec.z3d(i)] for i in range(sec.n3d())])

        d = np.cumsum(np.linalg.norm(points[1:, :] - points[:-1, :], axis=1))
        ds = arc * d[-1]
        index = np.argwhere(ds <= d).T[0, 0]
        if index == 0:
          dmin = 0
        else:
          dmin = d[index-1]
        dmax = d[index]
        
        a = points[index, :]
        b = points[index + 1, :]
        return (b - a) * (ds - dmin) / (dmax - dmin) + a
      
      
    def dist_from_soma(sec, arc):
      return np.linalg.norm(soma_pos() - arc2xyz(sec, arc))
    


    
    section_collection = {}
    h.distance(sec=bpo_cell.icell.soma[0])
    tab = [] #pd.DataFrame()
    for section_type in bpo_cell.seclist_names:
      section_collection[section_type] = {}
      if section_type != "all":
        for section in getattr(bpo_cell.icell, section_type):
          section_number = int(h.secname(sec=section).split("[")[-1].replace("]", ""))
          section_collection[section_type][section_number] = section
          for segment in section.allseg():
            try:
              tab.append(pd.Series({ "type":section_type,
                                 "segment":segment.x,
                                 "name":section,
                                 "number":section_number,
                                 "diam":segment.diam,
                                 "len":segment.area() / (segment.diam * np.pi),
                                 "pathdist":h.distance(segment.x, sec=section),
                                 "dist":dist_from_soma(section, segment.x),
                                 "order":Cell.branch_order(section, bpo_cell.icell.soma[0]),
                                 "area":segment.area()}).to_frame().T)
            except IndexError:
              pass
    tab = pd.concat(tab)
    tab = tab[tab.area > 0]
    tab["segment"] = tab["segment"].astype(float)
    tab["dist"] = tab["dist"].astype(float)
    tab["len"] = tab["len"].astype(float)
    tab["number"] = tab["number"].astype(int)
    
    return tab, section_collection        
          

  def get(self, target_feature=None, min_value=None, max_value=None, section_type="basal", optional_X=None, target_feature_distribution=None, shuffle=None):
    import pandas as pd
    
    f = self.morph_table.copy()
        
    if section_type:
        if type(section_type) != list:
            section_type = [ section_type ]
            
        f = f[f.type.isin(section_type)]
        
    
    if target_feature:
      if min_value:
        f = f[f[target_feature] >= min_value]
       
      if max_value:
        f = f[f[target_feature] < max_value]

    

    if shuffle:
      tmp = pd.DataFrame()
      while f.shape[0] > 0:
        idx = f.index[int(shuffle(name="uniform", a=0, b=1) * f.index.size)]
        tmp = pd.concat([tmp, f.loc[idx, :].to_frame().T])
        f.drop(idx, inplace=True)
      f = tmp

    if target_feature_distribution is None:
      target_feature_distribution = 'len'

    f['weights_cdf'] = f[target_feature_distribution].cumsum() / f[target_feature_distribution].sum()
    
    if optional_X:        
      f = f[optional_X <= f['weights_cdf']].iloc[[0], :]
    
    if f.shape[0] == 0:
        return None
      
    return [self.section[x["type"]][x["number"]](x["segment"]) for k, x in f.iterrows()]


if __name__ == '__main__':
  import numpy as np
  from numpy import linalg
  c = Cell('Test')
  c.make()
  c.product['MorphologyTable'].to_csv('../analysis/density/morphology_table.csv')

  import matplotlib.pyplot as plt
  import neurom
  from neurom import load_morphology, features
  from neurom import viewer
  _, ax = viewer.draw(neurom.load_morphology('test.swc'), mode='3d', color='black')
  ax.set_xlim([-350, 350])
  ax.set_ylim([-250, 450])
  ax.set_zlim([-275, 425])
  ax.set_xlabel('x ($\mu$m)')
  ax.set_ylabel('y ($\mu$m)')
  ax.set_zlabel('z ($\mu$m)')
  ax.set_axis_off()
  plt.show()

