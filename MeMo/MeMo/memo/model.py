#!/usr/bin/env python3
# -*- coding: utf-8 -*-



class Model:
    class ParamIterator:
        def __init__(self, model, params, models_only=False, filter_out=["name"]):
            self.__model = model
            self.__index = -1
            self.__params = sorted( params ) # sort the parameters so the visit will be always replicable
            self.__models_only = models_only
            self.__filter_out = filter_out
            
        def __next__(self):
            from .link import Link
            
            while self.__index < len(self.__params)-1:
                self.__index += 1
                
                pname = self.__params[self.__index]
                pval = getattr(self.__model, pname)
                if pname not in self.__filter_out and \
                    (not self.__models_only or self.__models_only and isinstance(pval, (Model, Link))):
                    return pname 
                
            raise StopIteration
            
    """
    Created on Wed Mar  2 20:14:03 2022
    @author: Francesco Cavarretta
       
    Abstract class representing a model archetype
    """
    
    def __init__(self, name, **kwargs):
        """
        Initialize a model

        Parameters
        ----------
        name: model identifier
        **kwargs : parameters of the model
        """
        
        # store the parameter names
        self.__model_attrs__ = {}
        
        # each model should have a name
        self.name = name
        
        # create parameters
        for varname, varvalue in kwargs.items():
            # check the parameters does not exist to not overwrite any
            # class attribute
            if varname not in self.__dict__:
                setattr(self, varname, varvalue)
                self.__model_attrs__[varname] = {}
                
                
    def itersubmodels(self):
        """
            Iterator for models
        """
        pi = Model.ParamIterator(self, list(self.__model_attrs__.keys()), models_only=True)
        while True:
            try:
                yield pi.__next__()
            except StopIteration:
                break
    
    
    def __iter__(self):
        """
            Iterator
        """
        return Model.ParamIterator(self, list(self.__model_attrs__.keys()), models_only=False)
    
    
    def __str__(self):
        '''
        Returns
        -------
        Model name
        '''
        return self.name


            
    def __setattr__(self, name, value):
        """
        Change the value of an attribute.
        If it is linked to lower level models,
        it updates their parameters alongside.

        Parameters
        ----------
        name : Str
            Attribute name
        value : Str
            Value of the attribute
        """
        # check whether the attribute is new
        new_attribute_flag = not hasattr(self, name)
        
        # set the value
        super().__setattr__(name, value) 
        
        if name == "name" or name == "__model_attrs__":
            # if it is "__model_attrs__ or name, just set and return
            return 
        
        if new_attribute_flag and name not in self.__model_attrs__: 
            # check whether is new
            self.__model_attrs__[name] = {}
            return
             

        # check for linked attributes
        # if the attribute is an attribute of the model
        for attrdest_ref, function in self.__model_attrs__[name].items(): 
            if type(attrdest_ref) == tuple:
                # then it is an attribute of the submodel
                output_model, attrdest = attrdest_ref  
            else:
                output_model, attrdest = super(), attrdest_ref
                
               
            # calculate the new value
            if function:
                # if there is a map function
                if isinstance(function, str):
                    # interpret the string, 
                    # which is a chunk of python code
                    
                    # run the code
                    _locals = locals()
                    
                    # compy the local variable
                    for varname in self.__model_attrs__:
                        _locals[varname] = getattr(self, varname)
                        
                    # run python script
                    exec(function, globals(), _locals)
                    
                    # read the value
                    value = _locals[attrdest]
                    
                elif callable(function):
                    # it is a function
                    # read the parameters of the function
                    value = function(*([self]+[
                        getattr(self, varname) for varname in function.__code__.co_varnames[1:function.__code__.co_argcount]
                        ]))

                    # nothing to change
                    if value is None:
                        continue 
                    
                else:
                    raise ValueError(f"The link for variable {name} was not properly defined (2)")

            # set the value
            output_model.__setattr__(attrdest, value) 
            
            

        update_function = {}


        def add_attrs_to_update(update_function, model_attrs):      
            to_scan = []
            for attrdest, value in model_attrs.items():
                if type(attrdest) == str and attrdest not in update_function and attrdest != name:
                    update_function[attrdest] = value
                    to_scan.append(attrdest)
            return to_scan
    
    
        to_scan = add_attrs_to_update(update_function, self.__model_attrs__[name])

        while len(to_scan):
            _to_scan = []
            for _name in to_scan:
                try:
                    _to_scan += add_attrs_to_update(update_function, self.__model_attrs__[_name])
                except KeyError:
                    pass
            to_scan = _to_scan
#        

        # check for linked attributes
        # if the attribute is an attribute of the model
        for attrdest, function in update_function.items(): 
                
               
            # calculate the new value
            if function:
                # if there is a map function
                if isinstance(function, str):
                    # interpret the string, 
                    # which is a chunk of python code
                    
                    # run the code
                    _locals = locals()
                    
                    # compy the local variable
                    for varname in self.__model_attrs__:
                        _locals[varname] = getattr(self, varname)
                        
                    # run python script
                    exec(function, globals(), _locals)
                    
                    # read the value
                    value = _locals[attrdest]
                    
                elif callable(function):
                    # it is a function
                    # read the parameters of the function
                    value = function(*([self]+[
                        getattr(self, varname) for varname in function.__code__.co_varnames[1:function.__code__.co_argcount]
                        ]))

                    # nothing to change
                    if value is None:
                        continue 
                    
                else:
                    raise ValueError(f"The link for variable {name} was not properly defined (2)")

            # set the value
            super().__setattr__(attrdest, value)             

             
            
                             
        

            
                
    def __linkattr__(self, attrsrc, attrdest, **kwargs):
        
        """
            Link attributes between two models 
            from the parent model to the child model
            
            Parameters
            attrsrc: attribute(s) name(s) of the parentmodel
            attrdest: name of the attribute in the destination model
            
            kwargs: it can contain two only parameters for now
            modelname: name of the destination model
            func: function of mapping
        """
        # standardize to something iterable
        if type(attrsrc) == str:
            attrsrc = (attrsrc, )
            
        # it can be either a link between variables of between models
        if len(kwargs) > 0:
            # there are not others parameters than "submodel" or "function"
            assert len(set(kwargs.keys()).difference(["submodel", "function"])) == 0
            
        # perform two checks
        if "submodel" in kwargs:       
            # retrieve the model
            submodel = kwargs["submodel"]
            
            # if it is a string, we need to retrieve it
            if type(submodel) == str:
                submodel = getattr(self, submodel)

            # which should have also that attribute
            assert isinstance(submodel, Model) and \
                hasattr(submodel, attrdest)
        else:
            submodel = None
            

        if "function" in kwargs:     
            function = kwargs["function"]
            
            # which should have also that attribute
            assert callable(function) or isinstance(function, str)
        else:
            function = None
            
            
        # reformat attrdest if needed
        if submodel:
            attrdest = (submodel, attrdest)
            
            
        # create the link(s)
        for _attrsrc in attrsrc:
            # source attribute existing
            if _attrsrc not in self.__model_attrs__:
                # add the link
                self.__model_attrs__[_attrsrc] = {}
                
            # update/create entry                
            self.__model_attrs__[_attrsrc][attrdest] = function        
            
            if hasattr(self, _attrsrc):
                # update the attribute in the model
                self.__setattr__(_attrsrc, getattr(self, _attrsrc))
            else:
                if type(attrdest) == tuple:
                    # update the attribute in the model
                    self.__setattr__(_attrsrc, getattr(*attrdest))
                else:
                    # update the attribute in the model
                    self.__setattr__(_attrsrc, getattr(self, attrdest))
                
                

    def copy(self, deep=True):
        """
            Create a soft copy of the object
            deep: If true, it returns a deep copy (default True),
            creating also new instances of the children models,
            otherwise a soft copy, 
            which continue to reference the same children models

        Returns
        -------
        Copy of the Model Object
        """        
        import copy
        return (copy.deepcopy if deep else copy.copy)(self)
    
    def __call__(self, deep=True):
        """
            Create a copy of the Model
            deep: If true, it returns a deep copy (default True)

        Returns
        -------
        Copy of the Model Object

        """
        return self.copy(deep=deep)
    

    def __len__(self):
        return 1

class ModelPopulation(Model):    
    
    def __iter__(self):
        """
            Iterator
        """
        params = list(self.__model_attrs__.keys())
        i = 0
        while i < len(params):
            if params[i].startswith("n_"):
                del params[i]
                continue
            i += 1
        return Model.ParamIterator(self, params)

    
    """
        It contains a population of different models.
        For each, we define the number of its instances.
        name: model group identifier
        **kwargs : parameters of the model.
        If the name begin with "n_[modelname]",
        it indicates a repetition of models [modelname]
    """
    def __init__(self, name, **kwargs):        
        # check whether the number of instance were fixed
        # otherwise create the variable n_[modelname]
        # and n_[modelname] needs to be create after the model vars
        from collections import OrderedDict 
        
        kwargs = OrderedDict(kwargs)
        for k in kwargs.keys():
            if k.startswith("n_"):
                kwargs.move_to_end(k)
                
        Model.__init__(self, name, **kwargs) 
        

                

    def __setattr__(self, attrname, value, *args):
        """
            Perform a type checking before fixing the values
        """        

        # set the attributes
        super().__setattr__(attrname, value, *args)
        
        # two only exception
        if attrname != "name" and attrname != "__model_attrs__":
            # type checking
            if attrname.startswith("n_"):     
                # we can fix numbers only for n_[modelname] or Models describing the number
                assert attrname[2:] in self.__model_attrs__ and (type(value) == int or isinstance(value, Model))
            else:
                # contains Model only in other cases
                assert isinstance(value, Model)        
                
            # set n instances
            nattrname = "n_" + attrname
            if not hasattr(self, nattrname):
                super().__setattr__(nattrname, 1, *args)
            
        

    def __len__(self):
        """
        Return the number of elements
        """
        n = 0
        for x in self.__model_attrs__.keys():
            if x.startswith("n_"):
                n += getattr(self, x)
        return n        
            
            
            

if __name__ == "__main__":
    m1 = Model("test1")
    m2 = Model("test2")
    m2.test2 = 2
    m1.test1 = 5
    
    m1.model2 = m2
    
    print (m1.test1, m2.test2)
        
    def myfunc(test1):
        return test1/2
        
    m1.__linkattr__("test1", "test2", submodel="model2", function=myfunc)
    #m1.__linkattr__("test1", "test2", submodel="model2", function="test2=test1*5")

    print (m1.test1, m2.test2)
    
    m1.test1 = 77
    
    print (m1.test1, m2.test2)


    m1_copy = m1.copy()
    
    m1_deep_copy = m1.copy(deep=True)
    
    m1_copy.test1 = 44.0
    m1_deep_copy.test1 = 96.0
    
    print (m1.test1, m2.test2)
    print (m1_copy.test1, m2.test2)
    print (m1_deep_copy.test1, m2.test2, m1_deep_copy.model2.test2)
    
    m3 = Model("test3")
    m3.test1 = 9
    m3.test2 = 10
    m3.__linkattr__("test1", "test2", function="test2=test1*2")
    print (m3.test1, m3.test2)
    
    mp = ModelPopulation('testpop', n_m1=5, m1=m1, m2=m2, m3=m3)
