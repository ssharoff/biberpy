#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2022  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool provides more reasonable udpipe processing for individual files from
# newdoc id = __id__628__idend__.
# text = John Barnes has been involved in the public sector for thirty years .
# 1	John	John	PROPN	NNP	Number=Sing	5	nsubj	_	_
# 2	Barnes	Barnes	PROPN	NNP	Number=Sing	1	flat	_	_
# 3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	aux	_	_
# extracting document-level trees via Udon2. The only action done at the moment is extraction of counts for the negative clauses:
# ratio 	#_negatives	#_clauses

import sys, re, os
import tempfile
import udon2

def extractrels(fname):
  verb_count = 0
  neg_count = 0
  roots = udon2.ConllReader.read_file(fname)
  for root in roots:
    verbs = root.select_by("upos", "VERB")
    verb_count += len(verbs)
    if len(verbs)>0:
      negations = root.select_by("lemma", "not")
      for x in negations:
        if x.parent.upos == 'VERB':
          neg_count += 1
  if verb_count>0:
    print(f'{(neg_count/verb_count):.5f}\t{neg_count}\t{verb_count}')
  else:
    print('0.000\t0\t0')

f=open(sys.argv[1]) if len(sys.argv)>1 else sys.stdin
curid=''
curtext=''
doccount=0
textptn='# newdoc id = __id__'
for l in f:
  if re.match(r'[0-9-]+\t', l):
      tf.write(l)
  elif l.startswith(textptn): # we're about to start a new text
    if curid: # already in processing
      tf.close()
      doccount += 1
      extractrels(tf.name)
      os.unlink(tf.name)
    tf = tempfile.NamedTemporaryFile(mode="w", dir=".", delete=False)
    curid=l[len(textptn):].split()[0]
    curtext=l[len(textptn):]
  else:
    tf.write(l)

if curid: # a file is left for processing 
  tf.close()
  extractrels(tf.name)
  os.unlink(tf.name)
print(f'processed {doccount} documents')
