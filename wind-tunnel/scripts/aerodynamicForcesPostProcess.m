close all; 
clear all; 
clc;

%% Import Local Path
addpath(genpath('../../'));            % Adding the main folder path

%% Set Experiment Path
experiment = 'exp_03_11_22';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables
% testIDs to be loaded in the script
testIDs = {'TID_2017','TID_0058','TID_0059','TID_0026','TID_0027', ...
           'TID_0028','TID_0029','TID_0030'};

for i = 1: length(testIDs)
    test.(testIDs{i}) = load([folderPath,testIDs{i},'/aerodynamicForces.mat']);
end

%% Assign plot variables
% selecting names of the components to be plotted
yVariable = {'dragForceCoeff',  'liftForceCoeff',   'sideForceCoeff', ...
             'rollTorqueCoeff', 'pitchTorqueCoeff', 'yawTorqueCoeff'};

% assigning the y labels for the plots
yLabel = {'$C_D A$','$C_L A$','$C_S A$','$C_r A l$','$C_p A l$','$C_y A l$'};

% assign the legend names for the plots
displayNames = {'exp: flight30','exp: flight50','exp: flight60', ...
                'exp: flight-Config28', 'exp: flight-Config27', 'exp: flight-Config26', ...
                'exp: flight-Config1', 'exp: flight-Config8'};

% set the plot lines appeareance
colors = {[0,0,0],[0,0,0],[0,0,0],[0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], [0.9290, 0.6940, 0.1250], [0,0.5,0], [1,0,1]};
lineStyles = {'-','--',':','-','-','-','-','-'};

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

%% HOVERING CONFIGURATIONS CFD DATA 

% cfdPath          = ['../../cfd/wind-tunnel/results/'];
% hovering_ke      = table2struct(readtable([cfdPath,'hovering-ke.txt']),"ToScalar",true);
% opts = detectImportOptions('hovering-ke.txt');
% hovering_kw      = table2struct(readtable([cfdPath,'hovering-kw.txt'],opts),"ToScalar",true);
% hovJointVar5_ke  = table2struct(readtable([cfdPath,'hovJointVar5-ke.txt'],opts),"ToScalar",true);
% hovJointVar5_kw  = table2struct(readtable([cfdPath,'hovJointVar5-kw.txt'],opts),"ToScalar",true);
% hovJointVar9_ke  = table2struct(readtable([cfdPath,'hovJointVar9-ke.txt'],opts),"ToScalar",true);
% hovJointVar9_kw  = table2struct(readtable([cfdPath,'hovJointVar9-kw.txt'],opts),"ToScalar",true);

%% FLIGHT CONFIGURATIONS CFD DATA

% flight30_ke = table2struct(readtable([cfdPath,'flight30-ke.txt']),"ToScalar",true);
% flight30_kw = table2struct(readtable([cfdPath,'flight30-kw.txt']),"ToScalar",true);
% flight50_ke = table2struct(readtable([cfdPath,'flight50-ke.txt']),"ToScalar",true);
% flight50_kw = table2struct(readtable([cfdPath,'flight50-kw.txt']),"ToScalar",true);
% flight60_ke = table2struct(readtable([cfdPath,'flight60-ke.txt']),"ToScalar",true);
% flight60_kw = table2struct(readtable([cfdPath,'flight60-kw.txt']),"ToScalar",true);


%% PLOTS

figure()
% fig1 = openfig("fig1.fig");

% plot(hovering_ke.beta,hovering_ke.CdA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar5_ke.beta,hovJointVar5_ke.CdA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar9_ke.beta,hovJointVar9_ke.CdA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30_ke.alpha(1:4),flight30_ke.CdA(1:4),'Color',colors{1},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight50_ke.alpha(2:5),flight50_ke.CdA(2:5),'Color',colors{2},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight50 Real. $k-\varepsilon$'); hold on;
% plot(flight60_ke.alpha(3:5),flight60_ke.CdA(3:5),'Color',colors{3},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 Real. $k-\varepsilon$'); hold on;


% plot(hovering_kw.beta,hovering_kw.CdA,'Color','r','LineStyle',':','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar5_kw.beta,hovJointVar5_kw.CdA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar9_kw.beta,hovJointVar9_kw.CdA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30.alpha(1:4),flight30.CdA_kw(1:4),'Color',colors{1},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50.alpha(2:5),flight50.CdA_kw(2:5),'Color',colors{2},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight60.alpha(3:5),flight60.CdA_kw(3:5),'Color',colors{3},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 SST $k-\omega$'); hold on;

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

% plot(hovering_ke.beta,hovering_ke.ClA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar5_ke.beta,hovJointVar5_ke.ClA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar9_ke.beta,hovJointVar9_ke.ClA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30.alpha(1:4),flight30.ClA_ke(1:4),'Color',colors{1},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 Real. $k-\epsilon$'); hold on;
% plot(flight50.alpha(2:5),flight50.ClA_ke(2:5),'Color',colors{2},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight50 Real. $k-\epsilon$'); hold on;
% plot(flight60.alpha(3:5),flight60.ClA_ke(3:5),'Color',colors{3},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 Real. $k-\epsilon$'); hold on;
% 
% plot(hovering_kw.beta,hovering_kw.ClA,'Color','r','LineStyle',':','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','r','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar5_kw.beta,hovJointVar5_kw.ClA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar9_kw.beta,hovJointVar9_kw.ClA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30.alpha(1:4),flight30.ClA_kw(1:4),'Color',colors{1},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50.alpha(2:5),flight50.ClA_kw(2:5),'Color',colors{2},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight60.alpha(3:5),flight60.ClA_kw(3:5),'Color',colors{3},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 SST $k-\omega$'); hold on;

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

% plot(hovering_ke.beta,-hovering_ke.CsA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar5_ke.beta,-hovJointVar5_ke.CsA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar9_ke.beta,-hovJointVar9_ke.CsA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30.alpha(1:4),-flight30.CsA_ke(1:4),'Color',colors{1},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 Real. $k-\epsilon$'); hold on;
% plot(flight50.alpha(2:5),-flight50.CsA_ke(2:5),'Color',colors{2},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight50 Real. $k-\epsilon$'); hold on;
% plot(flight60.alpha(3:5),-flight60.CsA_ke(3:5),'Color',colors{3},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 Real. $k-\epsilon$'); hold on;

% plot(hovering_kw.beta,-hovering_kw.CsA,'Color','r','LineStyle',':','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar5_kw.beta,-hovJointVar5_kw.CsA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar9_kw.beta,-hovJointVar9_kw.CsA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30.alpha(1:4),-flight30.CsA_kw(1:4),'Color',colors{1},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50.alpha(2:5),-flight50.CsA_kw(2:5),'Color',colors{2},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight60.alpha(3:5),-flight60.CsA_kw(3:5),'Color',colors{3},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 SST $k-\omega$'); hold on;

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

% plot(hovering_ke.beta,hovering_ke.CrAl,'Color','k','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar5_ke.beta,-hovJointVar5_ke.CrAl,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar9_ke.beta,-hovJointVar9_ke.CrAl,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30_ke.alpha(1:4),-flight30_ke.CrAl(1:4),'Color',colors{1},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight50_ke.alpha(2:5),-flight50_ke.CrAl(2:5),'Color',colors{2},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight60_ke.alpha(3:5),-flight60_ke.CrAl(3:5),'Color',colors{3},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;

% plot(hovering_kw.beta,hovering_kw.CrAl,'Color','k','LineStyle',':','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar5_kw.beta,-hovJointVar5_kw.CrAl,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar9_kw.beta,-hovJointVar9_kw.CrAl,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30_kw.alpha(1:4),-flight30_kw.CrAl(1:4),'Color',colors{1},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50_kw.alpha(2:5),-flight50_kw.CrAl(2:5),'Color',colors{2},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight60_kw.alpha(3:5),-flight60_kw.CrAl(3:5),'Color',colors{3},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;

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

% plot(hovering_ke.beta,hovering_ke.CpAl,'Color','k','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar5_ke.beta,-hovJointVar5_ke.CpAl,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar9_ke.beta,-hovJointVar9_ke.CpAl,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30_ke.alpha(1:4),-flight30_ke.CpAl(1:4),'Color',colors{1},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight50_ke.alpha(2:5),-flight50_ke.CpAl(2:5),'Color',colors{2},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight60_ke.alpha(3:5),-flight60_ke.CpAl(3:5),'Color',colors{3},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;

% plot(hovering_kw.beta,hovering_kw.CpAl,'Color','k','LineStyle',':','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar5_kw.beta,-hovJointVar5_kw.CpAl,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar9_kw.beta,-hovJointVar9_kw.CpAl,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30_kw.alpha(1:4),-flight30_kw.CpAl(1:4),'Color',colors{1},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50_kw.alpha(2:5),-flight50_kw.CpAl(2:5),'Color',colors{2},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight60_kw.alpha(3:5),-flight60_kw.CpAl(3:5),'Color',colors{3},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;


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

% plot(hovering_ke.beta,hovering_ke.CyAl,'Color','k','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar5_ke.beta,-hovJointVar5_ke.CyAl,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(hovJointVar9_ke.beta,-hovJointVar9_ke.CyAl,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30_ke.alpha(1:4),-flight30_ke.CyAl(1:4),'Color',colors{1},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight50_ke.alpha(2:5),-flight50_ke.CyAl(2:5),'Color',colors{2},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight60_ke.alpha(3:5),-flight60_ke.CyAl(3:5),'Color',colors{3},'Marker','o','LineStyle','--',...
%      'linewidth',1,'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;

% plot(hovering_kw.beta,hovering_kw.CyAl,'Color','k','LineStyle',':','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar5_kw.beta,-hovJointVar5_kw.CyAl,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(hovJointVar9_kw.beta,-hovJointVar9_kw.CyAl,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30_kw.alpha(1:4),-flight30_kw.CyAl(1:4),'Color',colors{1},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50_kw.alpha(2:5),-flight50_kw.CyAl(2:5),'Color',colors{2},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight60_kw.alpha(3:5),-flight60_kw.CyAl(3:5),'Color',colors{3},'Marker','o','LineStyle','-',...
%      'linewidth',1,'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;


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

%% Remove Local path
rmpath(genpath('../../'));
