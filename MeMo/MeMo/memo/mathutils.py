import model

class MathFunction(model.Model):
    def __init__(self, name, **kwargs):
        import numpy as np
        for p in kwargs.keys():
            if not isinstance(kwargs[p], np.ndarray):
                kwargs[p] = np.array(kwargs[p])
                
        model.Model.__init__(self, name, **kwargs)
        

        
