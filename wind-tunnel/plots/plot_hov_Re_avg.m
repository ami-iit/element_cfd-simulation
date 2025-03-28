close all; 
clear all; 
clc;

%% Set Experiment Path

experiment = 'exp_2022_11_03';    % Name of the experiment data folder: exp_2022_03_21 | exp_2022_11_03 | exp_2023_12_11
experimentPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables

testIDs = {'TID_0001','TID_0002','TID_0005','TID_0006'};

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
displayNames = {'hovering, config1', ...
                'hovering, config3', ...
                'hovering, config7', ...
                'hovering, config11', ...
                'hovering, config13', ...
                'hovering, config17', ...
                'hovering, config21', ...
                };

handlevisibility = {'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on', 'on'};


% set the plot lines appeareance
% colors = {[0, 0.4470, 0.7410], [0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], ...
%           [0.9290, 0.6940, 0.1250], [0, 1, 0]}; %[0, 0.22, 0.37]
colors = {[0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], [0.9290, 0.6940, 0.1250], ...
          [0, 1, 0], [0, 0.22, 0.37], ...
          [0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], [0.9290, 0.6940, 0.1250], ...
          [0, 1, 0], [0, 0.22, 0.37]};
          
lineStyles = {'-','-','-','-','-','-','-','-','-','-'};

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

varIndex = 2;

linewidth = 1.5;
fontsize = 12;

fig = figure();
x = test.(testIDs{3}).state.(xVariable) + OffSet;
y = zeros(length(x),length(testIDs));
for i = 1 : length(testIDs)
    testID = testIDs{i};
    y(:,i) = test.(testID).windAxesAero.(yVariable{varIndex});
end

yy = y;
y = yy(:,1:end);
y(1)

y_avg = mean(y,2);
y_max = max(y');
y_min = min(y');
f = fill([x;flipud(x)],[y_min,fliplr(y_max)],'cyan','FaceAlpha',0.3,'DisplayName','variation'); hold on;
f.EdgeColor = 'cyan';

plot(x,y_avg,'Color',[0,0,0],'LineStyle','-','linewidth',1.5,'DisplayName','mean','HandleVisibility','on'); hold on;


grid on;
xlim([0 90]);
ylim([-0.03 0.03]);

% ax = gca;
% ax.FontSize = fontsize;

ylabel(yLabel{varIndex},'Interpreter','latex');%,'FontSize',fontsize)
xlabel(xLabel,'Interpreter','latex');%,'FontSize',fontsize)
legend('Interpreter','latex','Location','se');%,'FontSize',fontsize)

saveF('fig1.pdf',[10 8])