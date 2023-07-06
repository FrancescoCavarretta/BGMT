class Cell:
    def __init__(self, name):
        self.name = name
        self.product = None
        
    def make(self):
        if self.product is None:
            raise Warning("Cell model not translated")
        return self.product    
    
    def __del__(self):
        del self.input
        del self.output
        del self.product
        
        self.input = self.output = self.product = None  

