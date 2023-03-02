close all;
clear all;
clc;

%% Initialization

% Test and point to be analyzed
experiment  = 'exp_21_03_22'; % Experiment data {exp_21_03_22, exp_28_10_22}
testID      = 'TID_0002';
testPointID = 'PT0010';
jointConfig = 'hovering'; % | hovering | flight30 | flight50 | flight60 |


%% Import filename list and add local path
addpath(genpath('../'));            % Adding the main folder path
folderPath    = ['../',experiment,'/data_GVPM'];
testpointList = dir([folderPath,'/',testID,'*.pth']);

% close scopes and clear previous test point data
close all;
clearvars -except testPointIndex jointConfig testID testpointList testPointID ...
    experiment folderPath

% Load data
folderPath    = ['../',experiment,'/data_Matlab/'];
testPoint.(testPointID) = load([folderPath,testID,'/pressureSensorsData/',testPointID,'.mat']);  % test point data loading

% Names of the covers and relative frames
coverNames = {'face_front','face_back','chest','backpack','pelvis','lt_pelvis_wing','rt_pelvis_wing',...
    'rt_arm_front','rt_arm_rear','lt_arm_front','lt_arm_rear', ...
    'rt_thigh_front','rt_thigh_rear','lt_thigh_front','lt_thigh_rear',...
    'rt_shin_front','rt_shin_rear','lt_shin_front','lt_shin_rear'};

% Initizalizing global values
globalMinPress = 1e4;
globalMaxPress = -1e4;

for j = 1:length(coverNames)

    %% Load cover data
    coverName = coverNames{j};
    opts = detectImportOptions('./srcPressureAnalysis/sensorsPlotting/chest_sensors_plotting.txt');
    pressureSensors = table2struct(readtable(['./srcPressureAnalysis/sensorsPlotting/',coverName,'_sensors_plotting.txt'],opts),"ToScalar",true);
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


    %% Time-varying pressures plot
    fig  = figure();
    cmap = colormap('hsv');
    nSensors = length(coverData.(coverName).meanPressValues(:,1));
    color = interp1(linspace(0,nSensors,length(cmap(:,1))), cmap, 1:nSensors);

    for i = 1 : nSensors
        plot(testPoint.(testPointID).pressureSensors.time,coverData.(coverName).pressValues(i,:), ...
            'Color',color(i,:),'DisplayName',coverData.(coverName).sensorsNames{i}); hold on;
        text(testPoint.(testPointID).pressureSensors.time(end),coverData.(coverName).pressValues(i,end), ...
            coverData.(coverName).sensorsNames{i},'Color',color(i,:));
    end
    grid on;
    ylabel('$\Delta p$ [Pa]','Interpreter','latex')
    xlabel('$t$ [s]','Interpreter','latex')
    title(coverName,'Interpreter','none')
%     legend('Location','best')

    %         % saving
    %         saveFolderName = 'postProcessPressureAnalysis';
    %         if (~exist(['./',saveFolderName],'dir'))
    %
    %             mkdir(['./',saveFolderName]);
    %         end
    %         saveas(fig2,['.\',saveFolderName,'\',coverName,'-',testID,'-',testPointID,'-plot.svg']);


end % end of cover iteration

%% Report additional data
fprintf(['rt_foot \x394p = ',num2str(testPoint.(testPointID).pressureSensors.meanValues.S1,3),' [Pa] \n']);
fprintf(['lt_foot \x394p = ',num2str(testPoint.(testPointID).pressureSensors.meanValues.S3,3),' [Pa] \n\n']);
fprintf(['Global pressure range: ',num2str(globalMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(globalMaxPress,3),' [Pa] \n']);
fprintf(['Total acquisition time: \x394T = ',num2str(testPoint.(testPointID).pressureSensors.time(end),3),' [s] \n']);

%% Remove path
rmpath(genpath('../'));            % Adding the main folder path