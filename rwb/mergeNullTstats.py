# mergeNullTstats(randout, nulltstatout, contrast):  Merge NullT statistics across chunks
# By: Felipe Giuste

### Command Line Argument Processing ###
import sys
print(sys.argv) # Index 0 lists all arguments
if(len(sys.argv) == 4):
    randout = sys.argv[1]
    nulltstatout = sys.argv[2]
    ncontrasts = int(sys.argv[3])
    print("randout: %s"%(randout,))
    print("nulltstatout: %s"%(nulltstatout,))
    print("ncontrasts: %s"%(ncontrasts,))
else:
    print("Incorrect number of arguments, should be 3\nWas: %s" % (len(sys.argv)-1))
    exit()

# NullTmerge: Merge NullT statistics across chunks: Does not consider all-zero chunks during final histogram calculation
# randout: Randomise nulltstatout directory
# nulltstatout: nulltstatout
def NullTmerge(contrast, randout, nulltstatout):
    import glob
    import numpy as np
    import re
    import os
    import csv
    from collections import Counter

    try:
        os.mkdir(nulltstatout)
    except FileExistsError:
        pass

    print('Merging Null Hypothesis T-values across chunks into %s' % nulltstatout)

    # Glob NullTCounters across chunks within contrast
    counterF = Counter()
    for modelT in glob.glob('%s/*/*/NullTCounter_%s.csv' % (randout, contrast)):
        # load chunk histogram:
        countertmp = np.genfromtxt(modelT)
        # convert to dictionary
        counterdict = {key: val for key, val in countertmp}
        # convert dictionary to Counter
        countertmp = Counter(counterdict)
        # Add histogram counts:
        counterF = counterF + countertmp

    # Save counterF to randout directory as 'nulltstatout/NullTCounter_contrast.csv';
    with open('%s/NullTCounter_%s.csv' % (nulltstatout, contrast), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        for key, value in counterF.items():
            writer.writerow([key, value])
    return(0)


# Run NullTMerge:
for contrast in range(1, ncontrasts+1):
    NullTmerge(contrast, randout=randout, nulltstatout=nulltstatout)