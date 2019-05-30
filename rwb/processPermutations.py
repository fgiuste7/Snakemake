# processPermutations(randout, ncontrasts): concatenates permutation-level output from FSL Randomise into compact histograms for later analysis
# By: Felipe Giuste

### Command Line Argument Processing ###
import sys
print(len(sys.argv))
if(len(sys.argv) == 3):
    print(sys.argv)
    randout = sys.argv[1]
    ncontrasts = sys.argv[2]
else:
    exit()

# Function grabs data matrix within nifti file (no header):
def getNII(nii):
    import nibabel as nib
    import numpy as np
    image_nii = nib.nifti1.load(nii)
    data_nii = image_nii.get_fdata(dtype=np.float64)
    image_nii.uncache()
    return(data_nii)

# Iterate through contrasts:
def processPermutations(randout, ncontrasts):
    # randout is randomise output directory for chunk containing permutation files (ending in _perm*.nii.gz)
    # Saves result in randout as: NullTCounter.csv
    from collections import Counter
    import glob
    import csv
    import numpy as np
    import os
    for contrast in range(1, ncontrasts+1):
        perms = glob.glob('%s/*_vox_tstat%s_perm*.nii.gz' %
                          (randout, contrast))
        perms.sort(key=lambda x: int(x.split('_perm')[-1].split('.nii.gz')[0]))

        counterF = Counter()
        for i in perms:
            # load nifti data:
            tmp = getNII(i)
            # round to tenths:
            tmp = np.round(tmp, decimals=1)
            # save as counter:
            countertmp = Counter(tmp.flatten())
            # Add to final counter:
            counterF = counterF + countertmp
            # delete perm data
            os.remove(i)

        # Save counterF to randout directory as 'NullTCounter.csv';
        with open('%s/NullTCounter_%s.csv' % (randout, contrast), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            for key, value in counterF.items():
                writer.writerow([key, value])

# Run:
processPermutations(randout, ncontrasts)