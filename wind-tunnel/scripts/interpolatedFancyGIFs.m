close all; 
clear all; 
clc;


%% Test
experiment = 'exp_03_11_22'; % Name of the experiment data folder

addpath(genpath('../'));            % Adding the main folder path
figFolderName = ['pressure_fancy_fig-',experiment];
testList = dir([figFolderName,'/*-0001.fig']);  % List of the test files

%% Create the folder to store the GIF file
saveFolderName = ['pressure_fancy_gif-',experiment];
if (~exist(['./',saveFolderName],'dir'))
    mkdir(['./',saveFolderName]);
end

for testIndex = 1:length(testList(:,1))
testID     = testList(testIndex).name(1:end-9);
filename   = [experiment,'-',testID,'.gif'];
testpointList = dir([figFolderName,'/',testID,'*.fig']);


%% Save each matlab .fig as a frame of the GIF file

for n = 1 : (length(testpointList(:,1)) - 1)

    [~,testPoint,~] = fileparts(testpointList(n,:).name(10:end-4));
    
    h = openfig([figFolderName,'/',testID,'-',testPoint,'.fig']);

    % Set the frame dimensions
    set(h, 'Position', [0 0 1620 1080]);
    
    % Capture the plot as an image
    frame      = getframe(h);
    im         = frame2im(frame);
    [imind,cm] = rgb2ind(im,256);
    
    % Write to the GIF File
    if n == 1
        imwrite(imind,cm,['.\',saveFolderName,'\',filename],'gif', 'Loopcount',inf);
    else
        imwrite(imind,cm,['.\',saveFolderName,'\',filename],'gif','WriteMode','append', 'DelayTime', 0.05);
    end
    close(h)
end

end


rmpath(genpath('../'));            % Removing the main folder path



