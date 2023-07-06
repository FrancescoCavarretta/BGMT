#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .model import Model
from .link import Link
        
class MicroCircuit:
    def __init__(self, name):
        self.name = name
        self.models = []
        self.links = []
        self.properties = dict()
        
    def add(self, x):
        if isinstance(x, Link):
            self.links.append(x)
            self.models.append(x.input)
            self.models.append(x.output)
            
        elif isinstance(x, Model):
            self.models.append(x)
        else:
            raise Exception(f"The object {x} cannot be part of the Model")
            
    def set(**kwargs):
        self.properties.update(kwargs)

