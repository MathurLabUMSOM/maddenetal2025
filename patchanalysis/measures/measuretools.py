# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:34:27 2024

@author: mbmad
"""
from functools import cache, wraps

class InvalidRecordingError(Exception):
    """
    Raise this error when an abffile fails the assumptions of a given measure.
    For example, attempting to find an action potential threshold when a trace 
    was recorded in voltage clamp configuration. This is a sign that a recording
    was incorrectly entered that somehow escaped being flagged by analysis 
    expectations.
    """
    pass

class NoResultError(Exception):
    "Raised by an measure function to omit a given output"

def withinEachSweepHzXuYuCu(func):
    return withinEachSweep('sampleRate',
                           'sweepX',
                           'sweepUnitsX',
                           'sweepY',
                           'sweepUnitsY',
                           'sweepC',
                           'sweepUnitsC')(func)


def acrossListofSweepsHzXuYuCu(func):
    return acrossListofSweeps('sampleRate',
                              'sweepX',
                              'sweepUnitsX',
                              'sweepY',
                              'sweepUnitsY',
                              'sweepC',
                              'sweepUnitsC')(func)


def withinEachSweep(*args):
    def decorator(func):
        @wraps(func)
        def wrapper(abffile):
            results = []
            for sweepnum in range(abffile.sweepCount):
                abffile.setSweep(sweepnum)
                attr = [getattr(abffile, arg, None) for arg in args]
                try:
                    res = func(*attr)
                except NoResultError:
                    pass
                else:
                    results.append(res)
            return results
        return wrapper
    return decorator


def acrossListofSweeps(*args):
    def decorator(func):
        @wraps(func)
        def wrapper(abffile):
            sweepsattr = {attr: [] for attr in args}
            for sweepnum in range(abffile.sweepCount):
                abffile.setSweep(sweepnum)
                for attr in args:
                    sweepsattr[attr].append(getattr(abffile, attr, None))
            sweepattr_args = tuple([sweepsattr[attr] for attr in args])
            return func(*sweepattr_args)
        return wrapper
    return decorator

@cache
def ms_to_samples(hz, *args):
    results = []
    for arg in args:
        if isinstance(arg, (int, float)):
            results.append(int(hz*arg/1000))
        elif arg is None:
            results.append(None)
        else:
            results.append(ms_to_samples(hz, *arg))
    return tuple(results)