# -*- coding: utf-8 -*-
"""
Created on Fri May 24 16:14:31 2024

@author: mbmad
"""

from patchanalysis.workers import Analysis
from patchanalysis import TimeSpan, NullSpan, FullSpan

from patchanalysis.measures.basic import area_under_curve, ap_count
from patchanalysis.measures.currentramp import ap_threshold, firstthreeratio, input_resistance, rheobase

import numpy as np


class Stim_Events(Analysis):
    def __init__(self,
                 stims_per_trace: int = 1,
                 baseline: TimeSpan = NullSpan()):
        super().__init__()

        # Area under the curve for the entire trace after baselining.
        self.add_measure(area_under_curve(region=FullSpan(),
                                          baseline=baseline,
                                          direction=1),
                         'AUC',
                         binsize=0,
                         binfunction=np.mean)

        # Number of action potentials per stimulation event.
        self.add_measure(ap_count(threshold=-20,
                                  stims_per_sweep=3),
                         'APs/LP',
                         binsize=0,
                         binfunction=np.mean)
    
    def __repr__(self):
        return 'Pincer Analysis: Stim_Events'


class CurrentRamp(Analysis):
    def __init__(self):
        super().__init__()

        # Action Potential Threshold
        self.add_measure(ap_threshold(),
                         'AP Threshold')
        self.add_measure(firstthreeratio(),
                         'First3 Ratio')
        self.add_measure(input_resistance(),
                         'Input Resistance')
        self.add_measure(rheobase(),
                         'Rheobase')
    def __repr__(self):
        return 'Pincer Analysis: CurrentRamp'