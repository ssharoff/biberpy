#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
"""Studying Biber exploration with respect to genres

It takes one parameter: 
 1. a file with Biber-like dimensions (with a header, IDs and the Cat column in the end 
paste l24.dat l24.cats | numlines | sed 's/^/ID-/'
ID-1    A01.pastVerbs   A03.presVerbs  Cat
ID-2    0.33333	0.75000 A1
ID-3    0.62500 1.04167 A1

It outputs:
 1. to STDOUT: Genre, Biber-dim, mean and median for the Genre
 2. to STDERR: ranges for each Biber-dim over the genres and the ratio of its median range to its median (how much it varies across the genres)
"""

import sys
import os
import re
import numpy as np
import pandas as pd

def range(l):
    return np.max(l)-np.min(l)
def split_genres(df1,catset):
    """Create a labeled scatter plot of a dataframe."""
    subsets={}
    for cat in catset:
        subsets[cat] = df1[(df1["Cat"] == cat)]
        print(f'{cat} -> {len(subsets[cat])} examples', file=sys.stderr)
    return subsets


fname=sys.argv[1]
df1 = pd.read_csv(open(fname), sep='\t', index_col='ID-1')
print(f'Read {fname} {len(df1)} rows', file=sys.stderr)

catlist ='A1 A4 A7 A8 A9  A11 A12 A14 A16 A17'.split()

subsets = split_genres(df1,catlist)

for col in df1.columns.tolist()[:-1]:
    mean_values=[]
    median_values=[]
    for cat in catlist:
        curvalues=subsets[cat][col]
        means = np.mean(curvalues)
        mean_values.append(means)
        medians = np.median(curvalues)
        median_values.append(medians)
        print(f'{cat[1:]}\t{col}\t{means*100:.6f}\t{medians*100:.6f}')
    print(col,range(mean_values),range(median_values),range(median_values)/(np.median(median_values)+1e-10),file=sys.stderr)
