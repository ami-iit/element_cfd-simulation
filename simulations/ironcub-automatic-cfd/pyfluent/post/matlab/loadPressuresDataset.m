% Function to load pressure data from dataset saved in hdf5 file format
function data = loadPressuresDataset(pressuresDataPath)
    
    % Get list of the dataset files
    datasetList = dir([pressuresDataPath,'/*.hdf5']);  
    datasetNumber = length(datasetList);
    
    % Initialize data struct
    data = struct();
    
    % Loop for each dataset file
    for datasetIndex = 1 : datasetNumber
        
        % Get dataset full path
        pressureDatasetFileName = datasetList(datasetIndex).name;
        pressureDatasetPath     = [pressuresDataPath,pressureDatasetFileName];
        
        % Get dataset joint config name
        jointConfigName = pressureDatasetFileName(11:end-5);

        % Initialize struct for single joint config data
        jointConfigData = struct();
    
        % Assign pitch and yaw angles, and surface names list
        jointConfigData.pitchAngles = str2double(h5read(pressureDatasetPath,'/pitchAngles'));
        jointConfigData.yawAngles   = str2double(h5read(pressureDatasetPath,'/yawAngles'));
        jointConfigData.surfaceList = h5read(pressureDatasetPath,'/surfaceList');
        
        % Assign pressure data for each single surface
        for surfaceIndex = 1 : length(jointConfigData.surfaceList)
            jointConfigData.(jointConfigData.surfaceList(surfaceIndex)) = h5read(pressureDatasetPath,['/',char(jointConfigData.surfaceList(surfaceIndex))]);
        end
        
        % Store all the data in the main struct
        data.(jointConfigName) = jointConfigData;
    
    end

end