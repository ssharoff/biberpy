#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Copyright (C) 2017-2021  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
'''
A script for collecting Biber-like features from one-line text collections and a dictionary.

Expanded from experiments in Intellitext

'''
import sys, os, re
import time
import argparse
import json, biberpy

doc=[]
docstring=''

parser = argparse.ArgumentParser(description="Multilingual Biber-like tagger")
parser.add_argument('-1', '--embeddings', type=str, help='embeddings, not implemented yet')
parser.add_argument('-f', '--format', type=str, default='ol', help='either ol (default) or json output by conll2json.py')
parser.add_argument('-l', '--language', type=str, default='en', help='language id for getting the annotation files')
parser.add_argument('-s', '--suppressheader', action='store_true', help='suppresses the default feature header')
parser.add_argument('-v', '--verbosity', type=int, default=1)
parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='one-doc-per-line corpus, plain or json')
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='output file')
parser.add_argument('-t', '--test', type=str, default='', help='Test only this function')

args = parser.parse_args()
biberpy.verbosity=args.verbosity

assert args.format in ['ol','json'], 'Wrong format, either ol or json is accepted. Requested: '+args.format

dirname=os.path.dirname(os.path.realpath(__file__))
biberpy.initwordlists(dirname,args.language,args.format)
dimnames=biberpy.dimnames
if not args.suppressheader:
    print('\t'.join([d+'.'+dimnames[d] for d in sorted(dimnames)]),file=args.outfile)
if args.verbosity>1:
    print('total %d dims in output' % len(dimnames),file=sys.stderr)

starttime=time.time()
for i,line in enumerate(args.infile):
    if args.format=='ol':
        biberpy.docstring=line.strip().lower()
        doc=re.findall(r'[.?,]|\w+',biberpy.docstring) # primitive tokenisation
    elif args.format=='json':
        doc=json.loads(line)
    if args.test:
        dims=biberpy.getbiberdims(doc,args.test)
        print(dims,file=args.outfile)
    else:
        dims=biberpy.getbiberdims(doc)
        print('\t'.join(['%.5f' % dims[d] for d in sorted(dimnames)]),file=args.outfile)
if args.verbosity>0:
    print('Processed %d files in %d sec' % (i+1, time.time()-starttime),file=sys.stderr)
