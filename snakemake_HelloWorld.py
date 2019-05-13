# Felipe Giuste
# 5/10/2019
# Snakefile
# For Testing Snakemake

import glob, os

#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------
# Obtain sample names from input directory contents:
SAMPLES = [fname.split('/')[-1].split('.txt')[0] for fname in glob.glob('./testdir/input/*')]
GOODBYES = expand("testdir/{sample}/output/goodbye.txt", sample = SAMPLES)


#-------------------------------------------------------------------------------
# Rules
#-------------------------------------------------------------------------------
localrules: all, make_goodbyes

rule all:
    input: GOODBYES
    shell:
        """
        echo "Sleeping"
        sleep 20
        echo "Hello World"
        """

rule make_goodbyes:
    input: "testdir/input/{sample}.txt"
    output: "testdir/{sample}/output/goodbye.txt"
    shell:
        """
        echo {wildcards.sample}
        echo {input}
        sleep 20
        touch {output}
        """