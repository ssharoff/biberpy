#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool applies frequency band features from a tsv file:
# lemma category comments
# The lemmas can come either from the text as a json file, which is output by UDPIPE and processed with , or from a frequency list which maps forms to lemmas
# it outputs a matrix for the categories plus the UNK field

import sys, re
import argparse
import json

def readlist(f):
    vocab={'UNK' : 'UNK'}
    for l in f:
        x=l.split('\t')
        if len(x)>1 and not x[0] in vocab:
            vocab[x[0]]=x[1]
    return vocab

def readnumlist(f):
    '''
    reads a numfile in the format
    1625260 years year NOUN Number=Plur
    This produces a "most frequent tag" substitute for tagging
    '''
    out={}
    for line in f:
        x=line.rstrip().split()
        if len(x)==5 and not x[1] in out:
            out[x[1].lower()]=(x[0],x[2],x[3], x[4])
    return out

parser = argparse.ArgumentParser(description="Adding information from the frequency bands")
parser.add_argument('-f', '--format', type=str, default='ol', help='either ol (default) or json output by conll2json.py')
parser.add_argument('-l', '--language', type=str, default='en', help='language id')
parser.add_argument('-s', '--suppressheader', action='store_true', help='suppresses the default feature header')
parser.add_argument('-v', '--verbosity', type=int, default=1)
parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='one-doc-per-line corpus, plain or json')
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='output file')

args = parser.parse_args()
ut.verbosity=args.verbosity

language=args.language
dirname=os.path.dirname(os.path.realpath(__file__))
assert args.format in ['ol','json'], 'Wrong format, either ol or json is accepted. Requested: '+args.format

wordlists = readlist(open(dirname+'/'+language+'_levels.lex', encoding="utf8"))
if args.format=='ol':
    taglist= readnumlist(open(dirname+'/'+language+'.tag.num', encoding="utf8"))
    if args.verbosity>0:
        print('Loaded %d words from %s' % (len(taglist), language+'.tag.num'), file=sys.stderr)

if args.embeddings:
    embeddings,w2i=ut.read_embeddings(args.embeddings)

if not args.suppressheader:
    print('\t'.join([d+'.'+dimnames[d] for d in sorted(dimnames)]),file=args.outfile)
if args.verbosity>1:
    print('total %d dims in output' % len(dimnames),file=sys.stderr)

starttime=time.time()
for i,line in enumerate(args.infile):
    if args.format=='ol':
        docstring=line.strip().lower()
        doc=docstring.split()
    elif args.format=='json':
        doc=json.loads(line)
    print('\t'.join(['%.5f' % dims[d] for d in sorted(dimnames)]),file=args.outfile)
if args.verbosity>0:
    print('Processed %d files in %d sec' % (i+1, time.time()-starttime),file=sys.stderr)


