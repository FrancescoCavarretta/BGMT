# This scripts scan the files and check the existence of files related to each cell

import pandas as pd
import numpy as np
import datetime
import os
import eFELExt as efel_ext
import NeuroSAGE as NS

import warnings
warnings.filterwarnings('ignore')




def _scan_files(dataset_path, data_filename, verbose_unknown=False): 
    """ scan the files in the directory
        collect filenames of each type,
        when the data are collected in multiple files
    """
    ns_filename = {'fi':list(), 'rmih':list(), 'tburst':list(), 'unknown':list()}
    for filename in os.listdir(dataset_path):
      if filename.startswith(data_filename):
        suffix = filename[len(data_filename):filename.index('.')].strip().lower()

        # add the path
        filename = os.path.join(dataset_path, filename)
        if 'fi' in suffix:
          ns_filename['fi'].append(filename)
        elif 'rmih' in suffix or 'ihrm' in suffix:
          ns_filename['rmih'].append(filename)
        elif 'burst' in suffix:
          ns_filename['tburst'].append(filename)
        else:
          ns_filename['unknown'].append(filename)
          if verbose_unknown:
            print ('Warning:\tfile content unknown', filename)
    return ns_filename


def _extract_electric_features(filenames, efeatures, thresholds, cur_bin={'fi':20.0, 'rmih':50.0, 'tburst':50.0}, tinit_stim=800.0, input_resistance_tinit=500, input_resistance_tstop=600):
  """
    here we extract the firing properties and convert to a Pandas DataFrame
    We return three data frames in output:
      1. f-I curves
      2. Sag amplitudes
      3. Burst
  """

  data_field_name = {'fi':'f-i', 'rmih':'ih', 'tburst':['0.2s -100~-500', '0.5s -100~-500', '1s -100~-500', '1.5s -100~-500', '2s -100~-500', '1.0s -100~-500', '2.0s -100~-500']}
  
  ##    # if the step amplitude is zero, it may occur that the step is detected as different from 2s in length
  ##    # when the step amplitude is zero, we assume this issue to occur, and account the entry for a valid f-i curve test
  ##    # similarly for sag amplitudes but we need hyperpolarizing deflection
  check = { 'fi':
            lambda k : k[1] == 2000.0 or k[0] == 0.0,
            'rmih':
            lambda k : k[1] == 2000.0 and k[0] < 0 or k[0] == 0.0,
            'tburst':
            lambda k : k[0] < 0 or k[0] == 0.0 }

  f = NS.DatasetReader(filenames, filter_flag=True)

  ret_data_frame = pd.DataFrame()
  for ef_type, ef_names in efeatures.items():
    
    df = pd.DataFrame(columns=ef_names + ['protocol', 'filename', 'file key', 'bias current', 'step current', 'total current'])

    for k, indices in f.trial_by_current(suffix=data_field_name[ef_type], \
                                         total_current_flag=True, \
                                         cur_bin=None).items():

      # check amplitude and length
      if check[ef_type](k): 
        
        for i in indices:
          trace = f.read_voltage_trace(i) # read the trace

          # trace info
          _filename = os.path.basename(f._get_file_reader(i)[0].filename)
          _file_key = f._get_key(i)

          # step length          
          if ef_type == 'tburst':
            if '0.2s' in _file_key:
             stim_dur = 200.0
            elif '0.5s' in _file_key:
             stim_dur = 500.0
            elif '1s' in _file_key or '1.0s' in _file_key:
             stim_dur = 1000.0         
            elif '1.5s' in _file_key:
             stim_dur = 1500.0
            elif '2s' in _file_key or '2.0s' in _file_key:
             stim_dur = 2000.0
          else:
            stim_dur = k[1]
                     
          # set firing threshold
          if type(thresholds) == float or type(thresholds) == int:
              efel_ext.efel.setThreshold(thresholds)
          elif type(thresholds) == dict:
              efel_ext.efel.setThreshold(thresholds[ef_type])
          else:
              efel_ext.efel.setThreshold(-30.0)
              if ef_type == 'fi':
                  try:
                      efel_ext.efel.setThreshold(thresholds[(_filename, _file_key)])
                  except:
                      print (_file_key)

          # reformat the output
          # the empty array for spikecount means zero spikes while for the other parameter the real value is NaN
          retval = efel_ext.getFeatureValues({'T':trace[:,0], 'V':trace[:,1], 'stim_start':[tinit_stim], 'stim_end':[tinit_stim+k[1]]}, ef_names)
          
          # correct input resistance
          if 'input_resistance' in ef_names:   
              retval['input_resistance'] = efel_ext.getFeatureValues({'T':trace[:,0], 'V':trace[:,1], 'stim_start':[input_resistance_tinit], 'stim_end':[input_resistance_tstop]}, ['input_resistance'])['input_resistance']
                
              
          # extend the retval with other informations
          retval['filename'] = f._get_file_reader(i)[0].filename
          retval['file key'] = f._get_key(i)
          retval['bias current'] = f.bias_amplitude(i)
          retval['step current'] = f.step_amplitude(i)
          retval['total current'] = k[0]
          retval['stim dur'] = stim_dur
          retval['protocol'] = ef_type
          retval['time stamp'] = f.time_stamp(i)
          
          df = df.append(retval, ignore_index=True, sort=False) 

    # append to the data frame
    ret_data_frame = ret_data_frame.append(df, ignore_index=True, sort=False)
  return ret_data_frame
    





def preprocess(filename_ml, filename_out, preprocess_function):
    df = pd.DataFrame() # output

    # read the file masterlist
    df_master_list = pd.read_csv(filename_ml)
    
    # iterate the feature extraction
    for irow, row in enumerate(df_master_list.iterrows()):
      # get the information about the experiments
      exp_info = row[1]['info']
      state = row[1]['state']
      
      # reformat
      _exp_info_tk = exp_info.split('S')
      # the date should match the fmt used for filenames
      for data_fmt in ['%d%b%y', '%d%B%y', '%e%b%y', '%e%B%y']:
        try:
          exp_date = datetime.datetime.strptime(_exp_info_tk[0], data_fmt)
          break
        except:
          exp_date = None
          
      # deal with the error of being unable to extract the exp. data
      if exp_date is None:
        print ('Warning:\tthe date was not read', row)
        continue
      
      exp_date= exp_date.strftime('%Y-%m-%d')
      slice_info = 'Slice' + _exp_info_tk[1]
      state = state.lower().replace('-', '')

      # get subdirectory name
      data_subdir = exp_date + '_NS'
      data_path_subdir = os.path.join(dataset_path, data_subdir)
      
      # get filename
      data_filename = exp_date + ' ' + slice_info 
      data_filename_ext = data_filename + '.hdf5'
      
      # full path
      full_path = os.path.join(dataset_path, \
                               os.path.join(data_subdir, \
                                            data_filename_ext))

      # check for the existance of a directory
      if not os.path.exists(data_path_subdir):
        print ('\n\nWarning:\tRetrieve this path', data_path_subdir, '\n\n')
        continue
      
      # check whether the file exists
      # if the single file does not exists
      # the data were broken in multiple files
      # with suffix fI, TBurst, RmIh
      if os.path.exists(full_path):
        ns_filename = [full_path]
        _other_files = _scan_files(data_path_subdir, data_filename)
        if len(_other_files['fi']) or len(_other_files['rmih']) or len(_other_files['tburst']):
          print ('Warning:\tThere are also others files that may be of interest beside', full_path)
          print ('\t\t', _other_files['fi'])
          print ('\t\t', _other_files['rmih'])
          print ('\t\t', _other_files['tburst'])

          # if it happens an I/O error when opening the file
          # we move to the multiple file format
          try:
            keys = NS.DatasetReader(ns_filename)._get_key_types()
            
            # check the keys in case
            # we absolutely need f-I curve data for our analysis sake
            if 'f-I' not in keys:
                print ('\t\tThe single file does not contain relevant data: we will use the multiple file format\n')
                ns_filename = _other_files
                    
          except KeyError:
            print ('\t\tThe single file is inconsistent: we will use the multiple file format\n')
            ns_filename = _other_files
      else:
        ns_filename = _scan_files(data_path_subdir, data_filename)
        

      # the file reader takes only string or list of strings as a argument
      # therefore we convert the dictionary to a list
      if type(ns_filename) == dict:
        ns_filename = ns_filename['fi'] + ns_filename['rmih'] + ns_filename['tburst']
      
      # we then run the real preprocessing and measure the electric features
      _df = preprocess_function(ns_filename) 

      # add the state (ie, 6ohda or control)
      _df['state'] = [state] * _df.shape[0]

      # application of some kind
      #_df['application'] = [np.nan] * _df.shape[0]
      
      # add the neuron id
      _df['slice id'] = [slice_info] * _df.shape[0]
      
      # add date
      _df['date'] = [exp_date] * _df.shape[0]
          
      # append to the final data frame 
      df = df.append(_df, ignore_index=True, sort=False)
      
      print ('File set', irow, '(', state, ') done')
      

    # store in a file
    df.to_csv(filename_out)
  

if __name__ == '__main__':
    dataset_path = 'dataset/'

    efeatures = {
      'fi':[
        'AP_amplitude',
        'AHP_depth',
        'AP_duration_half_width',
        'AP_width',
        'AP_count',
        'time_to_first_spike',
        'inv_first_ISI',
        'inv_second_ISI',
        'inv_last_ISI',
        'adaptation_index2',
        'voltage_base',
        'voltage_after_stim',
        'AP_count_before_stim',
        'AP_count_after_stim',
        'max_amp_difference',
        'clustering_index',
        'fast_AHP'
      ],
      'rmih':[
        'voltage_base',
        'AP1_amp_rev',
        'AP2_amp_rev',
        'time_to_first_spike',
        'AP_count_before_stim',
        'AP_count_after_stim',
        'inv_first_ISI',
        'inv_second_ISI',
        'inv_last_ISI',
        'voltage_after_stim',
        'sag_amplitude',
        'voltage_deflection',
        'input_resistance',
      ],
      'tburst':[
        'voltage_base',
        'AP1_amp',
        'AP2_amp',
        'time_to_first_spike',
        'AP_count_before_stim',
        'AP_count_after_stim',
        'inv_first_ISI',
        'inv_second_ISI',
        'inv_last_ISI',
        'voltage_after_stim',
        'sag_amplitude',
        'voltage_deflection',
      ]
    }

        

    def __extract_electric_features(ns_filename):
        return _extract_electric_features(ns_filename, efeatures, {'fi':-20.0, 'rmih':-35, 'tburst':-35})

    
    preprocess(os.path.join(dataset_path, 'MasterList_F-I.csv'), 'preprocessed_data_efeatures.csv', __extract_electric_features)
