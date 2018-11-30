#!/usr/bin/Rscript
# a simple script for providing a summary of a dataset
args=commandArgs(trailingOnly=T);
header = 0;
if (length(args)>1) {
    header = 1;
}
x=read.table(args[1],header=header);

print(dim(x));
print(summary(x));

