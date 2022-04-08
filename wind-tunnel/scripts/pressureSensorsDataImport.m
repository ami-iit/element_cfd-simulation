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
addpath(genpath('../'));            % Adding the main folder path
experiment = 'exp_21_03_22';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_GVPM'];
testFileList = dir([folderPath,'/*.GVP']);  % List of the test files

%% Initialize progress message
disp('progress: [0%] completed');

%% Operations for each test
for testIndex = 1 : length(testFileList)

    testFileName   = testFileList(testIndex).name;
    [~,testName,~] = fileparts(testFileName);   % extracting the test name from the file name

    pressFileList     = dir([folderPath,'/',testName,'*.pth']);
    meanPressFileList = dir([folderPath,'/',testName,'*.prm']);

    % Initialize data structure
    pressureSensors = struct();

    % Load pressure sensors names
    pressNames = readtable('Pressure_Sensors_Map.csv','Range','B:B');
    pressNames = table2array(pressNames);

    %% Loop for each test point
    for testPointIndex = 1 : (length(pressFileList(:,1)) - 1)

        % Import data from files
        pressFileName     = pressFileList(testPointIndex).name;
        meanPressFileName = meanPressFileList(testPointIndex).name;

        pressValues = readmatrix(pressFileName,'FileType','text','Range','E1');
        pressValues = pressValues(2:end,:);

        pressTimeStamp = readcell(pressFileName,'FileType','text');
        pressTimeStamp = datetime(vertcat(pressTimeStamp{2:end,1}), ...
                        'InputFormat','HH:mm:ss.SSSSSS dd/MM/yyyy', ...
                        'Format','ss.SSSSSS');
        pressTimeStamp = pressTimeStamp - pressTimeStamp(1);
        pressTimeStamp = seconds(pressTimeStamp);

        pressMeanValues = readmatrix(meanPressFileName,'FileType','text','Range','B:B');


        % Assign data to the struct variables
        pressureSensors.time = pressTimeStamp;

        for i = 1:length(pressNames)

            pressureSensors.values.(pressNames{i}) = pressValues(:,i);
            pressureSensors.meanValues.(pressNames{i}) = pressMeanValues(i);
        end

        pressureSensors.testID = str2double(testName(5:8));
        pressureSensors.pointID = testPointIndex;

        % Save imported struct data in workspace
        pointFileName = pressFileName(10:15);

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
    
    %% 
    status = testIndex/length(testFileList) * 100;
    clc;
    disp(['progress: [',num2str(round(status)),'%] completed']);
end

%% Complete conversion message
clc;
disp('conversion completed');

%% Remove local path
rmpath(genpath('../'));