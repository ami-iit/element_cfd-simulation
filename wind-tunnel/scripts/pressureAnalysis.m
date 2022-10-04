close all; 
clear all; 
clc;

%% Load geometric data

coverName = ['chest'];

geom = importGeometry(['./srcPressureAnalysis/',coverName,'.stl']);
opts = detectImportOptions('./srcPressureAnalysis/chest_sensors.txt');
pressureSensors = table2struct(readtable(['./srcPressureAnalysis/',coverName,'_sensors.txt'],opts),"ToScalar",true);
pressureSensorsNames = pressureSensors.Var1;
x_pressureSensors    = pressureSensors.Var2;
y_pressureSensors    = pressureSensors.Var3;
z_pressureSensors    = pressureSensors.Var4;

%% Load pressure data
addpath(genpath('../'));            % Adding the main folder path
experiment = 'exp_21_03_22';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_Matlab/'];

% Name of the test and test points to be loaded
testID = {'TID_0001'};
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

fprintf([num2str(min(min(pressValues)),3),' [Pa] \x2264 \x394p \x2264 ',num2str(max(max(pressValues)),3),' [Pa] \n']);
fprintf(['\x394T = ',num2str(testPoint.(testPointIDs{1}).pressureSensors.time(end),3),' [s] \n']);
fprintf(['rt_foot \x394p = ',num2str(testPoint.(testPointIDs{1}).pressureSensors.meanValues.S1,3),' [Pa] \n']);
fprintf(['lt_foot \x394p = ',num2str(testPoint.(testPointIDs{1}).pressureSensors.meanValues.S3,3),' [Pa] \n']);

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

if contains(coverName,'lt_thigh_front') || contains(coverName,'lt_shin_front') || contains(coverName,'face_back')
    view(180,270); light('Position',[1,1,-1]);   % lt_thigh_front, lt_shin_front
else 
    if contains(coverName,'lt_arm_front')
        view(0,0); light('Position',[1,-1,1]);
    else
        view(0,90); light();                         % other cases
    end
end
colorbar
caxis([min(meanPressValues) max(meanPressValues)])

figure()
for i = 1:length(meanPressValues)
    plot(testPoint.(testPointIDs{1}).pressureSensors.time,pressValues(i,:),"Color",cmap(i,:)); hold on;
end
grid on;
ylabel('$\Delta p$ [Pa]','Interpreter','latex')
xlabel('$t$ [s]','Interpreter','latex')

%% Remove from path

rmpath(genpath('../'));            % Adding the main folder path