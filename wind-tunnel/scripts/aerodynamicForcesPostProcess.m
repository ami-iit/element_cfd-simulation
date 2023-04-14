close all; 
clear all; 
clc;

%% Set Experiment Path

experiment = 'exp_03_11_22';    % Name of the experiment data folder: exp_21_03_22 | exp_03_11_22 
experimentPath = ['../',experiment,'/data_Matlab/'];

%% Load test variables

testIDs = {'TID_0015'};   % testIDs to be loaded in the script

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
displayNames = {'exp: flight30, $\beta=30^\circ$','exp: flight50, $\beta=30^\circ$','exp: flight60, $\beta=30^\circ$'};

% set the plot lines appeareance
colors = {[0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], [0.8500, 0.3250, 0.0980], [0.9290, 0.6940, 0.1250], ...
          [0, 0, 0], [0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], [0.9290, 0.6940, 0.1250], [0,0.5,0], [1,0,1]};
lineStyles = {'--','--',':',':','--','--','-','-'};

% setting x axis limits
xLimits = [0 90.1];


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

simulationNames = {'hovering_2','hovering_2_ROM'};

cfdPath = '../../cfd/wind-tunnel/results/';
opts    = detectImportOptions([cfdPath,'flight30_2.txt']);

for i = 1:length(simulationNames)
    cfdData.(simulationNames{i}) = table2struct(readtable([cfdPath,simulationNames{i},'.txt']),"ToScalar",true);
end


%% PLOTS
variable = {'CdA_ke','CdA_kw','ClA_ke','ClA_kw','CsA_ke','CsA_kw', ...
            'CrAl_ke','CrAl_kw','CpAl_ke','CpAl_kw','CyAl_ke','CyAl_kw'};

for varIndex = 1:length(variable)/2
    
    figure(varIndex)

    % plot CFD data
    for i = 1 : length(simulationNames)
        if matches(xVariable,'betaMeas')
            cfdPlotAngle = 'beta';
        else
            cfdPlotAngle = 'alpha';
        end
        plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).(variable{varIndex*2-1}),'Color',colors{i*2-1},'LineStyle',lineStyles{i*2-1}, ...
             'linewidth',2,'Marker','o','DisplayName',['CFD: ',simulationNames{i}(1:8),', Realizable $k-\varepsilon$']); hold on;
        plot(cfdData.(simulationNames{i}).(cfdPlotAngle),cfdData.(simulationNames{i}).(variable{varIndex*2}),'Color',colors{i*2},'LineStyle',lineStyles{i*2}, ...
             'linewidth',2,'Marker','o','DisplayName',['CFD: ',simulationNames{i}(1:8),', SST $k-\omega$']); hold on;
    end

    % plot experimental data
    for i = 1 : length(testIDs)
        plot(test.(testIDs{i}).state.(xVariable) + OffSet, test.(testIDs{i}).windAxesAero.(yVariable{varIndex}), ...
            'Color','k','LineStyle','-','linewidth',2,'DisplayName',displayNames{i});hold on;
    end

    grid on;
    xlim(xLimits)
    ylabel(yLabel{varIndex},'Interpreter','latex')
    xlabel(xLabel,'Interpreter','latex')
    legend('Interpreter','latex','Location','best')
    legend show

end