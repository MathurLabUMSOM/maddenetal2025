# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 13:08:36 2025

@author: mm4114
"""

from patchanalysis.analyses.currentclamp import Stim_Events, CurrentRamp
from patchanalysis.analyses.voltageclamp import PairedPulse_withSealTest
from patchanalysis.span import TimeSpan, NullSpan, FullSpan
import pandas as pd

"""
Use of dataframes allows user to write filepaths into an excel document which can then
be imported as a dataframe.
"""
df = pd.DataFrame(columns=['Filepath'])
df.loc['recording1'] = {'Filepath': '/path/to/file.abf'}
df.loc['recording2'] = {'Filepath': '/path/to/file2.abf'}

"""
This is an representative example analysis for a paired pulse stimulation protocol
This analysis was used in figures 1 and 2.
"""
pairedpulseanalysis = PairedPulse_withSealTest(TimeSpan((0, 200)),  # Baseline, first 200 ms
                                               TimeSpan(()),  # First peak,
                                               TimeSpan(()),  # Second peak,
                                               # Baseline used for capacitive current
                                               TimeSpan(()),
                                               # Location of capacitive current peak
                                               TimeSpan(())
                                               )
"""
This analysis extracts the peak sizes for each sweep and provides them in a dataframe
that can be saved to excel.
"""
results, errors = pairedpulseanalysis.process(df)

"""
This is a representative example analysis for a AUC and AP per LP measures.
This analysis was used in figures 4 and 5.
"""
auc_and_aplp_analysis = Stim_Events(stims_per_trace=3,
                                    baseline=TimeSpan((0, 200))
                                    )
"""
This analysis counts the number of action potentials and calculates the area
under the curve for each sweep and returns a dataframe that can be exported to excel.
"""
results, errors = auc_and_aplp_analysis.process(df)