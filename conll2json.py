#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool converts a conll file to one-doc-per-line json file

import sys, json
import re
outlist=[1,2,3,5]  # wform, lemma, pos, full features (5)
docnum=0
f = open(sys.argv[1]) if len(sys.argv)>1 else sys.stdin
outdoc=[]
for l in f:
    md = re.match(r'^[0-9-]+\t', l)
    if md:
        x=l.split()
        out=[x[i] for i in outlist]
        outdoc.append(out)
    elif l[:8]=='# newdoc' and len(outdoc)>0:
        docnum+=1
        print(json.dumps(outdoc))
        outdoc=[]
print(json.dumps(outdoc))
