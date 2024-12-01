#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Copyright (C) 2019  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
# The tool converts a one-doc-per-line text file to json
# using a spacy library
import sys, json
import spacy

f = open(sys.argv[1]) if (len(sys.argv)>1 and not sys.argv[1]=='-') else sys.stdin
nlp = spacy.load(sys.argv[2]) if len(sys.argv)>2 else spacy.load("en_core_web_lg")


outdoc=[]
for l in f:
    doc = nlp(l)
    outdoc=[]
    for token in doc:
        out=[token.text, token.lemma_, token.pos_, str(token.morph), token.dep_]
        outdoc.append(out)
    print(json.dumps(outdoc))
