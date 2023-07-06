#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 09:37:14 2022

@author: francesco
"""

from .model import Model, ModelPopulation
from .distribution import Distribution


    
class SpikeTrain(Model):
    time_conversion = {
        "tenth_ms":1e-4,
        "ms":1e-3,
        "s":1.0,
        "m":60,
        "h":3600.0
        }

    
    def __init__(self, name, **kwargs):    
        """
            It contains a model of spike trains.
            name: spike train identifier
            **kwargs : parameters of the spike train model.
        """
        from collections import OrderedDict
        
        kwargs = OrderedDict(kwargs)

        if "time_unit" not in kwargs:
            kwargs["time_unit"] = "s"
            
        if name == "abbasi":
            if "time" not in kwargs and "rate" not in kwargs:
                import numpy
                
                kwargs["time"] = numpy.linspace(0.0, kwargs["tstop"], num=int(round(kwargs["tstop"] / (kwargs["refractory_period"] * 0.5))) )
                kwargs["rate"] = numpy.full(kwargs["time"].shape[0], kwargs["mean_rate"], dtype=float)
                
            if "tstop" not in kwargs:
                kwargs["tstop"] = kwargs["time"][-1]
                
        elif name == "modulation":
            pass

        elif name == "burst":
            if "time" not in kwargs and "rate" not in kwargs:
                import numpy
                from . import burst
                
                if 'min_rate' not in kwargs:
                    kwargs['min_rate'] = 0.
                    
                if 'dt' not in kwargs:
                    kwargs['dt'] = 0.01
                #kwargs["time"] = numpy.linspace(0.0, kwargs["Tdur"], num=200)
                #kwargs["rate"] = numpy.full(kwargs["time"].shape[0], kwargs["max_rate"], dtype=float)   
                if kwargs['Tdur'] > 0:
                    kwargs["time"], kwargs["rate"] = burst.mk_burst_template(kwargs["Tpeak"], 
                                                             kwargs["Tdur"], 
                                                             kwargs["max_rate"], 
                                                             kwargs["fast_rise"], 
                                                             kwargs["fast_decay"],
                                                             min_rate=kwargs["min_rate"],
                                                             dt=(kwargs['refractory_period'] / 2.0))
                
            if "inter_time" not in kwargs and "inter_rate" not in kwargs:
                import numpy
                
                kwargs["inter_time"] = numpy.linspace(0.0, kwargs["tstop"], num=int(round(kwargs["tstop"] / (kwargs["refractory_period"] * 0.5))) )
                kwargs["inter_rate"] = numpy.full(kwargs["inter_time"].shape[0], kwargs["burst_mean_rate"], dtype=float)
            
        
        
        kwargs.move_to_end("time_unit")
        
        Model.__init__(self, name, **kwargs)
        

        if self.name == "abbasi":
            self.distribution = Distribution("gamma")
            self.__linkattr__("regularity", "k", submodel="distribution")
            self.__linkattr__("regularity", "theta", submodel="distribution", function="theta=1.0/regularity")
            
            self.__linkattr__("mean_rate", "rate", function="rate=rate/rate.mean()*mean_rate")
            
        elif self.name == "poissonian":
            self.distribution = Distribution("poisson")
            
            self.__linkattr__("mean_rate", "mean", submodel="distribution")
        elif self.name == "regular":
            self.distribution = Distribution("gamma")
        elif self.name == "burst":
            # if we generate a burst,
            # one distribution models the first-spike time of each burst
            # the second distribution the intra-burst isi
            self.inter_distribution = Distribution("gamma")
            
            self.__linkattr__("regularity", "k", submodel="inter_distribution")
            self.__linkattr__("regularity", "theta", submodel="inter_distribution", function="theta=1.0/regularity")
            
            self.intra_distribution = Distribution("gamma")
            self.__linkattr__("intra_burst_k", "k", submodel="intra_distribution")
            self.__linkattr__("intra_burst_theta", "theta", submodel="intra_distribution")
        elif self.name == "modulation":
            self.phase_distribution = Distribution("uniform", a=-0.5 / (1 + self.regularity), b=0.5 / (1 + self.regularity))
        else:
            raise NameError(f"Unknown type of Spike Train {self.name}")        
        
        
        
    def __setattr__(self, name, value, *args):
        """
        Conversion of time units
        """
        
        if name == "time_unit" and hasattr(self, "time_unit"):
            conversion_factor = SpikeTrain.time_conversion[self.time_unit]/SpikeTrain.time_conversion[value]
            
            if hasattr(self, "tstop"):
                super().__setattr__("tstop", getattr(self, "tstop") * conversion_factor, *args)
            
            super().__setattr__("refractory_period", getattr(self, "refractory_period") * conversion_factor, *args)
                
            if self.name == "abbasi":
                super().__setattr__("time", getattr(self, "time") * conversion_factor, *args)
        
        super().__setattr__(name, value, *args)
            
            
            
class SpikeTrainPopulation(ModelPopulation):
    def __init__(self, name, **kwargs):    
        """
            It contains a population of different spike train models.
            For each, we define the number of its instances.
            name: model group identifier
            **kwargs : parameters of the model.
            If the name begin with "n_[spiketrain]",
            it indicates a repetition of models [spiketrain]
        """
        ModelPopulation.__init__(self, name, **kwargs)  
            

    def __setattr__(self, attrname, value, *args):    
        """
            Perform a type checking before fixing the values
        """
        # two only exception, check it is a SpikeTrain
        if attrname != "name" and attrname != "__model_attrs__" and not attrname.startswith("n_"):  
            # contains Model only in other cases
            assert isinstance(value, SpikeTrain)  
        
        # set the attribute
        super().__setattr__(attrname, value, *args)

            
if __name__ == "__main__":
    import numpy as np
    st = SpikeTrain("abbasi", regularity=2.0, time=np.array([1,2,3,5,6]), rate=np.array([4,5,6,7,7]), mean_rate=3)
