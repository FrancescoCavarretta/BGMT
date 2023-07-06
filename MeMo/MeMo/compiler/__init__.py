
def _compile(models, links, base, simobj):
    """
    Compile a simulation object, and return a Marshall for the neuron simulator object

    Parameters
    ----------
    simobj : map
        precompiled object description

    Raises
    ------
    Warning
        if properties are ignored due to a mismatch

    Returns
    -------
    Marshall

    """
    
    # was it compiled?
    if "real_simobj" in simobj:
        return simobj["real_simobj"]
    
    # params
    init_params = []
    
    # if it is random, in our convention, seed is the 2nd arg
    if "seed" in simobj:
        init_params.append(simobj["seed"])
    
        
    def compile_model(models, links, simobj, init_params):    
        # retrieve the real representation of the class
        # and create an instance
        init_params += [simobj["object"].name, ]
        
        # real_class_name
        real_class_name = simobj["object"].__class__.__name__
        
        # create the class
        if not hasattr(base, real_class_name):
            real_class_name = "SimObject" if simobj["is_population"] else "Population"
                

        # create the class
        real_class = getattr(base, real_class_name)(*init_params)

        
        # copy all the attributes
        for attrname in simobj["object"]:
            # if there is a mismatch betcompilerween properties, print a warning
            #if not hasattr(real_class, attrname):
                 #raise Warning(f"Property {attrname} not found in class {simobj['object'].__class__.__name__}")
           #      continue
        
            if attrname in simobj["submodels"]:                
                # submodel ?
                attrval_tmp = simobj["submodels"][attrname]
                

                if type(attrval_tmp) == list:
                    # value is a list of attributes
                    attrval = [ _compile(models, links, base, _attrval_tmp) for _attrval_tmp in attrval_tmp ]
                else:
                    # value is a single attribute
                    attrval = _compile(models, links, base, attrval_tmp)
            else:
                # otherwise it is a numerical attribute
                attrval = getattr(simobj["object"], attrname)
                
            # # set the property
            setattr(real_class, attrname, attrval)
            
        return real_class



    def compile_link(models, links, simobj, init_params):
        # retrieve input and output records
        input = simobj["input"]
        output = simobj["output"]
        
        # real_class_name
        real_class_name = "%sTo%s" % (input["object"].__class__.__name__, output["object"].__class__.__name__)
        
        # create the class
        real_class = getattr(base, real_class_name)(*init_params)
        
        real_class.input = _compile(models, links, base, input)
        real_class.output = _compile(models, links, base, output)
        
        # set the filter attribute for the target on the output object
        if hasattr(simobj["object"], "target_feature"):
            for _attrname in [ "target_feature", "section_type", "min_value", "max_value", "target_feature_distribution" ]:                
                setattr(real_class, _attrname, getattr(simobj["object"], _attrname))

        # set distribution
        if "distribution" in simobj["submodels"]:
            attrval_tmp = simobj["submodels"]["distribution"]
            if type(attrval_tmp) == list:
                attrval = [ _compile(models, links, base, _attrval_tmp) for _attrval_tmp in  attrval_tmp ]
                
            else:
                attrval = _compile(models, links, base, attrval_tmp)

            setattr(real_class, "distribution", attrval)
            
        return real_class
    
    
    # add the compiled object
    simobj["real_simobj"] = (compile_link if simobj["is_link"] else compile_model)(models, links, simobj, init_params)
    
    return simobj["real_simobj"]


def compile(sim, base_mech=None):
    """
    Compile a simulation

    Parameters
    ----------
    sim : map
    {precompiled simulation, with seed assignment}
    """

    if base_mech is None:
        from .neuron import base
        base_mech = base
    
    for simobj in sim["models"].values():
        _compile(sim["models"], sim["links"], base_mech, simobj) 
    
    for simobj in sim["links"].values():
        _compile(sim["models"], sim["links"], base_mech, simobj)
        
    # let create the instance
    for simobj in sim["links"].values():
        simobj["real_simobj"].make()
    
    for simobj in sim["models"].values():
        simobj["real_simobj"].make()




def register_object(base, obj):
    setattr(base, obj.__name__, obj)



def clear(r):

    for so in r['links'].values():
        del so['real_simobj']
        
    for so in r['models'].values():
        del so['real_simobj']        
