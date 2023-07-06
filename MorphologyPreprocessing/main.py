


if __name__ == '__main__':
  import os
  import preprocessing
  import hoc2swc
  import sys
  import neuron

  neuron.h.load_file('MorphologyLoader.hoc')

  # print help screen 
  if '--help' in sys.argv:
    print ("To run type the following command\n\tpython main <input swc file> <output swc file>")
    quit()

  
  fin, fout = sys.argv[-2], sys.argv[-1]

  print ("preprocessing morphology", fin)
  cell = neuron.h.MorphologyLoader(fin) #  1. load morphology
  preprocessing.preprocess(cell)        #  2. preprocess
  print ("....done")


  # if the output file exists, we do not overwrite

  print ("Saving into", fout)
  if os.path.exists(fout):
    print ("\t", fout, "already exists and will be not overwritten")
    quit()

  hoc2swc._neuron2swc(cell.soma[0], fout) # save
  print ("....done")


