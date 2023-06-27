% Author: Antonello Paolino
%
% June 2023
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;
clear all;
clc;

%% Initialization

% Data to be displayed
dataPath = '../data/';
dataFile = [dataPath,'outputParameters.mat'];
load(dataFile);
jointConfigNames = fieldnames(data);

%% Aerodynamic forces application points definitions
aeroFrameNames = {'head', 'chest', 'chest_l_jet_turbine', 'chest_r_jet_turbine', ...
                  'l_upper_arm','l_arm_jet_turbine','r_upper_arm','r_arm_jet_turbine',...
                  'root_link','l_upper_leg','l_lower_leg','r_upper_leg','r_lower_leg'};

cfdLinkNames   = {'head', 'torso', 'left_back_turbine', 'right_back_turbine', ...
                  'left_arm','left_arm_turbine','right_arm','right_arm_turbine',...
                  'root_link','left_leg_upper','left_leg_lower','right_leg_upper','right_leg_lower'};

load('./src_post/aeroFrameTransforms.mat');



%% data for iDynTreeWrappers
componentPath  = getenv('IRONCUB_COMPONENT_SOURCE_DIR');
modelPath      = [componentPath,'/models/iRonCub-Mk1/iRonCub/robots/iRonCub-Mk1_Gazebo/'];
fileName       = 'model_stl.urdf';
meshFilePrefix = [componentPath,'/models'];
jointNames     = {'torso_pitch','torso_roll','torso_yaw', 'l_shoulder_pitch', 'l_shoulder_roll','l_shoulder_yaw', ...
                  'l_elbow', 'r_shoulder_pitch', 'r_shoulder_roll','r_shoulder_yaw','r_elbow', ...
                  'l_hip_pitch', 'l_hip_roll', 'l_hip_yaw','l_knee','r_hip_pitch','r_hip_roll','r_hip_yaw','r_knee'};

jointVel = zeros(23,1);
baseVel  = zeros(6,1);
gravAcc  = [0; 0; 9.81];

for jointConfigIndex = 1 : length(fieldnames(data))

    jointConfigName = jointConfigNames{jointConfigIndex};
    
    for simIndex = 1 : length(data.(jointConfigName).yawAngle(:))

        close all; % closing previously opened scopes

        yawAngle   = data.(jointConfigName).yawAngle(simIndex);
        pitchAngle = data.(jointConfigName).pitchAngle(simIndex);
        jointPos   = data.(jointConfigName).jointConfig * pi/180;
        
        %% initialize the robot
        R_yaw     = rotz(yawAngle);
        R_pitch   = roty(pitchAngle - 90);
        basePose  = [R_yaw * R_pitch, [10; 0; 0];
            zeros(1,3),         1];

        % idyntree initialization
        KinDynModel = iDynTreeWrappers.loadReducedModel(jointNames, 'root_link', modelPath, fileName, false);
        iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);

        
        %% FIGURE
        
        % robot visualization
        iDynTreeWrappers.prepareVisualization(KinDynModel, meshFilePrefix, 'color', [0.96,0.96,0.96], ...
            'material', 'dull', ... 'style', 'wireframe','wireframe_rendering',0.8, ...
            'transparency', 0.5, 'debug', true, 'view', [-45 5]);
        
        fig1 = figure(1);
       
        % Draw wind velocity vector
        windVector.position   = [8.7 0 0];
        windvector.components = [0.5 0 0];
        arrow3(windVector.position, windVector.position + windvector.components, '2.5b-', 0.8*norm(windvector.components),[],[]);
        text(8.7,0,0.07,'$V_w$','Interpreter','latex','FontSize',32,'Color','b');
        
        % Draw aerodynamic force vectors
        for i = 1 : length(cfdLinkNames)
            w_H_linkFrame       = iDynTreeWrappers.getWorldTransform(KinDynModel,aeroFrameNames{i});
            linkFrame_H_linkCoM = linkFrame_T_linkCoM(:,:,i);
            w_H_linkCoM         = w_H_linkFrame*linkFrame_H_linkCoM;
            aeroForcePosition   = w_H_linkCoM(1:3,4);

            dragForce = [data.(jointConfigName).([cfdLinkNames{i},'_cd'])(simIndex) 0 0];
            sideForce = [0 data.(jointConfigName).([cfdLinkNames{i},'_cs'])(simIndex) 0];
            liftForce = [0 0 data.(jointConfigName).([cfdLinkNames{i},'_cl'])(simIndex)];
            

            aeroForce = dragForce + sideForce + liftForce;
            
            arrow3(aeroForcePosition', aeroForcePosition' + 20*aeroForce, '2.5r-', 10*norm(aeroForce),[],[]);
        
        end

        %% Set figure
        axis([8.5 11 -1 1 -0.7 0.7])
        set(fig1, 'Position', [0 0 3840 2160]);
        grid off;
        title(['Simulation results, ',jointConfigName,', $\alpha=',num2str(round(pitchAngle),'%.0f'),'^\circ$, $\beta=',num2str(round(yawAngle),'%.0f'),'^\circ$'],'FontSize',22,'Interpreter','latex');

        % Set colors
        fig1.Color = [0,0,0];
        set(gcf, 'InvertHardCopy', 'off'); 

        ax = gca;
        ax.Position =  [-0.15,-0.2,1.2,1.4];

        ax.XTick = [];
        ax.YTick = [];
        ax.ZTick = [];

        ax.XTickLabel = [];
        ax.YTickLabel = [];
        ax.ZTickLabel = [];
        
        ax.Color  = [0,0,0];
        ax.XColor = [0,0,0];
        ax.YColor = [0,0,0];
        ax.ZColor = [0,0,0];

        %% saving
        % saveas(fig1,['.\',saveFolderName,'\',coverName,'-',testID,'-',testPointID,'.svg']);

        saveFolderName = 'data_post/figures/';
        if (~exist(['./',saveFolderName],'dir'))

            mkdir(['./',saveFolderName]);
        end
        saveas(fig1,['.\',saveFolderName,'\cfd-',jointConfigName,'-a',num2str(pitchAngle,'%02.f'),'-b',num2str(yawAngle,'%02.f'),'.fig']);

    
    end
end