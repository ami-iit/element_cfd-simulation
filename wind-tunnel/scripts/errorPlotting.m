close all; 
clear all; 
clc;


%% %%%%%%%%%%%%%%%%%%%%%%%%%%%% LOAD DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Set Experiment Path
experiment = 'exp_03_11_22';    % Name of the experiment data folder: exp_21_03_22 | exp_03_11_22 
experimentPath = ['../',experiment,'/data_Matlab/'];

% Load test data
testIDs = {'TID_0051','TID_0052','TID_0053'};   % testIDs to be loaded in the script
for i = 1: length(testIDs)
    test.(testIDs{i}) = load([experimentPath,testIDs{i},'/aerodynamicForces.mat']);
end

% Load CFD data 
simulationNames = {'flight30_cross60_2','flight50_cross60_2','flight60_cross60_2'};

cfdPath = '../../cfd/wind-tunnel/results/';
opts    = detectImportOptions([cfdPath,'flight30_2.txt']);
for i = 1:length(simulationNames)
    cfdData.(simulationNames{i}) = table2struct(readtable([cfdPath,simulationNames{i},'.txt']),"ToScalar",true);
end

%% %%%%%%%%%%%%%%%%%%%%%%%%% PLOT VARIABLES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% selecting names of the components to be plotted
yVariable = {'dragForceCoeff',  'liftForceCoeff',   'sideForceCoeff', ...
             'rollTorqueCoeff', 'pitchTorqueCoeff', 'yawTorqueCoeff'};

% assigning the y labels for the plots
yLabel = {'$\Delta C_D A$','$\Delta C_L A$','$\Delta C_S A$', ...
          '$\Delta C_r A l$','$\Delta C_p A l$','$\Delta C_y A l$'};

% assign the legend names for the plots
displayNames = {'exp: flight30, $\beta=30^\circ$','exp: flight50, $\beta=30^\circ$','exp: flight60, $\beta=30^\circ$'};

% set the plot lines appeareance
colors = {[0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], [0.9290, 0.6940, 0.1250], ...
          [0, 0, 0], [0.8500, 0.3250, 0.0980], [0, 0.4470, 0.7410], [0.9290, 0.6940, 0.1250], [0,0.5,0], [1,0,1]};
lineStyles = {'-','-','-','--','--','--','-','-'};

% setting x axis limits
xLimits = [20 70];

% assigning alpha or beta plotting
if max(test.(testIDs{1}).state.betaDes)-min(test.(testIDs{1}).state.betaDes) <= 1
    xVariable = 'alphaDes';
    xLabel = '$\alpha$ [deg]';
    OffSet = 45;    % Offset between robot and support bar

else
    xVariable = 'betaDes';
    xLabel = '$\beta$ [deg]';
    OffSet = 0;
end

% CFD variables to plot
cfdVariable = {'CdA_ke','CdA_kw','ClA_ke','ClA_kw','CsA_ke','CsA_kw', ...
               'CrAl_ke','CrAl_kw','CpAl_ke','CpAl_kw','CyAl_ke','CyAl_kw'};
% cfdVariable = {'CdA_ke','ClA_ke','CsA_ke','CrAl_ke','CpAl_ke','CyAl_ke'};

% initialize data struct for saving
error = struct();  % struct for saving error

% load error regression coefficients
data  = load([cfdPath,'error/regressionCoefficients.mat']);
coefs = data.coefs;

%% %%%%%%%%%%%%%%%%%%%%%%%%%% ERROR PLOTS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Drag Coefficient plot
for index = 1 : (length(cfdVariable)/2)
    error.alpha = cfdData.(simulationNames{i}).alpha;
    error.beta  = cfdData.(simulationNames{i}).beta;
    figure(index)
    for i = 1 : length(simulationNames)
        if matches(xVariable,'betaDes')
            cfdPlotAngle = 'beta';
        else
            cfdPlotAngle = 'alpha';
        end
    
        for j = 1 : length(testIDs)
            x_cfd = cfdData.(simulationNames{i}).(cfdPlotAngle);
            y_cfd_ke = cfdData.(simulationNames{i}).(cfdVariable{2*index-1});
%             y_cfd_kw = cfdData.(simulationNames{i}).(cfdVariable{2*index});
            x_wt  = test.(testIDs{j}).state.(xVariable) + OffSet;
            y_wt  = test.(testIDs{j}).windAxesAero.(yVariable{index});
            
            [~,commonValInd] = intersect(x_cfd,x_wt);

            if length(commonValInd) >=2
                x_plot    = x_cfd(commonValInd);
                y_plot_ke = y_wt(commonValInd) - y_cfd_ke(commonValInd);
%                 y_plot_kw = y_wt(commonValInd) - y_cfd_kw(commonValInd);
      
                plot(x_plot,y_plot_ke,'Color',[0, 0.4470, 0.7410],'LineStyle',lineStyles{i},'linewidth',2,...
                    'DisplayName',['config: ',simulationNames{i}(1:8),', model: Realizable $k-\varepsilon$']); hold on;
%                 plot(x_plot,y_plot_kw,'Color',[0.8500, 0.3250, 0.0980],'LineStyle',lineStyles{i},'linewidth',2,...
%                     'DisplayName',['config: ',simulationNames{i}(1:8),', model: SST $k-\omega$']); hold on;

                error.(cfdVariable{2*index-1}) = y_plot_ke;
%                 error.(cfdVariable{2*index})   = y_plot_kw;

                % regression curve
%               x_regression = linspace(x_plot(1),x_plot(end),1000);
                a = cfdData.(simulationNames{i}).alpha(commonValInd);
                b = cfdData.(simulationNames{i}).beta(commonValInd);
                
                c_ke = coefs.(cfdVariable{2*index-1});
                c_kw = coefs.(cfdVariable{2*index});
                y_regression_ke = c_ke(1)*ones(length(a),1) + c_ke(2)*a + c_ke(3)*a.^2 + ...
                                  c_ke(4)*b + c_ke(5)*b.^2 + c_ke(6)*a.*b;% + ...
%                                   c_ke(7)*sin(a) + c_ke(8)*sin(b) + ...
%                                   c_ke(9)*cos(a) + c_ke(10)*cos(b);
                y_regression_kw = c_kw(1)*ones(length(a),1) + c_kw(2)*a + c_kw(3)*a.^2 + ...
                                  c_kw(4)*b + c_kw(5)*b.^2 + c_kw(6)*a.*b;% + ...
%                                   c_kw(7)*sin(a) + c_kw(8)*sin(b) + ...
%                                   c_kw(9)*cos(a) + c_kw(10)*cos(b);

                plot(x_plot,y_regression_ke,'Color',[0, 0.4470, 0.7410],'LineStyle',':','linewidth',2,...
                    'DisplayName','regression, model: Realizable $k-\varepsilon$'); hold on;
%                 plot(x_plot,y_regression_kw,'Color',[0.8500, 0.3250, 0.0980],'LineStyle',':','linewidth',2,...
%                     'DisplayName','regression, model: SST $k-\omega$'); hold on;
            end
        end
    end
    
    grid on;
    xlim(xLimits)
    ylabel(yLabel{index},'Interpreter','latex')
    xlabel(xLabel,'Interpreter','latex')
    legend('Interpreter','latex','Location','best')
    legend show
end

%% %%%%%%%%%%%%%%%%%%%%%%%%%%% SAVE DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% % use just when there is a single simulation name
% 
% if (~exist([cfdPath,'/error'],'dir'))
% 
%     mkdir([cfdPath,'/error']);
% end
% 
% save([cfdPath,'/error/',simulationNames{1},'.mat'],'error')
%     