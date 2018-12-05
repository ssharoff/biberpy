#!/usr/bin/Rscript
1# an expanded R script for Biber-like processing from Intellitext

library(ggfortify)
library(stats)
library(cluster)


args=commandArgs(trailingOnly=T);
print(paste('Loading the source table',args[1]));
bd=read.table(args[1],header=1); # args=c('brown-biber.dat','brown-annot.dat');
d = dim(bd);
kfactors=5; # number of factors
topN=20; # number of features saved per factor
desc=bd; # no descriptions
flabels=sprintf("%d",seq(1,d[1]));
textclass=rep('unk',d[1])
colourcat=NULL;
if (length(args)>1) {
    print(paste('Loading the annotation table',args[2]));
    desc=read.table(args[2],header=1,row.names=3); 
    flabels=row.names(desc);
    textclass=desc[,1];
    colourcat='Top';
    if (length(args)>2) {
        colourcat=args[3];
    }
}
ROUTFILE=paste('loadings',args[1],sep='-');
cat('# Loadings for factors\n', file=ROUTFILE)

d.factanal <- factanal(bd, factors = kfactors, scores = 'regression')
pdf(paste('plots',args[1],'pdf',sep='.'));
autoplot(d.factanal, data = desc, x=1, y=2, colour = colourcat);
autoplot(d.factanal, data = desc, x=2, y=3, colour = colourcat);
autoplot(d.factanal, data = desc, x=3, y=4, colour = colourcat);
autoplot(d.factanal, data = desc, x=4, y=5, colour = colourcat);
autoplot(clara(d.factanal$scores,6), data = desc, frame = TRUE, colour = colourcat)  #, frame.type = 'norm'
dev.off();

bdout=data.frame(d.factanal$scores, textclass)
rownames(bdout) <- flabels;
write.table(bdout,file=paste('out',args[1],sep='-'))

for (i in c(1:kfactors)) { #   i=1;
    print(i)
    dimension = d.factanal$loadings[,i]
    dimension = dimension[order(-abs(dimension))]; #dimension1[1:4]
    cat(paste('Factor',i,'=',sep=''), file=ROUTFILE, append=TRUE);
    for (name in names(dimension[1:topN])) {
        cat(sprintf("%+1.4f*%s ", dimension[name], name), file=ROUTFILE, append=TRUE)
    }
    cat('\n', file=ROUTFILE, append=TRUE);
}

