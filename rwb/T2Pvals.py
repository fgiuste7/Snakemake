# T2Pvals(tstatout, ncontrasts): Calculate voxel-wise corrected P-Value
# By: Felipe Giuste

import numpy as np

### Command Line Argument Processing ###
import sys
print(sys.argv) # Index 0 lists all arguments
if(len(sys.argv) == 4):
    tstatout = sys.argv[1]
    pval_dir = sys.argv[2]
    ncontrasts = int(sys.argv[3])
    print("tstatout: %s"%(tstatout,))
    print("randout: %s"%(randout,))
    print("ncontrasts: %s"%(ncontrasts,))
else:
    print("Incorrect number of arguments, should be 3\nWas: %s" % (len(sys.argv)-1))
    exit()

# x: test T-value
# qtable: quantile table (2 columns)
# 1st column: NullTs
# 2nd column: percentage of NullTs <= first column value
def getAlpha(x, qtable):
    import numpy as np
    if(x > qtable[-1, 0]):
        return(0)
    if(x <= qtable[0, 0]):
        return(1)
    xless = x > qtable[:, 0]
    p_val = 1 - qtable[xless][-1, 1]
    return(p_val)

getAlpha_vect = np.vectorize(getAlpha, excluded=('qtable',))

def T2Pvals(tstatout, pval_dir, ncontrasts):
    import numpy as np
    import dask.array as da
    import zarr

    for contrast in range(1, ncontrasts+1):
        # open zarr file containing Test T-values
        testTs = da.from_zarr('%s/TestTval_%s.zarr' % (tstatout, contrast))
        nullTs = np.genfromtxt('%s/NullTCounter_%s.csv' %
                               (tstatout, contrast))

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

        p_values = da.apply_gufunc(getAlpha_vect, x=testTs, qtable=nullTs_quantile,
                                   signature="(),(j,k)->()",
                                   output_dtypes=float)

        print('contrast: %s' % contrast)
        print('p_values: %s' % p_values)
        # Create zarr file to hold p-values:
        pstore_path = '%s/corrPvals_%s.zarr' % (pval_dir, contrast)
        pstore = zarr.create(shape=testTs.shape,
                             dtype=float,
                             store=pstore_path)
        print('pstore: %s' % pstore)
        p_values.to_zarr(pstore)
        print('P-Values Stored: %s' % pstore_path)

T2Pvals(tstatout=tstatout, pval_dir=pval_dir, ncontrasts=ncontrasts)



