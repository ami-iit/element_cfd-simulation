close all; 
clear all; 
clc;


%% Test
experiment = 'exp_21_03_22'; % Name of the experiment data folder

addpath(genpath('../'));            % Adding the main folder path
figFolderName = ['pressure_fancy_fig-',experiment];
testList = dir([figFolderName,'/*-0001.fig']);  % List of the test files

%% Create the folder to store the GIF file
saveFolderName = ['pressure_fancy_gif-',experiment];
if (~exist(['./',saveFolderName],'dir'))
    mkdir(['./',saveFolderName]);
end

for testIndex = 2%:length(testList(:,1))
testID     = testList(testIndex).name(1:end-9);
filename   = [experiment,'-',testID];
testpointList = dir([figFolderName,'/',testID,'*.fig']);


%% Save each matlab .fig as a frame of the GIF file

v = VideoWriter(['.\',saveFolderName,'\',filename],'MPEG-4');
v.FrameRate = 20;
open(v)

for n = 1 : (length(testpointList(:,1)) )

    [~,testPoint,~] = fileparts(testpointList(n,:).name(10:end-4));
    
    h = openfig([figFolderName,'/',testID,'-',testPoint,'.fig']);

    % Set the frame dimensions
%     set(h, 'Position', [0 0 3840 2160]);
    
    % Capture the plot as a frame and append it to the file
    frame      = getframe(h);
    writeVideo(v,frame);
    
    % Close frame image
    close(h)
end

end
close(v)

rmpath(genpath('../'));            % Removing the main folder path



