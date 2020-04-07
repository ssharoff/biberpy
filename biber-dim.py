#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Copyright (C) 2017  Serge Sharoff
# This program is free software under GPL 3, see http://www.gnu.org/licenses/
'''
A script for collecting Biber-like features from one-line text collections and a dictionary.

Expanded from experiments in Intellitext

'''
import sys, os
import time
import argparse
import json
import smallutils as ut
import ahocorasick # to apply MWEs to a string

language='en'
dimnames={
    'A01' : "pastVerbs",
    'A03' : "presVerbs",
    'B04' : "placeAdverbials",
    'B05' : 'timeAdverbials',
    'C06' : '1persProns',
    'C07' : '2persProns',
    'C08' : '3persProns',
    'C09' : 'impersProns',
    'C10' : 'demonstrProns',
    'C11' : 'indefProns',
    'C12' : 'doAsProVerb',
    'D13' : 'whQuestions',
    'E14' : "nominalizations",
    'E16' : "Nouns",
    'F18' : "BYpassives",
    'G19' : "beAsMain",
    'H23' : "WHclauses",
    'H25' : "presPartClaus",
    'H33' : "piedPiping",
    'H34' : "sncRelatives",
    'H35' : "causative",
    'H36' : 'concessives',
    'H37' : 'conditional',
    'H38' : 'otherSubord',
    'I39' : "preposn",
    'I40' : "attrAdj",
    'I41' : "predAdj",
    'I42' : "ADV",
    'J43' : 'TTR',
    'J44' : 'wordLength',
    'K45' : 'conjuncts',
    'K46' : 'downtoners',
    'K47' : 'generalHedges',
    'K48' : 'amplifiers',
    'K49' : 'generalEmphatics',
    'K50' : 'discoursePart',
    'K55' : 'publicVerbs',
    'K56' : 'privateVerbs',
    'K57' : 'suasiveVerbs',
    'K58' : 'seemappear',
    'L52' : 'possibModals',
    'L53' : 'necessModals',
    'L54' : 'predicModals',
    'N59' : "contractions",
    'N60' : "thatDeletion",
    'N61' : "strandedPrep",
    'P66' : "syntNegn",
    'P67' : "analNegn"
}

wordlists={}
taglist={}
mwelist={}

doc=[]
docstring=''

# structure of the frequency list
frq0=0
lemma1=1
pos2=2
finepos3=3

# json record is a list: [wform,lemma,POS,fine-grained]
def wordAt(w):
    if isinstance(w,str):
        return w
    elif isinstance(w,list):
        return w[0].lower()
def lemmaAt(w):
    if isinstance(w,str):
        try:
            out=taglist[w][lemma1]
        except:
            out=w
    elif isinstance(w,list):
        out=w[1]
    return out
def posAt(w):
    if isinstance(w,str):
        try:
            out=taglist[w][pos2]
        except:
            out='PROPN'
    elif isinstance(w,list):
        out=w[2]
    return out
def fineposAt(w):
    if isinstance(w,str):
        try:
            out=taglist[w][finepos3]
        except:
            out='_'
    elif isinstance(w,list):
        out=w[3]
    return out

def isWordSet(w, type):
    return w in wordlists[type]

def findLemmaInSentence(doc, pos, ftclass, getloc=False): # the last parameter is for providing locations
    count=0
    out=[]
    for i,w in enumerate(doc):
        if (pos=='' or posAt(w)==pos) and lemmaAt(w) in wordlists[ftclass]:
            #found in single words
            count+=1
            if getloc:
                out.append(i)
    if ftclass in mwelist:
        A=mwelist[ftclass]
        for end_index, (insert_order, original_value) in A.iter(docstring):
            count+=1

    return count, out

def posWithLemmaFilter(doc, pos, ftclass):
    count, _ = findLemmaInSentence(doc, pos, ftclass)
    return count

def simplePartsOfSpeech(doc, pos, finepos='', getloc=False):
    count=0
    out=[]
    for i,w in enumerate(doc):
        mainposTrue=not pos or posAt(w)==pos
        fineposTrue=not finepos or (fineposAt(w).find(finepos)>=0)
        if mainposTrue and fineposTrue:
            count+=1
            if getloc:
                out.append(i)
    return count, out

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
        if wordAt(w).find("'")>=0:
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
        if (language=='en' and lemma[-4:] in ['tion','ment','ness', 'ism']) or\
           (language=='en' and lemma[-3:] in ['ism']) or\
           (language=='es' and lemma[-3:] in ['ión','nto','leo', 'cia', 'dad']) or\
           (language=='fr' and lemma[-3:] in ['ion', 'ent','ité', 'eté','nce', 'loi']) or\
           (language=='ru' and lemma[-3:] in ['ция','сть','ние','тие','тво']):
            nomCount+=1
    return nomCount

def conjuncts(doc):
    singleWords=posWithLemmaFilter(doc,'','conjunctsSingle')
    MWEs=0 #'conjunctsMWE'
    pCount=0
    # punctuation+else, punctuation+altogether, punctuation+rather
    pCount, pPositions = findLemmaInSentence(doc, '', 'beVerb', True);
    for loc in pPositions:
        try:
            prevPos = posAt(doc[loc-1])
            if not prevPos=="PUNCT":
                pCount+=1
        except:
            pCount+=1
    
    return singleWords+MWEs+pCount

def BYpassives(doc): # for English and Russian at the moment
    vCount, vPositions = simplePartsOfSpeech(doc, "", "Voice=Pass", True)
    passCount=0
    for loc in vPositions:
        try:
            nextWord = lemmaAt(doc[loc+1])
            if (language=='en' and nextWord=='by') :
                passCount+=1
            elif (language=='ru'):
                found=False
                for locIns in range(loc+2,loc-2):
                    finepos=fineposAt(doc[locIns])
                    if finepos.find('Case=Ins')>=0:
                        found=True
                        break
                if found:
                    passCount+=1
        except: # do nothing
            passCount+=1
    return passCount

def syntheticNegation(doc):
    noCount, noPositions = findLemmaInSentence(doc, '', 'notWord', True)
    for l in noPositions:
        try:
            pos = posAt(doc[l+1])
            nextWord = wordAt(doc[l+1])
            if not (pos in ['ADJ','NOUN'] and isWordSet(nextWord, 'quantifiers')):
                noCount+=-1
        except:
            noCount+=-1
    nNCount, _ = findLemmaInSentence(doc, '', "neitherWord")
    noCount += nNCount
    return noCount;

def osubordinators(doc):
    dCount, _ = findLemmaInSentence(doc, '', "osubordinators")
    return dCount

def discourseParticles(doc):
    dCount, dPositions = findLemmaInSentence(doc, '', 'discourseParticles', True)
    for l in dPositions:
        try:
            prevPos = posAt(doc[l-1])
            if not pos=='PUNCT':
                dCount+=-1
        except: #do nothing, we're at the begging of a document
            dCount+=0
    return dCount;

def presentParticipialClauses(doc):
    ppCount, ppPositions = simplePartsOfSpeech(doc, "VERB", "VerbForm=Ger", True)
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
            if not (isWordSet(previousLemma,'beVerb') and nextPos in ["ADJ","NOUN"]): 
                adjCount+=-1
        except:
            adjCount+=-1
    return adjCount

def piedPiping(doc):
    whCount, whPositions = findLemmaInSentence(doc, "", "piedPiping", True)
    for l in whPositions:
        try:
            prevPos = posAt(doc[l-1])
            if not prevPos=="ADP": 
                whCount+=-1
        except:
            whCount+=-1
    return whCount

def wordLength(doc):
    totLength = 0
    wordCount = 0
    for w in doc:
        word=wordAt(w)
        if not isWordSet(word, 'clausePunctuation'):
            totLength += len(word)
            wordCount+=1
    return totLength / (wordCount+0.000001)

def typeTokenRatio(doc):
    # Biber only looks at the first 400 words of each document 'to avoid 
    # skewing the results to give larger values for smaller documents'.
    biberLength = min(400,len(doc))
    seenBefore = {}
    tokenCounter = 0
    for w in doc[:biberLength]:
        if not isWordSet(wordAt(w), 'clausePunctuation'):
            tokenCounter+=1
            if not lemmaAt(w) in seenBefore:
                seenBefore[lemmaAt(w)] = 1
    return len(seenBefore)/(tokenCounter+0.000001)

def getbiberdims(doc):
    '''
    processes each document as a list of tokenised words
    '''
    dimlist={}
    normalise=len(doc)+0.000001
    dimlist['A01']=simplePartsOfSpeech(doc, "VERB", "Tense=Past")[0]/normalise
    #dimlist['A02']=(0 # ["perfect aspect verbs", \&perfectAspect, "s"],
    dimlist['A03']=simplePartsOfSpeech(doc,"VERB","Tense=Pres")[0]/normalise
    
    dimlist['B04']=posWithLemmaFilter(doc,'', "placeAdverbials")/normalise
    dimlist['B05']=posWithLemmaFilter(doc,'','timeAdverbials')/normalise
    
    dimlist['C06']=posWithLemmaFilter(doc,'','firstPersonPronouns')/normalise
    dimlist['C07']=posWithLemmaFilter(doc,'PRON','secondPersonPronouns')/normalise
    dimlist['C08']=posWithLemmaFilter(doc,'','thirdPersonPronouns')/normalise
    dimlist['C09']=posWithLemmaFilter(doc,'',"itWord")/normalise # impersonal
    dimlist['C10']=demonstrativePronouns(doc)/normalise
    dimlist['C11']=posWithLemmaFilter(doc,'','indefinitePronouns')/normalise
    dimlist['C12']=doAsProVerb(doc)/normalise
    
    dimlist['D13']=posWithLemmaFilter(doc,'','whQuestions')/normalise
    dimlist['E14']=nominalizations(doc)/normalise
    #gerund list missing
    dimlist['E16']=(simplePartsOfSpeech(doc, "NOUN")[0]/normalise)-dimlist['E14'] # we substract nominalizations
    
    #dimlist['F17']=0 # ["agentless passives", \&dummyFunction, "s"],
    dimlist['F18']= BYpassives(doc)/normalise # to debug

    dimlist['G19']=beAsMainVerb(doc)/normalise
    #dimlist['G20']= 0 # ["existential THERE", \&simplePartsOfSpeech, "w", "EX"],
    
    #dimlist['H21']=that verb complements
    #dimlist['H22']= 0 # ["THAT clauses as adjective complements", \&dummyFunction, "s"], # I'm glad that you like it
    dimlist['H23']= posWithLemmaFilter(doc,'','whMarkers')/normalise
    #dimlist['H24']=infinitives(doc)/normalise #simplePartsOfSpeech(doc,"VERB","VerbForm=Inf")[0]/normalise # + to
    dimlist['H25']=presentParticipialClauses(doc)/normalise
    #dimlist['H26']= 0 # ["past participial clauses", \&dummyFunction, "s"],
    #dimlist['H27']=0 # ["past participial WHIZ deletions", \&dummyFunction, "s"],
    #dimlist['H28']=0 # ["present participial WHIZ deletions", \&dummyFunction, "s"],
    #dimlist['H30']= 0 # ["THAT relative clauses on object positions", \&dummyFunction, "s"],
    #dimlist['H31']= 0 # ["WH relative clauses on subject positions", \&dummyFunction, "s"],
    #dimlist['H32']= 0 # ["WH relative clauses on object positions", \&dummyFunction, "s"],
    dimlist['H33']= piedPiping(doc)/normalise # the manner in which he was told
    dimlist['H34']=posWithLemmaFilter(doc,'',"sentenceRelatives")/normalise # Bob likes fried mangoes, which is the most disgusting
    dimlist['H35']=posWithLemmaFilter(doc,'',"becauseWord")/normalise
    dimlist['H36']=posWithLemmaFilter(doc,'','concessives')/normalise
    dimlist['H37']=posWithLemmaFilter(doc,'','conditionalSubordination')/normalise
    dimlist['H38']= osubordinators(doc)/normalise
    
    dimlist['I39']=simplePartsOfSpeech(doc, "ADP")[0]/normalise
    dimlist['I41']=predicativeAdjectives(doc)/normalise
    dimlist['I40']=(simplePartsOfSpeech(doc, "ADJ")[0]/normalise)-dimlist['I41']
    dimlist['I42']=simplePartsOfSpeech(doc,"ADV")[0]/normalise
    
    dimlist['J43']=typeTokenRatio(doc)
    dimlist['J44']=wordLength(doc)

    dimlist['K45']=conjuncts(doc)/normalise
    dimlist['K46']=posWithLemmaFilter(doc,'','downtopers')/normalise
    dimlist['K47']=posWithLemmaFilter(doc,'','generalHedges')/normalise
    dimlist['K48']=posWithLemmaFilter(doc,'','amplifiers')/normalise
    dimlist['K49']=posWithLemmaFilter(doc,'','generalEmphatics')/normalise
    dimlist['K50']=discourseParticles(doc)/normalise
    #dimlist['K51']= demonstratives /that/this/these/those/ excluding pronouns

    dimlist['L52']=posWithLemmaFilter(doc,'','possibilityModals')/normalise
    dimlist['L53']=posWithLemmaFilter(doc,'','necessityModals')/normalise
    dimlist['L54']=posWithLemmaFilter(doc,'','predictionModals')/normalise

    dimlist['K55']=posWithLemmaFilter(doc,'VERB','publicVerbs')/normalise
    dimlist['K56']=posWithLemmaFilter(doc,'VERB','privateVerbs')/normalise
    dimlist['K57']=posWithLemmaFilter(doc,'','suasiveVerbs')/normalise
    dimlist['K58']=posWithLemmaFilter(doc,'','seemappear')/normalise
    
    dimlist['N59']=contractions(doc)/normalise
    dimlist['N60']=thatDeletion(doc)/normalise

    dimlist['N61']=strandedPrepositions(doc)/normalise
    #dimlist['N62']= 0 # ["split infinitives", \&dummyFunction, "s"],
    #dimlist['N63']= 0 # ["split auxiliaries", \&dummyFunction, "s"],
    
    #dimlist['O64']=0 # ["phrasal coordination", \&dummyFunction, "s"],
    #dimlist['O65']=0 # ["independent clause coordination", \&dummyFunction, "s"],

    dimlist['P66']=syntheticNegation(doc)/normalise
    dimlist['P67']=posWithLemmaFilter(doc,'', "notWord")/normalise

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
            values = x[1].split(',')
            out[x[0]]=set([w.strip() for w in values])
            A = ahocorasick.Automaton()  #separately add an automaton structure for finding MWEs
            mwecur=[]
            for mwe in values:  
                mwe=mwe.strip()
                if mwe.find(' ')>0:
                    mwecur.append(mwe.lower())
            if len(mwecur)>0:
                for idx, key in enumerate(set(mwecur)):
                    A.add_word(key, (idx, key))
                A.make_automaton()
                mwelist[x[0]]=A
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

parser = argparse.ArgumentParser(description="Multilingual Biber-like tagger")
parser.add_argument('-1', '--embeddings', type=str, help='embeddings, not implemented yet')
parser.add_argument('-f', '--format', type=str, default='ol', help='either ol (default) or json output by conll2json.py')
parser.add_argument('-l', '--language', type=str, default='en', help='language id for getting the annotation files')
parser.add_argument('-s', '--suppressheader', action='store_true', help='suppresses the default feature header')
parser.add_argument('-v', '--verbosity', type=int, default=1)
parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='one-doc-per-line corpus, plain or json')
parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='output file')

args = parser.parse_args()
ut.verbosity=args.verbosity
language=args.language
dirname=os.path.dirname(os.path.realpath(__file__))
assert args.format in ['ol','json'], 'Wrong format, either ol or json is accepted. Requested: '+args.format

wordlists = readwordlists(open(dirname+'/'+language+'.properties'))
if args.format=='ol':
    taglist= readnumlist(open(dirname+'/'+language+'.tag.num'))
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
    dims=getbiberdims(doc)
    print('\t'.join(['%.5f' % dims[d] for d in sorted(dimnames)]),file=args.outfile)
if args.verbosity>0:
    print('Processed %d files in %d sec' % (i+1, time.time()-starttime),file=sys.stderr)
