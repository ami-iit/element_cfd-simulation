close all; 
clear all; 
clc;

%% Set Experiment Path

experiment = 'exp_2022_11_03';    % Name of the experiment data folder: exp_2022_03_21 | exp_2022_11_03 | exp_2023_12_11
experimentPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables

testIDs = {'TID_0001','TID_0002','TID_0015','TID_0016'};   % testIDs to be loaded in the script

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
displayNames = {'hovering, $|V|=12$ m/s', ...
                'hovering, $|V|=12$ m/s', ...
                'hovering, $|V|=19$ m/s', ...
                'hovering, $|V|=24$ m/s', ...
                };

handlevisibility = {'on', 'off', 'on', 'on','on'};


% set the plot lines appeareance
colors = {[0, 0.4470, 0.7410], [0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], ...
          [0.9290, 0.6940, 0.1250], [0, 1, 0]}; %[0, 0.22, 0.37]
% colors = {[0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], [0.9290, 0.6940, 0.1250], ...
          % [0, 1, 0], [0, 0.22, 0.37]};
          
lineStyles = {'-','-','-','-','-',':','-.'};

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

%% PLOTS

varIndex = 1;

linewidth = 1.5;
fontsize = 12;

fig = figure();
for i = 1 : length(testIDs)
    testID = testIDs{i};
    plot(test.(testID).state.(xVariable) + OffSet, test.(testID).windAxesAero.(yVariable{varIndex}), ...
         'Color',colors{i},'LineStyle',lineStyles{i},'linewidth',linewidth,'DisplayName',displayNames{i}, 'HandleVisibility',handlevisibility{i}); hold on;
end
grid on;
xlim([-90 90]);
ylim([0.20 0.31]);

% ax = gca;
% ax.FontSize = fontsize;

ylabel(yLabel{varIndex},'Interpreter','latex');%,'FontSize',fontsize)
xlabel(xLabel,'Interpreter','latex');%,'FontSize',fontsize)
legend('Interpreter','latex','Location','se');%,'FontSize',fontsize)

saveF('fig1.pdf',[10 8])