close all;
clear all;
clc;

%% Initialization

% Test and point to be analyzed
experiment  = 'exp_2023_12_11'; % Experiment: exp_2022_03_21 | exp_2022_11_03 | exp_2023_12_11
robotName   = 'iRonCub-Mk3';
testID      = 'TID_0001';
testPointID = 'PT0001';

% Path definition
matlabDataPath      = ['../',experiment,'/data_Matlab/'];
sensorsDirPath      = ['./srcPressureAnalysis/',robotName,'/sensorsPlotting/'];

%% Import filename list and add local path
% Load pressure data 
testPoint.(testPointID) = load([matlabDataPath,testID,'/pressureSensorsData/',testPointID,'.mat']);  % test point data loading

% Names of the covers and relative frames
coverList = dir([sensorsDirPath,'*.txt']);  % List of the covers files
              
% Initizalizing global values
globalMinPress = 1e4;
globalMaxPress = -1e4;

% Set file importing options
opts = detectImportOptions([sensorsDirPath,'chest_sensors_plotting.txt']);

for j = 1:length(coverList)

    %% Load cover data
    coverFileName   = coverList(j).name;
    coverName       = coverFileName(1:end-21);
    pressureSensors = table2struct(readtable([sensorsDirPath,coverFileName],opts),"ToScalar",true);
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

    for i = 1 : nSensors    % Plot the sensors data and print sensors name on plot
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

    % save pressure plot images
    saveFolder = ['./pressure-plots/',experiment,'/'];
    if (~exist(saveFolder,'dir'))
        mkdir(saveFolder);
    end
    fileName = [testID,'-',testPointID,'-',coverName,'-plot.svg'];
    saveas(fig,[saveFolder,fileName]);


end % end of cover iteration

%% Report additional data
fprintf(['Global pressure range: ',num2str(globalMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(globalMaxPress,3),' [Pa] \n']);
fprintf(['Total acquisition time: \x394T = ',num2str(testPoint.(testPointID).pressureSensors.time(end),3),' [s] \n']);