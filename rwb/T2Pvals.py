# T2Pvals(tstatout, ncontrasts): Calculate voxel-wise corrected P-Value
# By: Felipe Giuste

### Command Line Argument Processing ###
import sys
print(sys.argv) # Index 0 lists all arguments
if(len(sys.argv) == 5):
    tstatout = sys.argv[1]
    nulltstatout = sys.argv[2]
    pval_dir = sys.argv[3]
    contrast = int(sys.argv[4])
    print("tstatout: %s"%(tstatout,))
    print("nulltstatout: %s"%(nulltstatout,))
    print("pval_dir: %s"%(pval_dir,))
    print("contrast: %s"%(contrast,))
else:
    print("Incorrect number of arguments, should be 4\nWas: %s" % (len(sys.argv)-1))
    exit()

# x: test T-value
# qtable: quantile table (2 columns)
# 1st column: NullTs
# 2nd column: percentage of NullTs <= first column value
from dask import delayed
import numpy as np
def getAlpha(x, qtable):
    if(x > qtable[-1, 0]):
        return(0)
    if(x <= qtable[0, 0]):
        return(1)
    xless = x > qtable[:, 0]
    p_val = 1 - qtable[xless][-1, 1]
    return(p_val)
getAlpha_vect = np.vectorize(getAlpha, excluded=('qtable',))
gAv= delayed(getAlpha_vect, pure=True)


def T2Pvals(tstatout, nulltstatout, pval_dir, contrast):
    import numpy as np
    import dask.array as da
    import zarr

    #import dask_jobqueue.slurm as SLURM
    from dask_jobqueue.slurm import SLURMCluster
    from dask.distributed import Client

    print('Hello_1')

    # Slurm output to current working directory
    cluster = SLURMCluster(
        queue='HPG7s', # -p
        project= "dask_test_"+contrast, # -J
        cores=24, # --cpus-per-task
        memory="60GB", # --mem
        walltime='2190:00:00', # 3 months
        death_timeout=120,
        dashboard_address="http://170.140.138.165:8787", # doc-manager:8787
    )

    print('Hello_2')

    cluster.scale(10) # Number of workers (Nodes in a Dask cluster, not necessarily real Nodes)

    client = Client(cluster)

    #for contrast in range(1, ncontrasts+1):
    # open zarr file containing Test T-values
    testTvals = da.from_zarr('%s/TestTval_%s.zarr' % (tstatout, contrast))
    nullTs = np.genfromtxt('%s/NullTCounter_%s.csv' % (nulltstatout, contrast))

    # Process NullTs:
    # remove NullTs <= 0
    nullTs = nullTs[nullTs[:, 0] > 0]
    # Sort by first column (NullTs):
    nullTs = sorted(nullTs, key=lambda x: x[0])
    nullTs = np.array(nullTs)
    # Get cumulative sums of frequencies:
    nullTs_sums = np.cumsum(nullTs[:, 1], axis=0)
    # First column: sorted T-values:
    # Second column: their cumulative frequencies:
    nullTs_sums = np.stack((nullTs[:, 0], nullTs_sums), axis=1)

    # Total number of null-Ts:
    total_nullTs = nullTs_sums[-1, 1]
    print('Total Number of Null Hypothesis T-Values: %s' % total_nullTs)

    # nullTs_quantile:
    # 1st column: NullTs
    # 2nd column: percentage of NullTs <= first column value
    nullTs_quantile = nullTs_sums[:, 1]/total_nullTs
    nullTs_quantile = np.stack((nullTs[:, 0], nullTs_quantile), axis=1)

    T_cutoff_95 = nullTs_quantile[nullTs_quantile[:, 1] > 0.95][0]
    print('alpha=0.05 T-Value: %s' % T_cutoff_95)

    x_chunks = testTvals.numblocks[0]
    y_chunks = testTvals.numblocks[1]
    # List of delayed getAlpha() on chunks:
    jobs=[]
    # Iterate accross chunks:
    for i in range(x_chunks):
        for j in range(y_chunks):
            # delayed getAlpha() on chunk:
            jobs.append( gAv(testTvals.blocks[i,j], qtable=nullTs_quantile) )
    
    # Convert delayed function calls into returned arrays:
    jobs1 = [da.from_delayed(j, shape=testTvals.chunksize, dtype=np.float) for j in jobs]
    # Iterate accross jobs1 list of arrays and reformat into final array:
    for i in range(x_chunks):
        start= i * y_chunks
        end= start+ y_chunks
        try: 
            # Concatenate jobs1 corresponding to single row:
            p_values = da.concatenate( (p_values, da.concatenate(jobs1[start:end], axis=1)), axis=0 )
        except NameError:
            # Concatenate jobs1 corresponding to single row:
            p_values = da.concatenate(jobs1[start:end], axis=1 )

    print('contrast: %s' % contrast)
    print('p_values: %s' % p_values)
    # Create zarr file to hold p-values:
    pstore_path = '%s/corrPvals_%s.zarr' % (pval_dir, contrast)
    pstore = zarr.create(shape=testTvals.shape,
                            dtype=float,
                            store=pstore_path)
    print('pstore: %s' % pstore)
    p_values.to_zarr(pstore)
    print('P-Values Stored: %s' % pstore_path)

T2Pvals(tstatout=tstatout, nulltstatout=nulltstatout, pval_dir=pval_dir, contrast=contrast)



