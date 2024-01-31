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
experiment = 'exp_2023_12_11';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_GVPM'];
testList = dir([folderPath,'/*.GVP']);  % List of the test files

%% Operations for each file
for testIndex = 1:length(testList(:,1))

    %% Import data from file
    fileName = testList(testIndex).name;

    data = readmatrix([folderPath,'/',fileName],'FileType','text');  % importing the data from the file
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
        scaleAero.(forcesSTDNames{i}) = data(:,74+i);
        bodyAero.(xyzForcesNames{i}) = data(:,26+i);
        bodyAero.(xyzCoeffNames{i}) = data(:,62+i);
        windAxesAero.(aeroForceNames{i}) = data(:,38+i);
        windAxesAero.(aeroCoeffNames{i}) = data(:,50+i);
    end

    %% Modify body torques reference frame to the robot leg pitch axis
    
    if matches(experiment,{'exp_2022_03_21','exp_2022_11_03'})
        r_x = -0.497;    % [m] distance along x between the reference frames
        r_z =  0.021;   % [m] distance along z between the reference frames
    elseif matches(experiment,'exp_2023_12_11')
        r_x = -0.228;    % [m] distance along x between the reference frames
        r_z =  0.0485;   % [m] distance along z between the reference frames
    end
    
    bodyAero.xTorque = scaleAero.xTorque - scaleAero.yForce * r_z;
    bodyAero.yTorque = scaleAero.yTorque + scaleAero.xForce * r_z - scaleAero.zForce * r_x;
    bodyAero.zTorque = scaleAero.zTorque + scaleAero.yForce * r_x;

    % Non-dimensional torques evaluation (accounting only for dynamic
    % pressure because of unitary nominal surface, length and chord
    bodyAero.xTorqueCoeff = bodyAero.xTorque ./ (state.dynPress);
    bodyAero.yTorqueCoeff = bodyAero.yTorque ./ (state.dynPress);
    bodyAero.zTorqueCoeff = bodyAero.zTorque ./ (state.dynPress);

    %% Modify wind axes torques reference frame to the robot leg pitch axis
    
    % This is performed accounting for the transformation between the two
    % frames produced by the rotations alpha and beta in the wind tunnel

    windAxesAero.rollTorque  = - bodyAero.xTorque .*cosd(state.alphaMeas).*cosd(state.betaMeas) ...
                               - bodyAero.yTorque .*cosd(state.alphaMeas).*sind(state.betaMeas) ...
                               + bodyAero.zTorque .*sind(state.alphaMeas);
    windAxesAero.pitchTorque = - bodyAero.xTorque .*sind(state.betaMeas) ...
                               + bodyAero.yTorque .*cosd(state.betaMeas);
    windAxesAero.yawTorque   = - bodyAero.xTorque .*sind(state.alphaMeas).*cosd(state.betaMeas) ...
                               - bodyAero.yTorque .*sind(state.alphaMeas).*sind(state.betaMeas) ...
                               - bodyAero.zTorque .*cosd(state.alphaMeas);
    
    % Non-dimensional torques evaluation (accounting only for dynamic
    % pressure because of unitary nominal surface, length and chord
    windAxesAero.rollTorqueCoeff  = windAxesAero.rollTorque ./ (state.dynPress);
    windAxesAero.pitchTorqueCoeff = windAxesAero.pitchTorque ./ (state.dynPress);
    windAxesAero.yawTorqueCoeff   = windAxesAero.yawTorque ./ (state.dynPress);

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
