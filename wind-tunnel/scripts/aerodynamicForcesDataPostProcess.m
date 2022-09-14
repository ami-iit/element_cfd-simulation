close all; 
clear all; 
clc;

%% Import Local Path
addpath(genpath('../../'));            % Adding the main folder path

%% Set Experiment Path
experiment = 'exp_21_03_22';        % Name of the experiment data folder
folderPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables
% testIDs to be loaded in the script
testIDs = {'TID_0001', 'TID_0008', 'TID_0009', 'TID_0010', 'TID_0011'};

for i = 1: length(testIDs)
    test.(testIDs{i}) = load([folderPath,testIDs{i},'/aerodynamicForces.mat']);
end

%% Assign plot variables
% selecting the forces to be plotted
y1 = 'dragForceCoeff';
y2 = 'liftForceCoeff';
y3 = 'sideForceCoeff';

% assigning the y labels for the plots
yLabel1 = '$C_D A$';
yLabel2 = '$C_L A$';
yLabel3 = '$C_S A$';

% assign the legend names for the plots
displayNames = {'exp: hovering base conf.', ...
                'exp: hovering conf. 7', ...
                'exp: hovering conf. 8,', ...
                'exp: hovering conf. 9', ...
                'exp: hovering conf. 16'};

% set the plot lines appeareance
colors = {[0,0,0], [0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], ...
          [0.9290, 0.6940, 0.1250], [0, 0.5, 0]};
lineStyles = {'-',':',':',':',':',':'};

% set this value to select the x variable: beta = false, alpha = true
ALPHA_PLOTTING = false;


%% assigning alpha or beta plotting
if ALPHA_PLOTTING == true
    x = 'alphaMeas';
    xLabel = '$\alpha_{meas}$ [deg]';
    OffSet = 45;    % Offset between 

else
    x = 'betaMeas';
    xLabel = '$\beta_{meas}$ [deg]';
    OffSet = 0;
end

%% HOVERING CONFIGURATION CFD DATA 

% cfdPath = ['../../cfd/wind-tunnel/results/'];
% hovering_ke = table2struct(readtable([cfdPath,'hovering-ke.txt']),"ToScalar",true);
% hovering_kw = table2struct(readtable([cfdPath,'hovering-kw.txt']),"ToScalar",true);
% 
% %% FLIGHT CONFIGURATIONS CFD DATA
% 
% flight30_ke = table2struct(readtable([cfdPath,'flight30-ke.txt'],opts),"ToScalar",true);
% flight30_kw = table2struct(readtable([cfdPath,'flight30-kw.txt'],opts),"ToScalar",true);
% flight50_ke = table2struct(readtable([cfdPath,'flight50-ke.txt'],opts),"ToScalar",true);
% flight50_kw = table2struct(readtable([cfdPath,'flight50-kw.txt'],opts),"ToScalar",true);
% flight60_ke = table2struct(readtable([cfdPath,'flight60-ke.txt'],opts),"ToScalar",true);
% flight60_kw = table2struct(readtable([cfdPath,'flight60-kw.txt'],opts),"ToScalar",true);


%% PLOTS

figure()

% plot(hovering_ke.beta,hovering_ke.CdA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','b','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30_ke.alpha(1:4),flight30_ke.CdA(1:4),'Color',colors{1},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 Real. $k-\varepsilon$'); hold on;
% plot(flight50_ke.alpha(2:5),flight50_ke.CdA(2:5),'Color',colors{2},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight50 Real. $k-\varepsilon$'); hold on;
% plot(flight60_ke.alpha(3:5),flight60_ke.CdA(3:5),'Color',colors{3},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 Real. $k-\varepsilon$'); hold on;


% plot(hovering_kw.beta,hovering_kw.CdA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','r','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30.alpha(1:4),flight30.CdA_kw(1:4),'Color',colors{1},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50.alpha(2:5),flight50.CdA_kw(2:5),'Color',colors{2},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight60.alpha(3:5),flight60.CdA_kw(3:5),'Color',colors{3},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 SST $k-\omega$'); hold on;

for i = 1 : length(testIDs)

    plot(test.(testIDs{i}).state.(x) + OffSet, test.(testIDs{i}).windAxesAero.(y1), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5,'DisplayName',displayNames{i});hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim([0 90])
ylabel(yLabel1,'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()

% plot(hovering_ke.beta,-hovering_ke.CsA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','b','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30.alpha(1:4),flight30.ClA_ke(1:4),'Color',colors{1},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 Real. $k-\epsilon$'); hold on;
% plot(flight50.alpha(2:5),flight50.ClA_ke(2:5),'Color',colors{2},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight50 Real. $k-\epsilon$'); hold on;
% plot(flight60.alpha(3:5),flight60.ClA_ke(3:5),'Color',colors{3},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 Real. $k-\epsilon$'); hold on;

% plot(hovering_kw.beta,-hovering_kw.CsA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','r','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30.alpha(1:4),flight30.ClA_kw(1:4),'Color',colors{1},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50.alpha(2:5),flight50.ClA_kw(2:5),'Color',colors{2},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight60.alpha(3:5),flight60.ClA_kw(3:5),'Color',colors{3},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 SST $k-\omega$'); hold on;

for i = 1 : length(testIDs)

      plot(test.(testIDs{i}).state.(x) + OffSet, test.(testIDs{i}).windAxesAero.(y2), ...
          'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim([0 90])
ylabel(yLabel2,'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show


figure()
% plot(hovering_ke.beta,-hovering_ke.CsA,'Color','b','LineStyle','--','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','b','DisplayName','CFD: Real. $k-\varepsilon$'); hold on;
% plot(flight30.alpha(1:4),flight30.ClA_ke(1:4),'Color',colors{1},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 Real. $k-\epsilon$'); hold on;
% plot(flight50.alpha(2:5),flight50.ClA_ke(2:5),'Color',colors{2},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight50 Real. $k-\epsilon$'); hold on;
% plot(flight60.alpha(3:5),flight60.ClA_ke(3:5),'Color',colors{3},'Marker','o','LineStyle','--','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 Real. $k-\epsilon$'); hold on;

% plot(hovering_kw.beta,-hovering_kw.CsA,'Color','r','LineStyle','--','linewidth',1.5,...
%      'Marker','o','MarkerFaceColor','r','DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight30.alpha(1:4),flight30.ClA_kw(1:4),'Color',colors{1},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight30 SST $k-\omega$'); hold on;
% plot(flight50.alpha(2:5),flight50.ClA_kw(2:5),'Color',colors{2},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: SST $k-\omega$'); hold on;
% plot(flight60.alpha(3:5),flight60.ClA_kw(3:5),'Color',colors{3},'Marker','o','LineStyle','-','linewidth',1.5,...
%      'DisplayName','CFD: Flight60 SST $k-\omega$'); hold on;

for i = 1 : length(testIDs)

      plot(test.(testIDs{i}).state.(x) + OffSet, test.(testIDs{i}).windAxesAero.(y3), ...
          'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',1.5, 'DisplayName', displayNames{i}); hold on;
end

grid on;
% xlim([min(test.(testIDs{1}).state.(x))+OffSet ...
%       max(test.(testIDs{1}).state.(x))+OffSet])
xlim([0 90])
ylabel(yLabel3,'Interpreter','latex')
xlabel(xLabel,'Interpreter','latex')
legend('Interpreter','latex','Location','best')
legend show

%% Remove Local path
rmpath(genpath('../../'));
