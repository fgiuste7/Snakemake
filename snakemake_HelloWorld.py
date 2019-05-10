# Felipe Giuste
# 5/10/2019
# Snakefile
# For Testing Snakemake

import glob, os

#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------
# Obtain sample names from input directory contents:
SAMPLES = [fname.split('/')[-1] for fname in glob.glob('./testdir/input/*')]
GOODBYES = expand("{sample}/goodbye/goodbye.txt", sample = SAMPLES)


#-------------------------------------------------------------------------------
# Rules
#-------------------------------------------------------------------------------
localrules: all, make_goodbyes

rule all:
    input: GOODBYES
    output: 
    shell:
        """
        echo "Hello World"
        """

rule make_goodbyes:
    input: "testdir/input/{sample}"
    output: "{sample}/goodbye/goodbye.txt"
    shell:
        """
        echo {wildcards.sample}
        echo {input}
        touch {output}
        """