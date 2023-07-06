class Population:
    def __init__(self, name):
        self.name = name
        self.product = None
    
    def __getattr__(self, name):
        if not self.__dict__:
            setattr(self, name, None)
        return super().__getattr__(self, name)
    
    def make(self):
        if self.product is None:
            self.product = []
            for x in self.__dict__.values():
                if type(x) == list:
                    for obj in x:
                        obj.make()
                        self.product.append(obj)
        return self.product    
    
    
    def __del__(self):
        for p in self.product:
          del p
            
        del self.product
        self.product = None
