# mergeTstats(randout, tstatout, contrast): Merge test T-statistic files across chunks into single file for each contrast
# By: Felipe Giuste

### Command Line Argument Processing ###
import sys
print(sys.argv) # Index 0 lists all arguments
if(len(sys.argv) == 4):
    randout = sys.argv[1]
    tstatout = sys.argv[2]
    contrast = int(sys.argv[3])
    print("randout: %s"%(randout,))
    print("tstatout: %s"%(tstatout,))
    print("contrast: %s"%(contrast,))
else:
    print("Incorrect number of arguments, should be 3\nWas: %s" % (len(sys.argv)-1))
    exit()


# Function grabs data matrix within nifti file (no header):
def getNII(nii):
    import nibabel as nib
    import numpy as np
    image_nii = nib.nifti1.load(nii)
    data_nii = image_nii.get_fdata(dtype=np.float64)
    image_nii.uncache()
    return(data_nii)


# Merge test T-statistic files across chunks into single file:
def mergeTstats(randout, tstatout, contrast):
    import numpy as np
    from glob import glob
    import re, zarr
    zarrf= '%s/TestTval_%s.zarr' % (tstatout, contrast)
    print('Merging Test-T Values from contrast: %s' % contrast) 
    
    # randomise results: randout/rowSlice/chunk/chunk*
    # TODO: This line seems RAM heavy:
    testTvals= glob( '%s/*/*/*[0-9]_tstat%s.nii.gz' % (randout, contrast))
    
    # key: tstat filename
    # value: list of chunk coordinates (SourceStart, SourceEnd, TargetStart, TargetEnd)
    filedict= {}
    for ifile in testTvals:
        # RowStart-RowEnd_ColStart-ColEnd (inclusive)
        research= re.search( '.*/(.*?)-(.*?)_(.*?)-(.*?)_done/', ifile )
        chunk_coords= [research.group(1), research.group(2), research.group(3), research.group(4)]
        chunk_coords= [int(k) for k in chunk_coords]
        filedict[ifile]= chunk_coords
    
    # Find max Source/Target based on created niftis:
    tmp= np.array( list(filedict.values()) )
    tmp= np.max( tmp, axis=0)
    shape= [ tmp[i]+1 for i in [1,3] ] # shape of final array needs to include maximums for source and target
    print('Contrast %s Final Shape: %s' % (contrast, shape))
    
    # create zarr file to output final matrix (2D)
    testTvals= zarr.zeros(store= zarrf, shape= shape, chunks=(100,100))
    
    # loop through dictionary of input files to assign final values to testT:
    # i: tstat filename
    # j: chunk coords
    for i,j in filedict.items():
        tmpnii=getNII(i)
        # Assaign nifti Test T-values to testTvals:
        # Add one because chunk coordinates from filename are inclusive:
        testTvals.oindex[ j[0]:j[1]+1, j[2]:j[3]+1 ]= tmpnii
    print('### Test T-values Merged: %s' % zarrf )


# Merge test T-statistic files across chunks into single file for a contrast:
mergeTstats(randout=randout, tstatout=tstatout, contrast=contrast)
