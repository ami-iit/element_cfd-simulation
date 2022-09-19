% close all; 
% clear all; 
% clc;

%% Load geometric data

coverName = 'rt_shin_front';

geom = importGeometry(['./srcPressureAnalysis/',coverName,'.stl']);
pressureSensors = table2struct(readtable(['./srcPressureAnalysis/',coverName,'_sensors.txt']),"ToScalar",true);
pressureSensorsNames = pressureSensors.Var1;
x_pressureSensors    = pressureSensors.Var2;
y_pressureSensors    = pressureSensors.Var3;
z_pressureSensors    = pressureSensors.Var4;

%% Load pressure data
addpath(genpath('../../'));            % Adding the main folder path
experiment = 'exp_21_03_22';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_Matlab/'];

% Name of the test and test points to be loaded
testID = {'TID_0002'};
testPointIDs = {'PT0001'};

% load a single point data
testPoint.(testPointIDs{1}) = load([folderPath,testID{1},'/pressureSensorsData/',testPointIDs{1},'.mat']);

% assign mean pressure values data
meanPressValues = zeros(length(pressureSensorsNames),1);
pressValues     = zeros(length(pressureSensorsNames),length(testPoint.(testPointIDs{1}).pressureSensors.time));
for i = 1:length(meanPressValues)
    meanPressValues(i) = testPoint.(testPointIDs{1}).pressureSensors.meanValues.(pressureSensorsNames{i});
    pressValues(i,:)   = testPoint.(testPointIDs{1}).pressureSensors.values.(pressureSensorsNames{i});
end


%% DATA PLOTTING
figure()

h = pdegplot(geom); hold on
[X,Y,Z] = sphere;
radius  = 3;

cmap = colormap("jet");
cmap = interp1(linspace(min(meanPressValues),max(meanPressValues),length(cmap)),cmap,meanPressValues);

for i=1:length(x_pressureSensors)
surf(X*radius + x_pressureSensors(i), Y*radius + y_pressureSensors(i), Z*radius + z_pressureSensors(i), ...
     'FaceColor',cmap(i,:),'EdgeColor','none','FaceLighting','none')
end
axis([-100 100 -150 100 0 150])

view(0,90); light();                         % other cases
% view(180,270); light('Position',[1,1,-1]);   % lt_thigh_front, lt_shin_front

colorbar
caxis([min(meanPressValues) max(meanPressValues)])
disp(['min = ',num2str(min(meanPressValues)),'[Pa]']) 
disp(['max = ',num2str(max(meanPressValues)),'[Pa]']) 
