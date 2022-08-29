#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool restores the document ids lost through udpipe processing
# # text = __id__LABEL Versija.
# 1	__id__LABEL	__id__LABEL	X__...
# 2 Versija	versija	NOUN	Ncnsnn	Case=Nom|Gender=Neut|Number=Sing
#
# to
# # newdoc id = __id__LABEL
# text = Versija.
# 1 Versija	versija	NOUN	Ncnsnn	Case=Nom|Gender=Neut|Number=Sing

import sys, re

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
      print('\n# newdoc id = '+w)
      p=curtext.find(w)
      if p>0:
        curtext=curtext[p+len(w):]
        sys.stdout.write('# text = '+curtext)
    elif recount: # 2 Versija	versija	NOUN
      count+=1
      l=re.sub(r'^[0-9-]+\t', str(count)+'\t',l)
      sys.stdout.write(l)
    else:
      sys.stdout.write(l)
  elif l.startswith(fullptn): # we'll save # text for the future
    curid=l[len(textptn):].split()[0]
    curtext=l[len(textptn):]
  elif l.startswith(textptn): # normal text description 
    sys.stdout.write('\n'+l)
    recount=False

