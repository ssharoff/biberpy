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
"demonstrative pronouns",
'generalEmphatics',
'firstPersonPronouns',
"itWord",
"BE as main verb",
"becauseWord",
'indefinitePronouns',
'amplifiers',
'whQuestions',
'possibilityModals',
'whMarkers',
"strandedPrepositions",
"ADV",
"NOUN",
"placeAdverbials",
"Tense=Past",
'thirdPersonPronouns',
'publicVerbs',
"nominalizations",
'timeAdverbials',
'predictionModals',
'suasiveVerbs',
'necessityModals',
'possibilityModals',
'seemappear',
'downtopers'
)

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

def typeAt(w):
    return taglist[w][pos2]
def lemmaAt(w):
    return taglist[w][lemma1]
def isWordSet(w, type):
    return w in wordlists[type]
def isDemonstrativePronoun(doc, l):
    try:
        nextType = typeAt(doc[l+1])
        nextWord = doc[l+1]
    except:
        nextType = nextWord = ''
    if isWordSet(nextWord,'modalVerbs' ) or nextType=='PRON' or isWordSet(nextWord, 'clausePunctuation') or nextWord=='and':
        return False
    else:
        return True

def findLemmaInSentence(doc, pos, type, getloc=False):
    count=0
    out=[]
    for i,w in enumerate(doc):
        if w in taglist and (pos=='' or taglist[w][pos2]==pos) and taglist[w][lemma1] in wordlists[type]:
            count+=1
            if getloc:
                out.append(i)
    return count, out

def posWithLemmaFilter(doc, pos, type):
    count, _ = findLemmaInSentence(doc, pos, type)
    return count

def simplePartsOfSpeech(doc, pos, finepos='', getloc=False):
    count=0
    out=[]
    for i,w in enumerate(doc):
        if w in taglist and taglist[w][pos2]==pos:
            if not finepos or (taglist[w][finepos3].find(finepos)>=0):
                count+=1
                if getloc:
                    out.append(i)
    return count, out

def thatDeletion(doc):
    count, positions = findLemmaInSentence(doc, 'VERB', 'specialVerbs',True)
    thatcount = 0
    for l in positions:
        try:
            nextWord = doc[l+1]
            # First Biber prescription 
            if isDemonstrativePronoun(doc,l+1) or isWordSet(nextWord, 'subjectPronouns'):
                thatcount+=1
            else:
                nextType = typeAt(doc[l+1])
                typeAfter = typeAt(doc[l+2])
                lCounter=2
                # Second Biber prescription
                if nextType=="PRON" or nextType=="NOUN" and isWordSet(doc[l+lCounter], "modalVerbs"):
                    thatcount+=1
                else:
                    # Third and most complicated Biber prescription
                    if nextType in ["ADJ","ADV","DET","PRON"]:
                        # This is the optional adjective
                        if typeAfter=="ADJ":
                            lCounter+=1
                            typeAfter = typeAt(doc[l+lCounter])
                        # Then a noun
                        if typeAfter=="NOUN":
                            lCounter += 1
                            # Then if there's an auxiliary we accept this one
                            if isWordSet(doc[l+lCounter], "modalVerbs"):
                                thatcount+=1
        except:
            # the index is out of the doc length
            count+=-1
            
        # Only get to here if none of the prescriptions fit so
        # discount this one
        count+=-1
    return thatcount

def contractions(doc):
    count=0
    for w in doc:
        if w.find("'")>=0:
            count+=1
    return count
def demonstrativePronouns(doc):
    count, positions = findLemmaInSentence(doc, '', 'demonstrativePronouns', True);
    for l in positions:
        if not isDemonstrativePronoun(doc,l):
            count+=-1
    return count

def doAsProVerb(doc):
    # As usual we operate using BFI. First check if there are any DOs in the
    # sentence.
    doCount, doPositions = findLemmaInSentence(doc, '', 'doVerb', True);

    for doPosition in doPositions:
        try:
	    # If the DO is followed by and adverb then a verb
	    # or directly by a verb then it is NOT one we count
            # Also this condition should take into account the sentence
            # boundaries
            if typeAt(doc[doPosition+1])=='VERB' or (typeAt(doc[doPosition+1]) in ['ADV','PART'] and typeAt(doc[doPosition+2])=='VERB'):
                doCount+=-1
            else:
	        # Biber's other specification seems wrong, he says:
	        # 'punctuation WHP DO' implies a question but his WHP
	        # only includes who, whose and which. I think it should be
                # those four PLUS the whQuestions. Need to put in the prior
                # punctuation
                previousWord = doc[doPosition-1]
                if isWordSet(previousWord, 'whQuestions') or isWordSet(previousWord, 'whMarkers'):
                    doCount+=-1
        except:
            doCount+=-1
    return doCount

def beAsMainVerb(doc):
    # As usual we operate using BFI. First check if there are any BEs in the
    # sentence.
    beCount, bePositions = findLemmaInSentence(doc, '', 'beVerb', True);
    for loc in bePositions:
        # Biber's prescription for this is just that the BE is
	# followed by determiner, possessive pronoun, preposition,
        # title or adjective. We have to leave out title for now.
	# We also discount case where the BE is at the end of the sentence
	# (the SENT is at $end so the last word is at $end - 1).
        try:
            pos = typeAt(doc[loc+1])
            if not pos in ["DET","ADJ","PRON","ADP"]:
                beCount+=-1
        except:
            beCount+=-1
    return beCount

def strandedPrepositions(doc):
    prepCount, prepPositions = simplePartsOfSpeech(doc, "ADP", "", True);
    for loc in prepPositions:
        try:
            nextWord = doc[loc + 1]
            if not isWordSet(nextWord, 'clausePunctuation'):
                prepCount+=-1
        except:
            prepCount+=-1
    return prepCount;

def nominalizations(doc):
    nounCount, nounPositions = simplePartsOfSpeech(doc, "NOUN", "", True);
    nomCount=0
    for loc in nounPositions:
        lemma = lemmaAt(doc[loc])
        if lemma[-4:] in ['tion','ment','ness']:
            nomCount+=1
    return nomCount

def getbiberdims(doc):
    '''
    processes document as a list of tokenised words
    '''
    f1=posWithLemmaFilter(doc,'VERB','privateVerbs')/len(doc)
    f2=thatDeletion(doc)/len(doc)
    f3=contractions(doc)/len(doc)
    f4,_=simplePartsOfSpeech(doc,"VERB","Tense=Pres")
    f4=f4/len(doc)
    f5=posWithLemmaFilter(doc, 'PRON', 'secondPersonPronouns')/len(doc)
    f6=doAsProVerb(doc)/len(doc)
    f7=posWithLemmaFilter(doc,'', "notWord")/len(doc)
    f8=demonstrativePronouns(doc)/len(doc)
    f9=posWithLemmaFilter(doc,'','generalEmphatics')/len(doc)
    f10=posWithLemmaFilter(doc,'','firstPersonPronouns')/len(doc)
    f11=posWithLemmaFilter(doc,'',"itWord")/len(doc)
    f12=beAsMainVerb(doc)/len(doc)
    f13=posWithLemmaFilter(doc,'',"becauseWord")/len(doc)
    f14=0 # ["discourse particles", \&dummyFunction, "s"],
    f15=posWithLemmaFilter(doc,'','indefinitePronouns')/len(doc)
    f16=0 # => ["general hedges", \&dummyFunction, "s"],
    f17=posWithLemmaFilter(doc,'', 'amplifiers')/len(doc)
    f18=0 # ["sentence relatives", \&dummyFunction, "s"],
    f19=posWithLemmaFilter(doc,'','whQuestions')/len(doc)
    f20=posWithLemmaFilter(doc,'', 'possibilityModals')/len(doc)
    f21=0 # ["non-phrasal coordination", \&dummyFunction, "s"],
    f22=posWithLemmaFilter(doc,'', 'whMarkers')/len(doc)
    f23=strandedPrepositions(doc)/len(doc)
    f24,_=simplePartsOfSpeech(doc,"ADV")
    f24=f24/len(doc)
    f25=0 # ["conditional subordination", \&dummyFunction, "s"],
    f26,_=simplePartsOfSpeech(doc, "NOUN")
    f26=f26/len(doc)
    f27=0 # wordLength(doc)
    f28,_=simplePartsOfSpeech(doc, "ADP")
    f28=f28/len(doc)
    f29=0 # typeTokenRatio(doc)
    f30=0 # attributiveAdjectives, "s"],
    f31=posWithLemmaFilter(doc,'', "placeAdverbials")/len(doc)
    f32=0 # ["agentless passives", \&dummyFunction, "s"],
    f33=0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
    f34=0 # ["present participial WHIZ deletions", \&dummyFunction, "s"],
    f35,_=simplePartsOfSpeech(doc, "VERB", "Tense=Past")
    f35=f35/len(doc)
    f36=posWithLemmaFilter(doc,'', 'thirdPersonPronouns')
    f36=f36/len(doc)
    f37=0 # ["perfect aspect verbs", \&perfectAspect, "s"],
    f38=posWithLemmaFilter(doc,'', 'publicVerbs')/len(doc)
    f39=0 # \&syntheticNegation
    f40=0 # \&presentParticipialClauses
    f41 = 0 # ["present tense verbs", \&dummyFunction, "w"],
    f42 = 0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
    f43 = 0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
    f44 = 0 # ["pied piping constructions", \&dummyFunction, "s"],
    f45 = 0 # ["WH relative clauses on subject positions", \&dummyFunction, "s"],
    f46 = 0 # ["phrasal coordination", \&dummyFunction, "s"],
    f47=nominalizations(doc)/len(doc)
    f48=posWithLemmaFilter(doc,'', 'timeAdverbials')/len(doc)
    f49 = 0 # ["place adverbials", \&dummyFunction, "w"],
    f50=0 # \&infinitives
    f51=posWithLemmaFilter(doc,'', 'predictionModals')/len(doc)
    F52=posWithLemmaFilter(doc,'', 'suasiveVerbs')/len(doc)
    f53=0# ["conditional subordination", \&dummyFunction, "s"],
    f54=posWithLemmaFilter(doc,'', 'necessityModals')/len(doc)
    f55= 0 # ["split auxiliaries", \&dummyFunction, "s"],
    f56=posWithLemmaFilter(doc,'', 'possibilityModals')/len(doc)
    F57 = 0 # ["conjuncts", \&dummyFunction, "w"],
    F58 = 0 # ["past participial clauses", \&dummyFunction, "s"],
    F59 = 0 # ["BY-passives", \&dummyFunction, "s"],
    F60 = 0 # ["other adverbial subordinators", \&dummyFunction, "s"],
    f61=0 #\&predicativeAdjectives
    F62 = 0 # ["type/token ratio", \&dummyFunction, "d"],
    F63 = 0 # ["THAT clauses as verb complements", \&dummyFunction, "s"],
    f64=0 #\&demonstrativePronouns
    F65 = 0 # ["THAT relative clauses on object positions", \&dummyFunction, "s"],
    F66 = 0 # ["THAT clauses as adjective complements", \&dummyFunction, "s"],
    F67 = 0 # ["final prepositions", \&dummyFunction, "s"],
    F68 = 0 # ["existential THERE", \&simplePartsOfSpeech, "w", "EX"],
    F69 = 0 # ["demonstrative pronouns", \&demonstrativePronouns, "s"],
    F70 = 0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
    F71 = 0 # ["phrasal coordination", \&dummyFunction, "s"],
    f72=posWithLemmaFilter(doc,'', 'seemappear')/len(doc)
    f73=posWithLemmaFilter(doc,'', 'downtopers')/len(doc)
    F74 = 0 # ["concessive subordination", \&dummyFunction, "s"]);

    # return [f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f15,f17,f19,f20,f22,f23,f24,f26,f28,f31,f35,f36,f38,f47,f48,f51,F52,f54,f56,f72,f73]
    return [f6,f12,f23,f47]

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
    out['specialVerbs']=set.union(out['publicVerbs'],out['privateVerbs'],out['suasiveVerbs'])
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

print('\t'.join(['"'+d+'"' for d in dimlist]),file=fout)
if args.verbosity>1:
    print('total %d dims in the header' % len(dimlist),file=sys.stderr)

for line in f:
    doc=line.strip().lower().split()
    dims=getbiberdims(doc)
    print('\t'.join(['%.5f' % d for d in dims]),file=fout)
if args.verbosity>2:
    print('total %d dims in output' % len(dims),file=sys.stderr)
