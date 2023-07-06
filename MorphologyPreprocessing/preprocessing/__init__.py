
def preprocess(cell):
  import preprocessing.checking as checking
  import preprocessing.soma as soma
  import preprocessing.axon as axon
  import preprocessing.dendrites as dendrites
  
  checking.check(cell) # check the morphological representation
  
  # preprocess each section
  dendrites.preprocess(cell.soma[0])
  axon.preprocess(cell.axon[0])
  soma.preprocess(cell.soma[0])
  
