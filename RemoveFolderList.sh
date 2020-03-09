# DELETE
folderlist=$(\ls -d /HCP_Data/FG/1000Brains/sub-*/ses-*/freesurfer/)
for folder in ${folderlist}; do 
	\rm -r ${folder} &
done


# COPY
folderlist=$(\ls -d /nvme/1000Brains/sub-*)
for folder in ${folderlist}; do 
	cp -r ${folder} . &
done