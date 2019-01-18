#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import string, re
import numpy as np
from collections import defaultdict

verbosity = 1
#this only includes the ascii list:
#!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
punctuations = set(string.punctuation)
quotes=set('"“”‘’«»„“„”»«\'')
#the following is for regular expressions
punct=r'([\[\]\(\),.-/":<>”?“!»«‒‖–‗—‘―’‚‛„†‡‰‱′″‴‵‶‷‸‹›¡¿+\'|_’;%‘*=&°@ ~>§©])'

def myopen(fn, encoding='utf-8', errors='surrogateescape'):
    if fn.endswith('xz'):
        import lzma
        f= lzma.open(fn,"rt", encoding=encoding, errors=errors)
    elif fn.endswith('gz'):
        import gzip
        f= gzip.open(fn,"rt", encoding=encoding, errors=errors)
    else:
        f= open(fn, encoding=encoding, errors=errors)
    return(f)

def isfloat(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

def readfrqdict(dfile,limit=3000):
    '''
    reads a frequency list file:
    65819 the DET
     1263 Head PROPN
        9 Head ADJ
    only the first value for each headword is kept
    '''
    dictl={}
    frql={}
    i=0
    for l in open(dfile):
        i+=1
        match=re.match('\s*(\d+)\s+(.+)\s+(.+)',l)
        if match:
            frq=match.group(2)
            key=match.group(2)
            val=match.group(3)
            if (i<limit) and (not key in frql):
                frql[key]=frq
            elif (not key in dictl) and (not key in frql):
                dictl[key]=val
    return dictl, frql

def tokeniseall(s):
    return re.sub(punct,r' \1 ',s)

def mixedstr(l,dictl,frq):
    '''
    It outputs a mixed representation for a string: the words outside the frq list
    are replaced with their dictl codes (usually their POS)
    '''
    def convertword(w):
        wl=w.lower()
        if (wl in frq) or (wl[:9]=='__label__'):
            out=wl
        elif w[0].isdigit():
            out='[#]'
        elif wl in dictl:
            out=dictl[wl]
        elif w[0].isupper():
            out='PROPN'
        elif w[0].isalpha():
            out='NOUN'
        elif w[0] in quotes: # punctuation
            out='QUOTE'
        elif w[0] in punctuations: # punctuation
            out=w
        else: 
            out='RAREPUNCT'
        return(out)
    outdoc=[convertword(w) for w in tokeniseall(l.strip()).split()]
    return outdoc

def readtrain(filename, vocab_set, multilabel=0):
    '''
    reads annotated training sets in the format
    народных	ADJ-Inan-Gen-Plur
    народных	ADJ-Inan-Loc-Plur
    '''
    X=[]
    y=[]
    if multilabel:
        dict={}
    for line in open(filename):
        word, desc = line.strip().split("\t")
        if (not bool(vocab_set)) or (word in vocab_set):  # if the vocab set is known
            if multilabel:
                if word in dict:
                    y[dict[word]].append(desc)
                else:
                    X.append(word)
                    dict[word]=len(X)-1
                    y.append([desc])
            else:
                X.append(word)
                y.append(desc)
    return X, y

def readcosts(fn):
    """
       reading Levenshtein costs from fast_align output
    """
    cost={}
    for l in myopen(fn):
        [s,t,c]=l.split()
        cost[s+t]=1-2.7**float(c)
    return(cost)

def computecost(s,t,cost):
    """
       a simple backoff for Levenshtein character substitution costs
    """
    # if (s==t):
    #     cost = 0
    # el
    if (s+t) in cost.keys():
        cost = cost[s+t]
    else:
        cost = 1
    return(cost)


def iterative_levenshtein(s, t,cost):
    """ 
    dist[i,j] will contain the Levenshtein distance between the first i characters of s 
    and the first j characters of t
    Modified example from http://www.python-course.eu/levenshtein_distance.php
    """
    rows = len(s)+1
    cols = len(t)+1

    dist = [[0 for x in range(cols)] for x in range(rows)]
    # deletions for source prefixes
    for i in range(1, rows):
        dist[i][0] = i
    # insersions for target prefixes
    for i in range(1, cols):
        dist[0][i] = i
        
    for col in range(1, cols):
        for row in range(1, rows):
            dist[row][col] = min(dist[row-1][col] + computecost('<eps>',t[col-1],cost),  # deletion
                                 dist[row][col-1] + computecost(s[row-1],'<eps>',cost), # insertion
                                 dist[row-1][col-1] + computecost(s[row-1],t[col-1],cost)) # substitution

    return(dist[row][col]/max(cols,rows))

def getword(desc):
    return desc[desc.index('w:')+2:desc.index('~l:')]

def makemaps(descs):
    '''
    makes dictionaries of indices for words and complete descs like
    w:народных~l:народный~m:ADJ-Inan-Gen-Plur~e:ых~c:327 -0.45406 -0.21863
    w:народных~l:народный~m:ADJ-Inan-Loc-Plur~e:ых~c:327 0.12775 -0.20127
    by returning dictionaries with the words and descs to their position in the list
    '''
    desc2ind={}
    word2ind={}
    for i, desc in enumerate(descs):
        desc2ind[desc]=i
        word=getword(desc)
        if word in word2ind:
             word2ind[word].append(i)
        else:
            word2ind[word]=[i]
    return desc2ind, word2ind

def make_y(id2row,wlist,annot):
    '''
    it selects annotations for words in the embedding lexicon
    '''
    vocab=[]
    y=[]
    for i,w in enumerate(wlist):
        if w in id2row:
            vocab.append(w)
            y.append(annot[i])
    return vocab,y

class Space(object):

    def __init__(self, matrix_, id2row_):
        self.mat = matrix_
        self.id2row = id2row_
        self.create_row2id()

    def create_row2id(self):
        self.row2id = {}
        for idx, word in enumerate(self.id2row):
            if not word in self.row2id:
                #raise ValueError("Found duplicate word: %s" % (word))
                self.row2id[word] = idx

    @classmethod
    def build(cls, fname, lexicon=None, threshold=0, dim=0):
        #if a threshold is provided, we stop reading once it's reached
        #if a lexicon is provided, only words in the lexicon are loaded
        #if dim is provided, all spaces within MWEs are converted into ~
        id2row = []
        def filter_lines(f,ncols):
            for i,line in enumerate(f):
                x = line.split()
                xlen=len(x)
                word = '~'.join(x[0:xlen+1-ncols])
                
                if i != 0 and xlen>=ncols and (lexicon is None or word in lexicon) and (threshold==0 or i<threshold):
                    id2row.append(word)
                    word_length=len(word)
                    if (word_length>0):
                        yield line[word_length+1:]

        #get the number of columns
        if not dim:
            with myopen(fname,encoding='utf8') as f:
                f.readline()
                ncols = len(f.readline().split())
        else:
            ncols=dim+1
        with myopen(fname,encoding='utf8') as f:
            m = np.matrix(np.loadtxt(filter_lines(f,ncols),
                          comments=None, usecols=range(0,ncols-1)))

        return Space(m, id2row)

    def normalize(self):
        row_norms = np.sqrt(np.multiply(self.mat, self.mat).sum(1))
        row_norms = row_norms.astype(np.double)
        row_norms[row_norms != 0] = np.array(1.0/row_norms[row_norms != 0]).flatten()
        self.mat = np.multiply(self.mat, row_norms)

    def printmat(self):
        print('%d %d' % self.mat.shape)
        for i in range(len(self.id2row)):
            print(self.id2row[i] + ' ' + ' '.join(['%.5g' % x for x in self.mat[i].tolist()[0]]))

class expandabledict(dict):
    def __missing__(self, key):
        value = self[key] = len(self)()
        return value

def read_embeddings(emb_file, w2i=None, emb_size=300, vocab=None, threshold=0):
    if w2i is None: w2i = expandabledict() #defaultdict(lambda: len(w2i))
    embeddings = []
    with myopen(emb_file) as f:
        for i,line in enumerate(f):
            x = line.split()
            xlen=len(x)
            word = '~'.join(x[0:xlen-emb_size])
            if xlen>=emb_size and (vocab is None or word in vocab) and (threshold==0 or i<threshold) and not word in w2i:
                w2i[word] = len(w2i)
                embeddings.append(np.array(x[-emb_size:]))
    if vocab:
        if not '<unk>' in w2i:
            w2i['<unk>'] = len(w2i)
            embeddings.append(np.random.rand(emb_size)/emb_size) #np.zeros(emb_size))
        for word in vocab.difference(w2i): # for words missing in the embeddings, but present in the vocabulary
            w2i[word] = len(w2i)
            embeddings.append(np.random.rand(emb_size)/emb_size) #np.zeros(emb_size))
    embeddings = np.array(embeddings, dtype=np.float32)
    return(embeddings,w2i)
