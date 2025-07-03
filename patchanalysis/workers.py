# -*- coding: utf-8 -*-
"""
Created on Thu May  9 20:36:51 2024

@author: mbmad
"""
import numpy as np
import pandas as pd
import pyabf
from patchanalysis.measures.measuretools import InvalidRecordingError, NoResultError
from typing import Union


class WorkerAttemptedDestructiveOverwrite(Exception):
    """
    Raise if the alternative is destructively overwriting existing data in cases
    where it is unclear if that is desired behavior by the user. Generally methods
    should do what they are intended to do and that only. Thus an 'add' method
    should raise this rather than overwrite or alter an existing record. This
    can also be used as a protection against creating duplicate entries.
    """


class Analysis():
    def __init__(self, *args, **kwargs):
        self.measures = []
        self.expectations = []

    def __repr__(self):
        return 'Generic Pincer Analysis Object'

    def add_measure(self, func, name: str, dtype=np.float64, binsize: int = None, binfunction=np.mean):
        if name in [measure['name'] for measure in self.measures]:
            raise WorkerAttemptedDestructiveOverwrite(
                f'{name} already exists as a measure')
        self.measures.append({'name': name,
                              'function': makebinnedfunction(func, binsize, binfunction),
                              'binsize': binsize,
                              'binfunction': binfunction,
                              'dtype': dtype
                              })

    def add_expectation(self):
        pass

    def process(self, filepathsDF, report=False):
        errors = []
        resultsFrame = pd.DataFrame(
            columns=[measure['name'] for measure in self.measures])
        resultsFrame = resultsFrame.astype(
            {measure['name']: measure['dtype'] for measure in self.measures})
        for recordingID, filepath in filepathsDF['Filepath'].items():
            if report:
                print(f'Opening file at {filepath}')
            try:
                abffile = pyabf.ABF(filepath)
            except ValueError:
                errors.append(f'{filepath} does not exist or cannot be loaded')
            else:
                for measure in self.measures:
                    name = measure['name']
                    try:
                        resultsFrame.at[recordingID,
                                        name] = measure['function'](abffile)
                    except InvalidRecordingError as error:
                        errors.append(f'Recording is invalid for measure {
                                      name}: {error}')
                    except NoResultError:
                        resultsFrame.at[recordingID, name] = np.nan
        return resultsFrame, errors


def makebinnedfunction(func, binsize: int, binfunction) -> list:
    """
    Creates a function which seperates a list of outputs from the function func
    into bins, then applies a binfunction to each bin of results in the list.
    If the last bin is smaller than binsize, it is discarded.

    A binsize of zero results in binfunction being applied to all results
    from func, as if all results were a single large bin.

    Parameters
    ----------
    func : function
        A function which outputs a list.
    binsize : int
        The size of the bins in func's output to which binfunction is applied.
        A size of 0 results in a binfunction being applied to the entirety of
        func's outputs in a single large bin.
    binfunction : function or None
        The function to apply over each bin. If None, then no binning is applied.

    Returns
    -------
    List
        List of the outputs of binfucntion, applied over each bin of results
        from func.

    """
    if binsize is None:
        return func
    if binsize == 0:
        return lambda abffile: binfunction(func(abffile))

    def binnedfunction(abffile):
        results = func(abffile)
        results_binned = []
        while len(results) >= binsize:
            results_binned.append(binfunction(
                results[:binsize]
            ))
            del results[:binsize]
        return results_binned
    return binnedfunction


type Measure_Tuple = tuple[str, str]
type Measure_Input = list[Measure_Tuple, ...]


class Derived_Measures:
    def __init__(self, name : str = 'Derived_Measures', *args, **kwargs):
        self.measures = []
        self.name = name

    def add_measure(self, measure_inputs: list, func, name: str, dtype=np.float64):
        if name in [measure['name'] for measure in self.measures]:
            raise WorkerAttemptedDestructiveOverwrite(
                f'{name} already exists as a measure')
        if not isinstance(measure_inputs, list):
            raise ValueError('measure_inputs must be a list of Measure_Tuples')
        if not all(isinstance(measure, tuple) for measure in measure_inputs):
            raise ValueError(
                'All elements in a Measure_Input must be Measure_Tuples')
        if not (all(len(measure) == 2 for measure in measure_inputs) and all(
                isinstance(measure_name, str) for measure_tuple in measure_inputs for measure_name in measure_tuple)):
            raise ValueError(
                'All Measure_Tuples must be two elements long and contain two strings, the AnalysisID and measure name respectively')
        self.measures.append({'name': name,
                              'measure_inputs': measure_inputs,
                              'function': func,
                              'dtype': dtype
                              })

    def process(self, resultsFrame):
        derived_measures_frame = pd.DataFrame(
            columns=[measure['name'] for measure in self.measures])
        derived_measures_frame = derived_measures_frame.astype(
            {measure['name']: measure['dtype'] for measure in self.measures})
        derived_measures_frame.columns = pd.MultiIndex.from_tuples([(self.name, measure['name']) for measure in self.measures])
        for measure in self.measures:
            name = measure['name']
            measure_inputs = measure['measure_inputs']
            func = measure['function']
            resultsFrame_inputs_only: pd.DataFrame = resultsFrame[measure_inputs]
            derived_measures_frame[(self.name,name)] = resultsFrame_inputs_only.apply(func, axis=1)
        return derived_measures_frame
