#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool cleans a frequency list by leaving only the most frqt lowercased version

import sys

frqloc=0
wfloc=1
lemloc=2
posloc=3
fineposloc=4


f=sys.stdin if len(sys.argv)<2 or sys.argv[1]=='-' else open(sys.argv[1])

dicwf={}
for l in f:
    x=l.strip().split()
    wf=x[wfloc].lower()
    if not wf in dicwf:
        sys.stdout.write(l)
        dicwf[wf]=x[frqloc]
