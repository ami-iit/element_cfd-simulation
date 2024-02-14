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

    %% Modify body torques reference frame from scale to robot body
    
    if matches(experiment,{'exp_2022_03_21','exp_2022_11_03'})
        r_x = -0.497;   % [m] distance along x between the reference frames
        r_y =  0;       % [m] distance along y between the reference frames
        r_z =  0.021;   % [m] distance along z between the reference frames
    elseif matches(experiment,'exp_2023_12_11')
        r_x =  0;       % [m] distance along x between the reference frames
        r_y =  0.0485;  % [m] distance along y between the reference frames
        r_z =  0.228;   % [m] distance along z between the reference frames
    end
    
    bodyAero.xTorque = bodyAero.xTorque + bodyAero.zForce * r_y - bodyAero.yForce * r_z;
    bodyAero.yTorque = bodyAero.yTorque + bodyAero.xForce * r_z - bodyAero.zForce * r_x;
    bodyAero.zTorque = bodyAero.zTorque + bodyAero.yForce * r_x - bodyAero.xForce * r_y;

    % Non-dimensional torques evaluation (accounting only for dynamic
    % pressure because of unitary nominal surface, length and chord
    bodyAero.xTorqueCoeff = bodyAero.xTorque ./ (state.dynPress);
    bodyAero.yTorqueCoeff = bodyAero.yTorque ./ (state.dynPress);
    bodyAero.zTorqueCoeff = bodyAero.zTorque ./ (state.dynPress);

    %% Modify force/torques reference frame from robot body to wind axes
    
    % This is performed accounting for the transformation between the two
    % frames produced by the rotations alpha and beta in the wind tunnel

    wind_R_body = @(alpha, beta) roty(180) * rotz(beta) * roty(alpha);

    for i = 1 : length(state.alphaDes)

        % compute the force(f_b) and moment(m_b) in body frame
        f_b    = [bodyAero.xForce(i); bodyAero.yForce(i); bodyAero.zForce(i)];
        m_b    = [bodyAero.xTorque(i); bodyAero.yTorque(i); bodyAero.zTorque(i)];

        % transform f_b and m_b to wind axes (f_w, m_w)
        w_R_b  = wind_R_body(state.alphaDes(i),state.betaDes(i));
        f_w    = w_R_b * f_b;
        m_w    = w_R_b * m_b;

        % assign force/torque values
        windAxesAero.dragForce(i)   = f_w(1);
        windAxesAero.sideForce(i)   = f_w(2);
        windAxesAero.liftForce(i)   = f_w(3);
        windAxesAero.rollTorque(i)  = m_w(1);
        windAxesAero.pitchTorque(i) = m_w(2);
        windAxesAero.yawTorque(i)   = m_w(3);
    end
    
    % Non-dimensional force/torque evaluation (accounting only for dynamic
    % pressure because of unitary nominal surface, length and chord
    windAxesAero.dragForceCoeff   = windAxesAero.dragForce   ./ (state.dynPress);
    windAxesAero.sideForceCoeff   = windAxesAero.sideForce   ./ (state.dynPress);
    windAxesAero.liftForceCoeff   = windAxesAero.liftForce   ./ (state.dynPress);
    windAxesAero.rollTorqueCoeff  = windAxesAero.rollTorque  ./ (state.dynPress);
    windAxesAero.pitchTorqueCoeff = windAxesAero.pitchTorque ./ (state.dynPress);
    windAxesAero.yawTorqueCoeff   = windAxesAero.yawTorque   ./ (state.dynPress);

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
