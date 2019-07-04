# Felipe Giuste
# 6/28/2019
# Snakefile
# Randomise Whole Brain Nifti Analysis

import glob, os


#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
input_zarr="/HCP_Data/FG/fox_fullRes/sorted/Input.zarr"
input_order= "/HCP_Data/FG/fox_fullRes/model/fileOrder.txt"
output_directory= '/HCP_Data/FG/fox_fullRes/BrainNet/'
output_zarr= output_directory+"Adjacency_2.zarr"
maxSource=652090
maxTarget=652090
binSize=1000


#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------
# SAMPLES: Folder name containing niftis for a row (128 Sources):
SAMPLES = [fname.split('/')[-1].split('.nii')[0] for fname in glob.glob('%s/*'%nifti_directory)]
# CONTRASTS: List of contrast integers as string:
CONTRASTS = [ str(i) for i in range(1,ncontrasts+1) ]

# Rowslices Randomise output:
RANDOMISE = expand(randomise_directory+"/{sample}_done", sample = SAMPLES)
# Finished Test T-Statistic Merging across chunks:
TSTAT = expand(tstat_directory+"/TestTval_{contrast}.zarr", contrast = CONTRASTS)
# Finished Null T-Statistic Merging across chunks:
NULLTSTAT = expand(nulltstat_directory+"/NullTCounter_{contrast}.csv", contrast = CONTRASTS)
# Finished pvalue zarr files:
T2P = expand(pval_directory+"/corrPvals_{contrast}.zarr", contrast = CONTRASTS)



#-------------------------------------------------------------------------------
# Rules
#-------------------------------------------------------------------------------
localrules: all, T2Pvals

rule all:
    input: RANDOMISE[0:224] #T2P
    shell:
        """
        echo "Finito";
        """


# Execute Randomise on each nifti within a RowSlice folder: Starts Container=neuroimaging_{wildcards.sample}
# sample: rowSlice
# nii: chunk
rule randomise:
    input: niftidir= nifti_directory+"/{sample}"
    output: randomise_directory+"/{sample}_done" # RANDOMISE
    shell:
        """
        # Docker Container:
        docker run -t -d --rm -v {temp_directory}:{temp_directory}:rw -v {input[niftidir]}:/data:rw -v {model_directory}:/code:rw --name Randomise_{wildcards.sample} fgiuste/neuroimaging;
        
        chunklist=`ls {input[niftidir]} | sed s/.nii.gz//`
        for nii in $chunklist
        do
            if [ -d "{temp_directory}/{wildcards.sample}/${{nii}}_done" ]
            then
                echo "Found: {temp_directory}/{wildcards.sample}/${{nii}}_done; SKIPPING"
                continue
            fi

            # Create Chunk directory:
            mkdir -m777 -p {temp_directory}/{wildcards.sample}/${{nii}};

            # Randomise on Chunk within Container:
            run_randomise="randomise -i /data/${{nii}}.nii.gz -o {temp_directory}/{wildcards.sample}/${{nii}}/${{nii}} -d /code/{design_matrix} -t /code/{contrast_matrix} -n {npermutations} -R -N -x --permout";
            docker exec Randomise_{wildcards.sample} /bin/bash -c ". /home/startup.sh && ${{run_randomise}}"

            # Permutation processing:
            docker exec Randomise_{wildcards.sample} python /code/processPermutations.py {temp_directory}/{wildcards.sample}/${{nii}} {ncontrasts};
            echo 

            mv "{temp_directory}/{wildcards.sample}/${{nii}}" "{temp_directory}/{wildcards.sample}/${{nii}}_done"
        done

        # Shut down Container:
        docker stop Randomise_{wildcards.sample}

        # Copy final output to randomise_directory/sample_done:
        echo {output}
        mv {temp_directory}/{wildcards.sample} {output}
        """


# Merges Test tstat files from {randomise_directory}: Starts Container=neuroimaging_mergeTstats
# sample: rowSlice
rule mergeTstats:
    input:  randout= RANDOMISE,
    output: tstatout= tstat_directory+"/TestTval_{contrast}.zarr" # TSTAT
    shell:
        """
        mkdir -p {tstat_directory};

        # Docker Container:
        # data -> randout
        # output -> tstat_directory
        docker run -t -d --rm -v {randomise_directory}:/data:rw -v {tstat_directory}:/output:rw -v {model_directory}:/code:rw --name mergeTstats_{wildcards.contrast} fgiuste/neuroimaging;
        
        # Tmerge: randout, tstat_directory, contrast
        docker exec --user `id -u` mergeTstats_{wildcards.contrast} python /code/mergeTstats.py /data/ /output/ {wildcards.contrast};

        docker stop mergeTstats_{wildcards.contrast};
        """


# Merges Null-Distribution tstat files across chunks: Starts Container=mergeNullTstats
rule mergeNullTstats:
    input:  RANDOMISE
    output: nulltstatout= nulltstat_directory+"/NullTCounter_{contrast}.csv" # NULLTSTAT
    shell:
        """
        mkdir -p {nulltstat_directory};

        # Docker Container:
        # data -> randout
        # output -> nulltstat_directory
        docker run -t -d --rm -v {randomise_directory}:/data:rw -v {nulltstat_directory}:/output:rw -v {model_directory}:/code:rw --name mergeNullTstats_{wildcards.contrast} fgiuste/neuroimaging;
        
        # NullTmerge: randout, nulltstat_directory, contrast
        docker exec --user `id -u` mergeNullTstats_{wildcards.contrast} python /code/mergeNullTstats.py /data/ /output/ {wildcards.contrast};

        docker stop mergeNullTstats_{wildcards.contrast};
        """


# Converts Test T-values into corrected P-values using Null-Distribution T-values
# Runs locally utilizing Dask via Slurm
rule T2Pvals:
    input:  tstatout= tstat_directory+"/TestTval_{contrast}.zarr", #TSTAT,
            nulltstatout= nulltstat_directory+"/NullTCounter_{contrast}.csv" # NULLTSTAT
    output: pvalout= pval_directory+"/corrPvals_{contrast}.zarr" # T2P
    shell:
        """
        # Create pval_directory:
        mkdir -p {pval_directory};

        # T2Pvals: tstatout, nulltstat_directory, pval_directory, contrast
        python {model_directory}/T2Pvals.py {tstat_directory} {nulltstat_directory} {pval_directory} {wildcards.contrast};
        """


#-------------------------------------------------------------------------------
# Helper Rules
#-------------------------------------------------------------------------------

# DELETE RANDOMISE OUTPUT:
rule deleterandomise:
    input:  randout= randomise_directory+"/{sample}",
    output: randomise_directory+"/deleted_{sample}" # Rules w/o output run everytime
    shell:
        """
        rm -r {input[randout]};
        touch {output}
        """

# DELETE tstat OUTPUT:
rule deletetstat:
    input:  tstatout= tstat_directory+"/{sample}",
    output: tstat_directory+"/deleted_{sample}" # Rules w/o output run everytime
    shell:
        """
        rm -r {input[tstatout]};
        touch {output}
        """

# TODO: create slurm job config file to specify ntasks=1,c=1, manually override for larger jobs

# RUN:
# cp ~/Github/Snakemake/rwb/*.py 
# snakemake --jobs 500 --cluster "sbatch -p SMIs -J 'rwbSMIs' --ntasks=1 --cpus-per-task=1 --mem=500M"



# Example:
# docker run -t -d --rm -v /mnt/gv0/FoxNiftis/512-639:/data:rw -v /HCP_Data/FG/fox_fullRes/randomise//512-639:/output:rw -v /mnt/gv0/model/:/code:rw --name neuroimaging_512-639 fgiuste/neuroimaging bash; 
# docker exec neuroimaging_512-639 /bin/bash -c ". /home/startup.sh && randomise -i /data/512-639_100096-100223.nii.gz -o /output/512-639_100096-100223/512-639_100096-100223 -d /code/group_comparison.mat -t /code/group_comparison.con -n 5000 -R -N -x --permout"; 

#docker exec neuroimaging_{wildcards.sample} /bin/bash -c ". /home/startup.sh && $run_randomise"
