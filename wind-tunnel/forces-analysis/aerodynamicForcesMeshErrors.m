%% Description
% This script computes the error between the CFD simulations on
% iRonCub-Mk1 in the wind tunnel setup and the relative experimental data
% gathered during the experiments. The error is relative to different
% discretization of the mesh around the robot.
%%

close all; 
clear all;

%% Set Experiment Path

experiment = 'exp_2022_11_03';
experimentPath = ['../',experiment,'/data_Matlab/'];

%% WIND TUNNEL DATA
testIDs = {'TID_9001','TID_9001','TID_9001','TID_9001','TID_9001', ...
           'TID_0057','TID_0057','TID_0057','TID_0057','TID_0057'};   % testID to be loaded in the script
for i = 1: length(testIDs)
    test.(testIDs{i}) = load([experimentPath,testIDs{i},'/aerodynamicForces.mat']);
end
wt_var_names = {'dragForceCoeff',  'liftForceCoeff',   'sideForceCoeff', ...
                'rollTorqueCoeff', 'pitchTorqueCoeff', 'yawTorqueCoeff'};

%% CFD DATA 

simulationNames = {'hovering_2_953C','hovering_2_202C','hovering_2_050C','hovering_2_024C','hovering_2_011C', ...
                   'flight30_2_953C','flight30_2_202C','flight30_2_050C','flight30_2_024C','flight30_2_011C',};

cfdPath = './wind-tunnel-setup/global-results/';
opts    = detectImportOptions([cfdPath,'flight30_2_953C.txt']);

for i = 1:length(simulationNames)
    cfdData.(simulationNames{i}) = table2struct(readtable([cfdPath,simulationNames{i},'.txt']),"ToScalar",true);
end

cfd_var_names = {'CdA_ke','CdA_kw','ClA_ke','ClA_kw','CsA_ke','CsA_kw', ...
                 'CrAl_ke','CrAl_kw','CpAl_ke','CpAl_kw','CyAl_ke','CyAl_kw'};

%% Error evaluation

varIndex = 4;
disp(["Aerodynamic errors for ",cfd_var_names{varIndex}])
for i=1:length(testIDs)
    sim_name = simulationNames{i};
    wt_val = test.(testIDs{i}).windAxesAero.(wt_var_names{round(varIndex/2)});
    cfd_val = cfdData.(sim_name).(cfd_var_names{varIndex});
    if i>=6
        wt_val = wt_val(1:7);
        cfd_val = cfd_val(1:7);
    end
    delta = cfd_val - wt_val;
    nme = max(abs(delta)) / max(abs(wt_val));
    nrmse = sqrt(mean((delta).^2)) / max(abs(wt_val));
    disp([sim_name,"NRMSE",nrmse,"NME",nme])
end