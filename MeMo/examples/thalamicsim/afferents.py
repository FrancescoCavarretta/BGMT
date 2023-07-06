import numpy as np

import MeMo.memo.model as model
import MeMo.memo.link as link
import MeMo.memo.spiketrain as stn
import MeMo.memo.distribution as distr
import MeMo.memo.neuron as nrn

# distribution of synapses by Bodor et al 2008
bodor_et_al2008 = {
    "xlabels":[0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 'somatic'],
    "weights":[5.33673534681342, 10.590606603532123, 24.91409649347326, 8.85334015868954, 16.012285641156904, 5.302981827489134, 5.387125671871004, 3.6572178141796883, 8.91140900947019, 1.739665984131058, 1.733267212695175, 6.980899667263891]
    }

bodor_et_al2008['xlabels'] = bodor_et_al2008['xlabels'][:-1] + list(np.arange(2.6, 3.2, 0.2)) + bodor_et_al2008['xlabels'][-1:]

bodor_et_al2008['weights'] = bodor_et_al2008['weights'][:-1] + \
	list((np.arange(2.6, 3.2, 0.2) - 2.4) / (3 - 2.4) * (bodor_et_al2008["weights"][-1] - bodor_et_al2008["weights"][-2]) + bodor_et_al2008["weights"][-2]) + \
	bodor_et_al2008['weights'][-1:]

bodor_et_al2008["weights"] /= np.sum(bodor_et_al2008["weights"])


# modulators
mod_distr = {
    "xlabels":[0.5, 1, 3.5],
    "weights":[81.85, 12.38, 0.31]
    }
mod_distr['weights'] = (np.array(mod_distr['weights']) / np.sum(mod_distr['weights'])).tolist()

# rtn
rtn_distr = {
    "xlabels":[0.5, 1.0, 3.5],
    "weights":[8.05, 1.38, 0.25]
    }
rtn_distr['weights'] = (np.array(rtn_distr['weights']) / np.sum(rtn_distr['weights'])).tolist()

# snr
snr_distr = {
    "xlabels":[0.5, 1.0, 3.5],
    "weights":[0.        , 0.6, 0.43]
    }
snr_distr['weights'] = (np.array(snr_distr['weights']) / np.sum(snr_distr['weights']) * 0.9).tolist()
snr_distr['xlabels'] += ['somatic']
snr_distr['weights'] += [0.1]


class SynapticInputs(nrn.Model):

  def __init__(self, name, syn, spktr, cell, distribution=None, target=None, **kwargs):
    """
        Represent a set of synaptic inputs to the thalamocortical cells
        name: identifier of the inputs ('driver', 'modulator', 'snr', 'reticular')
        syn: model of synapse
        spktr: model of spike train
        cell: cell model
        distribution: information on the distribution (default:None)
        target: morphological information on the postsynaptic target (default:None)
    """

    # check synaptic input names
    assert name == 'driver' or name == 'modulator' or name == 'snr' or name == 'reticular'

    model.Model.__init__(self, name, **kwargs)

    self.syn = nrn.SynapseGroup("syn", syn=syn)
    self.spktr = stn.SpikeTrainPopulation("spktr", spktr=spktr)
    self.spktr2syn = link.Link(self.spktr, self.syn)

    self.cell = cell

    '''if distribution is None:
        distribution = { "driver":distr.Distribution("uniform"),
                        "modulator":distr.Distribution("uniform"),
                        "reticular":distr.Distribution("uniform"),
                        "snr":distr.Distribution("empirical", x=bodor_et_al2008["xlabels"], freq=bodor_et_al2008["weights"])
                        }[name]

    if target is None:
        target = { "driver":("dist", "basal", 0.0, 65, "area"),
                   "modulator":("dist", "basal", 65, None, "area"),
                   "reticular":("diam", "basal", None, None, "area"),
                   "snr":("diam", ["basal", "soma"], None, None, None)
                   }[name]'''


    if distribution is None:
        distribution = { "driver":distr.Distribution("uniform"),
                        "modulator":distr.Distribution("empirical", x=mod_distr["xlabels"], freq=mod_distr["weights"]),
                        "reticular":distr.Distribution("empirical", x=rtn_distr["xlabels"], freq=rtn_distr["weights"]),
                        "snr":distr.Distribution("empirical", x=snr_distr["xlabels"], freq=snr_distr["weights"])
                        }[name]


    if target is None:
        target = { "driver":("dist", "basal", 0.0, 65, "area"),
                   "modulator":("diam", "basal", None, None, None),
                   "reticular":("diam", "basal", None, None, None),
                   "snr":("diam", ["basal", "soma"], None, None, None)
                   }[name]


    self.syn2cell = link.Link(self.syn, self.cell, distribution=distribution, target=target)

    self.n = 1

    self.__linkattr__("n", "n_syn", submodel=self.syn)
    self.__linkattr__("n", "n_spktr", submodel=self.spktr)
    self.__linkattr__("erev", "erev", submodel=self.syn.syn)

    if not hasattr(self, "gsyn"):
        self.gsyn = 0.

    if hasattr(self.syn.syn, "gsyn_ampa") and hasattr(self.syn.syn, "gsyn_nmda"):
        self.ratio = self.syn.syn.ratio
        
        self.__linkattr__(("gsyn", "ratio"), "gsyn_ampa", submodel=self.syn.syn, function="gsyn_ampa=gsyn/(1+ratio)")
        self.__linkattr__(("gsyn", "ratio"), "gsyn_nmda", submodel=self.syn.syn, function="gsyn_nmda=gsyn*ratio/(1+ratio)")
        
    elif hasattr(self.syn.syn, "gsyn"):
        self.__linkattr__("gsyn", "gsyn", submodel=self.syn.syn)
    else:
        raise Warning("Unknown property name describing synaptic conductance")



class InputToThalamus(model.Model):
  def __init__(self, name, cell, driver, modulator, snrSync, snrASync, reticular, percent_sync_snr=1.0):
    model.Model.__init__(self, name, cell=cell, driver=driver, modulator=modulator, snrSync=snrSync, snrASync=snrASync, reticular=reticular, percent_sync_snr=percent_sync_snr)

    for inputname in ["driver", "modulator", "snrSync", "snrASync", "reticular"]:
      self.__linkattr__("n_" + inputname, "n", submodel=getattr(self, inputname))
      self.__linkattr__("gsyn_" + inputname, "gsyn", submodel=getattr(self, inputname))
      self.__linkattr__("erev_" + inputname, "erev", submodel=getattr(self, inputname))

    self.n_total = 0
    
    self.__linkattr__("n_snr", "n_total", function="n_total=n_driver+n_modulator+n_snr+n_reticular")
    self.__linkattr__("n_driver", "n_total", function="n_total=n_driver+n_modulator+n_snr+n_reticular")
    self.__linkattr__("n_modulator", "n_total", function="n_total=n_driver+n_modulator+n_snr+n_reticular")
    self.__linkattr__("n_reticular", "n_total", function="n_total=n_driver+n_modulator+n_snr+n_reticular")

    for inputname in ["snrSync", "snrASync"]:
      self.__linkattr__("erev_snr", "erev", submodel=getattr(self, inputname))
      self.__linkattr__("gsyn_snr", "gsyn", submodel=getattr(self, inputname))
      if inputname == 'snrSync':
        self.__linkattr__("n_snr", "n", function="n=int(round(n_snr * percent_sync_snr))", submodel=getattr(self, inputname))
        self.__linkattr__("percent_sync_snr", "n", function="n=int(round(n_snr * percent_sync_snr))", submodel=getattr(self, inputname))
      elif inputname == 'snrASync':
        self.__linkattr__("n_snr", "n", function="n=int(round(n_snr * (1-percent_sync_snr)))", submodel=getattr(self, inputname))
        self.__linkattr__("percenta_sync_snr", "n", function="n=int(round(n_snr * (1-percent_sync_snr)))", submodel=getattr(self, inputname))      



