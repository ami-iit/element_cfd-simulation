close all; clear all; clc;

%% Test
experiment = 'exp_03_11_22'; % Name of the experiment data folder
testID     = 'TID_0002';
filename   = [testID,'.gif'];

%% Import filename list and add local path
addpath(genpath('../'));            % Adding the main folder path
folderPath    = ['../',experiment,'/data_GVPM'];
testpointList = dir([folderPath,'/',testID,'*.pth']);


for n = 1 : (length(testpointList(:,1)) - 1)

    [~,testPoint,~] = fileparts(testpointList(n,:).name(12:15));
    
    h = openfig(['.\pressure-fig_',experiment,'\',testID,'-PT',testPoint,'.fig']);

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
        imwrite(imind,cm,filename,'gif', 'Loopcount',inf);
    else
        imwrite(imind,cm,filename,'gif','WriteMode','append', 'DelayTime', 0.5);
    end
    close(h)
end



