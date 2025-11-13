#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool compares two sets of data with respect to the features 
# and outputs the most significant differences with wilcoxon()
# since ttest_rel() is mostly not applicable

import sys
import numpy as np
import pandas as pd
import scipy.stats 

fnamea=sys.argv[1]
fnameb=sys.argv[2]

print(f'Comparing {fnamea} to {fnameb} with a paired Wilcoxon test')

Xa=pd.read_csv(fnamea,sep='\t')
Xb=pd.read_csv(fnameb,sep='\t')

differences = {}
for feature in list(Xa):
    x = Xa[feature].to_numpy()
    y = Xb[feature].to_numpy()
    # (v,p) = scipy.stats.ks_2samp(x,y)
    # if p>0.05:
    #     print(f'ok normality {feature} {p}')
    # else:
    #     print(f'no normality {feature} {p}')
    try:
        (t,p) = scipy.stats.wilcoxon(x,y)
        if p<0.05:
            differences[feature] = np.mean(y)/(np.mean(x)+1e-15)
            # the ratio of what is more common in y will be higher
    except:
        print(f'Identical values in {feature}', file=sys.stderr)
print(sorted(differences.items(), key=lambda x:x[1]))
