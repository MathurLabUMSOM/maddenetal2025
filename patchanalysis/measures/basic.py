# -*- coding: utf-8 -*-
"""
Created on Thu May 16 19:47:10 2024

@author: mbmad
"""
from patchanalysis.measures.measuretools import NoResultError, InvalidRecordingError, \
    withinEachSweep, withinEachSweepHzXuYuCu
from patchanalysis import TimeSpan, FullSpan, NullSpan
from patchanalysis.signal.peaks import find_peaks
import numpy as np


def area_under_curve(region: TimeSpan = FullSpan(),
                     baseline: TimeSpan = NullSpan(),
                     direction: int = -1) -> np.float64: 
    timespan_parameters = [region, baseline]

    @withinEachSweep('sampleRate', 'sweepX', 'sweepUnitsY', 'sweepY', 'sweepUnitsY')
    def measure(hz, sweepX, sweepUnitsX, sweepY, sweepUnitsY) -> float:
        for param in timespan_parameters:
            param.convertto_samples(hz)
            
        trace = baseline.baseline(sweepY)
        trace = region.crop(trace)
        trace = trace * direction
        auc = np.trapz(trace)/(hz/1000)
        return np.float64(auc)
    return measure


def ap_count(region: TimeSpan = FullSpan(),
             direction: int = 1,
             threshold: (float, int) = None,
             stims_per_sweep: int = 1
             ):
    timespan_parameters = [region]

    @withinEachSweep('sampleRate', 'sweepX', 'sweepUnitsY', 'sweepY', 'sweepUnitsY')
    def measure(hz, sweepX, sweepUnitsX, sweepY, sweepUnitsY) -> float:
        for param in timespan_parameters:
            param.convertto_samples(hz)
            
        trace = region.crop(sweepY)
        peaks = find_peaks(trace, threshold)
        return len(peaks) / stims_per_sweep
    return measure


def count_events(region: TimeSpan == FullSpan(),
                 baseline: TimeSpan = NullSpan(),
                 direction: int = 1,
                 height=None,
                 threshold=None,
                 distance=None,
                 prominence=None,
                 ):
    timespan_parameters = [region, baseline]

    @withinEachSweep('sampleRate', 'sweepX', 'sweepUnitsY', 'sweepY', 'sweepUnitsY')
    def measure(hz, sweepX, sweepUnitsX, sweepY, sweepUnitsY) -> float:
        for param in timespan_parameters:
            param.convertto_samples(hz)

        trace = baseline.baseline(sweepY)
        trace = region.crop(trace)
        trace = trace * direction
        peaklist = find_peaks(trace,
                              height=None,
                              threshold=None,
                              distance=None,
                              prominence=None,
                              width=None,
                              wlen=None,
                              rel_height=None,
                              plateau_size=None)[0]
        return len(peaklist)
    return measure


def peak_magnitude(region: TimeSpan = FullSpan(),
                   baseline: TimeSpan = NullSpan(),
                   direction: int = 1):
    timespan_parameters = [region, baseline]

    @withinEachSweep('sampleRate', 'sweepY')
    def measure(hz, sweepY):
        for param in timespan_parameters:
            param.convertto_samples(hz)

        trace = baseline.baseline(sweepY)
        trace = region.crop(trace)
        trace = trace * direction

        return np.max(trace)
    return measure
