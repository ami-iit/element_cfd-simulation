% Author: Antonello Paolino
%
% July 2023
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
basePose = eye(4);  % alpha=90 and beta=0


for linkIndex = 1 : length(cfdLinkNames)

    cfdLinkName = cfdLinkNames{linkIndex};
    aeroFrameName = aeroFrameNames{linkIndex};

    if matches(aeroFrameName, {'head','chest','root_link'})
        frameAxis = [0; 1; 0];
    else
        frameAxis = [0; 0; 1];
    end

    for jointConfigIndex = 1 : length(fieldnames(data))

        jointConfigName = jointConfigNames{jointConfigIndex};
        jointPos        = data.(jointConfigName).jointConfig * pi/180;

        % idyntree model initialization
        KinDynModel = iDynTreeWrappers.loadReducedModel(jointNames, 'root_link', modelPath, fileName, false);
        iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);

        % robot visualization
        %     iDynTreeWrappers.prepareVisualization(KinDynModel, meshFilePrefix, 'color', [0.96,0.96,0.96], ...
        %                                         'material', 'dull', 'transparency', 0.5, 'debug', true, 'view', [-45 5]);
        
        dummyVector = nan(length(data.(jointConfigName).yawAngle(:)), 1);
        linkAoAs = dummyVector;
        linkCdAs = dummyVector;
        linkClAs = dummyVector;
        linkCsAs = dummyVector;
        
        yawAngles   = dummyVector;
        pitchAngles = dummyVector;
        ironcubCdAs = dummyVector;
        ironcubClAs = dummyVector;
        ironcubCsAs = dummyVector;

        for simIndex = 1 : length(data.(jointConfigName).yawAngle(:))

            % adjust robot pose
            yawAngle   = data.(jointConfigName).yawAngle(simIndex);
            pitchAngle = data.(jointConfigName).pitchAngle(simIndex);
            R_yaw      = rotz(yawAngle);
            R_pitch    = roty(pitchAngle - 90);
            w_H_base   = [R_yaw * R_pitch, zeros(3,1);
                               zeros(1,3),         1];
            % Compute link AoA
            base_H_link       = iDynTreeWrappers.getRelativeTransform(KinDynModel,'root_link',aeroFrameName);
            w_H_link          = w_H_base * base_H_link;
            linkAxisVersor    = w_H_link(1:3,1:3) * frameAxis;
            linkAngleOfAttack = acosd(transpose(linkAxisVersor) * [-1; 0; 0]); % [deg]
            % Store data
            linkAoAs(simIndex) = linkAngleOfAttack;
            linkCdAs(simIndex) = data.(jointConfigName).([cfdLinkName,'_cd'])(simIndex);
            linkClAs(simIndex) = data.(jointConfigName).([cfdLinkName,'_cl'])(simIndex);
            linkCsAs(simIndex) = data.(jointConfigName).([cfdLinkName,'_cs'])(simIndex);
            
            if linkIndex == 1
                yawAngles(simIndex)   = yawAngle;
                pitchAngles(simIndex) = pitchAngle;
                ironcubCdAs(simIndex) = data.(jointConfigName).ironcub_cd(simIndex);
                ironcubClAs(simIndex) = data.(jointConfigName).ironcub_cl(simIndex);
                ironcubCsAs(simIndex) = data.(jointConfigName).ironcub_cs(simIndex);
            end

        end
        
        % plot link CdAs vs AoA
        figure(linkIndex);
        title(cfdLinkName,'Interpreter','none');
        scatter(linkAoAs,linkCdAs); hold on;
        xlabel('$\alpha_{link}$','Interpreter','latex');
        ylabel('$C_D A$','Interpreter','latex');
%         legend(jointConfigNames);
        grid on;
        
        % plot link ClAs vs AoA
        figure(length(cfdLinkNames)+linkIndex+1);
        title(cfdLinkName,'Interpreter','none');
        scatter(linkAoAs,linkClAs); hold on;
        xlabel('$\alpha_{link}$','Interpreter','latex');
        ylabel('$C_L A$','Interpreter','latex');
%         legend(jointConfigNames);
        grid on;
        
        % plot link CsAs vs AoA
        figure(2*length(cfdLinkNames)+linkIndex+2);
        title(cfdLinkName,'Interpreter','none');
        scatter(linkAoAs,linkCsAs); hold on;
        xlabel('$\alpha_{link}$','Interpreter','latex');
        ylabel('$C_S A$','Interpreter','latex');
%         legend(jointConfigNames);
        grid on;
        
        if linkIndex == 1

            % plot ironcub CdA vs AoA at beta=0
            figure(length(cfdLinkNames)+1);
            title('iRonCub ($\beta = 0^\circ$)','Interpreter','latex');
            plot(pitchAngles(yawAngles==0),ironcubCdAs(yawAngles==0)); hold on;
            xlabel('$\alpha$','Interpreter','latex');
            ylabel('$C_D A$','Interpreter','latex');
            legend(jointConfigNames);
            grid on;

            % plot ironcub ClA vs AoA at beta=0
            figure(2*length(cfdLinkNames)+2);
            title('iRonCub ($\beta = 0^\circ$)','Interpreter','latex');
            plot(pitchAngles(yawAngles==0),ironcubClAs(yawAngles==0)); hold on;
            xlabel('$\alpha$','Interpreter','latex');
            ylabel('$C_L A$','Interpreter','latex');
            legend(jointConfigNames);
            grid on;

            % plot ironcub CsA vs AoA at beta=0
            figure(3*length(cfdLinkNames)+3);
            title('iRonCub ($\beta = 0^\circ$)','Interpreter','latex');
            plot(pitchAngles(yawAngles==0),ironcubCsAs(yawAngles==0)); hold on;
            xlabel('$\alpha$','Interpreter','latex');
            ylabel('$C_S A$','Interpreter','latex');
            legend(jointConfigNames);
            grid on;

        end


    end

end

%% Create the folder to store the plots
saveFolderName = 'data_post/plots/';
if (~exist(['./',saveFolderName],'dir'))
    mkdir(['./',saveFolderName]);
end

%% Save the plots
for imgIndex = 1 : 3*length(cfdLinkNames)+3
    
    fig   = figure(imgIndex);
    title = get(gca,'title');
    yVar  = get(gca,'YLabel');
    if ~contains(title.String,'iRonCub')
        saveas(fig,[saveFolderName,title.String,'_C',yVar.String(4),'.svg'])
    else
        saveas(fig,[saveFolderName,'ironcub_C',yVar.String(4),'.svg'])
    end

end

