#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool cleans a CONLL file output by udpipe from a one-line corpus. Strating from:

# # newdoc
# # newpar
# # sent_id = 1
# # text = __id__http://www.wardbrothers.co.uk/products.php?productId=121 __idend__.
# 1       __id__http://www.wardbrothers.co.uk/products.php?productId=121  __id__http://www.wardbrothers.co.uk/products.php?productId=121  X       LS      _       _       _       _       _
# 2       __idend__.  __idend__.  SYM    NFP         _       _       _       _       _
# # sent_id = 2
# # text = The ' Baronet Supreme ' is upholstered using a needle teased hair pad to provide extra support , making it as comfortable as it is affordable .
# 1       The     the     DET     DT      Definite=Def|PronType=Art       _       _       _       _
# 2       '       '       PUNCT   ``      _       _       _       _       _
# 3       Baronet Baronet PROPN   NNP     Number=Sing     _       _       _       _


# it should produce
# # newdoc id = http://www.wardbrothers.co.uk/products.php?productId=121
# # newpar
# # sent_id = 2
# # text = The ' Baronet Supreme ' is upholstered using a needle teased hair pad to provide extra support , making it as comfortable as it is affordable .
 

import sys

f = sys.stdin if len(sys.argv)<2 or sys.argv[1]=='-' else open(sys.argv[1])
textptn = sys.argv[2] if len(sys.argv)>2 else '# text = '
idBeptn = sys.argv[3] if len(sys.argv)>3 else '__id__'
idEnptn = sys.argv[4] if len(sys.argv)>4 else '__idend__'
sentptn = sys.argv[5] if len(sys.argv)>5 else '# sent_id ='

doc=[]
docid=''
delayprinting = True
for l in f:
    if l.startswith(textptn):
        docidlocstarts = l.find(idBeptn)
        docidlocends = l.find(idEnptn,docidlocstarts)
        if docidlocstarts>0: # we have a docid
            docid = l[docidlocstarts:docidlocends]
            docidlocremain = l.find(' ',docidlocends) 
            if docidlocremain>0: # in case it's joined with the text after it
                rest = l[docidlocremain+1:]
                delayprinting = False
                print('# newdoc id = '+ docid)
                sys.stdout.write('# text = '+ rest)
            else:
                delayprinting = True
                print('# newdoc id = '+ docid)
        else:
            sys.stdout.write(l)
    elif delayprinting:
        if l.find(idEnptn)>0: # ideally we should correct the linenums
            delayprinting = False
    else:
        if l.find(idBeptn)<0 and l.find(idEnptn)<0 and not l.startswith('#'):
            sys.stdout.write(l)
