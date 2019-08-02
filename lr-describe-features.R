#!/usr/bin/Rscript
# a script for mapping Biber features to LR predictions for a label
library(caret)

args=commandArgs(trailingOnly=T); # args=c('ukwac-biber-sub.dat','ukwac-pred-sub.dat','__label__A1')
bibername=args[1]
predicname=args[2]
labelname=args[3]

c=read.table(bibername,header=1,nrows=500000); 
preC.model=preProcess(c, method = c("center", "scale"));
c=predict(preC.model,c);

desc=read.table(predicname,header=1,nrows=500000); 
flabels=rownames(desc);
textclass=desc[,1];

# print(table(textclass));

binary=(textclass==labelname)
print(labelname)
print(sum(binary))

glmLR=glm(binary~ .,data=c,family='binomial')
glm.out=summary(glmLR)
print(glm.out)
a.out=anova(glmLR, test = 'Chisq')
#save(c, desc, textclass, glmLR, glm.out, a.out, file=paste(args[2],args[3],'Rdat',sep='.'))
print(a.out)

#dev4=summary(a.out$Deviance)[5]
                                        #print(subset(a.out,a.out$Deviance>dev4))
print(head(a.out[order(-a.out$Deviance),],12));
x=glmLR$coefficients[rownames(head(a.out[order(-a.out$Deviance),],12),)]
print(x)
write.table(x,file=paste(labelname,'tsv',sep='.'))
#pA1=glm.out$coefficients[,4]  # p.values
# print(names(pA1[pA1<0.001]))
#print(glm.out$coefficients[which(pA1<0.001),1])

