import multiprocessing
import numpy as np
import os
import MeMo.nwbio as nwbio


#def save(filename_output, cfg_filename, file_max_size=10000):
#    cfg = np.load(cfg_filename, allow_pickle=True).tolist()
#    file_index = 0
#    fw = nwbio.FileWriter(filename_output  + ("_%d" % file_index) + ".nwb", str(cfg), "thalamic_data_id", max_size=None)    
#    for _cfg in cfg:
#        tmp_filename = _cfg['key'] + '.nwb'
#        if fw is None or len(fw.nwbfile.acquisition) >= file_max_size:
#            fw.close()
#            file_index += 1
#            fw = nwbio.FileWriter(filename_output  + ("_%d" % file_index) + ".nwb", str(cfg), "thalamic_data_id", max_size=None)
#        
#        try:
#            fr = nwbio.FileReader(tmp_filename)
#            for k in fr.nwbfile.acquisition.keys():
#               fw.add(k, *fr.read(k))
#            fr.close()
#        except: 
#            print('Warning', tmp_filename, 'was not read or does not exist')
#            
#    fw.close()
#
#    # remove files
#    for _cfg in cfg:
#        os.system('rm %s.nwb' % _cfg['key'])

        
#def main(cfg_filename, cmdline):
#    if MPI.COMM_WORLD.Get_rank() == 0:
#        return controller(cfg_filename, cmdline)
#    else:
#        return run()


#def controller(cfg_filename, cmdline):
    # open configurations
#    n_cfg = len(np.load(cfg_filename, allow_pickle=True).tolist())
 #   
  #  mpi_comm = MPI.COMM_WORLD
#
 #   # consumer available for running simulations
  #  free_ranks = list(range(1, mpi_comm.Get_size()))
#
 #   cfg_keys = sorted(list(range(n_cfg)))
  #  cfg_keys_to_use = cfg_keys + []
#
 #   print('Running')
#
 #   while len(cfg_keys_to_use):
  #      # occupy all the ranks
   #     while len(free_ranks) and len(cfg_keys_to_use):
    #        try:
     #           k = cfg_keys_to_use.pop()
   #
#

def main(cfg_filename, cmdline):
    n_cfg = len(np.load(cfg_filename, allow_pickle=True).tolist())
    args = [ ('./x86_64/special sim.py --config_file=%s --index=%d %s' % (cfg_filename, index, cmdline), ) for index in range(n_cfg) ]
    pool = multiprocessing.Pool()
    for r in pool.starmap(os.system, args, chunksize=int(n_cfg / multiprocessing.cpu_count())): pass
    pool.terminate()



if __name__ == '__main__':
    import sys

    file_max_size = 10000

    # read commandline arguments
    cmdline = ''
    for arg in sys.argv:
        if arg.startswith('--config_file'):
            # read configurations
            cfg_filename = arg.split('=')[1]
#        elif arg.startswith('--filename_output'):
#            # read filename but do not add
#            filename_output = arg.split('=')[1]
#            continue
        elif arg.startswith('--file_max_size'):
            # read filename but do not add
            file_max_size = int(arg.split('=')[1])
            continue
        cmdline += arg + ' '

    # run jobs
    main(cfg_filename, cmdline)

    # save data
    #save(filename_output, cfg_filename, file_max_size=file_max_size)
    
    sys.exit(0)


