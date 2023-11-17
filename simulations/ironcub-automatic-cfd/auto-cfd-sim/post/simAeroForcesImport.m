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
left_right_ind = [1 2 4 3 7 8 5 6 9 12 13 10 11];
stopIndex  = 0;
loopIter   = 1;

while (stopIndex < height(table1(:,1)))

    % acquiring data from the .csv file structure
    startIndex = stopIndex + 1;
    configName = table1.config{startIndex};
    data.(table1.config{startIndex}).jointConfig = table2array(table2(matches(table2{:,1},configName),2:end));
    for col = 2:length(varNames)
        data.(table1.config{startIndex}).(varNames{col}) = table2array(table1(matches(table1.config,configName),col));
    end
    stopIndex = startIndex + height(table1(matches(table1.config,configName),col)) - 1;
    
%%%%% mirroring symmetric configurations data %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    if matches(configName, {'hovering','flight30','flight60'})
        for i = 1 : length(data.(configName).yawAngle)
            if (data.(configName).yawAngle(i) ~= 0)
                % Update attitudes
                data.(configName).yawAngle   = [data.(configName).yawAngle; -data.(configName).yawAngle(i)];
                data.(configName).pitchAngle = [data.(configName).pitchAngle; data.(configName).pitchAngle(i)];
                fieldNames = fieldnames(data.(configName));
                for fieldIndex = 1 : length(fieldNames)
                    fieldName = fieldNames{fieldIndex};
                    aliasFieldName = fieldName;
                    if contains(aliasFieldName,'left')
                        aliasFieldName = ['right',fieldName(5:end)];
                    elseif contains(aliasFieldName,'right')
                        aliasFieldName = ['left',fieldName(6:end)];
                    end
                    if contains(aliasFieldName,'_cd')
                        data.(configName).(fieldName) = [data.(configName).(fieldName); data.(configName).(aliasFieldName)(i)];
                    elseif contains(fieldName,'_cl')
                        data.(configName).(fieldName) = [data.(configName).(fieldName); data.(configName).(aliasFieldName)(i)];
                    elseif contains(fieldName,'_cs')
                        data.(configName).(fieldName) = [data.(configName).(fieldName); -data.(configName).(aliasFieldName)(i)];
                    end
                end
            end
        end
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%% TODO: mirroring non-symmetric configurations data %%%%%%%%%%%%%%%%%%%
    if ~matches(configName, {'hovering','flight30','flight60'})
        aliasConfigName = [configName,'_alias'];
        data.(aliasConfigName).jointConfig = nan(1,19);
        data.(aliasConfigName).jointConfig(1) = data.(configName).jointConfig(1);
        data.(aliasConfigName).jointConfig(2:3) = -data.(configName).jointConfig(2:3);
        data.(aliasConfigName).jointConfig([4:7, 12:15]) = data.(configName).jointConfig([8:11, 16:19]);
        data.(aliasConfigName).jointConfig([8:11, 16:19]) = data.(configName).jointConfig([4:7, 12:15]);
        for i = 1 : length(data.(configName).yawAngle)
            % Update attitudes
            data.(aliasConfigName).yawAngle(i,:)   = -data.(configName).yawAngle(i);
            data.(aliasConfigName).pitchAngle(i,:) =  data.(configName).pitchAngle(i);
            fieldNames = fieldnames(data.(configName));
            for fieldIndex = 1 : length(fieldNames)
                fieldName = fieldNames{fieldIndex};
                aliasFieldName = fieldName;
                if contains(aliasFieldName,'left')
                    aliasFieldName = ['right',fieldName(5:end)];
                elseif contains(aliasFieldName,'right')
                    aliasFieldName = ['left',fieldName(6:end)];
                end
                if contains(fieldName,'_cd')
                    data.(aliasConfigName).(fieldName)(i,:) = data.(configName).(aliasFieldName)(i);
                elseif contains(fieldName,'_cl')
                    data.(aliasConfigName).(fieldName)(i,:) = data.(configName).(aliasFieldName)(i);
                elseif contains(fieldName,'_cs')
                    data.(aliasConfigName).(fieldName)(i,:) = -data.(configName).(aliasFieldName)(i);
                end
            end

        end
    end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


end

%% Save imported struct data in workspace
save([dataPath,'outputParameters.mat'],'data')


