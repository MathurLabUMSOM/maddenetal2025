# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:03:19 2024

@author: mbmad
"""

from patchanalysis.workers import Analysis
from patchanalysis.measures.basic import peak_magnitude
from patchanalysis.span import TimeSpan

class PairedPulse_withSealTest(Analysis):
    def __init__(self,
                  baseline: TimeSpan,
                  firstpeak: TimeSpan,
                  secondpeak: TimeSpan,
                  sealtestbaseline: TimeSpan,
                  sealtestpeak: TimeSpan,
                  binsize=1,
                  autocalculate_memprops=True):
        super().__init__()
        self.add_measure(peak_magnitude(firstpeak, baseline, -1),
                         'First Peak Magnitude',
                         binsize=binsize)
        self.add_measure(peak_magnitude(secondpeak, baseline, -1),
                         'Second Peak Magnitude',
                         binsize=binsize)
        self.add_measure(peak_magnitude(sealtestpeak, sealtestbaseline, -1),
                         'Capacitive Current Peak',
                         binsize=binsize)