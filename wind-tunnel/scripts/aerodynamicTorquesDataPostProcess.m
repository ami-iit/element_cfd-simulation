close all; 
clear all; 
clc;

%% Import Local Path
addpath(genpath('../'));            % Adding the main folder path

%% Set Experiment Path
experiment = 'exp_21_03_22';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables
% testIDs to be loaded in the script
testIDs = {'TID_0013','TID_0014','TID_0015'};

for i = 1: length(testIDs)
    test.(testIDs{i}) = load([folderPath,testIDs{i},'/aerodynamicForces.mat']);
end

%% Assign plot variables
% selecting the torques to be plotted
y1 = 'rollTorqueCoeff';
y2 = 'pitchTorqueCoeff';
y3 = 'yawTorqueCoeff';

% assigning the y labels for the plots
yLabel1 = '$C_r A l$';
yLabel2 = '$C_p A l$';
yLabel3 = '$C_y A l$';

% assign the legend names for the plots
displayNames = {'exp: Flight30 config.', 'exp: Flight50 config.', 'exp: Flight60 config.'};

% set the plot lines appeareance
colors = {[0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], ...
          [0.9290, 0.6940, 0.1250], [0, 0.5, 0]};
lineStyles = {'-','-','-',':',':',':'};

% set this value to select the x variable: beta = false, alpha = true
ALPHA_PLOTTING = true;

%% assigning alpha or beta plotting
if ALPHA_PLOTTING == 1
    x = 'alphaMeas';
    xLabel = '$\alpha_{meas}$ [deg]';
    OffSet = 45;    % Offset between 
else
    x = 'betaMeas';
    xLabel = '$\beta_{meas}$ [deg]';
    OffSet = 0;
end

%% HOVERING CONFIGURATION CFD DATA 

cfdPath = ['../../cfd/wind-tunnel/results/'];
opts = detectImportOptions([cfdPath,'hovering-ke.txt']);
hovering_ke = table2struct(readtable([cfdPath,'hovering-ke.txt'],opts),"ToScalar",true);
hovering_kw = table2struct(readtable([cfdPath,'hovering-kw.txt'],opts),"ToScalar",true);

%% FLIGHT CONFIGURATIONS CFD DATA

flight30_ke = table2struct(readtable([cfdPath,'flight30-ke.txt'],opts),"ToScalar",true);
flight30_kw = table2struct(readtable([cfdPath,'flight30-kw.txt'],opts),"ToScalar",true);
flight50_ke = table2struct(readtable([cfdPath,'flight50-ke.txt'],opts),"ToScalar",true);
flight50_kw = table2struct(readtable([cfdPath,'flight50-kw.txt'],opts),"ToScalar",true);
flight60_ke = table2struct(readtable([cfdPath,'flight60-ke.txt'],opts),"ToScalar",true);
flight60_kw = table2struct(readtable([cfdPath,'flight60-kw.txt'],opts),"ToScalar",true);

%% PLOTS
figure()

% plot(hovering_ke.beta,-hovering_ke.CrAl,'bo--','DisplayName', 'CFD: Real. $k-\epsilon$'); hold on;
plot(flight30_ke.alpha(1:4),-flight30_ke.CrAl(1:4),'Color',colors{1},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
plot(flight50_ke.alpha(2:5),-flight50_ke.CrAl(2:5),'Color',colors{2},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
plot(flight60_ke.alpha(3:5),-flight60_ke.CrAl(3:5),'Color',colors{3},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;

% plot(hovering_kw.beta,-hovering_kw.CrAl,'ro--','DisplayName', 'CFD: SST $k-\omega$'); hold on;
plot(flight30_kw.alpha(1:4),-flight30_kw.CrAl(1:4),'Color',colors{1},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
plot(flight50_kw.alpha(2:5),-flight50_kw.CrAl(2:5),'Color',colors{2},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
plot(flight60_kw.alpha(3:5),-flight60_kw.CrAl(3:5),'Color',colors{3},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;

for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(x) + OffSet, test.(testIDs{i}).windAxesAero.(y1), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim([20 70])
ylabel(yLabel1,'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show

figure()

% plot(hovering_ke.beta,-hovering_ke.CpAl,'bo--','DisplayName', 'CFD: Real. $k-\epsilon$'); hold on;
plot(flight30_ke.alpha(1:4),-flight30_ke.CpAl(1:4),'Color',colors{1},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
plot(flight50_ke.alpha(2:5),-flight50_ke.CpAl(2:5),'Color',colors{2},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
plot(flight60_ke.alpha(3:5),-flight60_ke.CpAl(3:5),'Color',colors{3},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;

% plot(hovering_kw.beta,-hovering_kw.CrAl,'ro--','DisplayName', 'CFD: SST $k-\omega$'); hold on;
plot(flight30_kw.alpha(1:4),-flight30_kw.CpAl(1:4),'Color',colors{1},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
plot(flight50_kw.alpha(2:5),-flight50_kw.CpAl(2:5),'Color',colors{2},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
plot(flight60_kw.alpha(3:5),-flight60_kw.CpAl(3:5),'Color',colors{3},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;


for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(x) + OffSet, test.(testIDs{i}).windAxesAero.(y2), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim([20 70])
ylabel(yLabel2,'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()

% plot(hovering_ke.beta,-hovering_ke.CyAl,'bo--','DisplayName', 'CFD: Real. $k-\epsilon$'); hold on;
plot(flight30_ke.alpha(1:4),-flight30_ke.CyAl(1:4),'Color',colors{1},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
plot(flight50_ke.alpha(2:5),-flight50_ke.CyAl(2:5),'Color',colors{2},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
plot(flight60_ke.alpha(3:5),-flight60_ke.CyAl(3:5),'Color',colors{3},'Marker','o','LineStyle','--',...
     'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;

% plot(hovering_kw.beta,-hovering_kw.CrAl,'ro--','DisplayName', 'CFD: SST $k-\omega$'); hold on;
plot(flight30_kw.alpha(1:4),-flight30_kw.CyAl(1:4),'Color',colors{1},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
plot(flight50_kw.alpha(2:5),-flight50_kw.CyAl(2:5),'Color',colors{2},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
plot(flight60_kw.alpha(3:5),-flight60_kw.CyAl(3:5),'Color',colors{3},'Marker','o','LineStyle','-',...
     'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;


for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(x) + OffSet, test.(testIDs{i}).windAxesAero.(y3), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim([20 70])
ylabel(yLabel3,'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show

%% Remove Local path
rmpath(genpath('../'));
