_mod_file_list = []
_mod_dest_dir = "./modfiles"


def register_modules(dirname):
  '''
  Add a directory containing mod files which should be compiled
  dirname: directory name
  '''
  
  import os
  import queue
  global _mod_file_list
  global _mod_dest_dir
  
  if not os.path.exists(dirname):
    # if the directory do not even exist, do not add it, just shot a warning
    raise Warning(f"Directory {dirname} does not exist")
  else:
    qdir = queue.Queue()
    qdir.put(dirname)
    # check the subdirectories, if required
    while not qdir.empty():
      cur_dirname = qdir.get()
      if os.path.isdir(cur_dirname):
        # if it is a directory, add the subdirectories, including files
        for x in os.listdir(cur_dirname):
          qdir.put(os.path.join(cur_dirname, x))
          
      elif os.path.splitext(cur_dirname)[1].lower() == ".mod":
          # check the ext. and add if it is a mod
          _mod_file_list.append(cur_dirname)


def compile():
  import os
  global _mod_dest_dir
  os.system(f"rm -rf {_mod_dest_dir} && mkdir {_mod_dest_dir}")
  for cur_dirname in _mod_file_list:
    os.system(f"cp {cur_dirname} {_mod_dest_dir}")
  os.system(f"nrnivmodl {_mod_dest_dir}")
  
