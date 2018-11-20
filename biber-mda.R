#!/usr/bin/Rscript
# This is the template R script for Biber-like processing from Intellitext

args=commandArgs(trailingOnly=T);
bd=read.table(args[1],header=1); # args=c('brown-biber.dat','brown-annot.dat');
d = dim(bd)
annot=0; # to test we loaded it or not
flabels=sprintf("%d",seq(1,d[1]));
textclass=rep('unk',d[1])
if (length(args)>1) {
    annot=read.table(args[2],header=1,row.names=3); 
    flabels=row.names(annot);
    textclass=annot[,1]
}
bd.pr = prcomp(bd)

# We deal with the first five dimensions
bdout=data.frame(bd.pr$x[,1:5], textclass)
row.names(bdout) <- flabels
write.table(bdout,file=paste('out',args[1],sep='-'))

for i in c(1:5) {
    i=1;
    dimension = bd.pr$rotation[,i];
    dimension = dimension[order(-abs(dimension))]; #dimension[1:3]
    write(dimension[1:10],file=paste('dims',i,args[1],sep='-'))
}
