import numpy as np
import os
import MeMo.nwbio as nwbio

def save(filename_output, cfg_filename, file_max_size=1000):
    cfg = np.load(cfg_filename, allow_pickle=True).tolist()
    file_index = 0
    fw = nwbio.FileWriter(filename_output  + ("_%d" % file_index) + ".nwb", str(cfg), "thalamic_data_id", max_size=None)    
    for _cfg in cfg:
        tmp_filename = _cfg['key'] + '.nwb'
        if fw is None or len(fw.nwbfile.acquisition) >= file_max_size:
            fw.close()
            file_index += 1
            fw = nwbio.FileWriter(filename_output  + ("_%d" % file_index) + ".nwb", str(cfg), "thalamic_data_id", max_size=None)

        try:
                fr = nwbio.FileReader(tmp_filename)
                for k in fr.nwbfile.acquisition.keys():
                        fw.add(k, *fr.read(k))
                fr.close()
        except: 
                print('Warning', tmp_filename, 'was not read or does not exist')


    fw.close()

    # remove files
    for _cfg in cfg:
        os.system('rm %s.nwb' % _cfg['key'])



if __name__ == '__main__':
    import sys

    file_max_size = 1000

    # read commandline arguments
    for arg in sys.argv:
        if arg.startswith('--config_file'):
            # read configurations
            cfg_filename = arg.split('=')[1]
        elif arg.startswith('--filename_output'):
            # read filename but do not add
            filename_output = arg.split('=')[1]
        elif arg.startswith('--file_max_size'):
            # read filename but do not add
            file_max_size = int(arg.split('=')[1])
    # save data
    save(filename_output, cfg_filename, file_max_size=file_max_size)
    
    sys.exit(0)

