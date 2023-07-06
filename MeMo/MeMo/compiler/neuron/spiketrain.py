class SpikeTrain:
    time_conversion = {
        "tenth_ms":1e-4,
        "ms":1e-3,
        "s":1.0,
        "m":60,
        "h":3600.0
        }
    
    def abbasi(self, distribution, time, rate, refractory_period, tstop):
        
        conversion_factor = SpikeTrain.time_conversion[self.time_unit]
        
        #print (tstop, refractory_period, conversion_factor)
        
        tstop *= conversion_factor
        refractory_period *= conversion_factor
        time *= conversion_factor

        #print (tstop, refractory_period, conversion_factor)
        
        UnGamma   =self.UnGamma
        Precision =self.Precision
        
        distr_mean = distribution.k * distribution.theta
        
        #print (tstop, refractory_period, distr_mean, distribution.k, distribution.theta)
        #import matplotlib.pyplot as plt
        #plt.plot(time, rate)
        #plt.show()        
        
        #max_frequency=None
        #min_frequency=None
        
        import numpy as np
        
        """ let's test the consistency of the configuration """
        #if max_frequency is None:
        max_frequency = 1.0 / refractory_period
        
        #if min_frequency is None:
        min_frequency = 0.0
          
        #assert min_frequency < max_frequency
        #assert max_frequency <= 1.0/refractory_period
          
        # calculate time bin sizeself._gen_spike_train(*self._args)
        TimeBinSz = time[1] - time[0]
          
          
        """ check validity of the numbstg.get()er and convert """
        def RateToISI(FRate):
            if FRate > max_frequency:
                FRate = max_frequency
            elif FRate < min_frequency:
                FRate = min_frequency
      
            try:
                return 1.0 / FRate
            except:
                return 1.0 / max_frequency
    
        # Pull spike times from Gamma distribution to generate AST
        # Params for Gamma: rate from rate template (and k from Lv distribution = reg)
        ISIs = []
        I = 0
        while I < len(time):
            # gamrnd = matlab fn for random arrays from gamma distribution. 
            # Given arguments get a mean firing rate of 1
            X = distribution() / distr_mean #np.random.gamma(Reg, scale=1.0/Reg)
            
            J = I
            for z in range(Precision):
                MeanRate = np.mean(rate[I:(J+1)]) # calculate mean rate over expected mean interval
                CurrentISI = X * RateToISI(MeanRate)  
                
                Jnew = min([ len(rate)-1, I+int(round(CurrentISI/TimeBinSz)) ])  # calculate the interval boundary
                if J == Jnew:
                    break
                J = Jnew

            if UnGamma:
                # for cases where templates have sudden large
                # increases in rate, which leads to very slow catchup performance wiht
                # default algorithm.  If algorithmflag==2 then the current interval is
                # examied for rate changes of factor > ungam, and if one is found, the
                # maximal rate for the original interval is determined.  Then the
                # original interval is shortened to the time where the rate exceeds
                # ungam, and a 2nd interval for the new max rate is added.
                MaxRate = np.max(rate[I:(J+1)])
                if MaxRate > UnGamma*rate[I]:
                    CurrentISI = refractory_period + X * RateToISI(MaxRate) - refractory_period
            
            if CurrentISI < refractory_period:
                CurrentISI = refractory_period
                
            ISIs.append(CurrentISI)
            I += int(round(CurrentISI/TimeBinSz))
        
        
        # spike times
        SpikeTimes = np.cumsum(ISIs)
        SpikeTimes = SpikeTimes[SpikeTimes <= tstop]
        
        SpikeTimes /= conversion_factor
        time /= conversion_factor
        return SpikeTimes

    
    def poissonian(self, distribution, refractory_period, tstop):
        conversion_factor = SpikeTrain.time_conversion[self.time_unit]
        tstop *= conversion_factor
        refractory_period *= conversion_factor
        
        import numpy as np
            
        SpikeTimes = np.array([0.])
        
        while SpikeTimes[-1] < tstop:
            while True:
                try:
                    CurrentISI = 1.0 / distribution()
                    while CurrentISI < refractory_period:
                        CurrentISI = 1.0 / distribution()
                    break
                except ZeroDivisionError:
                    continue
                
            SpikeTimes = np.concatenate((SpikeTimes, [SpikeTimes[-1] + CurrentISI]))
        
        SpikeTimes /= conversion_factor
        
        return SpikeTimes
    
    
    def regular(self, mean_rate, tstart, number):
        
        conversion_factor = SpikeTrain.time_conversion[self.time_unit]
        tstart *= conversion_factor
        isi = 1.0 / mean_rate * conversion_factor
        
        import numpy as np

        SpikeTimes = tstart + np.cumsum([isi] * number)
        
        SpikeTimes /= conversion_factor
        
        return SpikeTimes   


    def modulation(self, phase_distribution, phase, rate, amplitude, tstop, tinit):
        import numpy as np
        conversion_factor = SpikeTrain.time_conversion[self.time_unit]
        
        phase_rnd = phase_distribution() * 2 * np.pi

        time = np.linspace(tinit, tstop, int( rate * 100 * (tstop - tinit) * conversion_factor ) )
        y = np.sin(2 * np.pi * rate * (time - tinit) * conversion_factor + phase + phase_rnd) 
        #y = np.power(y, narrowness)
        #y = y * 2 - 1
        #S = (y[1:] - y[:-1]) * (time[1] - time[0]) * conversion_factor
        y = y * amplitude + 1
        #import matplotlib.pyplot as plt
        #plt.plot(time, y)
        #plt.show()
        return { 'time':time, 'y':y}
        


        
    def burst(self, inter_distribution, intra_distribution, \
              time, rate, \
              inter_time, inter_rate, min_inter_period, \
              refractory_period, tstop, tinit): #, tweak=True):
        
        import numpy as np

        
       # t_burst = self.abbasi(inter_distribution, inter_time, inter_rate, min_inter_period, tstop)
        
        bursts = []
        if self.Tdur > 0:
          #tspk = np.array([])
          #print (inter_distribution.theta)
          # time init of each burst
          t_burst_init = self.abbasi(inter_distribution, inter_time, inter_rate, min_inter_period, tstop) + tinit
          
          for tbi in t_burst_init:
              _tspk = self.abbasi(intra_distribution, time, rate, refractory_period, time[-1])
              _tspk = _tspk + tbi
              bursts.append(_tspk)
            
        return bursts #if tweak else tspk
            
    
    def __init__(self, name):
        self.name = name
        self.product = None
        
        self.time_unit = "s"
        
        if self.name == "abbasi" or self.name == "burst":
            self.UnGamma = None
            self.Precision = 100
            
        self.generation_function = getattr(self, name)
        for x in self.generation_function.__code__.co_varnames[1:self.generation_function.__code__.co_argcount]:
            setattr(self, x, None)


    def combine_with_modulation(self):
        import numpy as np

        mtime, my = self.modulation_model.product['time'], self.modulation_model.product['y']   
        mtime = mtime * self.modulation_model.time_conversion[self.modulation_model.time_unit]
        
        time, rate = self.time, self.rate
        time = time * self.time_conversion[self.time_unit]

        tstop = self.tstop * self.time_conversion[self.time_unit]
        
        dt = min([mtime[1] - mtime[0], time[1] - time[0]])
        
        tp = np.arange(0.0, tstop, dt)
        myp = np.interp(tp, mtime, my)
        
        try:
            myp[tp < mtime[0]] = 1.0
        except:
            pass
        try:
            myp[tp > mtime[-1]] = 1.0
        except:
            pass

        
        ratep = np.interp(tp, time, rate)
        combined_ratep = ratep * myp

        tp = tp / self.time_conversion[self.time_unit]
        #import matplotlib.pyplot as plt
        #plt.eventplot(self.product, lineoffset=2)
        
        self.product = self.abbasi(self.distribution, tp, combined_ratep, self.refractory_period, self.tstop)

        #plt.eventplot(self.product, lineoffset=1)
        #plt.show()

        
    def combine_with_bursts(self):
        import numpy as np
        
        for b in self.burst_model.product:
            idx_init = np.where(self.product <= (b[0] - self.refractory_period))[0]
            idx_end  = np.where(self.product >= (b[-1] + self.refractory_period))[0]
            
            if idx_init.size > 0 and idx_end.size > 0:
                self.product = np.concatenate((self.product[:(idx_init[-1]+1)], b, self.product[idx_end[0]:]))
            elif idx_init.size > 0 and idx_end.size == 0:
                self.product = np.concatenate((self.product[:(idx_init[-1]+1)], b))
            elif idx_init.size == 0 and idx_end.size > 0:
                self.product = np.concatenate((b, self.product[idx_end[0]:]))
                
        self.product = self.product[self.product < self.tstop]           
            
            
    def make(self):
        if self.product is None:
            if hasattr(self, "distribution") and self.distribution:
                self.distribution.make()
                
            if hasattr(self, "phase_distribution") and self.phase_distribution:
                self.phase_distribution.make()
                
            if hasattr(self, "intra_distribution") and self.intra_distribution:
                self.intra_distribution.make()
                
            if hasattr(self, "inter_distribution") and self.inter_distribution:
                self.inter_distribution.make()
                
            if hasattr(self, "burst_model") and self.burst_model:
                #print ('Here')
                self.burst_model.make()
                
            if hasattr(self, "modulation_model") and self.modulation_model:
                self.modulation_model.make()
                
            self.product = self.generation_function(*[getattr(self, x) for x in self.generation_function.__code__.co_varnames[1:self.generation_function.__code__.co_argcount]])

            if hasattr(self, "modulation_model") and self.modulation_model:
                self.combine_with_modulation()
                
            if hasattr(self, "burst_model") and self.burst_model:
                self.combine_with_bursts()
                
        return self.product
        
    
    def __del__(self):
        del self.product
        self.product = None
        
        if hasattr(self, "distribution") and self.distribution:
            del self.distribution
            self.distribution = None
