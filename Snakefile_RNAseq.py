# Felipe Giuste
# 6/15/2016
# Snakefile
# For PE RNA-seq, STAR-Cufflinks-eXpress-RSEM Pipeline

from snakemake.utils import R
import glob
import os


#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------

# FOLDERS = [os.path.basename(fname).split('R1.fastq')[0] for fname in glob.glob('fastqs/*R1.fastq*')]

# Obtain sample names from directory names
SAMPLES = [fname.split('/')[1] for fname in glob.glob('./*/')]

BAMS = expand("{sample}/STARout/Aligned.sortedByCoord.out.bam", sample = SAMPLES)
BAI = expand("{sample}/STARout/Aligned.sortedByCoord.out.bam.bai", sample = SAMPLES)
QC = expand("{sample}/QC/{sample}.finito", sample = SAMPLES)
FPKM = expand("{sample}/CuffOut/isoforms.count_tracking", sample = SAMPLES)
EXPRESSCOUNTS = expand("{sample}/eXpress/results.xprs", sample = SAMPLES)
RSEMCOUNTS = expand("{sample}/RSem/Quant.isoforms.results", sample = SAMPLES)

ANNOTATION =    '/home/fgiuste/Annotations/Gencode_v21/gencode.v21.annotation.gtf'
ANNOTATIONFA =  '/home/fgiuste/Annotations/Gencode_v21/gencode.v21.annotation.fa'

GENOMEFA = '/home/fgiuste/Assemblies/GRCh38/GRCh38.genome.fa'
STARINDEX = '/home/fgiuste/Assemblies/GRCh38/STARindices/STARhg38' 
KALLISTOINDEX = '/home/fgiuste/Assemblies/GRCh38/KallistoIndices/Kallisto_hg38.idx' 
RSEMREFERENCE = "/home/fgiuste/Annotations/Gencode_v21/RSem/gencode21"

STAR = '/home/kpelle2/STAR-master/bin/Linux_x86_64_static/STAR'
FASTQC = '/home/fgiuste/Tools/FastQC/fastqc'
SAMTOOLS = '/home/fgiuste/Tools/SamTools/bin/samtools'
EXPRESS = '/home/fgiuste/Tools/express-1.5.1-linux_x86_64/express'
RSEM = '/home/fgiuste/Tools/RSEM-1.2.31/rsem-calculate-expression' 
RSEMPREPARE = '/home/fgiuste/Tools/RSEM-1.2.31/rsem-prepare-reference'
RSEMPLOT = '/home/fgiuste/Tools/RSEM-1.2.31/rsem-plot-model'

# STAR_VERSION = subprocess.check_output("{STAR} --version", shell=True)
# FASTQC_VERSION = subprocess.check_output("{FASTQC} --version", shell=True)
# SAMTOOLS_VERSION = subprocess.check_output("{FASTQC} --version", shell=True)
# CUFFLINKS_VERSION = subprocess.check_output("cufflinks --version", shell=True)
# GFFREAD_VERSION = subprocess.check_output("gffread --version", shell=True)
# EXPRESS_VERSION = subprocess.check_output("{EXPRESS} --version", shell=True)
# RSEM_VERSION = subprocess.check_output("{RSEM} --version", shell=True)

# getting tool versions (from: https://bitbucket.org/snakemake/snakemake/wiki/Documentation#markdown-header-version-tracking):
# SOMECOMMAND_VERSION = subprocess.check_output("somecommand --version", shell=True)

#-------------------------------------------------------------------------------
# Rules
#-------------------------------------------------------------------------------
localrules: all, show_samples, STARindexing, Star, FastQC, bamIndex, Cufflinks, gtfToFasta, eXpress, RSemReference, TranscriptomeBamSort, RSem

rule all:
    input:  BAI, QC, FPKM, RSEMCOUNTS
    version: "1.0"
    message: "Final samples: {}".format(SAMPLES)
    shell:  
        """
        echo Finito: `date`
        """

rule show_samples:
    run:
        print("Samples: {} with {} fastq files".format(SAMPLES, len(SAMPLES)))

rule STARindexing:
    input: GENOMEFA
    output: STARINDEX + "/chrStart.txt"
    threads: 32
    resources:
        mem_gb = 32
    log:
        ".STARindexing/logs/STARindexing.log"
    benchmark:
        ".STARindexing/benchmarks/STARindexing.benchmark"
    shell:  
        """
        {STAR} --runMode genomeGenerate --runThreadN {threads} --genomeDir {STARINDEX} --genomeFastaFiles {input} &> {log}
        echo "STARindexing completed successfully"
        """

# Aligns to genome, but knows transcriptome annotation
# Gene Counts from STAR Example: /moreno/160413_MovemberTMA/CMO11123/R031-1/MovSTAR/STARoutReadsPerGene.out.tab
rule Star:
    input:  idir = "{sample}/fastqs/",
            genome = STARINDEX + "/chrStart.txt",
            annotation = ANNOTATION
    output: GenomeAlignment = "{sample}/STARout/Aligned.sortedByCoord.out.bam",
            TranscriptomeAlignment = "{sample}/STARout/Aligned.toTranscriptome.out.bam",
            GeneCounts = "{sample}/STARout/ReadsPerGene.out.tab" # not very accurate. Only counts reads overlapping exlusively to one gene, minimum of 1bp overlap
    threads: 20
    resources:
        mem_gb = 32
    log:
        "{sample}/logs/Star.log"
    benchmark:
        "{sample}/benchmarks/Star.benchmark"
    shell:  
        """
        fastq1=`echo {input[idir]}/*R1*.fastq.gz | tr ' ' ,`
        fastq2=`echo {input[idir]}/*R2*.fastq.gz | tr ' ' ,`
        {STAR} --runThreadN {threads} --genomeDir {STARINDEX} --sjdbGTFfile {input[annotation]} --readFilesIn ${{fastq1}} ${{fastq2}} --readFilesCommand zcat --quantMode TranscriptomeSAM GeneCounts --outSAMtype BAM SortedByCoordinate --outFileNamePrefix {wildcards.sample}/STARout/ &> {log}
        echo "Star {wildcards.sample} completed successfully"
        """

### Include mapping quality control: Picard? ###

rule FastQC:
    input: "{sample}/fastqs/"
    output: "{sample}/QC/{sample}.finito"
    threads: 2
    resources:
        mem_gb = 16
    params:
        odir = "{sample}/QC/"
    log:
        "{sample}/logs/FastQC.log"
    benchmark:
        "{sample}/benchmarks/FastQC.benchmark"
    shell:
        """
        mkdir -p {params[odir]}
        {FASTQC} -o {params[odir]} {input}/*R1*.fastq.gz &> {log}
        {FASTQC} -o {params[odir]} {input}/*R2*.fastq.gz &> {log}
        touch {output}  &> {log}
        echo "FastQC {wildcards.sample} completed successfully"
        """

rule bamIndex:
    input: "{sample}/STARout/Aligned.sortedByCoord.out.bam"
    output: "{sample}/STARout/Aligned.sortedByCoord.out.bam.bai"
    threads: 2
    resources:
        mem_gb = 16
    log:
        "{sample}/logs/bamIndex.log"
    benchmark:
        "{sample}/benchmarks/bamIndex.benchmark"
    shell: 
        """
        {SAMTOOLS} index {input}  &> {log}
        echo "bamIndex {wildcards.sample} completed successfully"
        """

# http://www.nature.com/nprot/journal/v7/n3/full/nprot.2012.016.html
rule Cufflinks:
    input:  aligned = "{sample}/STARout/Aligned.sortedByCoord.out.bam",
            annotation = ANNOTATION
    output: expression = "{sample}/CuffOut/isoforms.count_tracking",
            annotation = "{sample}/CuffOut/transcripts.gtf"
    threads: 12
    resources:
        mem_gb = 32
    params:
        odir = "{sample}/CuffOut/"
    log:
        "{sample}/logs/cufflinks.log"
    benchmark:
        "{sample}/benchmarks/cufflinks.benchmark"
    shell: 
        """
        cufflinks -p {threads} -G {input[annotation]} --library-type fr-firststrand --output-dir {params[odir]} {input[aligned]} &> {log}
        echo "Cufflinks {wildcards.sample} completed successfully"
        """

# http://cole-trapnell-lab.github.io/cufflinks/file_formats/#the-gffread-utility
rule gtfToFasta:
    input:  annotation = ANNOTATION,
            genome = GENOMEFA
    output: ANNOTATIONFA
    threads: 2
    resources:
        mem_gb = 16
    log:
        ".gtfToFasta/logs/transcriptCounts.log"
    benchmark:
        ".gtfToFasta/benchmarks/transcriptCounts.benchmark"
    shell:
        """
        gffread -w {output} -g {input[genome]} {input[annotation]} &> {log}
        echo "gtfToFasta completed successfully"
        """

# http://bio.math.berkeley.edu/eXpress/manual.html
# express --fr-stranded -o MSA11033-PoolA3-27631708/eXpress/ /moreno/felipe/Annotations/Gencode_v21/gencode.v21.annotation.fa  MSA11033-PoolA3-27631708/STARout/Aligned.sortedByCoord.out.bam
# !! WARNING !! Not working with Star outputs
rule eXpress:
    input:  aligned = "{sample}/STARout/Aligned.sortedByCoord.out.bam",
            annotation = ANNOTATIONFA
    output: "{sample}/eXpress/results.xprs"
    threads: 4
    resources:
        mem_gb = 20
    params:
        odir = "{sample}/eXpress/"
    log:
        "{sample}/logs/eXpress.log"
    benchmark:
        "{sample}/benchmarks/eXpress.benchmark"
    shell:
        """
        {EXPRESS} --fr-stranded -o {params[odir]} {input[annotation]} {input[aligned]} &> {log}
        echo "eXpress {wildcards.sample} completed successfully"
        """

# https://github.com/ENCODE-DCC/long-rna-seq-pipeline/blob/master/DAC/STAR_RSEM_prep.sh
rule RSemReference:
    input:  annotation = ANNOTATION,
            assembly = GENOMEFA
    output: RSEMREFERENCE + ".idx.fa"
    threads: 4
    resources:
        mem_gb = 30
    log:
        ".RSemReference/logs/RSemReference.log"
    benchmark:
        ".RSemReference/benchmarks/RSemReference.benchmark"
    shell:
        """
        {RSEMPREPARE} --gtf {input[annotation]} {input[assembly]} {RSEMREFERENCE} &> {log}
        echo "RSemReference completed successfully"
        """

# Makes RSEM deterministic, but takes a very long time to sort bam file
rule TranscriptomeBamSort:
    input:  aligned = "{sample}/STARout/Aligned.toTranscriptome.out.bam"
    output: sortedTranscriptome = "{sample}/STARout/Aligned.toTranscriptome.out.sorted.bam"
    threads: 20
    resources:
        mem_gb = 60
    log:
        "{sample}/logs/TranscriptomeBamSort.log"
    benchmark:
        "{sample}/benchmarks/TranscriptomeBamSort.benchmark"
    shell:
        """
        cat <( {SAMTOOLS} view -H {input[aligned]} ) <( {SAMTOOLS} view -@ {threads} {input[aligned]} | awk '{{printf "%s", $0 " "; getline; print}}' | sort -S {resources[mem_gb]} -T ./ | tr ' ' '\n' ) | {SAMTOOLS} view -@ {threads} -bS - > {output[sortedTranscriptome]} &> {log}
        echo "TranscriptomeBamSort {wildcards.sample} completed successfully"
        """

# http://deweylab.biostat.wisc.edu/rsem/convert-sam-for-rsem.html
# rsem-sam-validator

# http://deweylab.github.io/RSEM/
# https://github.com/ENCODE-DCC/long-rna-seq-pipeline/blob/master/DAC/STAR_RSEM.sh
rule RSem:
    input:  aligned = "{sample}/STARout/Aligned.toTranscriptome.out.bam",
            reference = RSEMREFERENCE + ".idx.fa"
    output: "{sample}/RSem/Quant.isoforms.results"
    priority: 5 # max priority=50, default=1, higher priority=finish first
    threads: 12
    resources:
        mem_gb = 50
    log:
        "{sample}/logs/RSem.log"
    benchmark:
        "{sample}/benchmarks/RSem.benchmark"
    shell:
        """
        mem_mb=`python -c "print {resources[mem_gb]} * 1000"`
        {RSEM}  -p {threads} --ci-memory ${{mem_mb}} --paired-end --forward-prob 0 --bam --estimate-rspd --calc-ci --no-bam-output --seed 12345 {input[aligned]} {RSEMREFERENCE} {wildcards.sample}/RSem/Quant &> {log}
        echo "RSem {wildcards.sample} completed successfully"
        """

rule RSemPlotModel:
    input:  "{sample}/RSem/Quant.isoforms.results.isoforms.results"
    output: "{sample}/RSem/Quant.pdf"
    threads: 2
    resources:
        mem_gb = 30
    log:
        "{sample}/logs/RSemPlotModel.log"
    benchmark:
        "{sample}/benchmarks/RSemPlotModel.benchmark"
    shell:
        """
        {RSEMPLOT} {wildcards.sample}/RSem/Quant {sample}/RSem/Quant.pdf &> {log}
        echo "RSemPlotModel {wildcards.sample} completed successfully"
        """

rule KallistoIndex:
    input: ANNOTATIONFA
    output: KALLISTOINDEX
    threads: 2
    resources:
        mem_gb = 30
    log:
        ".KallistoIndex/logs/KallistoIndex.log"
    benchmark:
        ".KallistoIndex/benchmarks/KallistoIndex.benchmark"
    shell:
        """
        kallisto index -i {output} {input}} &> {log}
        echo "KallistoIndex completed successfully"
        """

rule Kallisto:
    input:  index = KALLISTOINDEX,
            idir = "{sample}/fastqs/"
    output: "{sample}/Kallisto/"
    threads: 2
    resources:
        mem_gb = 30
    log:
        "{sample}/logs/RSemPlotModel.log"
    benchmark:
        "{sample}/benchmarks/RSemPlotModel.benchmark"
    shell:
        """
        kallisto quant -i {input[index]} -o {output} -b 100 --fr-stranded reads_1.fastq.gz reads_2.fastq.gz        ########### Figure this out !!! #####
        echo "Kallisto {wildcards.sample} completed successfully"
        """

### May use txinport for gene level quantification (http://bioconductor.org/packages/release/bioc/html/tximport.html) ###

# To run:
# snakemake -n
# nohup snakemake --cores 24 --resources mem_gb=100 --rerun-incomplete --prioritize RSem &

# Installing python3:
# http://stackoverflow.com/questions/3239343/make-install-but-not-to-default-directories
# ./configure --prefix=/home/felipe/Tools/Python3
# make && make install
# install libraries in: /moreno/felipe/lib/python3.5
# pip3 install snakemake

# python setup.py install --prefix=/moreno/felipe/HTSeq/




# Copy STAR counts from /moreno
# for f in /moreno/160413_MovemberTMA/CMO11123/R031-*/MovSTAR/STARoutReadsPerGene.out.tab; do origin=$f; destination=/home/fgiuste/Data/Movember/`echo $f | cut -d '/' -f5 `/; mkdir $destination; cp $origin $destination; done
# for f in /moreno/160413_MovemberTMA/MSA11033/MSA11033-*/MovSTAR/STARoutReadsPerGene.out.tab; do origin=$f; destination=/home/fgiuste/Data/Movember/`echo $f | cut -d '/' -f5 `/; mkdir $destination; cp $origin $destination; done

# Copy fastq files from /moreno
# for f in /moreno/160413_MovemberTMA/CMO11123/R031-*/*.fastq.gz; do origin=${f} ; destination=/home/fgiuste/Data/Movember/`echo $f | cut -d '/' -f5 `/; mkdir -p $destination; cp $origin $destination & done
# for f in /moreno/160413_MovemberTMA/MSA11033/MSA11033-*/*.fastq.gz; do origin=${f} ; destination=/home/fgiuste/Data/Movember/`echo $f | cut -d '/' -f5 `/; mkdir -p $destination; cp $origin $destination & done







