# usually comes from a list brown corpus IDs
sed -r 's/^([A-C])/news\t\1\t\1/; s/^([DH])/misc\t\1\t\1/; s/^([EFG])/nonfiction\t\1\t\1/; s/^(J)/academ\t\1\t\1/; s/^([K-R])/fiction\t\1\t\1/;s/^"ID"/"Top"\t"Brown"\t"ID"/'
