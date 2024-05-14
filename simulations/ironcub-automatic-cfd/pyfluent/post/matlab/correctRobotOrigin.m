function [] = correctRobotOrigin(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc)

    % Origin correction
    world_R_Fluent  = rotx(90)*roty(-90);   % by definition
    world_H_fluent  = [world_R_Fluent, zeros(3,1);
                           zeros(1,3),         1];
    
    world_H_base    = iDynTreeWrappers.getWorldTransform(KinDynModel,'root_link');
    world_H_l_hip_2 = iDynTreeWrappers.getWorldTransform(KinDynModel,'l_hip_2');
    world_H_r_hip_2 = iDynTreeWrappers.getWorldTransform(KinDynModel,'r_hip_2');
    
    world_d_fluent  = (world_H_l_hip_2(1:3,4) + world_H_r_hip_2(1:3,4))/2 +world_H_r_hip_2(1:3,1:3)*[0;0;0];
    world_H_fluent(1:3,4) = world_d_fluent;
    fluent_H_world = [world_R_Fluent', -world_R_Fluent'*world_d_fluent;
                           zeros(1,3),         1];
    
    
    basePose = fluent_H_world*basePose;
    iDynTreeWrappers.setRobotState(KinDynModel, basePose, jointPos, baseVel, jointVel, gravAcc);

end