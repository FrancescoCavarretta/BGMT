from bluepyopt.ephys.parameterscalers import ParameterScaler
from bluepyopt.ephys.parameterscalers import DictMixin
from math import exp, log


class NrnSegmentAxonDistanceScaler(ParameterScaler, DictMixin):

    def __init__(self,
                 axon_prox_multiplier,
                 axon_dist_multiplier,
                 somatic_multiplier,
                 dend_1st_order_multiplier,
                 dend_deep_multiplier,
                 name=None, comment=''):
      super(NrnSegmentAxonDistanceScaler, self).__init__(name, comment)

      self.axon_prox_multiplier=axon_prox_multiplier
      self.axon_dist_multiplier=axon_dist_multiplier
      self.somatic_multiplier=somatic_multiplier
      self.dend_1st_order_multiplier=dend_1st_order_multiplier
      self.dend_deep_multiplier=dend_deep_multiplier



    def get_depth(self, sec, sim):
        depth = 1
        sref = sim.neuron.h.SectionRef(sec=sec)
        while sref.has_parent() and \
              ("soma" not in sim.neuron.h.secname(sec=sref.parent)):
            sref = sim.neuron.h.SectionRef(sec=sref.parent)
            depth += 1
        return depth
    
                

    def scale(self, value, segment, sim=None):
        """Scale a value based on a segment"""
        if isinstance(value, dict):
            value = value["value"]
        else:
            value = value

        """Scale a value based on a segment"""
        ## if it is not an axon, then it is the same coefficient as proximal
        secname = sim.neuron.h.secname(sec=segment.sec)
        if "axon" in secname:
            ## for dendrite we distinguish by order
            sref = sim.neuron.h.SectionRef(sec=segment.sec)

            # if the parent is soma than it is a first order
            if "soma" in sim.neuron.h.secname(sec=sref.parent):
                multiplier = self.axon_prox_multiplier
            else:
                multiplier = self.axon_dist_multiplier
                
        elif "soma" in secname:
            multiplier = self.somatic_multiplier
        else:
            ## for dendrite we distinguish by order
            sref = sim.neuron.h.SectionRef(sec=segment.sec)
            
            # we assume that no parent is equivalent to soma
            if not sref.has_parent():
                multiplier = self.somatic_multiplier

            # if the parent is soma than it is a first order
            elif "soma" in sim.neuron.h.secname(sec=sref.parent):
                multiplier = self.dend_1st_order_multiplier
            else:
                multiplier = self.dend_deep_multiplier
        
        return multiplier*value


    def __str__(self):
        """String representation"""
        return ""










class NrnSegmentNaDistanceScaler(ParameterScaler, DictMixin):

    def __init__(self,
                 axon_prox_multiplier,
                 axon_dist_multiplier,
                 name=None,
                 comment=''):
      super(NrnSegmentNaDistanceScaler, self).__init__(name, comment)

      self.axon_prox_multiplier=axon_prox_multiplier
      self.axon_dist_multiplier=axon_dist_multiplier


    def get_depth(self, sec, sim):
        depth = 1
        sref = sim.neuron.h.SectionRef(sec=sec)
        while sref.has_parent() and \
              ("soma" not in sim.neuron.h.secname(sec=sref.parent)):
            sref = sim.neuron.h.SectionRef(sec=sref.parent)
            depth += 1
        return depth
    
                

    def scale(self, value, segment, sim=None):
        """Scale a value based on a segment"""
        if isinstance(value, dict):
            value = value["value"]
        else:
            value = value


        """Scale a value based on a segment"""
        ## if it is not an axon, then it is the same coefficient as proximal
        secname = sim.neuron.h.secname(sec=segment.sec)
        if "axon" in secname:
            ## for dendrite we distinguish by order
            sref = sim.neuron.h.SectionRef(sec=segment.sec)

            # if the parent is soma than it is a first order
            if "soma" in sim.neuron.h.secname(sec=sref.parent):
                multiplier = self.axon_prox_multiplier
            else:
                multiplier = self.axon_dist_multiplier
        elif "soma" in secname:
            multiplier = 1.0
        else:
            order = self.get_depth(segment.sec, sim)
            multiplier = 1.0 / (2**(order-1))

        return multiplier*value


    def __str__(self):
        """String representation"""
        return ""

    


class NrnSegmentCaTDistanceScaler(ParameterScaler, DictMixin):
    def __init__(self,
                 name=None,
                 comment=''):
      super(NrnSegmentCaTDistanceScaler, self).__init__(name, comment)





    def get_depth(self, sec, sim):
        depth = 1
        sref = sim.neuron.h.SectionRef(sec=sec)
        while sref.has_parent() and \
              ("soma" not in sim.neuron.h.secname(sec=sref.parent)):
            sref = sim.neuron.h.SectionRef(sec=sref.parent)
            depth += 1
        return depth


    
                

    def scale(self, value, segment, sim=None):
        """Scale a value based on a segment"""
        if isinstance(value, dict):
            value = value["value"]
        else:
            value = value

        """Scale a value based on a segment"""
        ## if it is not an axon, then it is the same coefficient as proximal
        secname = sim.neuron.h.secname(sec=segment.sec)
        if "axon" in secname:
            multiplier = 0
        elif "soma" in secname:
            multiplier = 1.
        else:
            order = self.get_depth(segment.sec, sim)
            if order == 1:
                multiplier = 2.
            else:
                multiplier = 0.5
        
        return multiplier*value


    def __str__(self):
        """String representation"""
        return ""









class NrnSegmentCaLDistanceScaler(ParameterScaler, DictMixin):
    def __init__(self,
                 name=None,
                 comment=''):
      super(NrnSegmentCaLDistanceScaler, self).__init__(name, comment)





    def get_depth(self, sec, sim):
        depth = 1
        sref = sim.neuron.h.SectionRef(sec=sec)
        while sref.has_parent() and \
              ("soma" not in sim.neuron.h.secname(sec=sref.parent)):
            sref = sim.neuron.h.SectionRef(sec=sref.parent)
            depth += 1
        return depth


    
                

    def scale(self, value, segment, sim=None):
        """Scale a value based on a segment"""
        if isinstance(value, dict):
            value = value["value"]
        else:
            value = value


        """Scale a value based on a segment"""
        ## if it is not an axon, then it is the same coefficient as proximal
        secname = sim.neuron.h.secname(sec=segment.sec)
        if "axon" in secname:
            multiplier = 0.0
        elif "soma" in secname:
            multiplier = 1.0
        else:
            if self.get_depth(segment.sec, sim) == 1 and \
               (segment.sec.L*segment.x) < 10.0:
                multiplier = (1.25/2.5)
            else:
                multiplier = (0.75/2.5)
        return multiplier*value


    def __str__(self):
        """String representation"""
        return ""
