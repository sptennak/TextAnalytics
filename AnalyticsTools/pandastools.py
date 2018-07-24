# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5  2:53:30 2018

@author: Sumudu Tennakoon
"""
import io
import os
import sys
import traceback
import pandas as pd
import numpy as np

def read_string(string, sep=',', header='infer', names=None, nrows=None, lineterminator=None, comment=None):
    try:
        return pd.read_csv(io.StringIO(string), sep=sep, header=header, names=names, nrows=nrows, lineterminator=lineterminator, comment=comment)
    except:
        print('Error Converting String to DataFrame: {}'.format(traceback.print_exc()))
        return pd.DataFrame()
    
        