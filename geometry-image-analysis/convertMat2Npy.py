import scipy as sp 
import numpy as np
import pathlib
import h5py

# Define dataset path
datasetDir = pathlib.Path(__file__).parents[0] / "dataset"
matFilePath1 = datasetDir / "datasetFull_1pt.mat"
matFilePath2 = datasetDir / "datasetFull_2pt.mat"
npyFilePath = datasetDir / "datasetFull.npy"

# Load dataset .mat file
arrays1 = {}
f1 = h5py.File(str(matFilePath2))

for k1, v1 in f1.items():
    arrays1[k1] = np.array(v1)

# arrays2 = {}
# f2 = h5py.File(str(matFilePath2))

# for k2, v2 in f2.items():
#     arrays2[k2] = np.array(v2)

# Assign imgMatrix to variable
imgMatrix1 = arrays1['imgMatrix']
# imgMatrix2 = arrays2['imgMatrix']

# Transform imgMatrix to 4D numpy array keeping the dimension order
imgMatrix = np.transpose(imgMatrix1, (3, 2, 1, 0))
# imgMatrix2_np = np.transpose(imgMatrix2, (3, 2, 1, 0)).astype(np.float32)

# Concatenate imgMatrix1_np and imgMatrix2_np along the first axis
# imgMatrix = np.concatenate((imgMatrix1_np, imgMatrix2_np), axis=0)

######## Debugging ####################################################
# data = np.zeros( (600,800,3), dtype=np.float32)
# data[:,:,0] = imgMatrix[0,0,:,:]
# data[:,:,1] = imgMatrix[0,0,:,:]
# data[:,:,2] = imgMatrix[0,0,:,:]

# data = np.dstack((firstChannel, secondChannel, thirdChannel))

# from matplotlib import pyplot as plt
# plt.imshow(data, interpolation='nearest')
# plt.show()
########################################################################

# Save imgMatrix as .npy file
np.save(str(npyFilePath), imgMatrix)

print('wow')