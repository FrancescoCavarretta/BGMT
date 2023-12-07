from mpi4py import MPI
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

        
def main(cfg_filename, cmdline, init_index=None, end_index=None):
    if MPI.COMM_WORLD.Get_rank() == 0:
        return controller(cfg_filename, cmdline, init_index=init_index, end_index=end_index)
    else:
        return run()


def controller(cfg_filename, cmdline, init_index=None, end_index=None):
    # open configurations
    n_cfg = len(np.load(cfg_filename, allow_pickle=True).tolist())
    
    mpi_comm = MPI.COMM_WORLD

    # consumer available for running simulations
    free_ranks = list(range(1, mpi_comm.Get_size()))

    cfg_keys = sorted(list(range(n_cfg)))
    cfg_keys_to_use = cfg_keys + []

    if init_index and end_index:
      cfg_keys_to_use = cfg_keys_to_use[init_index:end_index+1]
    elif init_index:
      cfg_keys_to_use = cfg_keys_to_use[init_index:]
    elif end_index:
      cfg_keys_to_use = cfg_keys_to_use[:end_index+1]


    print('Running')

    while len(cfg_keys_to_use):
        # occupy all the ranks
        while len(free_ranks) and len(cfg_keys_to_use):
            try:
                k = cfg_keys_to_use.pop()
            except IndexError:
                break

            # assemble message
            message = {'cfg_filename':cfg_filename, 'cmdline':cmdline, 'index':cfg_keys.index(k)}
            rank = free_ranks.pop()

            # submit
            mpi_comm.send(obj=message, dest=rank, tag=0)
            
        # receive the message
        message = mpi_comm.recv()

        #print('file saved')
        free_ranks.append(message['rank'])

    # processes left
    while len(free_ranks) < mpi_comm.Get_size() - 1:
        # receive the message
        message = mpi_comm.recv()

        #print('file saved')
        free_ranks.append(message['rank'])

    # send termination signal to all
    for rank in range(1, mpi_comm.Get_size()):
        mpi_comm.send(obj=None, dest=rank, tag=0)

    print('finished')


def run():
    mpi_comm = MPI.COMM_WORLD

    rank = mpi_comm.Get_rank()

    # receive a message
    message = mpi_comm.recv(source=0, tag=0)

    while message:
        # pack output
        index = message['index']
        cfg_filename = message['cfg_filename']
        cmdline = message['cmdline']
        os.system('./x86_64/special sim.py --config_file=%s --index=%d %s' % (cfg_filename, index, cmdline))
        dict_message = dict(output=None, rank=rank, key=None)

        # send out
        mpi_comm.send(obj=dict_message, dest=0, tag=0)
        
        # receive a message
        message = mpi_comm.recv(source=0, tag=0)
    




if __name__ == '__main__':
    import sys

    file_max_size = 10000
    init_index = end_index = None
    # read commandline arguments
    cmdline = ''
    for arg in sys.argv:
        if arg.startswith('--config_file'):
            # read configurations
            cfg_filename = arg.split('=')[1]
        elif arg.startswith('--init_index'):
            init_index=int(arg.split('=')[1])
        elif arg.startswith('--end_index'):
            end_index=int(arg.split('=')[1])
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
    main(cfg_filename, cmdline, init_index=init_index, end_index=end_index)

    # save data
    #save(filename_output, cfg_filename, file_max_size=file_max_size)
    
    sys.exit(0)


