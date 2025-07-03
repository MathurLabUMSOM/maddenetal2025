# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 16:54:02 2024

@author: mbmad
"""

from patchanalysis.measures.measuretools import NoResultError, InvalidRecordingError, \
    withinEachSweep, withinEachSweepHzXuYuCu
from patchanalysis import TimeSpan, FullSpan, NullSpan
from scipy.signal import find_peaks

import numpy as np
    
def ap_threshold(region: TimeSpan = FullSpan()):
    @withinEachSweep('sweepC', 'sweepY')
    def measure(sweepC, sweepY) -> np.float64:
        whereramp = np.gradient(sweepC) != 0
        trace_rampregion = sweepY[whereramp]
        ap_peak_inds = find_peaks(trace_rampregion, threshold=-20)
        if len(ap_peak_inds) == 0:
            raise NoResultError('No Action Potentials')
        trace_ramp_rise = trace_rampregion[:ap_peak_inds[0]]
        inflectionpoint = np.argmax(np.gradient(np.gradient(trace_ramp_rise)))-2 #correction for shifting with gradient
        return np.float64(trace_ramp_rise[inflectionpoint])
    return measure

def firstthreeratio(region: TimeSpan = FullSpan()):
    @withinEachSweep('sweepC', 'sweepY')
    def measure(sweepC, sweepY) -> np.float64:
        whereramp = np.gradient(sweepC) != 0
        trace_rampregion = sweepY[whereramp]
        ap_peak_inds = find_peaks(trace_rampregion, threshold=-20)
        if len(ap_peak_inds) < 3:
            raise NoResultError('Insuffient Number of Action Potetials')
        return np.float64((ap_peak_inds[1] - ap_peak_inds[0]) / (ap_peak_inds[2] - ap_peak_inds[1]))
    return measure

def input_resistance(region: TimeSpan = FullSpan()):
    @withinEachSweep('sweepC', 'sweepY')
    def measure(sweepC, sweepY) -> np.float64:
        whereramp = np.gradient(sweepC) != 0
        trace_rampregion = sweepY[whereramp]
        ap_peak_inds = find_peaks(trace_rampregion, threshold=-20)
        if ap_peak_inds != []:
            trace_ramp_rise = trace_rampregion[:ap_peak_inds[0]]
            inflectionpoint = np.argmax(np.gradient(np.gradient(trace_ramp_rise)))-2 #correction for shifting with gradient
            trace_ramp_rise = trace_ramp_rise[:inflectionpoint]
        else:
            trace_ramp_rise = trace_rampregion
        in_resist = np.average(np.gradient(trace_ramp_rise))
        return np.float64(in_resist)
    return measure

def rheobase(region: TimeSpan = FullSpan()):
    @withinEachSweep('sweepC', 'sweepY')
    def measure(sweepC, sweepY) -> np.float64:
        whereramp = np.gradient(sweepC) != 0
        trace_rampregion = sweepY[whereramp]
        command_rampregion = sweepC[whereramp]
        ap_peak_inds = find_peaks(trace_rampregion, threshold=-20)
        if ap_peak_inds == []:
            raise NoResultError('No Action Potentials')
        trace_ramp_rise = trace_rampregion[:ap_peak_inds[0]]
        inflectionpoint = np.argmax(np.gradient(np.gradient(trace_ramp_rise)))-2 #correction for shifting with gradient
        return np.float64(command_rampregion[inflectionpoint])
    return measure
        
if __name__ == '__main__':
    import pyabf
    x = pyabf.ABF('G:\\Data\\24606034.abf')
    print(ap_threshold()(x))
    print(firstthreeratio()(x))
    print(input_resistance()(x))