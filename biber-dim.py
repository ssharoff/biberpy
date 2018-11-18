#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Copyright (C) 2017  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
'''
A script for collecting Biber-like features from one-line text collections and a dictionary.

Expanded from experiments in Intellitext

'''
import sys
import time
import argparse
import smallutils as ut

language='en'
dimnames={
    'f01' : 'privateVerbs',
    'f02' : 'thatDeletion',
    'f03' : 'contractions',
    'f04' : 'PresVerbs',
    'f05' : 'secondPersonPronouns',
    'f06' : 'doAsProVerb',
    'f07' : "negation",
    'f08' : 'demonstrativePronouns',
    'f09' : 'generalEmphatics',
    'f10' : 'firstPersonPronouns',
    'f11' : "itPronoun",
    'f12' : 'beAsMainVerb',
    'f13' : "causation",
#   'f14' : 0 # ["discourse particles", \&dummyFunction, "s"],
    'f15' : 'indefinitePronouns',
#   'f16' : 0 # ["general hedges", \&dummyFunction, "s"],
    'f17' : 'amplifiers',
#   'f18' : 0 # ["sentence relatives", \&dummyFunction, "s"],
    'f19' : 'whQuestions',
    'f20' : 'possibilityModals',
#   'f21' : 0 # ["non-phrasal coordination", \&dummyFunction, "s"],
    'f22' : 'whMarkers',
    'f23' : 'strandedPrepositions',
    'f24' : 'ADV',
#   'f25' : 0 # ["conditional subordination", \&dummyFunction, "s"],
    'f26' : "NOUN",
    'f27' : 'wordLength',
    'f28' : "ADP",
    'f29' : 'typeTokenRatio',
#   'f30' : 0 # attributiveAdjectives, "s"],
    'f31' : "placeAdverbials",
#   'f32' : 0 # ["agentless passives", \&dummyFunction, "s"],
#   'f33' : 0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
#   'f34' : 0 # ["present participial WHIZ deletions", \&dummyFunction, "s"],
    'f35' : 'PastVerbs',
    'f36' : 'thirdPersonPronouns',
#   'f37' : 0 # ["perfect aspect verbs", \&perfectAspect, "s"],
    'f38' : 'publicVerbs',
    'f39' : 'syntheticNegation',
#    'f40' : 'presentParticipialClauses',
#   'f41' :  0 # ["present tense verbs", \&dummyFunction, "w"],
#   'f42' :  0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
#   'f43' :  0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
#   'f44' :  0 # ["pied piping constructions", \&dummyFunction, "s"],
#   'f45' :  0 # ["WH relative clauses on subject positions", \&dummyFunction, "s"],
#   'f46' :  0 # ["phrasal coordination", \&dummyFunction, "s"],
    'f47' : 'nominalizations',
    'f48' : 'timeAdverbials',
#   'f49' :  0 # ["place adverbials", \&dummyFunction, "w"],
#   'f50' : 0 # \&infinitives
    'f51' : 'predictionModals',
    'f52' : 'suasiveVerbs',
#   'f53' : 0# ["conditional subordination", \&dummyFunction, "s"],
    'f54' : 'necessityModals',
#   'f55' :  0 # ["split auxiliaries", \&dummyFunction, "s"],
    'f56' : 'possibilityModals',
#   'f57' :  0 # ["conjuncts", \&dummyFunction, "w"],
#   'f58' :  0 # ["past participial clauses", \&dummyFunction, "s"],
#   'f59' :  0 # ["BY-passives", \&dummyFunction, "s"],
#   'f60' :  0 # ["other adverbial subordinators", \&dummyFunction, "s"],
    'f61' :  'predicativeAdjectives',
#   'f62' :  0 # ["type/token ratio", \&dummyFunction, "d"],
#   'f63' :  0 # ["THAT clauses as verb complements", \&dummyFunction, "s"],
#   'f64' : 0 #\&demonstrativePronouns
#   'f65' :  0 # ["THAT relative clauses on object positions", \&dummyFunction, "s"],
#   'f66' :  0 # ["THAT clauses as adjective complements", \&dummyFunction, "s"],
#   'f67' :  0 # ["final prepositions", \&dummyFunction, "s"],
#   'f68' :  0 # ["existential THERE", \&simplePartsOfSpeech, "w", "EX"],
#   'f69' :  0 # ["demonstrative pronouns", \&demonstrativePronouns, "s"],
#   'f70' :  0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
#   'f71' :  0 # ["phrasal coordination", \&dummyFunction, "s"],
    'f72' : 'seemappear',
    'f73' : 'downtopers'
#   'f74' :  0, # ["concessive subordination", \&dummyFunction, "s"]);
}
wordlists={}
taglist={}

frq0=0
lemma1=1
pos2=2
finepos3=3

def wordAt(w):
    #no fancy word structure at the moment
    #ideally we need a record containing the word form and its analysis 
    return w
def lemmaAt(w):
    try:
        out=taglist[w][lemma1]
    except:
        out=w
    return out
def posAt(w):
    try:
        out=taglist[w][pos2]
    except:
        out='PROPN'
    return out
def fineposAt(w):
    try:
        out=taglist[w][finepos3]
    except:
        out='_'
    return out
def isWordSet(w, type):
    return w in wordlists[type]
def isDemonstrativePronoun(doc, l):
    try:
        nextPos = posAt(doc[l+1])
        nextWord = wordAt(doc[l+1])
    except:
        nextPos = nextWord = ''
    if isWordSet(nextWord,'modalVerbs' ) or nextPos=='PRON' or isWordSet(nextWord, 'clausePunctuation') or nextWord=='and':
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
            nextWord = wordAt(doc[l+1])
            # First Biber prescription 
            if isDemonstrativePronoun(doc,l+1) or isWordSet(nextWord, 'subjectPronouns'):
                thatcount+=1
            else:
                nextPos = posAt(doc[l+1])
                posAfter = posAt(doc[l+2])
                lCounter=2
                # Second Biber prescription
                if nextPos=="PRON" or nextPos=="NOUN" and isWordSet(wordAt(doc[l+lCounter]), "modalVerbs"):
                    thatcount+=1
                else:
                    # Third and most complicated Biber prescription
                    if nextPos in ["ADJ","ADV","DET","PRON"]:
                        # This is the optional adjective
                        if posAfter=="ADJ":
                            lCounter+=1
                            posAfter = posAt(doc[l+lCounter])
                        # Then a noun
                        if posAfter=="NOUN":
                            lCounter += 1
                            # Then if there's an auxiliary we accept this one
                            if isWordSet(wordAt(doc[l+lCounter]), "modalVerbs"):
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
            if posAt(doc[doPosition+1])=='VERB' or (posAt(doc[doPosition+1]) in ['ADV','PART'] and posAt(doc[doPosition+2])=='VERB'):
                doCount+=-1
            else:
	        # Biber's other specification seems wrong, he says:
	        # 'punctuation WHP DO' implies a question but his WHP
	        # only includes who, whose and which. I think it should be
                # those four PLUS the whQuestions. Need to put in the prior
                # punctuation
                previousWord = wordAt(doc[doPosition-1])
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
            pos = posAt(doc[loc+1])
            if not pos in ["DET","ADJ","PRON","ADP"]:
                beCount+=-1
        except:
            beCount+=-1
    return beCount

def strandedPrepositions(doc):
    prepCount, prepPositions = simplePartsOfSpeech(doc, "ADP", "", True)
    for loc in prepPositions:
        try:
            nextWord = wordAt(doc[loc + 1])
            if not isWordSet(nextWord, 'clausePunctuation'):
                prepCount+=-1
        except:
            prepCount+=-1
    return prepCount;

def nominalizations(doc):
    nounCount, nounPositions = simplePartsOfSpeech(doc, "NOUN", "", True)
    nomCount=0
    for loc in nounPositions:
        lemma = lemmaAt(doc[loc])
        if lemma[-4:] in ['tion','ment','ness']:
            nomCount+=1
    return nomCount

def syntheticNegation(doc):
    noCount, noPositions = findLemmaInSentence(doc, '', 'notWord', True)
    for l in noPositions:
        pos = posAt(doc[l+1])
        nextWord = wordAt(doc[l+1])
        if not (pos in ['ADJ','NOUN'] and isWordSet(nextWord, 'quantifiers')):
            noCount+=-1
    nNCount, _ = findLemmaInSentence(doc, '', "neitherWord")
    noCount += nNCount
    return noCount;

def presentParticipialClauses(doc):
    ppCount, ppPositions = simplePartsOfSpeech(doc, "", "VerbForm=Ger", True)
    for l in ppPositions:
        try:
            w0 = wordAt(doc[l-1])
            if isWordSet(w0, 'clausePunctuation'):
                ppCount+=-1
        except:
            ppCount+=-1
    return ppCount

def predicativeAdjectives(doc):
    adjCount, adjPositions = simplePartsOfSpeech(doc, "ADJ", "", True)
    for l in adjPositions:
        try:
            previousLemma = lemmaAt(doc[l-1])
            nextPos = posAt(doc[l+1])
            if not (previousLemma=='be' and nextPos in ["ADJ","NOUN"]): 
                adjCount+=-1
        except:
            adjCount+=-1
    return adjCount

def wordLength(doc):
    totLength = 0
    wordCount = 0
    for w in doc:
        if not isWordSet(wordAt(w), 'clausePunctuation'):
            totLength += len(w)
            wordCount+=1
    return totLength / wordCount

def typeTokenRatio(doc):
    # Biber only looks at the first 400 words of each document 'to avoid 
    # skewing the results to give larger values for smaller documents'.
    biberLength = min(400,len(doc))
    seenBefore = {}
    tokenCounter = 0
    for w in doc[:biberLength]:
        if not isWordSet(wordAt(w), 'clausePunctuation'):
            tokenCounter+=1
            if not w in seenBefore:
                seenBefore[w] = 1
    return len(seenBefore)/tokenCounter

def getbiberdims(doc):
    '''
    processes document as a list of tokenised words
    '''
    dimlist={}
    dimlist['f01']=posWithLemmaFilter(doc,'VERB','privateVerbs')/len(doc)
    dimlist['f02']=thatDeletion(doc)/len(doc)
    dimlist['f03']=contractions(doc)/len(doc)
    f4,_=simplePartsOfSpeech(doc,"VERB","Tense=Pres")  # we'll have to delete the list first for division
    dimlist['f04']=f4/len(doc)
    dimlist['f05']=posWithLemmaFilter(doc,'PRON','secondPersonPronouns')/len(doc)
    dimlist['f06']=doAsProVerb(doc)/len(doc)
    dimlist['f07']=posWithLemmaFilter(doc,'', "notWord")/len(doc)
    dimlist['f08']=demonstrativePronouns(doc)/len(doc)
    dimlist['f09']=posWithLemmaFilter(doc,'','generalEmphatics')/len(doc)
    dimlist['f10']=posWithLemmaFilter(doc,'','firstPersonPronouns')/len(doc)
    dimlist['f11']=posWithLemmaFilter(doc,'',"itWord")/len(doc)
    dimlist['f12']=beAsMainVerb(doc)/len(doc)
    dimlist['f13']=posWithLemmaFilter(doc,'',"becauseWord")/len(doc)
    #dimlist['f14']=0 # ["discourse particles", \&dummyFunction, "s"],
    dimlist['f15']=posWithLemmaFilter(doc,'','indefinitePronouns')/len(doc)
    #dimlist['f16']=0 # ["general hedges", \&dummyFunction, "s"],
    dimlist['f17']=posWithLemmaFilter(doc,'','amplifiers')/len(doc)
    #dimlist['f18']=0 # ["sentence relatives", \&dummyFunction, "s"],
    dimlist['f19']=posWithLemmaFilter(doc,'','whQuestions')/len(doc)
    dimlist['f20']=posWithLemmaFilter(doc,'','possibilityModals')/len(doc)
    #dimlist['f21']=0 # ["non-phrasal coordination", \&dummyFunction, "s"],
    dimlist['f22']=posWithLemmaFilter(doc,'','whMarkers')/len(doc)
    dimlist['f23']=strandedPrepositions(doc)/len(doc)
    f24,_=simplePartsOfSpeech(doc,"ADV")
    dimlist['f24']=f24/len(doc)
    #dimlist['f25']=(0 # ["conditional subordination", \&dummyFunction, "s"],
    f26,_=simplePartsOfSpeech(doc, "NOUN")
    dimlist['f26']=f26/len(doc)
    dimlist['f27']=wordLength(doc)
    f28,_=simplePartsOfSpeech(doc, "ADP")
    dimlist['f28']=f28/len(doc)
    dimlist['f29']=typeTokenRatio(doc)
    #dimlist['f30']=(0 # attributiveAdjectives, "s"],
    dimlist['f31']=posWithLemmaFilter(doc,'', "placeAdverbials")/len(doc)
    #dimlist['f32']=0 # ["agentless passives", \&dummyFunction, "s"],
    #dimlist['f33']=0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
    #dimlist['f34']=0 # ["present participial WHIZ deletions", \&dummyFunction, "s"],
    f35,_=simplePartsOfSpeech(doc, "VERB", "Tense=Past")
    dimlist['f35']=f35/len(doc)
    dimlist['f36']=posWithLemmaFilter(doc,'','thirdPersonPronouns')/len(doc)
    #dimlist['f37']=(0 # ["perfect aspect verbs", \&perfectAspect, "s"],
    dimlist['f38']=posWithLemmaFilter(doc,'','publicVerbs')/len(doc)
    dimlist['f39']=syntheticNegation(doc)/len(doc)
    #dimlist['f40']=presentParticipialClauses(doc)/len(doc)
    #dimlist['f41']= 0 # ["present tense verbs", \&dummyFunction, "w"],
    #dimlist['f42']= 0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
    #dimlist['f43']= 0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
    #dimlist['f44']= 0 # ["pied piping constructions", \&dummyFunction, "s"],
    #dimlist['f45']= 0 # ["WH relative clauses on subject positions", \&dummyFunction, "s"],
    #dimlist['f46']= 0 # ["phrasal coordination", \&dummyFunction, "s"],
    dimlist['f47']=nominalizations(doc)/len(doc)
    dimlist['f48']=posWithLemmaFilter(doc,'','timeAdverbials')/len(doc)
    #dimlist['f49']= 0 # ["place adverbials", \&dummyFunction, "w"],
    #dimlist['f50']=0 # \&infinitives
    dimlist['f51']=posWithLemmaFilter(doc,'','predictionModals')/len(doc)
    dimlist['f52']=posWithLemmaFilter(doc,'','suasiveVerbs')/len(doc)
    #dimlist['f53']=0# ["conditional subordination", \&dummyFunction, "s"],
    dimlist['f54']=posWithLemmaFilter(doc,'','necessityModals')/len(doc)
    #dimlist['f55']= 0 # ["split auxiliaries", \&dummyFunction, "s"],
    dimlist['f56']=posWithLemmaFilter(doc,'','possibilityModals')/len(doc)
    #dimlist['f57']= 0 # ["conjuncts", \&dummyFunction, "w"],
    #dimlist['f58']= 0 # ["past participial clauses", \&dummyFunction, "s"],
    #dimlist['f59']= 0 # ["BY-passives", \&dummyFunction, "s"],
    #dimlist['f60']= 0 # ["other adverbial subordinators", \&dummyFunction, "s"],
    dimlist['f61']=predicativeAdjectives(doc)/len(doc)
    #dimlist['f62']= 0 # ["type/token ratio", \&dummyFunction, "d"],
    #dimlist['f63']= 0 # ["THAT clauses as verb complements", \&dummyFunction, "s"],
    #dimlist['f64']=0 #\&demonstrativePronouns
    #dimlist['f65']= 0 # ["THAT relative clauses on object positions", \&dummyFunction, "s"],
    #dimlist['f66']= 0 # ["THAT clauses as adjective complements", \&dummyFunction, "s"],
    #dimlist['f67']= 0 # ["final prepositions", \&dummyFunction, "s"],
    #dimlist['f68']= 0 # ["existential THERE", \&simplePartsOfSpeech, "w", "EX"],
    #dimlist['f69']= 0 # ["demonstrative pronouns", \&demonstrativePronouns, "s"],
    #dimlist['f70']= 0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
    #dimlist['f71']= 0 # ["phrasal coordination", \&dummyFunction, "s"],
    dimlist['f72']=posWithLemmaFilter(doc,'','seemappear')/len(doc)
    dimlist['f73']=posWithLemmaFilter(doc,'','downtopers')/len(doc)
    #dimlist['f74']= 0, # ["concessive subordination", \&dummyFunction, "s"]);

    return dimlist

def readwordlists(f):
    '''
    reads lists in the format
    firstPersonPronouns = I,we,me,us,my,our,myself,ourselves
    '''
    out={}
    for i,line in enumerate(f):
        x=line.strip().split(' = ')
        if len(x)==2:
            out[x[0]]=set([w.strip() for w in x[1].split(',')])
        else:
            if ut.verbosity>0 and len(line)>1:
                print('Error in line %i, %s' % (i,line), file=sys.stderr)
    if ut.verbosity>1:
        print('Read total %d classes' % len(out), file=sys.stderr)
        print(sorted(out.keys()), file=sys.stderr)
    out['specialVerbs']=set.union(out['publicVerbs'],out['privateVerbs'],out['suasiveVerbs'])
    out['modalVerbs']=set.union(out['possibilityModals'],out['necessityModals'],out['predictionModals'])
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
parser.add_argument('-1', '--embeddings', type=str, help='embeddings, not added yet')
parser.add_argument('-t', '--testfile', type=str, help='one-doc-per-line corpus')
parser.add_argument('-o', '--outfile', type=str, default='-', help='output file')
parser.add_argument('-l', '--language', type=str, default='en', help='language id for getting the annotation files')

parser.add_argument('-v', '--verbosity', type=int, default=1)

args = parser.parse_args()
ut.verbosity=args.verbosity
language=args.language

f=sys.stdin if args.testfile=='-' else ut.myopen(args.testfile)
fout=sys.stdout if args.outfile=='-' else open(args.outfile,"w")

wordlists = readwordlists(open(language+'.properties'))
taglist= readnumlist(open(language+'.tag.num'))
if args.verbosity>0:
    print('Loaded %d words from %s' % (len(taglist), language+'.tag.num'), file=sys.stderr)

if args.embeddings:
    embeddings,w2i=ut.read_embeddings(args.embeddings)

print('\t'.join([d+'.'+dimnames[d] for d in sorted(dimnames)]),file=fout)
if args.verbosity>1:
    print('total %d dims in output' % len(dimnames),file=sys.stderr)

starttime=time.time()
for i,line in enumerate(f):
    doc=line.strip().lower().split()
    dims=getbiberdims(doc)
    print('\t'.join(['%.5f' % dims[d] for d in sorted(dimnames)]),file=fout)
if args.verbosity>0:
    print('Processed %d files in %d sec' % (i, time.time()-starttime),file=sys.stderr)
