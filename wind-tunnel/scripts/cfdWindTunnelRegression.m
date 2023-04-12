%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script automatically imports the GVPM wind tunnel experiments data 
% exported in .mat format and performs regression on the acquired dataset
%
% Author: Antonello Paolino
%
% April 2022
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;
clear all; 
clc;

%% %%%%%%%%%%%%%%%%%%%%%%%%%%%% LOAD DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Set Experiment Path
cfdPath = '../../cfd/wind-tunnel/results/error/';
testList = dir(cfdPath);  % List of the test files


data = struct();

variable = {'alpha','beta','CdA_ke','CdA_kw','ClA_ke','ClA_kw','CsA_ke','CsA_kw', ...
               'CrAl_ke','CrAl_kw','CpAl_ke','CpAl_kw','CyAl_ke','CyAl_kw'};

for i = 1:length(variable)
    data.(variable{i}) = nan(3,1);
end


% Load error data
for testIndex = 1:length(testList(:,1)) % from 3 to avoid '.' and '..' directories and regressionCoefficients file
    if ~matches(testList(testIndex).name,{'.','..','regressionCoefficients.mat'})
        testID        = testList(testIndex).name(1:end-4);
        test.(testID) = load([cfdPath,testID,'.mat']);

        for i = 1:length(variable)
            if isfield(test.(testID).error,variable{i})
                variable_add = test.(testID).error.(variable{i});
            else
                variable_add = nan(length(test.(testID).error.(variable{1})),1);
            end
            variable_old       = data.(variable{i});
            data.(variable{i}) = cat(1,variable_old,variable_add);
        end
    end
end

%% %%%%%%%%%%%%%%%%%%%%%%%%% CdA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

coefs = struct();

for i = 3 : length(variable)

    validIndices = ~isnan(data.(variable{i}));

    a = data.alpha(validIndices);
    b = data.beta(validIndices);

    X = [ones(length(a),1), a, a.^2, b, b.^2, a.*b];

%     coefs.(variable{i}) = lasso(X,data.(variable{i})(validIndices));

    coefs.(variable{i}) = pinv(X)*data.(variable{i})(validIndices);

end

%% %%%%%%%%%%%%%%%%%%% SAVE COEFFICIENTS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

save([cfdPath,'regressionCoefficients.mat'],'coefs');






