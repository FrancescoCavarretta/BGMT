import warnings
warnings.filterwarnings("ignore")

import gc
gc.collect(2)

import os

import pandas as pd
import numpy as np

import MeMo.memo.neuron as nrn
import MeMo.compiler as compiler
import MeMo.compiler.precompiler as precompiler
import MeMo.compiler.neuron as base
import MeMo.compiler.neuron.util.recorder as recorder
import MeMo.memo.spiketrain as stn
import MeMo.memo.microcircuit as mc
import MeMo.nwbio as nwbio

# import and register cell model
import vmcell
compiler.register_object(base, vmcell.Cell)

# models of thalamic connections
from afferents import SynapticInputs, InputToThalamus

# read default values of synaptic conductance and their numbers
try:
  _gsyn = np.load('gsyn.npy', allow_pickle=True).tolist()
  gsyn = { 'SNR':_gsyn['SNR'], 'RTN':_gsyn['RTN'], 'MOD':_gsyn['CX'], 'DRV':_gsyn['CN_VM']}  
  del _gsyn
except:
  gsyn = { 'SNR':0., 'RTN':0., 'MOD':0., 'DRV':0. }
  print('Warning: default synaptic conductances not found')
print('gsyn', gsyn)

#try:
#  _nsyn = np.load('nsyn.npy', allow_pickle=True).tolist()
#  nsyn = { 'SNR':_nsyn['SNR'], 'RTN':nsyn['RTN'], 'MOD':_nsyn['CX'], 'DRV':395 } #_nsyn['CN_VM'] }
#  del _nsyn
#except:
#syn = { 'SNR':25, 'RTN':400, 'MOD':1450, 'DRV':350 }
nsyn = { 'SNR':25, 'RTN':400, 'MOD':1450, 'DRV':350 }
#nsyn = { 'SNR':25, 'RTN':400, 'MOD':1450, 'DRV':125 }
#  print('Warning: default number of synapses not found')
print('nsyn', nsyn)


# register modules
from MeMo.compiler.neuron import modules as neuron_modules
neuron_modules.register_modules(os.path.join(os.path.dirname(__file__), 'synapses'))
#neuron_modules.compile()


def mk_in_vivo_presyn_activity(tstop,
                               snr_params, rtn_params, drv_params, mod_params,
                               basic_tonic_settings=dict(refractory_period=3.0),
                               basic_burst_settings=dict(fast_rise=False, fast_decay=True, refractory_period=1.5, intra_burst_k=3, intra_burst_theta=0.1),
                               time_unit='ms', snr_sync_burst=True, snr_async_burst=True):
    import copy
     
    # tweak burst template in sync and async for snr
    if 'burst' in snr_params and snr_params['burst'] is not None:
        # parameters for SYNCHRONOUS nigral inputs
        snr_params_sync = copy.deepcopy(snr_params)
        snr_params_sync['burst']['regularity'] = snr_params_sync['burst']['regularity_sync']
        del snr_params_sync['burst']['regularity_sync']

        # parameters for ASYNCHRONOUS nigral inputs
        snr_params_async = copy.deepcopy(snr_params)
        snr_params_async['burst']['regularity'] = snr_params_async['burst']['regularity_async']
        del snr_params_async['burst']['regularity_async']
    else:
        snr_params_sync = snr_params_async = snr_params

    # build the spike trains
    st = []
    for kwargs, burst_flag in [ (snr_params_sync, snr_sync_burst), (snr_params_async, snr_async_burst), (rtn_params, True), (drv_params, True), (mod_params, True) ]:
        # read and attach firing rate template, if any
        if 'template' in kwargs and kwargs['template']:
            kwargs.update(kwargs['template'])
            del kwargs['template']

        # read and attach firing rate template for modulation, if any
        if 'modulation' in kwargs and kwargs['modulation']:
            modulation_model = stn.SpikeTrain('modulation', time_unit=time_unit, **kwargs['modulation'])
            del kwargs['modulation']
        else:
            modulation_model = None

        # read and attach firing rate template for bursting, if any
        if 'burst' in kwargs and kwargs['burst']:
            kwargs_burst = copy.deepcopy(kwargs['burst'])
            del kwargs['burst']

            if not burst_flag:
                kwargs_burst['Tdur'] = 0.0

            burst_model = stn.SpikeTrain('burst', time_unit=time_unit, **basic_burst_settings, **kwargs_burst)
#           burst_model = stn.SpikeTrain('burst', time_unit=time_unit, **basic_burst_settings, **kwargs['burst'])
#           del kwargs['burst']
        else:
            burst_model = None

        # create spike train 
        st.append(stn.SpikeTrain("abbasi", tstop=tstop, time_unit=time_unit, modulation_model=modulation_model, burst_model=burst_model, **basic_tonic_settings, **kwargs))

    return st


def mk_vm_model(cellid, lesioned_flag, snrST_sync, snrST_async, rtnST, drvST, modST, 
                       snr_param ={"n":nsyn['SNR'], "g":gsyn['SNR'], 'burst':None},
                       rtn_param={"n":nsyn['RTN'], "g":gsyn['RTN']},
                       drv_param={"n":nsyn['DRV'], "g":gsyn['DRV'], 'NmdaAmpaRatio':0.6},
                       mod_param={"n":nsyn['MOD'], "g":gsyn['MOD'], 'NmdaAmpaRatio':1.91}):
  # instantiate cell
  cell =  nrn.Cell("TC", cellid=cellid, lesioned_flag=lesioned_flag)

  # model of synapses
#  snrSyn = nrn.Synapse("GABAA", erev=-76.4, tau=14.0)
#  rtnSyn = nrn.Synapse("GABAA", erev=-76.4, tau=14.0)
  snrSyn = nrn.Synapse("GABAA", erev=-81, tau=14.0)
  rtnSyn = nrn.Synapse("GABAA", erev=-81, tau=14.0)
  drvSyn = nrn.Synapse("AmpaNmda", erev=0.0, ratio=drv_param['NmdaAmpaRatio'])
  modSyn = nrn.Synapse("AmpaNmda", erev=0.0, ratio=mod_param['NmdaAmpaRatio'])
  
  # instantiate synaptic inputs
  si_drv = SynapticInputs("driver", drvSyn, drvST, cell)
  si_mod = SynapticInputs("modulator", modSyn, modST, cell)
  si_snr_sync = SynapticInputs("snr", snrSyn, snrST_sync, cell)
  si_snr_async = SynapticInputs("snr", snrSyn, snrST_async, cell)
  si_rtn = SynapticInputs("reticular", rtnSyn, rtnST, cell)

  # instantiate a container for all the inputs
  conn = InputToThalamus("InputToVMThalamus", cell, si_drv, si_mod, si_snr_sync, si_snr_async, si_rtn, percent_sync_snr=(1 if snr_param['burst'] is None else snr_param['burst']['percent_sync']))
  
  # set numbers and conductance of the synapses
  conn.n_snr    =  snr_param['n']
  conn.n_reticular = rtn_param['n']
  conn.n_modulator = mod_param['n']
  conn.n_driver    = drv_param['n']

  conn.gsyn_snr    = snr_param['g']
  conn.gsyn_reticular = rtn_param['g']
  conn.gsyn_modulator = mod_param['g']
  conn.gsyn_driver    = drv_param['g']

  # microcircuit
  vmcircuit = mc.MicroCircuit("VMThalamus")
  vmcircuit.add(conn)

  return vmcircuit, conn


def _iterate_input_property(retsim, name, conn, entity_type="models", **kwargs):
  from collections.abc import Iterable
  for inputname, obj in [ ('modulator', getattr(conn.modulator, name)), ('driver', getattr(conn.driver, name)), ('reticular', getattr(conn.reticular, name)), ('snr sync', getattr(conn.snrSync, name)), ('snr async', getattr(conn.snrASync, name)) ]:
    for i, p0 in  enumerate(retsim[entity_type][obj]["real_simobj"].product):
      if isinstance(p0, Iterable):
        if type(p0) == dict or type(p0) == map:
          yield inputname, i, p0[kwargs['info_name']]
        else:
          for p1 in p0.product:
            yield inputname, i, p1
      else:
        yield inputname, i, p0

  
def _save_spike_train(filename, retsim, conn):
  tab = {'neuron class':list(), 'cellid':list(), 'spike time':list()}
  for inputname, i, tspk in _iterate_input_property(retsim, 'spktr', conn):

    # create entry
    tab['neuron class'].append(inputname)
    tab['cellid'].append(i)
    tab['spike time'].append(tspk.product)

  # format the table
#  tab = pd.concat(tab)
#  tab.loc[tab['neuron class'] == 'snr async', 'cellid'] += tab.loc[tab['neuron class'] == 'snr sync', 'cellid'].nunique()
#  tab['cellid'] = tab['cellid'].replace(['snr sync', 'snr async'], 'snr')

  # output
  np.save(filename, tab, allow_pickle=True)


def _save_syn_distribution(filename, retsim, conn):
  from neuron import h
  tab = pd.DataFrame()
  for inputname, i, p in _iterate_input_property(retsim, 'syn2cell', conn, entity_type="links", info_name="Segment"):
    sec, x = p.product['Segment']['Section'], p.product['Segment']['Arc']

    # create entry
    tmp = pd.Series()
    tmp['input name'] = inputname
    tmp['input index'] = i
    tmp['section name'] = h.secname(sec=sec)
    tmp['section arc'] = x
    tmp['path distance'] = h.distance(x, sec=sec)
    tmp['target diam'] = sec(x).diam
    tmp['target area'] = sec(x).area()
    
    tab = pd.concat([tab, tmp.to_frame().T])
    
  # output
  tab.to_csv(filename)


def _mk_mem_recorders(section, varnames, fmt='%s[%d](%f).%s', dt=0.05):
  recordings = {}

  for varname in varnames:
    recordings[varname] = list()

  for sectype in section:
    # iterate the sections
    for i in section[sectype]:
      # iterate the segments
#      for seg in section[sectype][i]:
        segments = [ seg for seg in section[sectype][i] ]
        #seg = segments[int(len(segments) / 2)]
        for seg in segments:
          # create recording for each variable
          for varname in varnames:
            # test whether it is a density variable
            if hasattr(seg, varname):
              recordings[varname].append(recorder.Recorder(getattr(seg, varname), seg=seg, dt=dt, density_variable=True)) #varname.startswith('_ref_i_output'))

  for varname in recordings:
    recordings[varname] = recorder.GroupRecorder(recordings[varname], mean_flag=False)


  return recordings


def _mk_syn_recorders(retsim, conn, fmt='syn.%s[%d](%f).%s', dt=0.05):
  recordings = {}    

  for inputname, i, p in _iterate_input_property(retsim, 'syn2cell', conn, entity_type="links", info_name="Segment"): 
    if inputname not in recordings:
      recordings[inputname] = []

    s, x = p.product['Segment']['Section'], p.product['Segment']['Arc']
    syn = p.input.product
    recordings[inputname].append(recorder.Recorder(getattr(syn, '_ref_i'), seg=s(x)))
    #recordings[inputname].append(recorder.Recorder(getattr(syn, '_ref_g'), seg=s(x)))

  for inputname in recordings:
    recordings[inputname] = recorder.GroupRecorder(recordings[inputname])

  return recordings


def _sum_recordings(recordings, dt=None, mean_flag=False):
  res = recordings[0].get(dt=dt)
  for i in range(1, len(recordings)):
    res[:, 1] = res[:, 1] + recordings[i].get(dt=dt)[:, 1]
  if mean_flag:
    res[:, 1] = res[:, 1] / len(recordings)
  return res


def nrn_run(retsim, circ, conn, tstop, seed, varnames, all_section_recording=False, all_synapse_recording=False, dt=0.05, vinit=-78.0, celsius=37.5, ena=69, ek=-105, all_section_current_recording=False, sum_current=False, no_simulation=False, **kwargs):
  # if all section recording, record even the currents
  all_section_current_recording = all_section_current_recording or all_section_recording
  
  # instantiate the recorders
  recordings = {}

  # instantiate recorders for sections
  if all_section_recording:
    section = retsim["models"][conn.cell]["real_simobj"].section
  else:
    section = {"somatic":retsim["models"][conn.cell]["real_simobj"].section["somatic"]}
    
  # instantiate recorders for sections
  if all_section_current_recording:
    current_section = retsim["models"][conn.cell]["real_simobj"].section
  else:
    current_section = {"somatic":retsim["models"][conn.cell]["real_simobj"].section["somatic"]}
    
  # create recorders for membrane mechs
  # currents
  recordings.update(_mk_mem_recorders(current_section, [s for s in varnames if '_ref_i' in s], dt=dt))

  # all the others
  recordings.update(_mk_mem_recorders(section, [s for s in varnames if '_ref_i' not in s], dt=dt))

  # instantiate recorders for synapse
  if all_synapse_recording:
    recordings.update(_mk_syn_recorders(retsim, conn, dt=dt))

  # run simulation
  if not no_simulation:
    base.runtime.run(tstop, vinit=vinit, recordings=recordings, celsius=celsius, ena=ena, ek=ek, **kwargs)

  # dt for interpolations
  if sum_current:
    # group recordings
    recordings_ = {}
    for krec, objrec in recordings.items():
      krec_type = krec.split('.')[-1]
      # voltage membrane should not be averaged/summed
      if krec_type == '_ref_v':
        recordings_[krec] = objrec.get(dt=dt)
      else:
        if krec_type not in recordings_:
          recordings_[krec_type] = list()
        recordings_[krec_type].append(objrec)

    # sum recordings
    for krec in recordings_.keys():
      if type(recordings_[krec]) == list:
#        recordings_[krec] = _sum_recordings(recordings_[krec], dt=dt, mean_flag=True)
        recordings_[krec] = _sum_recordings(recordings_[krec], dt=dt, mean_flag=False)
    
    return recordings_

  return { k:r.get(dt=dt) for k, r in recordings.items() }


def run(cellid, seed, lesioned_flag, tstop, varnames, save_spike_train=None, save_syn_distribution=None, snr_async_no_burst=False, snr_sync_no_burst=False, **kwargs):
  param = dict({
          'snr':dict({"regularity":5.0, "mean_rate":50.0, "n":nsyn['SNR'],  "g":gsyn['SNR'], 'burst':None, 'modulation':None, 'template':None }),
          'rtn':dict({"regularity":5.0, "mean_rate":10.0, "n":nsyn['RTN'], "g":gsyn['RTN'], 'burst':None, 'modulation':None, 'template':None}),
          'drv':dict({"regularity":5.0, "mean_rate":30.0, "n":nsyn['DRV'], "g":gsyn['DRV'], 'modulation':None, 'NmdaAmpaRatio':0.6, 'template':None }),
          'mod':dict({"regularity":5.0, "mean_rate":1.1, "n":nsyn['MOD'], "g":gsyn['MOD'], 'modulation':None, 'NmdaAmpaRatio':1.91, 'template':None})
          })


  # read optional parameters
  for k, v in kwargs.items():
    param_tokens = k.split('__')
    
    if len(param_tokens) == 2:
      param[param_tokens[0]][param_tokens[1]] = v

    elif len(param_tokens) == 3:
      if param[param_tokens[0]][param_tokens[1]] is None:
        param[param_tokens[0]][param_tokens[1]] = {}
      param[param_tokens[0]][param_tokens[1]][param_tokens[2]] = v
  
  # create default synaptic inputs
  snrST_sync, snrST_async, rtnST, drvST, modST = mk_in_vivo_presyn_activity(tstop, param['snr'], param['rtn'], param['drv'], param['mod'], snr_sync_burst=not snr_sync_no_burst, snr_async_burst=not snr_async_no_burst)

  # replace inputs if defined
  if 'snrST_sync' in kwargs:
    bgST_sync = kwargs['snrST_sync']
    
  if 'snrST_async' in kwargs:
    bgST_async = kwargs['snrST_async']
    
  if 'rtnST' in kwargs:
    rtnST = kwargs['rtnST']
    
  if 'drvST' in kwargs:
    drvST = kwargs['drvST']
    
  if 'modST' in kwargs:
    modST = kwargs['modST']

  # instantiate the simulation
  circ, conn = mk_vm_model(cellid, lesioned_flag, snrST_sync, snrST_async, rtnST, drvST, modST, snr_param=param['snr'], rtn_param=param['rtn'], drv_param=param['drv'], mod_param=param['mod'])

  # precompile & compile the network representation
  retsim = precompiler.precompile(circ, seed)
  compiler.compile(retsim, base)

  # save spike trains
  if save_spike_train:
    if save_spike_train == '#':
      save_spike_train = 'st_%d_%d_%d_%g_%g.txt' % (cellid, seed, int(lesioned_flag), param['snr']['burst']['percent_sync'], param['snr']['burst']['Tdur'])
    _save_spike_train(save_spike_train, retsim, conn)

  # save synaptic distributions
  if save_syn_distribution:
    _save_syn_distribution(save_syn_distribution, retsim, conn)
    
  # run and return
  return nrn_run(retsim, circ, conn, tstop, (seed, 0), varnames, **kwargs)


def run_and_save(key, cellid, seed, lesioned_flag, tstop, varnames, tcut_init=None, tcut_end=None, **kwargs):
    # run simulation
    output = run(cellid, seed, lesioned_flag, tstop, varnames, **kwargs)
    
    # store to nwb file
    # pack info
    sim_info = kwargs.copy().update({'key':key, 'cellid':cellid, 'seed':seed, 'lesioned':lesioned_flag, 'tstop':tstop })

    # store to nwb file

    if True:
      fw = nwbio.FileWriter(key + ".nwb", str(sim_info), "thalamic_data_id", max_size=None)
      for key_res, data_res in output.items():
        if tcut_init and tcut_end:
          data_res = data_res[np.logical_and(data_res[:, 0] >= tcut_init, data_res[:, 0] <= tcut_end), :]
        elif tcut_init:
          data_res = data_res[data_res[:, 0] >= tcut_init, :]
        elif tcut_end:
          data_res = data_res[data_res[:, 0] <= tcut_end, :]
        try:
          fw.add(key + '.' + key_res, data_res[:, 0], data_res[:, 1])
        except IndexError:
          print('data_res', data_res)
      fw.close()
    else:
      output = {}
      for key_res, data_res in output.items():
        if tcut_init and tcut_end:
          data_res = data_res[np.logical_and(data_res[:, 0] >= tcut_init, data_res[:, 0] <= tcut_end), :]
        elif tcut_init:
          data_res = data_res[data_res[:, 0] >= tcut_init, :]
        elif tcut_end:
          data_res = data_res[data_res[:, 0] <= tcut_end, :]
        output[key + '.' + key_res] = (data_res[:, 0], data_res[:, 1])
      np.save(key + ".npy", output, allow_pickle=True)


if __name__ == '__main__':  
  import sys

  # extract arguments
  def strvector(value):
    return [ x for x in values.split(',') ]
  

  # get all the params
  param = { }
  arg_type = {
    'dt':float,
    'index':int,
    'cellid':int,
    'tstop':float,
    'seed':int,
    'current_recording':strvector,
    'tcut_init':float,
    'tcut_end':float
  }
    

  for arg in sys.argv:
    if arg.startswith('--'):
      tokens = arg.split('=')
      if len(tokens) > 1:
        name, value = tokens[0][2:], tokens[1]

        # check the type
        if name in arg_type and arg_type[name]:
          value = arg_type[name](value)
        elif name.endswith('__g') or name.endswith('__NmdaAmpaRatio'):
          value = float(value)
        elif name.endswith('__n'):
          value = int(value)
        elif name.endswith('__regularity') or name.endswith('__mean_rate'):
          value = float(value)             
      else:
        name, value = tokens[0][2:], True

      param[name] = value


  if 'config_file' in param:
    param.update(dict(np.load(param['config_file'], allow_pickle=True).tolist()[param['index']]))

  # recording variables
  var_recording = [ "_ref_v" ]

  # total current
  if 'total_current_recording' in param:
    var_recording.append("_ref_i_membrane_")
  
  # ion channels
  if 'all_current_recording' in param:
    current_recording_suffix = ["BK", "iM", "TC_iT_Des98", "TC_iL", "TC_ih_Bud97", "TC_iD", "TC_iA", "SK_E2", "nat_TC_HH", "nap_TC_HH", "k_TC_HH"]
#    current_recording_suffix = ["BK", "iM", "TC_iT_Des98", "TC_ih_Bud97", "TC_iA"]

  elif 'current_recording' in param:
    current_recording_suffix = [param['current_recording']]
  else:
    current_recording_suffix = []

  for suffix in current_recording_suffix:
    var_recording.append("_ref_i_output_" + suffix)
  
  # remove other params
  other_param = param.copy()
  for name in ['key', 'cellid', 'seed', 'lesioned', 'tstop', 'config_file', 'index' ]:
    if name in param:
      del other_param[name]

  # print parameters
  print(param)
  print(other_param)
  
  # run and output
  run_and_save(param['key'], param['cellid'], param['seed'], 'lesioned' in param, param['tstop'], var_recording,
                        **other_param)
  sys.exit(0)
