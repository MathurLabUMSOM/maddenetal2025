# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 17:06:38 2024

@author: mbmad
"""

from typing import TypeAlias, Union, Tuple, List
import numpy as np

Span: TypeAlias = Tuple[int, int]
SpanList: TypeAlias = List[Span]


class TimeSpan:
    # Base factors are in us units
    _defaultunits = {'us': 1, 'ms': 1000, 's': 1000000, 'sec': 1000000, 'min': 60000000,
                     'Null': 10**10}

    def __init__(self, region: Union[Span, SpanList], unit: str = 'ms', factor=None, forcecreate=False):
        """
        Create a TimeSpan object representing a specific region of an arbitrary
        1-dimensional array with an arbitrary sampling rate.

        Parameters
        ----------
        region : Union[Span,SpanList]
            Tuple of ints or list of tuples of ints which describe the endpoints
            of a region or series of time regions in a recorded ephys trace.
        unit : str, optional
            Time unit for the endpoints in region. The default is 'ms'.

        Raises
        ------
        ValueError
            Raised if region is incorrectly formatted or unit is not a TimeSpan
            unit.

        Returns
        -------
        None.

        """
        # Enforce correct inputs
        self._units = self._defaultunits
        if unit not in self._units.keys() and forcecreate is False:
            raise ValueError(f'{unit} is not a TimeSpan Unit.')
        if forcecreate and factor is None:
            raise ValueError(f'force creation requires a factor')

        # Enforce correct inputs and convert region to appropriate format
        if not isinstance(region, (list, tuple)):
            raise ValueError(
                'Input must be Span (tuple of two integers) or list of Spans')
        if isinstance(region, list):
            for span in region:
                if not (isinstance(span, tuple) and len(span) == 2 and all(isinstance(x, int) for x in span)):
                    raise ValueError(
                        "Each element in the list must be a tuple of two integers.")
        if isinstance(region, tuple):
            if not (isinstance(region, tuple) and len(region) == 2 and all(isinstance(x, int) for x in region)):
                raise ValueError(
                    "Each element in the list must be a tuple of two integers.")
            region = [region]
        self.region = region
        self.region = self._removeoverlap(self.region)

        # Set unit and factor
        if forcecreate:
            self.unit = unit
            self.factor = factor
        else:
            self.unit = unit
            self.factor = self._units[unit]

    def __add__(self, other):
        """Magic method to allow TimeSpans to be added to each other (Union)"""
        compatible_objs = self._makefriendly(self, other)
        new_spans = []
        for obj in compatible_objs:
            new_spans += obj.region
        return TimeSpan(new_spans, compatible_objs[0].unit)

    def __sub__(self, other):
        # TODO
        pass

    def __repr__(self):
        """Magic method to generate a descriptive representation of the TimeSpan object"""
        return 'Pincer TimeSpan including ' + ' '.join(str(x) for x in self.region).replace('(', '[') + ' in unit (' + self.unit + ')'

    def convertto(self, unit: str, new_factor: int = None, region_only: bool = False):
        """
        Convert the timespan to a given unit.

        Parameters
        ----------
        unit : str
            Target unit.
        factor : int, optional
            Required if unit is not a default TimeSpan unit. Is the number of
            us in a single unit of the determined type. The default is None.
        region_only : bool, optional
            If true, does not return a converted TimeSpan, instead returns the
            endpoints in correct format (list of tuples). The default is False.

        Raises
        ------
        TypeError
            Raised when a unit is not a default unit and factor is not defined.

        Returns
        -------
        TimeSpan
            A new timespan object with the converted endpoints.

        """
        if unit not in self._units and new_factor is None:
            raise TypeError(f'{unit} is not a valid unit')
        if unit in self._units:
            new_factor = self._units[unit]
        cnv_region = [tuple([(edge*self.factor) //
                            new_factor for edge in span]) for span in self.region]
        if region_only:
            return cnv_region
        return TimeSpan(cnv_region, unit, factor=new_factor, forcecreate=True)

    def convertto_samples(self, samplerate_hz: int):
        """
        Converts a TimeSpan object in place to 'samples' units given a specific
        sample rate.

        Parameters
        ----------
        samplerate_hz : int
            Sampling rate of the recorded trace.

        Returns
        -------
        None.

        """
        if self.factor == (1000000 // samplerate_hz) and self.unit == 'samples':
            return
        self.region = self.convertto('samples',
                                     new_factor=1000000 // samplerate_hz,
                                     region_only=True)
        self.factor = 1000000 // samplerate_hz
        self.unit = 'samples'

    def crop(self, arraylike: np.ndarray):
        """
        Crops a 1D array to the desired TimeSpan

        This method crops the input 1D array to the specified TimeSpan regions.
        The unit of the TimeSpan must be set to 'Samples' for the cropping to
        be applied.

        Parameters
        ----------
        arraylike : np.ndarray
            1D array for cropping.

        Raises
        ------
        TypeError
            Raised if the unit of the timespan is not Samples.

        Returns
        -------
        np.ndarray
            Cropped array.

        """
        if self.unit == 'samples':
            return np.concatenate([arraylike[slice(*region)]
                                   for region in self.region])
        raise TypeError('Unit must be samples to apply to array')

    def baseline(self, arraylike: np.ndarray):
        """
        Subtract baseline from the input arraylike.

        This method calculates the baseline value from the specified regions 
        and subtracts it from the input arraylike. The baseline is calculated 
        as the average value across all regions specified in the object. 
        The unit attribute of the object must be set to 'samples' for this 
        method to work correctly.

        Parameters
        ----------
        arraylike : np.ndarray
            DESCRIPTION.

        Raises
        ------
        TypeError
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if self.unit != 'samples':
            raise TypeError('Unit must be samples to apply to array')
        baseline_regions = np.concatenate([arraylike[slice(*region)]
                                           for region in self.region])
        baseline_value = np.average(baseline_regions)
        return arraylike - baseline_value

    @property
    def valid_units(self):
        """Returns list of default TimeSpan units"""
        units = ', '.join(self._units.keys())
        return units

    @property
    def unit_factor(self):
        """Reports the current unit's conversion factor (to us)"""
        return self._unit[self.unit]

    @staticmethod
    def _makefriendly(*objs):
        """Internal utility method to make the units of two TimeSpan objects match"""
        if not all(obj._units == objs[0]._units for obj in objs):
            raise TypeError('Not all TimeSpans have equivalent unit sets')
        unitfactorlist = [obj._units[obj.unit] for obj in objs]
        allunitfactors = [
            factor for factor in objs[0]._units.values() if factor <= min(unitfactorlist)]
        friendly_factor = None
        for new_factor in sorted(allunitfactors, reverse=True):
            remainders = [unitfactor %
                          new_factor for unitfactor in unitfactorlist]
            if max(remainders) == 0:
                friendly_factor = new_factor
                break
        friendly_unit = {v: k for k, v in objs[0]._units.items()}[
            friendly_factor]
        return [obj.convertto(friendly_unit) for obj in objs]

    @staticmethod
    def _removeoverlap(regions: SpanList):
        """Internal utility method to join overlapping regions in a TimeSpan"""
        result = []
        for span in sorted(regions):
            if not result or span[0] > result[-1][1]:
                result.append(span)
            else:
                lastspan = result[-1]
                result[-1] = (lastspan[0], max(lastspan[1], span[1]))
        return result


class _NullSpan(TimeSpan):
    def __init__(self):
        self.region = []
        self.unit = 'Null'
        self._units = self._defaultunits

    def __repr__(self):
        return 'Pincer TimeSpan representing no portion of the trace (null)'

    def convertto_samples(self, samplerate_hz):
        pass

    def crop(self, arraylike: np.ndarray):
        return np.asarray([])

    def baseline(self, arraylike: np.ndarray):
        return arraylike


_singleton_NullSpan = _NullSpan()


def NullSpan(unique=False):
    if unique == True:
        return _NullSpan()
    return _singleton_NullSpan


class _FullSpan(TimeSpan):
    def __init__(self):
        self.region = []
        self.unit = 'Null'
        self._units = self._defaultunits

    def __repr__(self):
        return 'Pincer TimeSpan including the entire trace (dummy TimeSpan, aka FullSpan)'

    def convertto_samples(self, samplerate_hz):
        pass

    def crop(self, arraylike: np.ndarray):
        return arraylike

    def baseline(self, arraylike: np.ndarray):
        baseline_value = np.average(arraylike)
        return arraylike - baseline_value


_singleton_FullSpan = _FullSpan()


def FullSpan(unique=False):
    if unique == True:
        return _FullSpan()
    return _singleton_FullSpan
