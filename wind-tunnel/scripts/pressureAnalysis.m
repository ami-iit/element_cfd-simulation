close all;
clear all;
clc;

%% Initialization

% Test and point to be analyzed
jointConfig = 'hovering'; % | hovering | flight30 | flight50 | flight60 |
testID = 'TID_0002';

%% Import filename list and add local path
addpath(genpath('../'));            % Adding the main folder path
experiment    = 'exp_21_03_22';        % Name of the experiment data folder
folderPath    = ['../',experiment,'/data_GVPM'];
testpointList = dir([folderPath,'/',testID,'*.pth']);

for iii = 1 : (length(testpointList(:,1)) - 1)

    [~,testPointID,~] = fileparts(testpointList(iii,:).name(10:15));

    close all;
    clearvars -except jointConfig testID testpointList testPointID

    % folders initialization
    addpath(genpath('../'));                            % Adding the main folder path
    experiment = 'exp_21_03_22';                        % Name of the experiment folder
    folderPath = ['../',experiment,'/data_Matlab/'];    % Path to the experiment data

    % Load data
    test.(testID) = load([folderPath,testID,'/aerodynamicForces.mat']);                                 % test data loading
    testPoint.(testPointID) = load([folderPath,testID,'/pressureSensorsData/',testPointID,'.mat']);  % test point data loading

    % Names of the covers and relative frames
    coverNames = {'face_front','face_back','chest','backpack','pelvis','lt_pelvis_wing','rt_pelvis_wing',...
        'rt_arm_front','rt_arm_rear','lt_arm_front','lt_arm_rear', ...
        'rt_thigh_front','rt_thigh_rear','lt_thigh_front','lt_thigh_rear',...
        'rt_shin_front','rt_shin_rear','lt_shin_front','lt_shin_rear'};
    frameNames = {'head','head','chest','chest','root_link','root_link','root_link', ...
        'r_upper_arm','r_upper_arm','l_upper_arm','l_upper_arm', ...
        'r_upper_leg','r_upper_leg','l_upper_leg','l_upper_leg', ...
        'r_lower_leg','r_lower_leg','l_lower_leg','l_lower_leg'};

    % Initialize robot position
    if matches(jointConfig,'hovering')
        offsetAngle = 90;   % [deg]
        jointPos    = [0,0,0,-10,25,40,15,-10,25,40,15,0,10,7,0,0,0,0,10,7,0,0,0]* pi/180;
    elseif matches(jointConfig,'flight30')
        offsetAngle = 45;   % [deg]
        jointPos    = [0,0,0,-40.7,11.3,26.5,58.3,-40.7,11.3,26.5,58.3,0,10,7,0,0,0,0,10,7,0,0,0]* pi/180;
    elseif matches(jointConfig,'flight50')
        offsetAngle = 45;   % [deg]
        jointPos    = [0,0,0,-31.3,19,26.3,45.3,-31.3,19,26.3,45.3,0,10,7,0,0,0,0,10,7,0,0,0]* pi/180;
    elseif matches(jointConfig,'flight60')
        offsetAngle = 45;   % [deg]
        jointPos    = [0,0,0,-25,24,30,35,-25,24,30,35,0,10,7,0,0,0,0,10,7,0,0,0]* pi/180;
    end

    % robot attitude angles in wind tunnel
    yawAngle   = test.(testID).state.betaMeas(str2double(testPointID(end-3:end)));  % [deg]
    pitchAngle = test.(testID).state.alphaMeas(str2double(testPointID(end-3:end))) + offsetAngle;  % [deg]

    % set base Pose according to yaw and pitch angles
    R_yaw     = rotz(yawAngle);
    R_pitch   = roty(pitchAngle - 90);
    basePose  = [R_yaw * R_pitch, [0.3; 0; 0];
        zeros(1,3),          1];

    % data for using iDynTreeWrappers functions
    modelPath  = 'C:\Users\apaolino\code\component_ironcub\models\iRonCub-Mk1\iRonCub\robots\iRonCub-Mk1_Gazebo\';
    fileName   = 'model_stl.urdf';
    meshFilePrefix = 'C:\Users\apaolino\code\component_ironcub\models';
    jointNames = {'torso_pitch','torso_roll','torso_yaw', 'l_shoulder_pitch', 'l_shoulder_roll','l_shoulder_yaw', ...
        'l_elbow', 'r_shoulder_pitch', 'r_shoulder_roll','r_shoulder_yaw','r_elbow', 'l_hip_pitch', 'l_hip_roll', ...
        'l_hip_yaw','l_knee','l_ankle_pitch','l_ankle_roll', 'r_hip_pitch','r_hip_roll','r_hip_yaw','r_knee','r_ankle_pitch','r_ankle_roll'};
    jointVel = zeros(23,1);
    baseVel  = zeros(6,1);
    gravAcc  = [0; 0; 9.81];

    % idyntree initialization
    KinDynModel = iDynTreeWrappers.loadReducedModel(jointNames, 'root_link', modelPath, fileName, false);
    iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);

    % Initizalizing global values
    globalMinPress = 1e4;
    globalMaxPress = -1e4;

    for j = 1:length(coverNames)

        %% Load geometric data
        coverName = coverNames{j};
        coverData.(coverName).geom = stlread(['./srcPressureAnalysis/',coverName,'.stl']);
        opts = detectImportOptions('./srcPressureAnalysis/chest_sensors.txt');
        pressureSensors = table2struct(readtable(['./srcPressureAnalysis/',coverName,'_sensors.txt'],opts),"ToScalar",true);
        coverData.(coverName).sensorsNames = pressureSensors.Var1;
        coverData.(coverName).x_sensors    = pressureSensors.Var2;
        coverData.(coverName).y_sensors    = pressureSensors.Var3;
        coverData.(coverName).z_sensors    = pressureSensors.Var4;

        % assign cover pressure values data
        for i = 1:length(coverData.(coverName).sensorsNames)
            coverData.(coverName).meanPressValues(i,1) = testPoint.(testPointID).pressureSensors.meanValues.(coverData.(coverName).sensorsNames{i});
            coverData.(coverName).pressValues(i,:)   = testPoint.(testPointID).pressureSensors.values.(coverData.(coverName).sensorsNames{i});
        end

        localMinPress = min(coverData.(coverName).meanPressValues);
        localMaxPress = max(coverData.(coverName).meanPressValues);
        fprintf([coverName,' pressure range: ',num2str(localMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(localMaxPress,3),' [Pa] \n']);

        if localMinPress < globalMinPress
            globalMinPress = localMinPress;
        end
        if localMaxPress > globalMaxPress
            globalMaxPress = localMaxPress;
        end



        %% Pressure map plot initialization

        % Move pressure sensors locations from cover to global coordinates
        w_H_l = iDynTreeWrappers.getWorldTransform(KinDynModel,frameNames{j});

        xyz_sensors = [coverData.(coverName).x_sensors, coverData.(coverName).y_sensors, coverData.(coverName).z_sensors]/1000;
        for i = 1:length(xyz_sensors(:,1))
            v_link  = [transpose(xyz_sensors(i,:)); 1];
            v_world = w_H_l*v_link;
            coverData.(coverName).x_globalSensors(i,1) = v_world(1);
            coverData.(coverName).y_globalSensors(i,1) = v_world(2);
            coverData.(coverName).z_globalSensors(i,1) = v_world(3);
        end

        % Move geometry vertices from cover to global coordinates
        coverData.(coverName).patchPoints        = coverData.(coverName).geom.Points/1000;
        coverData.(coverName).patchFaces         = coverData.(coverName).geom.ConnectivityList;
        for i = 1:length(coverData.(coverName).patchPoints(:,1))
            v_link  = [transpose(coverData.(coverName).patchPoints(i,:)); 1];
            v_world = w_H_l*v_link;
            coverData.(coverName).patchPoints(i,:)   = transpose(v_world(1:3));
        end

        % Create mean pressure values interpolation function on cover mesh
        coverData.(coverName).interpFunction    = scatteredInterpolant(coverData.(coverName).x_sensors,coverData.(coverName).y_sensors,coverData.(coverName).z_sensors,coverData.(coverName).meanPressValues);

    end % end of cover iteration


    %% PLOTTING

    %% robot visualization [debug]
    iDynTreeWrappers.prepareVisualization(KinDynModel, meshFilePrefix, 'color', [0.96,0.96,0.96], ...
        'material', 'dull', ... 'style', 'wireframe','wireframe_rendering',0.8, ...
        'transparency', 0.3, 'debug', true, 'view', [-45 20]);

    %% Pressure map plot
    fig1 = figure(1);
    for j = 1:length(coverNames)
        % plot the cover surface interpolated contour
        coverData.(coverNames{j}).interpPressValues = coverData.(coverNames{j}).interpFunction(coverData.(coverNames{j}).geom.Points);
        p = patch('Faces',coverData.(coverNames{j}).patchFaces,'Vertices',coverData.(coverNames{j}).patchPoints,...
            'FaceVertexCData',coverData.(coverNames{j}).interpPressValues,'FaceColor','interp','EdgeColor','none'); hold on;
    end

    axis([-0.5 1 -1 1 -1 1])
    set(fig1, 'Position', [0 0 2304 1296]);
    if matches(jointConfig,'hovering')
        title(['Pressure map, ',jointConfig,', $\beta=',num2str(yawAngle,'%.0f'),'^\circ$'],'FontSize',22,'Interpreter','latex');
    else
        title(['Pressure map, ',jointConfig,', $\alpha=',num2str(pitchAngle,'%.0f'),'^\circ$'],'FontSize',22,'Interpreter','latex');
    end

    % set colormap
    cmap = colormap("jet");

    %% pressure sensors map plot
    % % initialize generic sphere coordinates and pressure values vector
    % [X,Y,Z] = sphere;
    % radius  = 0.003;
    % pressValuesVector = linspace(globalMinPress,globalMaxPress,length(cmap));
    %
    % for j = 1:length(coverNames)
    %     % set sensor points colors
    %     colors = interp1(pressValuesVector, cmap, coverData.(coverNames{j}).meanPressValues);
    %     for i=1:length(coverData.(coverNames{j}).x_globalSensors)
    %         % plot pressures at sensors locations
    %         surf(X*radius + coverData.(coverNames{j}).x_globalSensors(i), Y*radius + coverData.(coverNames{j}).y_globalSensors(i), ...
    %              Z*radius + coverData.(coverNames{j}).z_globalSensors(i), 'FaceColor', colors(i,:), 'EdgeColor', 'none'); hold on;
    %     end
    % end

    %%  set colorbar
    caxis([globalMinPress globalMaxPress])
    c                   = colorbar('FontSize', 16);
    c.Label.String      = '$\Delta p$ [Pa]';
    c.Label.FontSize    = 22;
    c.Label.Interpreter = 'latex';
    c.Label.Rotation    = 0;
    c.Label.Units       = 'data';
    pos = get(c,'Position');
    c.Label.Position(1) = -3; % to change its position

    


    % % saving
    % saveas(fig1,['.\',saveFolderName,'\',coverName,'-',testID,'-',testPointID,'.svg']);

    saveFolderName = 'hovering-pressure';
    if (~exist(['./',saveFolderName],'dir'))

        mkdir(['./',saveFolderName]);
    end
    saveas(fig1,['.\',saveFolderName,'\',testID,'-',testPointID,'.fig']);

    %% Time-varying pressures plot
    % for j = 1:length(coverNames)
    %     fig2 = figure();
    %     for i = 1:length(meanPressValues)
    %         plot(testPoint.(testPointID).pressureSensors.time,pressValues(i,:),"Color",cmap(i,:)); hold on;
    %     end
    %     grid on;
    %     ylabel('$\Delta p$ [Pa]','Interpreter','latex')
    %     xlabel('$t$ [s]','Interpreter','latex')
    %     title(coverName,'Interpreter','none')

    %     % saving
    %     saveFolderName = 'postProcessPressureAnalysis';
    %     if (~exist(['./',saveFolderName],'dir'))
    %
    %         mkdir(['./',saveFolderName]);
    %     end
    %     saveas(fig2,['.\',saveFolderName,'\',coverName,'-',testID,'-',testPointID,'-plot.svg']);
    % end

    %% Report data
    fprintf(['rt_foot \x394p = ',num2str(testPoint.(testPointID).pressureSensors.meanValues.S1,3),' [Pa] \n']);
    fprintf(['lt_foot \x394p = ',num2str(testPoint.(testPointID).pressureSensors.meanValues.S3,3),' [Pa] \n\n']);
    fprintf(['Global pressure range: ',num2str(globalMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(globalMaxPress,3),' [Pa] \n']);
    fprintf(['Total acquisition time: \x394T = ',num2str(testPoint.(testPointID).pressureSensors.time(end),3),' [s] \n']);


    %% Remove from path

    rmpath(genpath('../'));            % Adding the main folder path

end