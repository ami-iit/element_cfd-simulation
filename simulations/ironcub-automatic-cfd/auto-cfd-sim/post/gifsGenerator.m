close all; 
clear all; 
clc;


%% Test
figFolderName = 'data_post/figures/';
testList      = dir([figFolderName,'/cfd-*-a00-b00.fig']);  % List of the test files

%% Create the folder to store the GIF file
saveFolderName = 'data_post/gifs/';
if (~exist(['./',saveFolderName],'dir'))
    mkdir(['./',saveFolderName]);
end

%% Cycle init
dataPath = '../data/';
dataFile = [dataPath,'outputParameters.mat'];
load(dataFile);
jointConfigNames = fieldnames(data);


%% Save each matlab .fig as a frame of the GIF file

for jointConfigIndex = 1 : length(fieldnames(data))

    jointConfigName = jointConfigNames{jointConfigIndex};

    for simIndex = 1 : length(data.(jointConfigName).yawAngle(:))

        yawAngle   = data.(jointConfigName).yawAngle(simIndex);
        pitchAngle = data.(jointConfigName).pitchAngle(simIndex);

        h = openfig([figFolderName,'/cfd-',jointConfigName,'-a',num2str(pitchAngle,'%02.f'),'-b',num2str(yawAngle,'%02.f'),'.fig']);

        % Set the frame dimensions
        set(h, 'Position', [0 0 1620 1080]);

        % Capture the plot as an image
        frame      = getframe(h);
        im         = frame2im(frame);
        [imind,cm] = rgb2ind(im,256);

        % Write to the GIF File
        if simIndex == 1
            imwrite(imind,cm,['./',saveFolderName,'/cfd-',jointConfigName,'.gif'],'gif','Loopcount',inf);
        else
            imwrite(imind,cm,['./',saveFolderName,'/cfd-',jointConfigName,'.gif'],'gif','WriteMode','append', 'DelayTime', 0.05);
        end
        close(h)
    end

end



