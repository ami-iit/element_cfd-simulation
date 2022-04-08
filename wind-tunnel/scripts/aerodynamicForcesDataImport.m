%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script automatically imports the GVPM wind tunnel experiments data 
% from the scale forces measurements into matlab workspace files (.mat 
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
testList = dir([folderPath,'/*.GVP']);  % List of the test files

%% Operations for each file
for testIndex = 1:length(testList(:,1))

    %% Import data from file
    fileName = testList(testIndex).name;

    data = readmatrix(fileName,'FileType','text');  % importing the data from the file
    data = data(1:(end-1),:);   % remove the final zeros line

    %% Initialize data structures
    state        = struct();  % wind tunnel and model state data
    scaleAero    = struct();  % forces and coeffs w.r.t. scale axes
    bodyAero     = struct();  % forces and coeffs w.r.t. body axes
    windAxesAero = struct();  % forces and coeffs w.r.t. wind axes

    %% Assign variable names
    stateAngles    = {'alphaDes', 'betaDes', 'alphaMeas', 'betaMeas'};  % [deg]
    stateCond      = {'windSpeed','dynPress', 'airDens', 'totPress', 'airTemp', 'airRelHumid'}; % [m/s; Pa; kg/m^3; Pa; K; -]
    xyzForcesNames = {'xForce', 'yForce', 'zForce', 'xTorque', 'yTorque', 'zTorque'}; % [N; N; N; Nm; Nm; Nm]
    xyzCoeffNames  = {'xForceCoeff', 'yForceCoeff', 'zForceCoeff', 'xTorqueCoeff', 'yTorqueCoeff', 'zTorqueCoeff'};
    forcesSTDNames = {'xForceSTD', 'yForceSTD', 'zForceSTD', 'xTorqueSTD', 'yTorqueSTD', 'zTorqueSTD'};
    aeroForceNames = {'dragForce', 'sideForce', 'liftForce', 'rollTorque', 'pitchTorque', 'yawTorque'}; % [N; N; N; Nm; Nm; Nm]
    aeroCoeffNames = {'dragForceCoeff', 'sideForceCoeff', 'liftForceCoeff', 'rollTorqueCoeff', 'pitchTorqueCoeff', 'yawTorqueCoeff'};

    %% Assign data to the struct variables
    for i = 1:length(stateAngles)
        state.(stateAngles{i}) = data(:,1+i);
    end

    for i = 1:length(xyzForcesNames)
        state.(stateCond{i}) = data(:,8+i);
        scaleAero.(xyzForcesNames{i}) = data(:,14+i);
        scaleAero.(forcesSTDNames{i}) = data(:,73+i);
        bodyAero.(xyzForcesNames{i}) = data(:,26+i);
        bodyAero.(xyzCoeffNames{i}) = data(:,61+i);
        windAxesAero.(aeroForceNames{i}) = data(:,38+i);
        windAxesAero.(aeroCoeffNames{i}) = data(:,50+i);
    end

    %% Save imported struct data in workspace

    if (~exist(['../',experiment,'/data_Matlab'],'dir'))

        mkdir(['../',experiment,'/data_Matlab']);
    end

    [~,testName,~] = fileparts(fileName);

    if (~exist(['../',experiment,'/data_Matlab/',num2str(testName)],'dir'))

        mkdir(['../',experiment,'/data_Matlab/',num2str(testName)]);
    end

    save(['../',experiment,'/data_Matlab/',num2str(testName),'/aerodynamicForces.mat'],'state','scaleAero','windAxesAero','bodyAero')

end

%% Remove local path
rmpath(genpath('../'));
