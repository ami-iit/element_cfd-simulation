% Author: Antonello Paolino
%
% November 2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;
clear all;
clc;

%% Initialization

% Experiment and test to be mapped
experiment  = 'exp_03_11_22';   % 'exp_21_03_22' | 'exp_03_11_22'
addpath(genpath('../'));    
GVPM_folderPath = ['../',experiment,'/data_GVPM'];
testList = dir([GVPM_folderPath,'/*.GVP']);  % List of the test files

for testIndex = 1%:length(testList(:,1))

    testID = testList(testIndex).name(1:end-4);

    %% Import data

    % adding the main folder path
    GVPM_folderPath = ['../',experiment,'/data_GVPM'];
    testpointList   = dir([GVPM_folderPath,'/',testID,'*.pth']);

    % Import robot joint positions
    testConfig = readcell(['./srcPressureAnalysis/localConfigurations/',experiment,'-test-config.csv']);
    configSet  = (testConfig{matches(testConfig(:),testID),2});
    configName = (testConfig{matches(testConfig(:),testID),3});

    % Assign the joints configuration relative to the test
    jointPosData = importdata(['./srcPressureAnalysis/localConfigurations/',experiment,'-',configSet,'-config.csv']);
    jointPos     = jointPosData.data(matches(jointPosData.textdata(:),configName),:) * pi/180;

    %% Find test total pressure range

    % Initialize min and max values
    testMaxPress = -1e4;
    testMinPress = 1e4;

    for testPointIndex = 1 : (length(testpointList(:,1)) - 1)
        % loading the workspaces for each test point
        [~,testPointID,~]       = fileparts(testpointList(testPointIndex,:).name(10:15));
        wsFolderPath            = ['../',experiment,'/data_Matlab/'];
        testPoint.(testPointID) = load([wsFolderPath,testID,'/pressureSensorsData/',testPointID,'.mat']);  % test point data loading
        % assigning the max and min values
        pressArray    = struct2array(testPoint.(testPointID).pressureSensors.meanValues);
        maxPointPress = max(pressArray);
        minPointPress = min(pressArray);
        % update test max and min pressures
        if maxPointPress > testMaxPress, testMaxPress = maxPointPress; end
        if minPointPress < testMinPress, testMinPress = minPointPress; end
    end

    %% Start point cycle

    N_interp_points = 10;
    N_total_points  = (N_interp_points - 1 ) * (length(testpointList(:,1)) - 1) + 1;

    for testPointIndex = 1 : N_total_points

        % close scopes and clear previous test point data
        close all;
        clearvars -except testPointIndex jointConfig testID testpointList ...
            experiment testMaxPress testMinPress configSet configName jointPos ...
            testList N_interp_points N_total_points
        
        % Interpolated indices
        lowerIndex = floor((testPointIndex-1)/N_interp_points + 1);
        upperIndex = ceil((testPointIndex-1)/N_interp_points + 1);

        if lowerIndex == upperIndex && testPointIndex<N_total_points
            upperIndex = upperIndex + 1;
        elseif lowerIndex == upperIndex && testPointIndex==N_total_points
            lowerIndex = lowerIndex - 1;
        end
        
        [~,lowerTestPointID,~] = fileparts(testpointList(lowerIndex,:).name(10:15));
        [~,upperTestPointID,~] = fileparts(testpointList(upperIndex,:).name(10:15));

        % Load data from matlab workspaces
        wsFolderPath            = ['../',experiment,'/data_Matlab/'];
        test.(testID)           = load([wsFolderPath,testID,'/aerodynamicForces.mat']);                                 % test data loading
        testPoint.(lowerTestPointID) = load([wsFolderPath,testID,'/pressureSensorsData/',lowerTestPointID,'.mat']);  % lower test point data loading
        testPoint.(upperTestPointID) = load([wsFolderPath,testID,'/pressureSensorsData/',upperTestPointID,'.mat']);  % upper test point data loading

        % Names of the covers and relative frames
        coverNames = {'face_front','face_back','chest','backpack','pelvis','lt_pelvis_wing','rt_pelvis_wing',...
            'rt_arm_front','rt_arm_rear','lt_arm_front','lt_arm_rear', ...
            'rt_thigh_front','rt_thigh_rear','lt_thigh_front','lt_thigh_rear',...
            'rt_shin_front','rt_shin_rear','lt_shin_front','lt_shin_rear'};
        frameNames = {'head','head','chest','chest','root_link','root_link','root_link', ...
            'r_upper_arm','r_upper_arm','l_upper_arm','l_upper_arm', ...
            'r_upper_leg','r_upper_leg','l_upper_leg','l_upper_leg', ...
            'r_lower_leg','r_lower_leg','l_lower_leg','l_lower_leg'};

        % Initialize support angle
        if matches(configSet,'hovering')
            offsetAngle = 90;   % [deg]
        elseif matches(configSet,'flight')
            offsetAngle = 45;   % [deg]
        end
        
        % robot attitude angles in wind tunnel
        yawAngle   = interp1([lowerIndex upperIndex],test.(testID).state.betaMeas([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
        pitchAngle = interp1([lowerIndex upperIndex],test.(testID).state.alphaMeas([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1) + offsetAngle;

        % set base Pose according to yaw and pitch angles
        R_yaw     = rotz(yawAngle);
        R_pitch   = roty(pitchAngle - 90);
        basePose  = [R_yaw * R_pitch, [10; 0; 0];
                          zeros(1,3),         1];

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
            coverData.(coverName).geom = stlread(['./srcPressureAnalysis/covers/',coverName,'.stl']);
            opts = detectImportOptions('./srcPressureAnalysis/sensorsMapping/chest_sensors.txt');
            pressureSensors = table2struct(readtable(['./srcPressureAnalysis/sensorsMapping/',coverName,'_sensors.txt'],opts),"ToScalar",true);
            coverData.(coverName).sensorsNames = pressureSensors.Var1;
            coverData.(coverName).x_sensors    = pressureSensors.Var2;
            coverData.(coverName).y_sensors    = pressureSensors.Var3;
            coverData.(coverName).z_sensors    = pressureSensors.Var4;

            % assign cover pressure values data
            for i = 1:length(coverData.(coverName).sensorsNames)
                lowerMeanPress = testPoint.(lowerTestPointID).pressureSensors.meanValues.(coverData.(coverName).sensorsNames{i});
                upperMeanPress = testPoint.(upperTestPointID).pressureSensors.meanValues.(coverData.(coverName).sensorsNames{i});
                coverData.(coverName).meanPressValues(i,1) = interp1([lowerIndex upperIndex]*ones(1,length(testPoint.(lowerTestPointID).pressureSensors.meanValues.(coverData.(coverName).sensorsNames{i}))), ...
                                                              [testPoint.(lowerTestPointID).pressureSensors.meanValues.(coverData.(coverName).sensorsNames{i}) ...
                                                              testPoint.(upperTestPointID).pressureSensors.meanValues.(coverData.(coverName).sensorsNames{i})], ...
                                                              (testPointIndex-1)/N_interp_points + 1 );
                %coverData.(coverName).pressValues(i,:)   = testPoint.(testPointID).pressureSensors.values.(coverData.(coverName).sensorsNames{i});
            end

            localMinPress = min(coverData.(coverName).meanPressValues);
            localMaxPress = max(coverData.(coverName).meanPressValues);
            %         fprintf([coverName,' pressure range: ',num2str(localMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(localMaxPress,3),' [Pa] \n']);

            if localMinPress < globalMinPress
                globalMinPress = localMinPress;
            end
            if localMaxPress > globalMaxPress
                globalMaxPress = localMaxPress;
            end


            %% Pressure map initialization

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

        %% robot visualization
        iDynTreeWrappers.prepareVisualization(KinDynModel, meshFilePrefix, 'color', [0.96,0.96,0.96], ...
            'material', 'dull', ... 'style', 'wireframe','wireframe_rendering',0.8, ...
            'transparency', 0.3, 'debug', true, 'view', [-45 5]);

        %% Pressure map plot
        fig1 = figure(1);
        for j = 1:length(coverNames)
            % plot the cover surface interpolated contour
            coverData.(coverNames{j}).interpPressValues = coverData.(coverNames{j}).interpFunction(coverData.(coverNames{j}).geom.Points);
            p = patch('Faces',coverData.(coverNames{j}).patchFaces,'Vertices',coverData.(coverNames{j}).patchPoints,...
                'FaceVertexCData',coverData.(coverNames{j}).interpPressValues,'FaceColor','interp','EdgeColor','none'); hold on;
        end

        % Set arrow sizes
        cylPosition   = 9;
        cylRadius     = 0.01;
        cylLength     = 0.25;
        arrowRatio    = 0.2;

        % Draw wind velocity vector
        [Xc,Yc,Zc] = cylinder(cylRadius);
        Zc         = Zc * cylLength;
        surf(Zc + cylPosition,Yc,Xc,'FaceColor',[0, 0.4470, 0.7410],'EdgeColor','none');
        patch(Zc(1,:) + cylPosition,Yc(1,:),Xc(1,:),[0, 0.4470, 0.7410]);
        Yh(1,:) = Yc(1,:)*2;
        Yh(2,:) = Yc(2,:)*0;
        Xh(1,:) = Xc(1,:)*2;
        Xh(2,:) = Xc(2,:)*0;
        Zh      = Zc * arrowRatio;
        surf(Zh + cylPosition + cylLength,Yh,Xh,'FaceColor',[0, 0.4470, 0.7410],'EdgeColor','none');
        patch(Zh(1,:) + cylPosition + cylLength,Yh(1,:),Xh(1,:),[0, 0.4470, 0.7410]);

        % Assign wind velocity vector name
        text(0.35*cylLength + cylPosition,0,0.05,'$V_w$','Interpreter','latex','FontSize',24);


        axis([9 11 -1 1 -1 1])
        set(fig1, 'Position', [0 0 2304 1296]);

        title(['Pressure map, ',configSet,'-',configName,', $\alpha=',num2str(round(pitchAngle),'%.0f'),'^\circ$, $\beta=',num2str(round(yawAngle),'%.0f'),'^\circ$'],'FontSize',22,'Interpreter','latex');

        ax = gca;
        ax.Position(1) = ax.Position(1) + 0.05;

        cmap = colormap("jet");

        %%  set colorbar
        caxis([round(testMinPress) round(testMaxPress)])
        c                   = colorbar('FontSize', 16, 'Location', 'east');
        if round(testMinPress) ~= c.Ticks(1)
            c.Ticks = [round(testMinPress) c.Ticks];
        elseif round(testMaxPress) ~= c.Ticks(end)
            c.Ticks = [c.Ticks round(testMaxPress)];
        end
        c.Position          = [0.9 0.135 0.025 0.68];
        c.AxisLocation      = 'in';
        c.Label.String      = '$\Delta p$ [Pa]';
        c.Label.FontSize    = 22;
        c.Label.Interpreter = 'latex';
        c.Label.Rotation    = 0;
        c.Label.Units       = 'normalized';
        c.Label.Position    = [0.5 1.08 0]; % to change its position

        %% Forces plots
        if matches(configSet,'hovering')
            xPlotVariable = test.(testID).state.betaMeas;
            xPlotLabel    = '$\beta$';
            xMarkerAngle  = yawAngle;
            dragValue  = interp1([lowerIndex upperIndex],test.(testID).windAxesAero.dragForceCoeff([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
            liftValue  = interp1([lowerIndex upperIndex],test.(testID).windAxesAero.liftForceCoeff([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
            sideValue  = interp1([lowerIndex upperIndex],test.(testID).windAxesAero.sideForceCoeff([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
        else
            xPlotVariable = test.(testID).state.alphaMeas + offsetAngle;
            xPlotLabel    = '$\alpha$';
            xMarkerAngle  = pitchAngle;
            dragValue  = interp1([lowerIndex upperIndex],test.(testID).windAxesAero.dragForceCoeff([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
            liftValue  = interp1([lowerIndex upperIndex],test.(testID).windAxesAero.liftForceCoeff([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
            sideValue  = interp1([lowerIndex upperIndex],test.(testID).windAxesAero.sideForceCoeff([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
        end

        

        % Drag area plot
        axes('Position',[.03 .6 .22 .25])
        box on
        plot(xPlotVariable, test.(testID).windAxesAero.dragForceCoeff, 'Color', 'k', ...
            'LineStyle', '-', 'linewidth', 1.5, 'DisplayName','$C_D A$'); hold on;
        scatter(xMarkerAngle, dragValue, ...
            30, 'red', 'filled', 'HandleVisibility', 'off'); hold on;
        grid on;
        xlim([min(xPlotVariable) max(xPlotVariable)])
        xlabel(xPlotLabel,'Interpreter','latex')
        legend('Interpreter','latex','Location','best')
        legend show

        % Lift and side force areas
        axes('Position',[.03 .2 .22 .25])
        box on
        plot(xPlotVariable, test.(testID).windAxesAero.liftForceCoeff, 'Color', 'b', ...
            'LineStyle', '-', 'linewidth', 1.5, 'DisplayName','$C_L A$'); hold on;
        plot(xPlotVariable, test.(testID).windAxesAero.sideForceCoeff, 'Color', 'y', ...
            'LineStyle', '-', 'linewidth', 1.5, 'DisplayName','$C_S A$'); hold on;
        scatter(xMarkerAngle, liftValue, ...
            30, 'red', 'filled', 'HandleVisibility', 'off'); hold on;
        scatter(xMarkerAngle, sideValue, ...
            30, 'red', 'filled', 'HandleVisibility', 'off'); hold on;
        grid on;
        xlim([min(xPlotVariable) max(xPlotVariable)])
        xlabel(xPlotLabel,'Interpreter','latex')
        legend('Interpreter','latex','Location','best')
        legend show


        %% saving
        % saveas(fig1,['.\',saveFolderName,'\',coverName,'-',testID,'-',testPointID,'.svg']);

        saveFolderName = ['pressure_interp_fig-',experiment];
        if (~exist(['./',saveFolderName],'dir'))

            mkdir(['./',saveFolderName]);
        end
        saveas(fig1,['.\',saveFolderName,'\',testID,'-',num2str(testPointIndex,'%04.f'),'.fig']);


        %% Report additional data
        %     fprintf(['rt_foot \x394p = ',num2str(testPoint.(testPointID).pressureSensors.meanValues.S1,3),' [Pa] \n']);
        %     fprintf(['lt_foot \x394p = ',num2str(testPoint.(testPointID).pressureSensors.meanValues.S3,3),' [Pa] \n\n']);
        %     fprintf(['Global pressure range: ',num2str(globalMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(globalMaxPress,3),' [Pa] \n']);
        %     fprintf(['Total acquisition time: \x394T = ',num2str(testPoint.(testPointID).pressureSensors.time(end),3),' [s] \n']);

    end
end

%% Remove path
rmpath(genpath('../'));            % Adding the main folder path