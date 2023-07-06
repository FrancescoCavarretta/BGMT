from os import listdir
from os.path import isfile, join

mypath = 'jaeger'


for filename in listdir(mypath):
  filename = join(mypath, filename)
  print ('filename=', filename, isfile(filename))
  if isfile(filename) and filename.endswith('.swc') and not filename.endswith('.my.swc') :
    
    print ('\tfilename=', filename, isfile(filename), '\n')
    filename_out = filename.replace('.swc', '.my.swc')

    fi = open(filename, 'r')
    fo = open(filename_out, 'w')

    l = fi.readline().strip()
    _pt_index_soma_last = -1
    while l:
      if l.startswith('#'):
        fo.write(l+'\n')
      else:
        tk = l.split()
        args = [ float(tk[i]) for i in range(len(tk)) ]
        _pt_index = int(tk[0])
        _pt_type = int(tk[1])
        _pt_parent = int(tk[-1])
        
        if _pt_type == 16:
          _pt_type = 1
        elif _pt_parent == -1:
          _pt_parent = _pt_index_soma_last
          

        if _pt_type == 1: 
          _pt_index_soma_last = _pt_index
          
        args[1] = _pt_type
        args[-1] = _pt_parent

        fo.write((('%g '*(len(tk)-1))+'%g\n')%tuple(args))
        
          
      l = fi.readline().strip()

    fi.close()
    fo.close()
