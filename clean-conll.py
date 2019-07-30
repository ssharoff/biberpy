#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool cleans a CONLL file output by udpipe from a one-line corpus. Strating from:

# # newdoc
# # newpar
# # sent_id = 1
# # text = __id__http://www.wardbrothers.co.uk/products.php?productId=121
# 1       __id__http://www.wardbrothers.co.uk/products.php?productId=121  __id__http://www.wardbrothers.co.uk/products.php?productId=121  X       LS      _       _       _       _       SpacesAfter=\s\s
# # sent_id = 2
# # text = The ' Baronet Supreme ' is upholstered using a needle teased hair pad to provide extra support , making it as comfortable as it is affordable .
# 1       The     the     DET     DT      Definite=Def|PronType=Art       _       _       _       _
# 2       '       '       PUNCT   ``      _       _       _       _       _
# 3       Baronet Baronet PROPN   NNP     Number=Sing     _       _       _       _
# ...
# text = </doc> __id__http://www.tripod.lycos.co.uk/directory/music/samples___loops/?PAGE=0&ORDER=pop
# 1       </      </      SYM     NFP     _       _       _       _       SpaceAfter=No
# 2       doc     doc     NOUN    NN      Number=Sing     _       _       _       SpaceAfter=No
# 3       >       >       PUNCT   -RRB-   _       _       _       _       SpacesAfter=\s\n
# 4       __id__http://www.tripod.lycos.co.uk/directory/music/samples___loops/?PAGE=0&ORDER=pop   __id__http://www.tripod.lycos.co.uk/directory/music/samples___loops/?PAGE=0&ORDER=pop   NOUN    NN      Number=Sing     _       _       _
#        SpacesAfter=\s\s

# # newdoc id = http://www.wardbrothers.co.uk/products.php?productId=121
# # newpar
# # sent_id = 2
# # text = The ' Baronet Supreme ' is upholstered using a needle teased hair pad to provide extra support , making it as comfortable as it is affordable .
 

import sys

f = sys.stdin if len(sys.argv)<2 or sys.argv[1]=='-' else open(sys.argv[1])
textptn = sys.argv[2] if len(sys.argv)>2 else '# text = __id__'
sentptn = sys.argv[3] if len(sys.argv)>3 else '# sent_id ='

doc=[]
docid=''
delayprinting = True
for l in f:
    if l.startswith(textptn):
        docid = l[len(textptn):]
        docidloc = docid.find(' ') 
        if docidloc>0: # in case it combined with the text below
            docid = docid[:docidloc]
            delayprinting = False
        else:
            delayprinting = True
        print('# newdoc id = '+ docid)
    elif delayprinting:
        if l.startswith(sentptn):
            delayprinting = False
            sys.stdout.write(l)
    else:
        sys.stdout.write(l)
