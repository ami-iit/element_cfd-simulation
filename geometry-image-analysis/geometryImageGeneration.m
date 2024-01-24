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

% Import joint positions data
jointPosDataPath = '.\src\';
jointPosFileName = 'jointConfigurationsFixed.csv';

data = importdata([jointPosDataPath,jointPosFileName]);

jointConfigNames  = data.rowheaders;
jointPosData      = data.data;

% Set x, y, z limits for the views and define interpolation functions
x_lim = [-0.48, 0.42];
y_lim = [-0.57, 0.57];
z_lim = [-0.73, 0.62];

deltas = [x_lim(2)-x_lim(1), y_lim(2)-y_lim(1), z_lim(2)-z_lim(1)];

x_vec = [x_lim(1); x_lim(1); x_lim(1); x_lim(1); x_lim(2); x_lim(2); x_lim(2); x_lim(2)];
y_vec = [y_lim(1); y_lim(1); y_lim(2); y_lim(2); y_lim(1); y_lim(1); y_lim(2); y_lim(2)];
z_vec = [z_lim(1); z_lim(2); z_lim(1); z_lim(2); z_lim(1); z_lim(2); z_lim(1); z_lim(2)];

% x_val = [-1; -1; -1; -1;  1;  1;  1;  1];
% y_val = [-1; -1;  1;  1; -1; -1;  1;  1];
% z_val = [-1;  1; -1;  1; -1;  1; -1;  1];

back_dist   = scatteredInterpolant( x_vec, y_vec, z_vec,  x_vec - x_lim(1) );
right_dist  = scatteredInterpolant( x_vec, y_vec, z_vec,  y_vec - y_lim(1) );
up_dist     = scatteredInterpolant( x_vec, y_vec, z_vec,  z_vec - z_lim(1) );
front_dist  = scatteredInterpolant( x_vec, y_vec, z_vec, -x_vec + x_lim(2) );
left_dist   = scatteredInterpolant( x_vec, y_vec, z_vec, -y_vec + y_lim(2) );
bottom_dist = scatteredInterpolant( x_vec, y_vec, z_vec, -z_vec + z_lim(2) );

interp_functions = {right_dist, front_dist, up_dist, left_dist, back_dist, bottom_dist};

% Define views
front_view = [-90 0];
left_view = [0 0];
back_view = [90 0];
right_view = [180 0];
up_view = [-90 90];
bottom_view = [-90 -90];

views  = [180 0; -90 0; 180 90; 0 0; 90 0; 0 -90];
limits = [x_lim y_lim z_lim];

% set resolution
resolution = [800 600];

%% idyntree code initialization
modelPath  = [ironcubSoftwarePath,'/models/iRonCub-Mk1/iRonCub/robots/iRonCub-Mk1_Gazebo/'];
fileName   = 'model_stl.urdf';
meshFilePrefix = [ironcubSoftwarePath,'/models'];
jointNames = {'torso_pitch','torso_roll','torso_yaw', 'l_shoulder_pitch', 'l_shoulder_roll','l_shoulder_yaw', ...
              'l_elbow', 'r_shoulder_pitch', 'r_shoulder_roll','r_shoulder_yaw','r_elbow', 'l_hip_pitch', 'l_hip_roll', ...
              'l_hip_yaw','l_knee','l_ankle_pitch','l_ankle_roll', 'r_hip_pitch','r_hip_roll','r_hip_yaw','r_knee','r_ankle_pitch','r_ankle_roll'};

KinDynModel = iDynTreeWrappers.loadReducedModel(jointNames, 'root_link', modelPath, fileName, false);

%% %%%%%%%%%%%%%%%%%%%%%%  Images generation %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set robot joint configuration from data (TO BE TRANSFORMED INTO FOR
% CYCLE)
jointConfigNumber = length(jointConfigNames);

jointConfigStart  = 1;
jointConfigEnd    = jointConfigNumber;

% initialize data matrix
imgMatrix = zeros(jointConfigEnd - jointConfigStart + 1 , 1, resolution(2), resolution(1));

for jointConfigIndex = jointConfigStart : jointConfigEnd

    jointConfigName = jointConfigNames{jointConfigIndex};
    jointPos        = jointPosData(jointConfigIndex,:);
    
    %% set robot state
    % set base Pose according to yaw and pitch angles
    pitchAngle = 90;
    yawAngle   = 0;
    
    R_yaw      = rotz(yawAngle);
    R_pitch    = roty(pitchAngle - 90);
    basePose   = [R_yaw * R_pitch, zeros(3,1);
                       zeros(1,3),         1];
    
    jointPos = jointPos*pi/180; % hovering
    jointVel = zeros(23,1);
    baseVel  = zeros(6,1);
    gravAcc  = [0; 0; 9.81];
    
    iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);

    %% Display Image
    close all hidden    % close all figures (also the hidden ones)
    fig = figure('visible','on');
    fig.Units = "pixels";
    fig.Position = [300 300 resolution];
    fig.Color = 'none';
    fig.InvertHardcopy = 'off';
    t = tiledlayout(2,3,'TileSpacing','none','Padding','none');
    for i = 1 : 6
        ax(i) = nexttile;
        view = views(i,:);
        interp_fun = interp_functions{i};
        [viz, objects] = prepViz(KinDynModel, meshFilePrefix, interp_fun, limits, ...
                                'color', [0.96,0.96,0.96], 'material', 'dull', ...
                                'transparency', 1, 'debug', true, 'view', view, 'reuseFigure', 'gcf');
    
        camlight(0, 0)
        
        % create colormap
        n = 50;                         % number of colors
        min_color = 0.1;
        max_color = 0.9;
        C = linspace(min_color,max_color,n);        % Color from min to max
        cmap = ([C(:), C(:), C(:)]);    % create colormap

        colormap(ax(i),flipud(cmap));
        clim([0 deltas(3)])
    end
    
    % Save image
    imgDirectory = '.\img\';
    imgFileName  = [jointConfigName,'.png'];
    % imwrite(getframe(fig).cdata,[imgDirectory, imgFileName],'png');

    A = getframe(fig).cdata;
    colorMatrix = im2double(A(:,:,1));
    colorMatrix(colorMatrix<min_color) = 0;
    colorMatrix(colorMatrix>max_color) = 0;

    % interpolate back the values from colormap to distance
    y2 = max(deltas);
    y1 = 0;
    x2 = max_color;
    x1 = min_color;
    m = (y2 - y1)/(x2 - x1);

    distMatrix = colorMatrix*0;
    distMatrix(colorMatrix~=0) = m*(colorMatrix(colorMatrix~=0) - x1);

    % debug view of non-zero values in matrices
    % figure()
    % spy(colorMatrix);
    % 
    % figure()
    % spy(distMatrix);

    % Assign distance matrix
    imgMatrix( jointConfigIndex-jointConfigStart+1, 1, :, :) = distMatrix;

    disp(['[INFO]: configuration ',num2str(jointConfigIndex),'/',num2str(jointConfigEnd),' completed'])
        
    datasetDir  = '.\dataset\';
    datasetName = ['dataset_',num2str(jointConfigIndex),'.mat'];

    if rem(jointConfigIndex,500)==0
        save([datasetDir,datasetName],'imgMatrix','-v7.3');
        disp(['[INFO]: dataset saved in: ',datasetDir,datasetName]);
    end

end



