%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script automatically imports the GVPM wind tunnel experiments data 
% from the pressure sensors measurements into matlab workspace files (.mat 
% format)
%
% Author: Antonello Paolino
%
% April 2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;
clear all;
clc;

%% Import filename list and add local path
experiment         = 'exp_2023_12_11';        % Name of the experiment data folder
windTunnelDataPath = ['../',experiment,'/data_GVPM/'];
testFileList       = dir([windTunnelDataPath,'/*.GVP']);  % List of the test files

%% Initialize progress message
disp('progress: [0%] completed');
tic

%% Operations for each test
for testIndex = 1 : length(testFileList)

    testFileName   = testFileList(testIndex).name;
    [~,testName,~] = fileparts(testFileName);   % extracting the test name from the file name

    pressFileList     = dir([windTunnelDataPath,testName,'*.pth']);
    meanPressFileList = dir([windTunnelDataPath,testName,'*.prm']);

    % Initialize data structure
    pressureSensors = struct();

    % Load pressure sensors names
    pressNames = readtable([windTunnelDataPath,'Pressure_Sensors_Map.csv'],'Range','B:B');
    pressNames = table2array(pressNames);

    %% Loop for each test point

    if matches(experiment,'exp_2023_12_11')
        testPointNumber = length(meanPressFileList(:,1));
    else
        testPointNumber = length(meanPressFileList(:,1)) - 1; % last one is a zeros file
    end

    for testPointIndex = 1 : testPointNumber
        
        if ~matches(experiment,'exp_2023_12_11')

            % Import time-varying data from files
            pressFileName  = pressFileList(testPointIndex).name;
            pressValues    = readmatrix([windTunnelDataPath,pressFileName],'FileType','text','Range','E1');
            pressValues    = pressValues(2:end,:);
            pressTimeStamp = readcell([windTunnelDataPath,pressFileName],'FileType','text');
            pressTimeStamp = datetime(vertcat(pressTimeStamp{2:end,1}), ...
                                      'InputFormat','HH:mm:ss.SSSSSS dd/MM/yyyy', ...
                                      'Format','ss.SSSSSS');
            pressTimeStamp = pressTimeStamp - pressTimeStamp(1);
            pressTimeStamp = seconds(pressTimeStamp);

            % Assign data to the struct variables
            pressureSensors.time = pressTimeStamp;
            for i = 1:length(pressNames)
                pressureSensors.values.(pressNames{i}) = pressValues(:,i);
            end

        end

        % Import averaged data from files
        meanPressFileName = meanPressFileList(testPointIndex).name;
        pressMeanValues   = readmatrix([windTunnelDataPath,meanPressFileName],'FileType','text','Range','B:B');

        % Assign data to the struct variables
        for i = 1:length(pressNames)
            pressureSensors.meanValues.(pressNames{i}) = pressMeanValues(i);
        end
        pressureSensors.testID = str2double(testName(5:8));
        pressureSensors.pointID = testPointIndex;

        % Save imported struct data in workspace
        pointFileName = meanPressFileName(10:15);

        if (~exist(['../',experiment,'/data_Matlab'],'dir'))

            mkdir(['../',experiment,'/data_Matlab']);
        end

        if (~exist(['../',experiment,'/data_Matlab/',num2str(testName)],'dir'))

            mkdir(['../',experiment,'/data_Matlab/',num2str(testName)]);
        end

        if (~exist(['../',experiment,'/data_Matlab/',num2str(testName),'/pressureSensorsData'],'dir'))

            mkdir(['../',experiment,'/data_Matlab/',num2str(testName),'/pressureSensorsData']);
        end

        save(['../',experiment,'/data_Matlab/',num2str(testName),'/pressureSensorsData/',pointFileName,'.mat'],'pressureSensors')

    end
    
    %% status display
    status = testIndex/length(testFileList) * 100;
    clc;
    disp(['progress: [',num2str(round(status)),'%] completed']);

    elapsedTime = toc;
    totalTime = elapsedTime/(status/100);
    remainingTime = totalTime - elapsedTime;
    disp(['remaining time: [',num2str(round(remainingTime)),'s]']);
end

%% Complete conversion message
clc;
disp('conversion completed');