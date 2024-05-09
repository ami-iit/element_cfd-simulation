function data = importFluentData(surfacePressuresFilePath, l_turb_local_H_fluent)

fluentData = importdata(surfacePressuresFilePath);

data = struct();
data.x_fluent = fluentData.data(:,2);
data.y_fluent = fluentData.data(:,3);
data.z_fluent = fluentData.data(:,4);
data.press  = fluentData.data(:,5);

l_turb_local_coord = l_turb_local_H_fluent*[data.x_fluent data.y_fluent data.z_fluent ones(length(data.x_fluent),1)]';
l_turb_local_coord = l_turb_local_coord';

data.x_local  = l_turb_local_coord(:,1);
data.y_local  = l_turb_local_coord(:,2);
data.z_local  = l_turb_local_coord(:,3);

end