% Author: Antonello Paolino
%
% November 2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;
clear all;
clc;

%% Initialization

% Experiment and test to be mapped
experiment      = 'exp_03_11_22';   % 'exp_21_03_22' | 'exp_03_11_22'
robotName       = 'iRonCub-Mk1';

% Path definition
if matches(robotName,'iRonCub-Mk1')
    ironcubSoftwarePath  = getenv('IRONCUB_SOFTWARE_SOURCE_DIR');
elseif matches(robotName,'iRonCub-Mk3')
    ironcubSoftwarePath  = getenv('IRONCUB_COMPONENT_SOURCE_DIR');
end
windTunnelDataPath  = ['../',experiment,'/data_GVPM/'];
matlabDataPath      = ['../',experiment,'/data_Matlab/'];
coversPath          = ['./srcPressureAnalysis/',robotName,'/covers/'];
sensorsMapPath      = ['./srcPressureAnalysis/',robotName,'/sensorsMapping/'];
sensorsPlotPath     = ['./srcPressureAnalysis/',robotName,'/sensorsPlotting/'];

% get the list of all the tests
testList        = dir([windTunnelDataPath,'/*.GVP']);  % List of the test files

for testIndex = 51%:length(testList(:,1))

    testID = testList(testIndex).name(1:end-4);

    %% Import data

    % adding the main folder path
    testpointList   = dir([windTunnelDataPath,'/',testID,'*.pth']);
    test.(testID) = load([matlabDataPath,testID,'/aerodynamicForces.mat']);  % test data loading

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
        testPoint.(testPointID) = load([matlabDataPath,testID,'/pressureSensorsData/',testPointID,'.mat']);  % test point data loading
        % assigning the max and min values
        pressArray    = struct2array(testPoint.(testPointID).pressureSensors.meanValues);
        maxPointPress = max(pressArray);
        minPointPress = min(pressArray);
        % update test max and min pressures
        if maxPointPress > testMaxPress, testMaxPress = maxPointPress; end
        if minPointPress < testMinPress, testMinPress = minPointPress; end
    end

    %% Interpolation variables
    
    deltaAngleInterp = 1; % [deg]

    if matches(configSet,'hovering')
        deltaAngleTest = abs(test.(testID).state.betaDes(2) - test.(testID).state.betaDes(1));
    else
        deltaAngleTest = abs(test.(testID).state.alphaDes(2) - test.(testID).state.alphaDes(1));
    end
    N_interp_points  = round(deltaAngleTest/deltaAngleInterp);
    N_testPoints     = length(fieldnames(testPoint));
    N_total_points   = N_interp_points * (N_testPoints - 1) + 1;
    

    %% Start point cycle
    for testPointIndex = 1 : N_total_points

        % close scopes and clear previous test point data
        close all;
        clearvars -except *Path testPointIndex jointConfig testID testpointList ...
            experiment testMaxPress testMinPress configSet configName jointPos ...
            testList N_interp_points N_total_points test deltaAngleInterp
        
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
        testPoint.(lowerTestPointID) = load([matlabDataPath,testID,'/pressureSensorsData/',lowerTestPointID,'.mat']);  % lower test point data loading
        testPoint.(upperTestPointID) = load([matlabDataPath,testID,'/pressureSensorsData/',upperTestPointID,'.mat']);  % upper test point data loading

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
        yawAngle   = interp1([lowerIndex upperIndex],test.(testID).state.betaDes([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1);
        pitchAngle = interp1([lowerIndex upperIndex],test.(testID).state.alphaDes([lowerIndex upperIndex]),(testPointIndex-1)/N_interp_points + 1) + offsetAngle;

        % set base Pose according to yaw and pitch angles
        R_yaw     = rotz(yawAngle);
        R_pitch   = roty(pitchAngle - 90);
        basePose  = [R_yaw * R_pitch, [10; 0; 0];
                          zeros(1,3),         1];

        % data for using iDynTreeWrappers functions
        modelPath  = [ironcubSoftwarePath,'/models/iRonCub-Mk1/iRonCub/robots/iRonCub-Mk1_Gazebo/'];
        fileName   = 'model_stl.urdf';
        meshFilePrefix = [ironcubSoftwarePath,'/models'];
        jointNames = {'torso_pitch','torso_roll','torso_yaw', 'l_shoulder_pitch', 'l_shoulder_roll','l_shoulder_yaw', ...
                      'l_elbow', 'r_shoulder_pitch', 'r_shoulder_roll','r_shoulder_yaw','r_elbow', 'l_hip_pitch', 'l_hip_roll', ...
                      'l_hip_yaw','l_knee','l_ankle_pitch','l_ankle_roll', 'r_hip_pitch','r_hip_roll','r_hip_yaw','r_knee','r_ankle_pitch','r_ankle_roll'};
        jointVel = zeros(23,1);
        baseVel  = zeros(6,1);
        gravAcc  = [0; 0; 9.81];

        % idyntree initialization
        KinDynModel = iDynTreeWrappers.loadReducedModel(jointNames, 'root_link', modelPath, fileName, false);
        iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);
        
        % Set import file options
        opts = detectImportOptions([sensorsMapPath,'chest_sensors.txt']);

        for j = 1:length(coverNames)

            %% Load geometric data
            coverName = coverNames{j};
            coverData.(coverName).geom = stlread([coversPath,coverName,'.stl']);
            pressureSensors = table2struct(readtable([sensorsMapPath,coverName,'_sensors.txt'],opts),"ToScalar",true);
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
        if matches(configSet,'hovering')
            xPlotVariable = test.(testID).state.betaDes;
            interpXPlotVariable = (test.(testID).state.betaDes(1):deltaAngleInterp:test.(testID).state.betaDes(end))';
            xPlotLabel    = '$\beta$';
        else
            xPlotVariable = test.(testID).state.alphaDes + offsetAngle;
            interpXPlotVariable = (test.(testID).state.alphaDes(1):deltaAngleInterp:test.(testID).state.alphaDes(end))' + offsetAngle;
            xPlotLabel    = '$\alpha$';
        end
        
        interpolatedDragForceCoeff = interp1(xPlotVariable,test.(testID).windAxesAero.dragForceCoeff,interpXPlotVariable,'pchip');
        interpolatedLiftForceCoeff = interp1(xPlotVariable,test.(testID).windAxesAero.liftForceCoeff,interpXPlotVariable,'pchip');
        interpolatedSideForceCoeff = interp1(xPlotVariable,test.(testID).windAxesAero.sideForceCoeff,interpXPlotVariable,'pchip');

        

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

        % Set wind vector properties
        windVector.Position   = [8.9 0 0];
        windVector.Components = [0.3 0 0];
        windVector.Color      = [0 0.75 1];        

        % Draw wind velocity vector
        arrow3d(windVector.Position, windVector.Components, windVector.Color);

        % Display wind velocity vector name
        text(0.35*windVector.Components(1) + windVector.Position(1),0,0.07,'$V_w$','Interpreter','latex','FontSize',48,'Color',windVector.Color);

        % Draw aerodynamic force
%         arrow3d(basePose(1:3,4), 4*[interpolatedDragForceCoeff(testPointIndex) interpolatedLiftForceCoeff(testPointIndex) interpolatedSideForceCoeff(testPointIndex)], [1 1 0], 0.006);


        axis([8.5 11 -1 1 -0.7 0.7])
        set(fig1, 'Position', [0 0 3840 2160]);
        grid off;
        title(['Pressure map, ',configSet,'-',configName,', $\alpha=',num2str(round(pitchAngle),'%.0f'),'^\circ$, $\beta=',num2str(round(yawAngle),'%.0f'),'^\circ$'],'FontSize',22,'Interpreter','latex');
        
        % Set colors
        fig1.Color = [0,0,0];
        set(gcf, 'InvertHardCopy', 'off'); 

        ax = gca;
        ax.Position = [0.05,-0.2,1,1.4]; % [-0.2,-0.2,1.2,1.4]

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
        

        %%  set colormap and colorbar 
        cmap = colormap("jet");

        %caxis([round(testMinPress) round(testMaxPress)])
        caxis([-203 173])
        c = colorbar('FontSize', 16, 'Location', 'east');
        c.Position          = [0.9 0.135 0.02 0.68];
        c.AxisLocation      = 'in';
        c.Color             = [1,1,1];
        c.FontSize          = 32;
        c.Label.String      = '$\Delta p$ [Pa]';
        c.Label.FontSize    = 48;
        c.Label.Interpreter = 'latex';
        c.Label.Rotation    = 0;
        c.Label.Units       = 'normalized';
        c.Label.Position    = [0.5 1.08 0]; % to change its position

        %% Forces plots
%         if matches(configSet,'hovering')
%             xPlotVariable = test.(testID).state.betaDes;
%             interpXPlotVariable = (test.(testID).state.betaDes(1):deltaAngleInterp:test.(testID).state.betaDes(end))';
%             xPlotLabel    = '$\beta$';
%         else
%             xPlotVariable = test.(testID).state.alphaDes + offsetAngle;
%             interpXPlotVariable = (test.(testID).state.alphaDes(1):deltaAngleInterp:test.(testID).state.alphaDes(end))' + offsetAngle;
%             xPlotLabel    = '$\alpha$';
%         end
%         
%         
%         interpolatedDragForceCoeff = interp1(xPlotVariable,test.(testID).windAxesAero.dragForceCoeff,interpXPlotVariable,'pchip');
%         interpolatedLiftForceCoeff = interp1(xPlotVariable,test.(testID).windAxesAero.liftForceCoeff,interpXPlotVariable,'pchip');
%         interpolatedSideForceCoeff = interp1(xPlotVariable,test.(testID).windAxesAero.sideForceCoeff,interpXPlotVariable,'pchip');

        % Drag area plot
        axes()
        box on
        plot(interpXPlotVariable(1:testPointIndex), interpolatedDragForceCoeff(1:testPointIndex), 'Color', 'green', ...
            'LineStyle', '-', 'linewidth', 2, 'DisplayName','$C_D A$'); hold on;
        scatter(interpXPlotVariable(testPointIndex), interpolatedDragForceCoeff(testPointIndex), ...
            45, 'green', 'filled', 'HandleVisibility', 'off'); hold on;
        grid on;
        axis([min(xPlotVariable) max(xPlotVariable) 0.01*floor(min(100*test.(testID).windAxesAero.dragForceCoeff)) 0.01*ceil(max(100*test.(testID).windAxesAero.dragForceCoeff))])
        xlabel(xPlotLabel,'Interpreter','latex','FontSize',20)
        legend('Interpreter','latex','Location','nw','FontSize',20,'Color',[0,0,0],'TextColor',[1,1,1])
        legend show

        ax2 = gca;
        ax2.Position = [.03 .6 .22 .25];
        ax2.Color  = [0,0,0];
        ax2.XColor = [1,1,1];
        ax2.YColor = [1,1,1];
        ax2.ZColor = [1,1,1];
        ax2.GridLineStyle = '--';
        ax2.Box = 'off';


        % Lift and side force areas
        axes()
        box on
        plot(interpXPlotVariable(1:testPointIndex), interpolatedLiftForceCoeff(1:testPointIndex), 'Color', 'white', ...
            'LineStyle', '-', 'linewidth', 2, 'DisplayName','$C_L A$'); hold on;
        plot(interpXPlotVariable(1:testPointIndex), interpolatedSideForceCoeff(1:testPointIndex), 'Color', 'magenta', ...
            'LineStyle', '-', 'linewidth', 2, 'DisplayName','$C_S A$'); hold on;
        scatter(interpXPlotVariable(testPointIndex), interpolatedLiftForceCoeff(testPointIndex), ...
            45, 'white', 'filled', 'HandleVisibility', 'off'); hold on;
        scatter(interpXPlotVariable(testPointIndex), interpolatedSideForceCoeff(testPointIndex), ...
            45, 'magenta', 'filled', 'HandleVisibility', 'off'); hold on;
        grid on;
        axis([min(xPlotVariable) max(xPlotVariable) 0.01*floor(min(100*[test.(testID).windAxesAero.liftForceCoeff; test.(testID).windAxesAero.sideForceCoeff])) ...
            0.01*ceil(max(100*[test.(testID).windAxesAero.liftForceCoeff; test.(testID).windAxesAero.sideForceCoeff]))])
        xlabel(xPlotLabel,'Interpreter','latex','FontSize',20)
        legend('Interpreter','latex','Location','e','FontSize',20,'Color',[0,0,0],'TextColor',[1,1,1])
        legend show

        ax3 = gca;
        ax3.Position = [.03 .2 .22 .25];
        ax3.Color  = [0,0,0];
        ax3.XColor = [1,1,1];
        ax3.YColor = [1,1,1];
        ax3.ZColor = [1,1,1];
        ax3.GridLineStyle = '--';
        ax3.Box = 'off';

        %% saving
        % saveas(fig1,['.\',saveFolderName,'\',coverName,'-',testID,'-',testPointID,'.svg']);
        saveFolderName = ['pressure_fancy_fig-',experiment];
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
% rmpath(genpath('../'));            % Adding the main folder path