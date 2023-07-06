The directory <i>mouselight-vm</i> contains swc files of thalamocortical neuron morphologies from ventromedial thalamus.

The directory <i>jaeger</i> contains swc files of thalamocortical neuron morphologies from ventromedial thalamus which are only partially reconstructed; 
these morphologies were analyzed to define the tapering rule for the dendritic diameters.

To run the preprocessing script, from terminal execute the command<br><br>
<i>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;python main.py &lt; input swc file &gt; &lt; output swc file &gt;
</i>

The preprocessing of morphology consists of <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1. Checking consistency of 'topology' <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Setting axon diameter and length, leaving the proximal portion only, ie, axon initial segment<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Setting soma size in accord with anatomical measurements <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 4. Setting dendritic diameters, which tapers at each branch point <br>
<br>
For any inquiry, contact the author, Francesco Cavarretta &lt; francescocavarretta@hotmail.it &gt;, or his PI, Dieter Jaeger &lt; djaeger@emory.edu &gt;, from Emory University.
