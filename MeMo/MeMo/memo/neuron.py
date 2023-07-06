#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 09:37:14 2022

@author: francesco
"""

from .model import Model, ModelPopulation


class Cell(Model):  
    def __init__(self, name, **kwargs):    
        """
            Representation of a cell
            name:identifier
            **kwargs : parameters of the cell
        """
        Model.__init__(self, name, **kwargs)
    
    
    
class Synapse(Model):
    def __init__(self, name, **kwargs):    
        """
            Representation of a synapse
            name:identifier
            **kwargs : parameters of the synapse
        """
        if name == "AmpaNmda":
            # add conductance
            if "gsyn_ampa" not in kwargs:
                kwargs["gsyn_ampa"] = 0.
                
            if "gsyn_nmda" not in kwargs:
                kwargs["gsyn_nmda"] = 0.
                
            if "erev" not in kwargs:
                kwargs["erev"] = 0.

            if "tau" not in kwargs:
                kwargs["tau"] = 3.        

        else:
            # add conductance
            if "gsyn" not in kwargs:
                kwargs["gsyn"] = 0.
                
            if "erev" not in kwargs:
                kwargs["erev"] = -75.

            if "tau" not in kwargs:
                kwargs["tau"] = 6.        
            
        Model.__init__(self, name, **kwargs)
        
        
    def __setattr__(self, attrname, value, *args):    
        """
            Perform a type checking before fixing the values
        """
        # two only exception, check it is a SpikeTrain
        if attrname != "name" and attrname != "__model_attrs__":  
            # contains Model only in other cases
            assert isinstance(value, Model) or type(value) == int or type(value) == float
        
        # set the attribute
        super().__setattr__(attrname, value, *args)
            
            
            
class SynapseGroup(ModelPopulation):
    def __init__(self, name, **kwargs):    
        """
            It contains a group of synapse.
            For each, we define the number of its instances.
            name: model group identifier
            **kwargs : parameters of the model.
            If the name begin with "n_[synapse]",
            it indicates a repetition of models [synapse]
        """
        ModelPopulation.__init__(self, name, **kwargs)  
            

    def __setattr__(self, attrname, value, *args):    
        """
            Perform a type checking before fixing the values
        """
        # two only exception, check it is a SpikeTrain
        if attrname != "name" and attrname != "__model_attrs__" and not attrname.startswith("n_"):  
            # contains Model only in other cases
            assert isinstance(value, Synapse)  
        
        # set the attribute
        super().__setattr__(attrname, value, *args)

            
