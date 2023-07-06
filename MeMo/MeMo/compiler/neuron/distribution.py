class RNG:
    __distribution__ = {
        "uniform":("neuron", "uniform","a", "b"),
        "discunif":("neuron", "discunif","a", "b"),
        "normal":("neuron", "normal","mean", "var"),
        "poisson":("neuron", "poisson","mean"),
        "gamma":("numpy", "gamma", "k", "theta"),
        "empirical":("neuron","uniform","a","b")
        }
    
    
    def neuron(self):
        import neuron as nrn    
        rng = nrn.h.Random()
        rng.Random123(*self.seed)
        return rng
    
    def numpy(self):
        import numpy as np
        return np.random.Generator(np.random.Philox(*self.seed))
        
    
    def __init__(self, seed, name, **kwargs):
        self.seed = seed
        self.name = name
        self.params = kwargs
        self._params = RNG.__distribution__[name]
        self._rng = {
            "numpy":getattr(self, "numpy")(),
            "neuron":getattr(self, "neuron")()
            }
        
    
    def __call__(self, interval=False, **kwargs):
        
        # if some parameter differs from the default, it is passed as an optional argument
        param_src = self.params
        param_src["name"] = self.name
        param_src.update(kwargs)
        #print (param_src)
        
        rng_name = RNG.__distribution__[param_src["name"]][0]
        distr_name = RNG.__distribution__[param_src["name"]][1]
        param_names = RNG.__distribution__[param_src["name"]][2:]
        
        _rng = self._rng[rng_name]
        
        if param_src["name"] == "empirical":
            import numpy as np
            
            i = np.where(_rng.uniform(0, 1) <= param_src["cdf"])[0][0] # bin index

            if param_src["x"][i] == "somatic":
                return param_src["x"][i]
            else:
                if interval:
#                    try:
#                    dx = (param_src["x"][i+1] - param_src["x"][i]) / 2
#                    except TypeError:
#                        dx = (param_src["x"][i] - param_src["x"][i-1]) / 2
#                    return param_src["x"][i] - dx, param_src["x"][i] + dx # return an interval corresponding to the bin
                     if i > 0:
                       return param_src["x"][i-1], param_src["x"][i]
                     else:
                       return 0.0, param_src["x"][i]
                     
                else:
                    return param_src["x"][i] # single value
        X = getattr(_rng, distr_name)(*[ param_src[pname] for pname in param_names ])
        #print ("X:", X, distr_name, [ param_src[pname] for pname in param_names ])
        return X
    
    
    def __del__(self):
        del self._rng
        self._rng = None


class Distribution:
    __distribution__ = {
        "uniform":("a", "b"),
        "discunif":("a", "b"),
        "normal":("mean", "var"),
        "poisson":("mean"),
        "gamma":("k", "theta"),
        "empirical":("x", "cdf")
        }
    
           
    
    def __init__(self, seed, name):
        self.name = name
        self.product = None
        self.seed = seed
        self.params = Distribution.__distribution__[name]
        
        
    def make(self):
        if self.product is None:
            self.product = RNG(self.seed, self.name, **{ pname:getattr(self, pname)  for pname in self.params }) 
        return self.product
        
    
    def __call__(self, interval=False, **kwargs):
        return self.product(interval=interval, **kwargs)
    
    def __del__(self):
        del self.product
        self.product = None
