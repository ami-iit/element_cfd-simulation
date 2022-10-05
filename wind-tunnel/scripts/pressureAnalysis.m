close all; 
clear all; 
clc;

%% Initialization

% Test and point to be analyzed
testID = {'TID_0002'};
testPointID = {'PT0001'};
coverNames = {'face_front','chest','rt_thigh_front','lt_thigh_front', ...
              'rt_shin_front','lt_shin_front'};

globalMinPress = 1e4;
globalMaxPress = -1e4;

for j = 1:length(coverNames)

    %% Load geometric data
    coverName = coverNames{j};
    geom = importGeometry(['./srcPressureAnalysis/',coverName,'.stl']);
    opts = detectImportOptions('./srcPressureAnalysis/chest_sensors.txt');
    pressureSensors = table2struct(readtable(['./srcPressureAnalysis/',coverName,'_sensors.txt'],opts),"ToScalar",true);
    pressureSensorsNames = pressureSensors.Var1;
    x_pressureSensors    = pressureSensors.Var2;
    y_pressureSensors    = pressureSensors.Var3;
    z_pressureSensors    = pressureSensors.Var4;

    %% LOAD PRESSURE DATA
    addpath(genpath('../'));            % Adding the main folder path
    experiment = 'exp_21_03_22';        % Name of the experiment data folder
    folderPath = ['../',experiment,'/data_Matlab/'];    % Path to the experiment data folder
    testPoint.(testPointID{1}) = load([folderPath,testID{1},'/pressureSensorsData/',testPointID{1},'.mat']);  % test point loading

    % assign pressure values data
    meanPressValues = zeros(length(pressureSensorsNames),1);
    pressValues     = zeros(length(pressureSensorsNames),length(testPoint.(testPointID{1}).pressureSensors.time));
    for i = 1:length(meanPressValues)
        meanPressValues(i) = testPoint.(testPointID{1}).pressureSensors.meanValues.(pressureSensorsNames{i});
        pressValues(i,:)   = testPoint.(testPointID{1}).pressureSensors.values.(pressureSensorsNames{i});
    end
    
    localMinPress = min(min(pressValues));
    localMaxPress = max(max(pressValues));
    fprintf([coverName,' pressure range: ',num2str(localMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(localMaxPress,3),' [Pa] \n']);

    if localMinPress < globalMinPress
        globalMinPress = localMinPress;
    end
    if localMaxPress > globalMaxPress
        globalMaxPress = localMaxPress;
    end

    %% DATA PLOTTING INITIALIZATION
    % initialize generic sphere coordinates
    [X,Y,Z] = sphere;
    radius  = 3;
    
    
    %% PLOT PRESSURE MAP
    fig = figure();
    h = pdegplot(geom); hold on     % plot geometry
    cmap = colormap("jet");         % initialize colormap
    cmap = interp1(linspace(min(meanPressValues),max(meanPressValues),length(cmap)),cmap,meanPressValues);
    for i=1:length(x_pressureSensors)
        surf(X*radius + x_pressureSensors(i), Y*radius + y_pressureSensors(i), Z*radius + z_pressureSensors(i), ...
            'FaceColor',cmap(i,:),'EdgeColor','none','FaceLighting','none');
    end
    if contains(coverName,'face_front')
        axis([-100 100 -100 150 0 150])
    else
        axis([-100 100 -150 100 0 150])
    end
    colorbar
    caxis([min(meanPressValues) max(meanPressValues)])
    title(coverName,'Interpreter','none')
    
    if contains(coverName,'lt_thigh_front') || contains(coverName,'lt_shin_front') || contains(coverName,'face_back')
        view(180,270); light('Position',[1,1,-1]);   % lt_thigh_front, lt_shin_front
        else
            if contains(coverName,'lt_arm_front')
                view(0,0); light('Position',[1,-1,1]);
            else
                view(0,90); light();                         % other cases
            end
    end
    
    saveas(fig,['.\postProcess\',coverName,'-',testID{1},'-',testPointID{1},'.svg']);

    %% PLOT TIME-VARYING PRESSURES
    fig = figure();
    for i = 1:length(meanPressValues)
        plot(testPoint.(testPointID{1}).pressureSensors.time,pressValues(i,:),"Color",cmap(i,:)); hold on;
    end
    grid on;
    ylabel('$\Delta p$ [Pa]','Interpreter','latex')
    xlabel('$t$ [s]','Interpreter','latex')
    title(coverName,'Interpreter','none')

    saveas(fig,['.\postProcess\',coverName,'-',testID{1},'-',testPointID{1},'-plot.svg']);
end

%% DATA REPORTING
fprintf(['rt_foot \x394p = ',num2str(testPoint.(testPointID{1}).pressureSensors.meanValues.S1,3),' [Pa] \n']);
fprintf(['lt_foot \x394p = ',num2str(testPoint.(testPointID{1}).pressureSensors.meanValues.S3,3),' [Pa] \n\n']);
fprintf(['Global pressure range: ',num2str(globalMinPress,3),' [Pa] \x2264 \x394p \x2264 ',num2str(globalMaxPress,3),' [Pa] \n']);
fprintf(['Total acquisition time: \x394T = ',num2str(testPoint.(testPointID{1}).pressureSensors.time(end),3),' [s] \n']);


%% Remove from path

rmpath(genpath('../'));            % Adding the main folder path