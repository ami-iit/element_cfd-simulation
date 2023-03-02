close all; 
clear all; 
clc;

%% Set Experiment Path

experiment = 'exp_03_11_22';    % Name of the experiment data folder: exp_21_03_22 | exp_03_11_22 
experimentPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables

testIDs = {'TID_0059'};   % testIDs to be loaded in the script

for i = 1: length(testIDs)
    test.(testIDs{i}) = load([experimentPath,testIDs{i},'/aerodynamicForces.mat']);
end

%% Assign plot variables
% selecting names of the components to be plotted
yVariable = {'dragForceCoeff',  'liftForceCoeff',   'sideForceCoeff', ...
             'rollTorqueCoeff', 'pitchTorqueCoeff', 'yawTorqueCoeff'};

% assigning the y labels for the plots
yLabel = {'$C_D A$','$C_L A$','$C_S A$','$C_r A l$','$C_p A l$','$C_y A l$'};

% assign the legend names for the plots
displayNames = {'exp: flight60'};

% set the plot lines appeareance
colors = {[0 0 0],[0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], [0.9290, 0.6940, 0.1250], [0,0.5,0], [1,0,1]};
lineStyles = {'-','-','-','-','-','-','-','-'};

% setting x axis limits
xLimits = [20 70];


%% assigning alpha or beta plotting
if max(test.(testIDs{1}).state.betaDes)-min(test.(testIDs{1}).state.betaDes) <= 1
    xVariable = 'alphaMeas';
    xLabel = '$\alpha_{meas}$ [deg]';
    OffSet = 45;    % Offset between robot and support bar

else
    xVariable = 'betaMeas';
    xLabel = '$\beta_{meas}$ [deg]';
    OffSet = 0;
end

%% CFD DATA 

simulationNames = {'flight60_2'};

cfdPath = '../../cfd/wind-tunnel/results/';
opts    = detectImportOptions([cfdPath,'flight30_2.txt']);

for i = 1:length(simulationNames)
    cfdData.(simulationNames{i}) = table2struct(readtable([cfdPath,simulationNames{i},'.txt']),"ToScalar",true);
end


%% PLOTS

figure()
% fig1 = openfig("fig1.fig");

% plot CFD data
for i = 1 : length(simulationNames)
    if matches(xVariable,'betaMeas')
        cfdPlotAngle = 'beta';
    else
        cfdPlotAngle = 'alpha';
    end
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CdA_ke,'Color','b','LineStyle','--','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: Realizable $k-\varepsilon$'); hold on;
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CdA_kw,'Color','r','LineStyle',':','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
end

% plot experimental data
for i = 1 : length(testIDs)
    plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{1}), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5,'DisplayName',displayNames{i});hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim(xLimits)
ylabel(yLabel{1},'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()
% fig2 = openfig("fig2.fig");

% plot CFD data
for i = 1 : length(simulationNames)
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).ClA_ke,'Color','b','LineStyle','--','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: Realizable $k-\varepsilon$'); hold on;
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).ClA_kw,'Color','r','LineStyle',':','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
end

% plot experimental data
for i = 1 : length(testIDs)
    plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{2}), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim(xLimits)
ylabel(yLabel{2},'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure() 
% fig3 = openfig("fig3.fig"); 

% plot CFD data
for i = 1 : length(simulationNames)
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CsA_ke,'Color','b','LineStyle','--','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: Realizable $k-\varepsilon$'); hold on;
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CsA_kw,'Color','r','LineStyle',':','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
end

% plot experimental data
for i = 1 : length(testIDs)

      plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{3}), ...
          'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim(xLimits)
ylabel(yLabel{3},'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()
% fig4 = openfig("fig4.fig");

% plot CFD data
for i = 1 : length(simulationNames)
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CrAl_ke,'Color','b','LineStyle','--','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: Realizable $k-\varepsilon$'); hold on;
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CrAl_kw,'Color','r','LineStyle',':','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
end

% plot experimental data
for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{4}), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim(xLimits)
ylabel(yLabel{4},'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()
% fig5 = openfig("fig5.fig"); 

% plot CFD data
for i = 1 : length(simulationNames)
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CpAl_ke,'Color','b','LineStyle','--','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: Realizable $k-\varepsilon$'); hold on;
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CpAl_kw,'Color','r','LineStyle',':','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
end

% plot experimental data
for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{5}), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim(xLimits)
ylabel(yLabel{5},'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()
% fig6 = openfig("fig6.fig"); 

% plot CFD data
for i = 1 : length(simulationNames)
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CyAl_ke,'Color','b','LineStyle','--','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: Realizable $k-\varepsilon$'); hold on;
    plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).CyAl_kw,'Color','r','LineStyle',':','linewidth',1.5,...
         'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
end

% plot experimental data
for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{6}), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim(xLimits)
ylabel(yLabel{6},'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show
