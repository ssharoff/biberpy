#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Copyright (C) 2017  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
'''
A script for collecting Biber-like features from one-line text collections and a dictionary.

Expanded from experiments in Intellitext

'''
import sys, re
import numpy as np
import argparse
import smallutils as ut

dimlist=(
"private verbs",
"THAT deletion",
"contractions",
"present tense verbs",
"second person pronouns",
"D0 as pro-verb",
"analytic negation",
"demonstrative pronouns")

language='en'
wordlists={}
taglist={}

frq0=0
lemma1=1
pos2=2
finepos3=3

#Full list from Perl:
# F1 => ["private verbs", \&posWithLemmaFilter, "w", "V.*", $privateVerbs],
# F2 => ["THAT deletion", \&thatDeletion, "s"],
# F3 => ["contractions", \&contractions, "w"],
# F4 => ["present tense verbs", \&simplePartsOfSpeech, "w", "VV,VVZ"],
# F5 => ["second person pronouns", \&simpleWords, "w", $secondPersonPronouns],
# F6 => ["D0 as pro-verb", \&doAsProVerb, "s"],
# F7 => ["analytic negation", \&simpleLemmas, "w", "not"],
# F8 => ["demonstrative pronouns", \&demonstrativePronouns, "s"],
# F9 => ["general emphatics", \&simpleWords, "w", $generalEmphatics],
# F10 => ["first person pronouns", \&simpleWords, "w", $firstPersonPronouns],
# F11 => ["pronoun IT", \&simpleWords, "w", "it"],
# F12 => ["BE as main verb", \&beAsMainVerb, "s"],
# F13 => ["Causative subordination", \&simpleWords, "w", "because"],
# F14 => ["discourse particles", \&dummyFunction, "s"],
# F15 => ["indefinite pronouns", \&simpleWords, "w", $indefinitePronouns],
# F16 => ["general hedges", \&dummyFunction, "s"],
# F17 => ["amplifiers", \&simpleWords, "w", $amplifiers],
# F18 => ["sentence relatives", \&dummyFunction, "s"],
# F19 => ["WH questions", \&simpleWords, "w", $whQuestions],
# F20 => ["possibility modals", \&simpleWords, "w", $possibilityModals],
# F21 => ["non-phrasal coordination", \&dummyFunction, "s"],
# F22 => ["WH clauses", \&simpleWords, "w", $whMarkers],
# F23 => ["final prepositions", \&strandedPrepositions, "s"],
# F24 => ["adverbs", \&simplePartsOfSpeech, "w", "RB,RBR,RBS"],
# F25 => ["conditional subordination", \&dummyFunction, "s"],
# F26 => ["nouns", \&simplePartsOfSpeech, "w", "N.*"],
# F27 => ["word length", \&wordLength, "d"],
# F28 => ["prepositions", \&simplePartsOfSpeech, "w", "IN"],
# F29 => ["type/token ratio", \&typeTokenRatio, "d"],
# F30 => ["attributive adjectives", \&attributiveAdjectives, "s"],
# F31 => ["place adverbials", \&simpleWords, "w", $placeAdverbials],
# F32 => ["agentless passives", \&dummyFunction, "s"],
# F33 => ["past participial WHIZ deletions", \&dummyFunction, "s"],
# F34 => ["present participial WHIZ deletions", \&dummyFunction, "s"],
# F35 => ["past tense verbs", \&simplePartsOfSpeech, "w", "VVD"],
# F36 => ["third person pronouns", \&simpleWords, "w", $thirdPersonPronouns],
# F37 => ["perfect aspect verbs", \&perfectAspect, "s"],
# F38 => ["public verbs", \&posWithLemmaFilter, "w", "V.*", $publicVerbs],
# F39 => ["synthetic negation", \&syntheticNegation, "s"],
# F40 => ["present participial clauses", \&presentParticipialClauses, "s"],
# F41 => ["present tense verbs", \&dummyFunction, "w"],
# F42 => ["past participial WHIZ deletions", \&dummyFunction, "s"],
# F43 => ["WH relative clauses on object positions", \&dummyFunction, "s"],
# F44 => ["pied piping constructions", \&dummyFunction, "s"],
# F45 => ["WH relative clauses on subject positions", \&dummyFunction, "s"],
# F46 => ["phrasal coordination", \&dummyFunction, "s"],
# F47 => ["nominalizations", \&nominalizations, "w", "NN.*"],
# F48 => ["time adverbials", \&simpleWords, "w", $timeAdverbials],
# F49 => ["place adverbials", \&dummyFunction, "w"],
# F50 => ["infinitives", \&infinitives, "s"],
# F51 => ["prediction modals", \&dummyFunction, "w"],
# F52 => ["suasive verbs", \&dummyFunction, "w"],
# F53 => ["conditional subordination", \&dummyFunction, "s"],
# F54 => ["necessity modals", \&simpleWords, "w", $necessityModals],
# F55 => ["split auxiliaries", \&dummyFunction, "s"],
# F56 => ["possibility modals", \&simpleWords, "w", $possibilityModals],
# F57 => ["conjuncts", \&dummyFunction, "w"],
# F58 => ["past participial clauses", \&dummyFunction, "s"],
# F59 => ["BY-passives", \&dummyFunction, "s"],
# F60 => ["other adverbial subordinators", \&dummyFunction, "s"],
# F61 => ["predicative adjectives", \&predicativeAdjectives, "s"],
# F62 => ["type/token ratio", \&dummyFunction, "d"],
# F63 => ["THAT clauses as verb complements", \&dummyFunction, "s"],
# F64 => ["demonstratives", \&demonstrativePronouns, "s"],
# F65 => ["THAT relative clauses on object positions", \&dummyFunction, "s"],
# F66 => ["THAT clauses as adjective complements", \&dummyFunction, "s"],
# F67 => ["final prepositions", \&dummyFunction, "s"],
# F68 => ["existential THERE", \&simplePartsOfSpeech, "w", "EX"],
# F38 => ["public verbs", \&posWithLemmaFilter, "w", "V.*", $publicVerbs],
# F69 => ["demonstrative pronouns", \&demonstrativePronouns, "s"],
# F70 => ["WH relative clauses on object positions", \&dummyFunction, "s"],
# F71 => ["phrasal coordination", \&dummyFunction, "s"],
# F72 => ["SEEM/APPEAR", \&posWithLemmaFilter, "w", "V.*", $seemappear],
# F73 => ["downtopers", \&posWithLemmaFilter, "w", "RB", $downtopers],
# F74 => ["concessive subordination", \&dummyFunction, "s"]);

def checkWordSet(w, type):
    return w in wordlists[type]
def isDemonstrativePronoun(doc, pos):
    nextType = typeAt(doc,pos+1)
    nextWord = doc[pos+1]
    return checkWordSet(nextWord,"modalVerbs" ) or nextType=="PRON" 
	# wordCheck($nextWord, "and,".$clausePunctuation.",\'s"))

def findLemmaInSentence(doc, pos, type, getpos=False):
    count=0
    out=[]
    for i,w in enumerate(doc):
        if w in taglist and taglist[w][pos2]==pos and taglist[w][lemma1] in wordlists[type]:
            count+=1
            if getpos:
                out.append(i)
    return count, out

def posWithLemmaFilter(doc, pos, type):
    count, _ =findLemmaInSentence(doc, pos, type)
    return count

def simpleLemmas(doc, lemma):
    count=0
    for w in doc:
        if w in taglist and taglist[w][lemma1]==lemma:
            count+=1
    return count

def simplePartsOfSpeech(doc, pos, finepos=''):
    count=0
    for w in doc:
        if w in taglist and taglist[w][pos2]==pos:
            if not finepos or (taglist[w][finepos3].find(finepos)>=0):
                count+=1
    return count

def thatDeletion(doc):
    count, positions = findLemmaInSentence(doc, 'specialVerbs',True)
    for pos in positions:
        try:
            nextWord = doc[pos+1]
            # First Biber prescription 
            if isDemonstrativePronoun(doc,pos + 1) or wordCheck(nextWord, 'subjectPronouns'):
                next
            nextType = typeAt(doc[pos+1])
            typeAfter = typeAt(doc[pos+2])
            posCounter=2
            # Second Biber prescription
            if nextType=="PRON" or nextType=="NOUN":
                if checkWordSet(doc[pos+posCounter], "modalVerbs"):
                    next
            # Third and most complicated Biber prescription
            if nextType in ["ADJ","ADV","DET","PRON"]:
                # This is the optional adjective
                if typeAfter=="ADJ":
                    posCounter+=1
                    typeAfter = typeAt(doc[pos+posCounter])
                # Then a noun
                if typeAfter=="NOUN":
                    posCounter += 1
                    # Then if there's an auxiliary we accept this one
                    if checkWordSet(doc[pos+posCounter], "modalVerbs"):
                        next
        except:
            # the index is out of the doc length
            count+=-1
            
        # Only get to here if none of the prescriptions fit so
        # discount this one
        count+=-1
    return count

def contractions(doc):
    count=0
    for w in doc:
        if w.find("'")>=0:
            count+=1
    return count
def demonstrativePronouns(doc):
    count, positions = findLemmaInSentence(doc, 'demonstrativePronouns', True);
    for pos in positions:
        if not isDemonstrativePronoun(pos):
            count+=-1
    return count

def getbiberdims(doc):
    '''
    processes document as a list of tokenised words
    '''
    f1=posWithLemmaFilter(doc,'VERB','privateVerbs')/len(doc)
    f2=thatDeletion(doc)/len(doc)
    f3=contractions(doc)/len(doc)
    f4=simplePartsOfSpeech(doc,"VERB","Tense=Present")/len(doc)
    f5=posWithLemmaFilter(doc, 'PRON', 'secondPersonPronouns')/len(doc)
    f6=0#doAsProVerb(doc)/len(doc)
    f7=simpleLemmas(doc, "not")/len(doc)
    f8=demonstrativePronouns(doc)/len(doc)
    return [f1,f2,f3,f4,f5,f6,f7,f8]

def readwordlists(f):
    '''
    reads lists in the format
    firstPersonPronouns = I,we,me,us,my,our,myself,ourselves
    '''
    out={}
    for line in f:
        x=line.strip().split(' = ')
        if len(x)==2:
            out[x[0]]=set(x[1].split(','))
    return out

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

parser = argparse.ArgumentParser(description="A Keras Model for Genre Classification")
parser.add_argument('-1', '--embeddings', type=str, help='source embeddings')
parser.add_argument('-t', '--testfile', type=str, help='one-doc-per-line corpus')
parser.add_argument('-o', '--outfile', type=str, default='-', help='output file')
parser.add_argument('-l', '--language', type=str, help='language id for getting the annotation files')

parser.add_argument('-v', '--verbosity', type=int, default=1)

outname=re.sub(' ','=','_'.join(sys.argv))
outname=re.sub('/','@',outname)

args = parser.parse_args()
ut.verbosity=args.verbosity

f=sys.stdin if args.testfile=='-' else ut.myopen(args.testfile)
fout=sys.stdout if args.testfile=='-' else open(args.outfile,"w")

wordlists=readwordlists(open(args.language+'.properties'))
numfile=args.language+'.tag.num'
taglist=readnumlist(open(args.language+'.tag.num'))

if args.embeddings:
    embeddings,w2i=ut.read_embeddings(args.embeddings)

print(' '.join(['"'+d+'"' for d in dimlist]),file=fout)
if args.verbosity>1:
    print('total %d dims in the header' % len(dimlist),file=sys.stderr)

for line in f:
    doc=line.strip().lower().split()
    dims=getbiberdims(doc)
    if args.verbosity>2:
        print('total %d dims in output' % len(dims),file=sys.stderr)
    print(' '.join(['%.5f' % d for d in dims]),file=fout)
