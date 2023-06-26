%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script automatically imports the CFD simulated data in Fluent and
% exported in .csv format, coverting them into .mat format
%
% Author: Antonello Paolino
%
% June 2023
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;
clear all; 
clc;

%% Initialization
% Experiment and test to be mapped
dataPath = '../data/';
dataFile = [dataPath,'outputParameters.csv'];

srcPath  = '../src/';
jointConfigFile = [srcPath,'jointConfig.csv'];

opts     = detectImportOptions(dataFile);
opts.PreserveVariableNames = false;         % Changing from '-' to '_' in the variable names
table1   = readtable(dataFile,opts);

opts     = detectImportOptions(jointConfigFile);
opts.PreserveVariableNames = false;         % Changing from '-' to '_' in the variable names
table2   = readtable(jointConfigFile,opts);

varNames = table1.Properties.VariableNames;

%% Data struct generation
data       = struct();
stopIndex  = 0;
loopIter   = 1;

while (stopIndex < height(table1(:,1)))
    startIndex = stopIndex + 1;
    configName = table1.config{startIndex};
    data.(table1.config{startIndex}).jointConfig = table2array(table2(matches(table2{:,1},configName),2:end));
    for col = 2:length(varNames)
        data.(table1.config{startIndex}).(varNames{col}) = table2array(table1(matches(table1.config,configName),col));
    end
    stopIndex = startIndex + height(table1(matches(table1.config,configName),col)) - 1;
end

%% Save imported struct data in workspace
save([dataPath,'outputParameters.mat'],'data')


