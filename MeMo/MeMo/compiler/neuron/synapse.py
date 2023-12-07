from .model_population import *

class Synapse:
    def __init__(self, name):
        self.name = name
        self.product = None
        self.make()
        
    @property
    def tau(self):
        if self.name == "AmpaNmda":
            return getattr(self, self.name).ampatau
        else:
            return getattr(self, self.name).tau
    
    @tau.setter
    def tau(self, value):
        if self.name == "AmpaNmda":
            getattr(self, self.name).ampatau = value
        else:
            getattr(self, self.name).tau = value

    @property
    def tau1(self):
        return getattr(self, self.name).tau1
    
    @tau1.setter
    def tau1(self, value):
        getattr(self, self.name).tau1 = value

    @property
    def tau2(self):
        return getattr(self, self.name).tau2
    
    @tau2.setter
    def tau2(self, value):
        getattr(self, self.name).tau2 = value
        
    @property
    def erev(self):
        return getattr(self, self.name).e
    
    @erev.setter
    def erev(self, value):
#        print(self.name, 'Erev', getattr(self, self.name).e, 'mV')
        getattr(self, self.name).e = value
#        print(self.name, 'Erev', getattr(self, self.name).e, 'mV')
#        print()
        
    @property
    def gsyn(self):
        return getattr(self, self.name).g_max
    
    @gsyn.setter
    def gsyn(self, value):
        getattr(self, self.name).g_max = value

    @property
    def gsyn_nmda(self):
        return getattr(self, self.name).gnmda_max
    
    @gsyn_nmda.setter
    def gsyn_nmda(self, value):
        getattr(self, self.name).gnmda_max = value

    @property
    def gsyn_ampa(self):
        return getattr(self, self.name).gampa_max
    
    @gsyn_ampa.setter
    def gsyn_ampa(self, value):
        getattr(self, self.name).gampa_max = value
    
    def make(self):
        if self.product is None:
            from neuron import h
            self.Section = h.Section()
            setattr(self, self.name, getattr(h, "MeMo_" + self.name)())

            getattr(self, self.name).loc(0.5, sec=self.Section)

            self.product = getattr(self, self.name) 
        return self.product    
    
    def __del__(self):
        del self.product
        self.product = None
                



    
    

class SynapseGroup(Population):
    def __init__(self, name):
        Population.__init__(self, name)
        
        
class SpikeTrainPopulation(Population):
    def __init__(self, name):
        Population.__init__(self, name)
        
        
class SpikeTrainToSynapse:
    def __init__(self):
        self.input = None
        self.output = None
        self.product = None
        
        
    def make(self):
        if self.product is None:
            from neuron import h
            
            self.input.make()
            self.output.make()
            
            self.Vector = h.Vector(self.input.product)
            self.VecStim = h.MeMo_VecStim()
            self.VecStim.play(self.Vector)
            self.NetCon = h.NetCon(self.VecStim, self.output.product)
            self.product = { "Vector":self.Vector, "VecStim":self.VecStim, "NetCon":self.NetCon }
        return self.product       
    
    
    def __del__(self):
        del self.input
        del self.output
        del self.product
        
        self.input = self.output = self.product = None  
    
    
        
class SpikeTrainPopulationToSynapseGroup:
    def __init__(self):
        self.input = None
        self.output = None
        self.product = None
        
    def make(self):
        if self.product is None:
            from neuron import h
            
            self.input.make()
            self.output.make()
            
            self.product = []
            n = min([len(self.input.product), len(self.output.product)])
            for i in range(n):
                st2syn = SpikeTrainToSynapse()
                st2syn.input = self.input.product[i]
                st2syn.output = self.output.product[i]
                st2syn.make()
                self.product.append(st2syn)
            
        return self.product 
    
    def __del__(self):
        
        del self.input
        del self.output
        
        for p in self.product:
            del p
            
        del self.product
        
        self.input = self.output = self.product = None        


class SynapseToCell:
    def __init__(self):
        self.input = None
        self.output = None
        self.product = None
        self.distribution = None
        self.target_feature, self.section_type, self.min_value, self.max_value, self.target_feature_distribution = None, None, None, None, None
        
        
    def make(self):
        if self.product is None:
            #print (self.target_feature, self.section_type, self.min_value, self.max_value, self.target_feature_distribution)
            from neuron import h
            
            self.input.make()
            self.output.make()
            
            if self.distribution:
                self.distribution.make()

            while True:            
                if self.distribution.name == "empirical":
                        try:
                            X = self.distribution(interval=True)
                            if X == "somatic":
                                targets = self.output.get(section_type="somatic", optional_X=self.distribution(name="uniform", a=0, b=1), target_feature_distribution=self.target_feature_distribution)
                            else:
                                targets = self.output.get(target_feature=self.target_feature, min_value=X[0], max_value=X[1], section_type=self.section_type, 
                                                          optional_X=self.distribution(name="uniform", a=0, b=1), target_feature_distribution=self.target_feature_distribution)
                        except IndexError:
                            targets = None
                else:
                    targets = self.output.get(target_feature=self.target_feature, min_value=self.min_value, max_value=self.max_value, section_type=self.section_type,
                                              optional_X=self.distribution(name="uniform", a=0, b=1), target_feature_distribution=self.target_feature_distribution)

                if targets:
                    break
            
            segment = targets[0]
      
            self.input.product.loc(segment.x, sec=segment.sec)
            self.product = { self.input.name:self.input.product,
                            "Segment":{"Arc":segment.x,
                                       "Section":segment.sec}}
        return self.product     
    
    def __del__(self):
        del self.input
        del self.output
        del self.product
        
        self.input = self.output = self.product = None   


class SynapseGroupToCell:
    def __init__(self):
        self.input = None
        self.output = None
        self.product = None
        self.distribution = None
        self.target_feature, self.section_type, self.min_value, self.max_value, self.target_feature_distribution = None, None, None, None, None

        
    def make(self):
        if self.product is None:
            from neuron import h
            
            self.input.make()
            self.output.make()
            
            self.product = []
            for i in range(len(self.input.product)):
                syn2cell = SynapseToCell()
                if self.distribution:
                    syn2cell.distribution = self.distribution[i]
                    syn2cell.target_feature, syn2cell.section_type, syn2cell.min_value, syn2cell.max_value, syn2cell.target_feature_distribution = self.target_feature, self.section_type, self.min_value, self.max_value, self.target_feature_distribution
                syn2cell.input = self.input.product[i]
                syn2cell.output = self.output
                syn2cell.make()
                self.product.append(syn2cell)
            
        return self.product     
      
    def __del__(self):
        del self.input
        del self.output
        
        for p in self.product:
            del p
            
        del self.product
        
        self.input = self.output = self.product = None    
