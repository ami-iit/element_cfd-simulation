close all;
clear all;
clc;

%% %% Initialization %%%%
robotName       = 'iRonCub-Mk1';

% Path definition
if matches(robotName,'iRonCub-Mk1')
    ironcubSoftwarePath  = getenv('IRONCUB_SOFTWARE_SOURCE_DIR');
elseif matches(robotName,'iRonCub-Mk3')
    ironcubSoftwarePath  = getenv('IRONCUB_COMPONENT_SOURCE_DIR');
end

pressuresDataPath = '../data/pressures/';

%% %%%%%%%%%%%%%%%%%%%%% Robot model initialization %%%%%%%%%%%%%%%%%%%%%%%

% iDynTreeWrappers functions data
modelPath  = [ironcubSoftwarePath,'/models/iRonCub-Mk1/iRonCub/robots/iRonCub-Mk1_Gazebo/'];
fileName   = 'model_stl.urdf';
meshFilePrefix = [ironcubSoftwarePath,'/models'];
jointNames = {'torso_pitch','torso_roll','torso_yaw', 'l_shoulder_pitch', 'l_shoulder_roll','l_shoulder_yaw', ...
              'l_elbow', 'r_shoulder_pitch', 'r_shoulder_roll','r_shoulder_yaw','r_elbow', 'l_hip_pitch', 'l_hip_roll', ...
              'l_hip_yaw','l_knee','l_ankle_pitch','l_ankle_roll', 'r_hip_pitch','r_hip_roll','r_hip_yaw','r_knee','r_ankle_pitch','r_ankle_roll'};

% set constant values
jointVel = zeros(23,1);
baseVel  = zeros(6,1);
gravAcc  = [0; 0; 9.81];

% load the robot model
KinDynModel = iDynTreeWrappers.loadReducedModel(jointNames, 'root_link', modelPath, fileName, false);

%% %%%%%%%%%%%%%%%%%%%%%%%%%%% Set robot state %%%%%%%%%%%%%%%%%%%%%%%%%%%%
% set pitch and yaw angles
pitchAngle = 45;
yawAngle   = 0;

% set base Pose according to yaw and pitch angles
R_yaw      = rotz(yawAngle);
R_pitch    = roty(pitchAngle - 90);
basePose   = [R_yaw * R_pitch, zeros(3,1);
                   zeros(1,3),         1];

% set joint configuration
jointPos = [0.0,0.0,0.0,-10.0,25.0,40.0,15.0,-10.0,25.0,40.0,15.0,0.0,10.0,7.0,0.0,0.0,0.0,0.0,10.0,7.0,0.0,0.0,0.0]*pi/180; % hovering

% set robot state and move root_link to Fluent origin
iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);
correctRobotOrigin(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);

% robot visualization
[viz, objects] = iDynTreeWrappers.prepareVisualization(KinDynModel, meshFilePrefix, 'color', [0.96,0.96,0.96], ...
            'material', 'dull', ... 'style', 'wireframe','wireframe_rendering',0.8, ...
            'transparency', 0.2, 'debug', true, 'view', [-45 5]);


%% %%%%%%%%%%%%%%%%%%% IMPORT AND MODIFY FLUENT DATA %%%%%%%%%%%%%%%%%%%%%%

% set surface names from Fluent data and corresponding frame names
surfaceNames = {'head','torso','torso_pitch','left_back_turbine','right_back_turbine', ...
                'left_arm','left_turbine','right_arm','right_turbine', ...
                'root_link','left_leg_upper','left_leg_lower','right_leg_upper','right_leg_lower'};
surfaceFrames = {'head','chest','torso_pitch','chest_l_jet_turbine','chest_r_jet_turbine', ...
                 'l_upper_arm','l_arm_jet_turbine','r_upper_arm','r_arm_jet_turbine', ...
                 'root_link','l_upper_leg','l_lower_leg','r_upper_leg','r_lower_leg'};

% axes of the symmetric planes used for imaging
surfaceRefAxes = [1,1,1,1,1,2,1,2,1,2,1,2,1,2];  


surfaceNumber = length(surfaceNames);

for surfaceIndex = 1 : surfaceNumber  %%% use in place of next line %%%
    % surfaceIndex = 6;

    surfaceName = surfaceNames{surfaceIndex};
    surfaceFrame = surfaceFrames{surfaceIndex};
    surfaceRefAxis = surfaceRefAxes(surfaceIndex);

    % assign 30 deg rotation to the turbine local frames
    rotatedSurfaceNames = {'left_turbine','right_turbine','left_back_turbine','right_back_turbine'};
    if matches(surfaceName,rotatedSurfaceNames), rotationAngle = 30;
    else, rotationAngle = 0;
    end

    % get local frame transform
    fluent_H_link = iDynTreeWrappers.getWorldTransform(KinDynModel,surfaceFrame);
    fluent_R_link_local = fluent_H_link(1:3,1:3)*rotz(rotationAngle);
    fluent_d_link_local = fluent_H_link(1:3,4);
    link_local_H_fluent = [fluent_R_link_local', -fluent_R_link_local' * fluent_d_link_local;
        zeros(1,3),                                           1];

    % Import Fluent Data
    jointConfigName =  'hovering';
    surfacePressuresFilePath = [pressuresDataPath,jointConfigName,'-',num2str(pitchAngle),'-',num2str(yawAngle),'-ironcub_',surfaceName,'.txt'];
    data = importFluentData(surfacePressuresFilePath, link_local_H_fluent);

    % Display loaded data
    figure(1)
    pcshow([data.x_fluent data.y_fluent data.z_fluent], data.press);

    %% Generate 2D images
    if surfaceRefAxis == 1
        x = data.y_local;
        y = data.z_local;
        z = data.x_local;
    elseif surfaceRefAxis == 2
        x = data.x_local;
        y = data.z_local;
        z = data.y_local;
    elseif surfaceRefAxis == 3
        x = data.x_local;
        y = data.y_local;
        z = data.z_local;
    end

    % set indices for the sides of the component
    in1 = z > 0;
    in2 = z < 0;

    % create scatter interpolation functions of the pressures
    F_interp1    = scatteredInterpolant(x(in1), y(in1), data.press(in1), "linear", "none");
    F_interp2    = scatteredInterpolant(x(in2), y(in2), data.press(in2), "linear", "none");
    % F_interp1_ex = scatteredInterpolant(x(in1), y(in1), data.press(in1), "linear", "nearest");
    % F_interp2_ex = scatteredInterpolant(x(in2), y(in2), data.press(in2), "linear", "nearest");

    % Building the image grid boundaries
    tol   = 0.01;
    x_min = min(x) - tol;
    x_max = max(x) + tol;
    y_min = min(y) - tol;
    y_max = max(y) + tol;
    
    % Create a pixelNum x pixelNum image grid
    pixelNum = 256;
    x_img = linspace(x_min, x_max, pixelNum);
    y_img = linspace(y_min, y_max, pixelNum);
    [X_img, Y_img] = meshgrid(x_img, y_img);

    % interpolate input values over the image grid
    press_sampled_1    = F_interp1(X_img,Y_img);
    press_sampled_2    = F_interp2(X_img,Y_img);
    % press_sampled_1_ex = F_interp1_ex(X_img,Y_img);
    % press_sampled_2_ex = F_interp2_ex(X_img,Y_img);

    % get the indices of the grid points inside the component polygon
    shrinkFactor    = 0.5;
    boundaryIndices = boundary(x,y,shrinkFactor);
    maskIndices     = inpolygon(X_img, Y_img, x(boundaryIndices), y(boundaryIndices));

    % remove values outside the component polygon
    press_sampled_1(~maskIndices) = NaN;
    press_sampled_2(~maskIndices) = NaN;

    %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Plots %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    fig2 = figure('Position',[100 400 1080 480]);
    tiledlayout(2,3)

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SIDE 1 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % Plot imported 3D data as 2D
    nexttile
    pcshow([x(in1) y(in1) z(in1)], data.press(in1), "ViewPlane","XY");
    title("Side-1 3D","Color","w")

    % Plot 2D interpolated data
    nexttile
    contourf(X_img, Y_img, press_sampled_1);
    axis([x_min x_max y_min y_max])
    title('Side-1 contour',"Color","w")
    axis equal

    % Plot 2D images
    nexttile
    im = image(flipud(press_sampled_1),'CDataMapping','scaled');
    title('Side-1 image',"Color","w")
    axis equal

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SIDE 2 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % Plot imported 3D data as 2D
    nexttile
    pcshow([x(in2) y(in2) z(in2)], data.press(in2), "ViewPlane","XY");
    title("Side-2 3D","Color","w")

    % Plot 2D interpolated data
    nexttile
    contourf(X_img, Y_img, press_sampled_2);
    axis([x_min x_max y_min y_max])
    title('Side-2 contour',"Color","w")
    axis equal

    % Plot 2D images
    nexttile
    image(flipud(press_sampled_2),'CDataMapping','scaled');
    title('Side-2 image',"Color","w")
    axis equal

end

