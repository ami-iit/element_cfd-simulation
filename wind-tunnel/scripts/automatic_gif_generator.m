close all; 
clear all; 
clc;


%% Test
experiment = 'exp_03_11_22'; % Name of the experiment data folder

addpath(genpath('../'));            % Adding the main folder path
GVPM_folderPath    = ['../',experiment,'/data_GVPM'];
testList = dir([GVPM_folderPath,'/*.GVP']);  % List of the test files

%% Create the folder to store the GIF file
    saveFolderName = ['pressure_gif-',experiment];
    if (~exist(['./',saveFolderName],'dir'))

        mkdir(['./',saveFolderName]);
    end

for testIndex = 1:length(testList(:,1))
testID     = testList(testIndex).name(1:end-4);
filename   = [experiment,'-',testID,'.gif'];
testpointList = dir([GVPM_folderPath,'/',testID,'*.pth']);


%% Save each matlab .fig as a frame of the GIF file

for n = 1 : (length(testpointList(:,1)) - 1)

    [~,testPoint,~] = fileparts(testpointList(n,:).name(12:15));
    
    h = openfig(['.\pressure_fig-',experiment,'\',testID,'-PT',testPoint,'.fig']);

    % Set the frame dimensions
    set(h, 'Position', [0 0 2304 1296]);

%     axis tight manual % this ensures that getframe() returns a consistent size
%     axis([-0.5 1 -1 1 -1 1])
    
    % Capture the plot as an image
    frame      = getframe(h);
    im         = frame2im(frame);
    [imind,cm] = rgb2ind(im,256);
    
    % Write to the GIF File
    if n == 1
        imwrite(imind,cm,['.\',saveFolderName,'\',filename],'gif', 'Loopcount',inf);
    else
        imwrite(imind,cm,['.\',saveFolderName,'\',filename],'gif','WriteMode','append', 'DelayTime', 0.5);
    end
    close(h)
end

end


rmpath(genpath('../'));            % Removing the main folder path



