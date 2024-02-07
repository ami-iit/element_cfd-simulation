close all; 
clear all; 
clc;

%% Set Experiment Path

experiment = 'exp_2023_12_11';    % Name of the experiment data folder: exp_2022_03_21 | exp_2022_11_03 | exp_2023_12_11
experimentPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables

testIDs = {'TID_0033','TID_0032','TID_0034'};   % testIDs to be loaded in the script

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
displayNames = {'flight30: V=12 m/s', ...
                'flight30: V=17 m/s', ...
                'flight30: V=21 m/s', ...
                'flight30: V=30 m/s', ...
                };

% set the plot lines appeareance
colors = {[0, 0, 0],[0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], ...
          [0.42, 0.16, 0.0980], [0.9290, 0.6940, 0.1250], [0, 1, 0]}; %[0, 0.22, 0.37]
          
lineStyles = {'-','--',':','-.'};

% setting x axis limits
% xLimits = [-90 0];


%% assigning alpha or beta plotting
if max(test.(testIDs{1}).state.betaDes)-min(test.(testIDs{1}).state.betaDes) <= 1
    xVariable = 'alphaMeas';
    xLabel = '$\alpha_{meas}$ [deg]';
    OffSet = 0;    % Offset between robot and support bar

else
    xVariable = 'betaDes';
    xLabel = '$\beta_{des}$ [deg]';
    OffSet = 0;
end

%% CFD DATA 
% 
% simulationNames = {'flight30_2_953C','flight30_2_202C','flight30_2_050C','flight30_2_024C','flight30_2_011C'};
% cfdPlotNames    = {'flight30-953C','flight30-202C','flight30-050C','flight30-024C','flight30-011C'};
% 
% cfdPath = '../../results/wind-tunnel-setup/global-results/';
% opts    = detectImportOptions([cfdPath,'flight30_2_953C.txt']);
% 
% for i = 1:length(simulationNames)
%     cfdData.(simulationNames{i}) = table2struct(readtable([cfdPath,simulationNames{i},'.txt']),"ToScalar",true);
% end

% variable = {'CdA_ke','CdA_kw','ClA_ke','ClA_kw','CsA_ke','CsA_kw', ...
%             'CrAl_ke','CrAl_kw','CpAl_ke','CpAl_kw','CyAl_ke','CyAl_kw'};

%% PLOTS

fig = figure();
fig.Position = [150,150,1920,1024];
tiledlayout(2,3);
for varIndex = 1:length(yVariable)
    % figure(varIndex)
    % plot CFD data
%     for i = 1 : length(simulationNames)
%         if matches(xVariable,'betaMeas')
%             cfdPlotAngle = 'beta';
%         else
%             cfdPlotAngle = 'alpha';
%         end
% %         plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).(variable{varIndex*2-1}),'Color',colors{i*2-1},'LineStyle',lineStyles{i*2-1}, ...
% %              'linewidth',2,'Marker','o','DisplayName',['CFD: ',cfdPlotNames{i},', Realizable $k-\varepsilon$']); hold on;
%         plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).(variable{varIndex*2}),'Color',colors{i*2},'LineStyle',lineStyles{i*2}, ...
%              'linewidth',2,'Marker','o','DisplayName',['CFD: ',cfdPlotNames{i},', SST $k-\omega$']); hold on;
%     end
    
    nexttile
    % plot experimental data
    for i = 1 : length(testIDs)
        testID = testIDs{i};
        plot(test.(testID).state.(xVariable) + OffSet, test.(testID).windAxesAero.(yVariable{varIndex}), ...
            'Color',colors{1},'LineStyle',lineStyles{i},'linewidth',2,'DisplayName',displayNames{i}); hold on;
    end

    grid on;

    ax.FontSize = 24;
    xlim([25 65])
    ylabel(yLabel{varIndex},'Interpreter','latex','FontSize',24)
    xlabel(xLabel,'Interpreter','latex','FontSize',24)
    legend('Interpreter','latex','Location','best','FontSize',12)
    legend show

end