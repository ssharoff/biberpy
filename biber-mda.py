#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool performs Factor Analysis with Biber dimensions as a replacement of the R script

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

fname = sys.argv[1] # "brown-biber.dat"
dname = sys.argv[2] # "brown-annot.dat" 
df= pd.read_csv(fname,sep="\t")
desc= pd.read_csv(dname,sep="\t")

# following https://www.datacamp.com/tutorial/introduction-factor-analysis
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
chi_square_value, p_value = calculate_bartlett_sphericity(df)
# H1: The matrix of population correlations is not equal to I.

from factor_analyzer.factor_analyzer import calculate_kmo
kmo_all, kmo_model=calculate_kmo(df)
# the degree to which each observed variable is predicted, without error, by the other variables in the dataset

print(f"Bartlett test p value {p_value}, Kaiser-Meyer-Olkin value {kmo_model:.3f}")
assert p_value<0.05, print(f"Bartlett test p value {p_value} doesn't allow FA.")
assert kmo_model>=0.6, print(f"Kaiser-Meyer-Olkin (KMO) value {kmo_model} doesn't allow FA.")

from factor_analyzer import FactorAnalyzer
# Create factor analysis object and perform factor analysis
MAX_FACTORS=10
fa = FactorAnalyzer(n_factors=MAX_FACTORS)

#fa.analyze(df, 10, rotation=None)
fa.fit(df)
# Check Eigenvalues
ev, v = fa.get_eigenvalues()
nfactors=min(np.sum(ev>1.0),MAX_FACTORS)

print(f"Selecting {nfactors} factors")
print("Explaining the variance (SS Loading, Explained Variance, Cumulative Variance)")

print(fa.get_factor_variance())

pd.DataFrame(fa.loadings_[:,:nfactors], index=df.columns).to_csv(f"loadings-{fname}",sep="\t")

# Please suggest the Python code using matplotlib for following factor analysis code in R:
# d <- factanal(bd, factors = 6, scores = 'regression')
# autoplot(d, data = bd, x=1, y=2);

categories = desc['Top']
unique_categories = categories.unique()
palette = sns.color_palette('tab10', len(unique_categories))
color_map = {category: palette[i] for i, category in enumerate(unique_categories)}

# Map each category to a color
colors = categories.map(color_map)

z=fa.transform(df)

for f1 in range(nfactors):
    for f2 in range(nfactors):
        if not f1==f2:
            plt.figure(figsize=(10, 6))
            plt.scatter(z[:, f1], z[:, f2],  c=colors, alpha=0.7, edgecolor='k')
            handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=category)
                       for category, color in color_map.items()]
            plt.legend(handles=handles, title='Categories', loc='best')

            # Set plot labels and title
            f1a=f1+1 # just for presentation 
            f2a=f2+1
            plt.xlabel(f'Factor {f1a}')
            plt.ylabel(f'Factor {f2a}')
            plt.title(f'Factor Analysis: Factor {f1a} vs Factor {f2a}')
            plt.grid(True)
            plt.savefig(f"{fname}-fa-{f1a}-{f2a}.pdf", format="pdf", bbox_inches="tight")
            plt.close()
