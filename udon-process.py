#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2022  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool provides more reasonable udpipe processing for individual files, first selecting individual texts from
# # text = __id__LABEL Versija.
# 1	__id__LABEL	__id__LABEL	X__...
# 2 Versija	versija	NOUN	Ncnsnn	Case=Nom|Gender=Neut|Number=Sing
#
# then extracting document-level trees via Udon2. The only action done at the moment is extraction of counts for the negative clauses:
# ratio 	negatives	clauses

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
recount=False
idptn='__id__'
textptn='# text = '
fullptn=textptn+idptn
for l in f:
  if re.match(r'[0-9-]+\t', l):
    w=l.split('\t')[1]
    if w.startswith(idptn): # 1	__id__LABEL	__id__LABEL	X__...
      recount=True
      count=0
      p=curtext.find(w)
      if p>0:
        curtext=curtext[p+len(w):]
        tf.write('# text = '+curtext)
    elif recount: # 2 Versija	versija	NOUN
      count+=1
      l=re.sub(r'^[0-9-]+\t', str(count)+'\t',l)
      tf.write(l)
    elif curid: # this will skip the top lines before we get the first it
      tf.write(l)
  elif l.startswith(fullptn): # we're about to start a new text
    if curid: # already in processing
      tf.close()
      extractrels(tf.name)
      os.unlink(tf.name)
    tf = tempfile.NamedTemporaryFile(mode="w", dir=".", delete=False)
    curid=l[len(textptn):].split()[0]
    curtext=l[len(textptn):]
  elif l.startswith(textptn): # normal text description 
    tf.write('\n'+l)
    recount=False

if curid: # a file is left for processing 
  tf.close()
  extractrels(tf.name)
  os.unlink(tf.name)
