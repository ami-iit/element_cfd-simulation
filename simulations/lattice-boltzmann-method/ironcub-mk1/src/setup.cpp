#include "setup.hpp"

void main_setup() { // iRonCub; required extensions in defines.hpp: FP16C, EQUILIBRIUM_BOUNDARIES, SUBGRID, INTERACTIVE_GRAPHICS

	// ############################################################################ SET ROBOT ATTITUDE  ###############################################################################
	const float alpha = 90.0f;	// [deg] base pitch angle
	const float beta = 0.0f;	// [deg] base yaw angle

	// ################################################################## define simulation box size, viscosity and volume force ###################################################################
	const uint3 lbm_N = resolution(float3(0.5f, 1.0f, 0.8f), 1000); // input: simulation box aspect ratio and VRAM occupation in MB, output: grid resolution
	const float si_u = 17.0f;						// [m/s] flow speed
	const float si_length = 1.0f;					// [m] characteristic length 
	const float si_T = 1.0f;						// [s] total simulation time 
	const float video_length = 10.0f;				// [s] video lenght (==si_T -> normal speed, >si_T -> slow motion, <si_T -> fast forward)
	const float si_nu = 1.48E-5f;					// [m^2/s] kinematic viscosity 
	const float si_rho = 1.225f;					// [kg/m^3] density 
	const float lbm_length = 0.33f*(float)lbm_N.y;	// length of simulation box
	const float lbm_u = 0.1f;
	units.set_m_kg_s(lbm_length, lbm_u, 1.0f, si_length, si_u, si_rho);
	print_info("Re = "+to_string(to_uint(units.si_Re(si_length, si_u, si_nu))));

	// generate lattice Boltzmann object
	LBM lbm(lbm_N, 1u, 1u, 1u, units.nu(si_nu)); // run on 1 x 1 x 1 GPUs

	// ###################################################################### define geometry rotation data ########################################################################################
	const float si_t_start_rot = 10.0f; 						// time to start rotation [s]
	const float si_t_end_rot   = 1.5f; 							// time to end rotation [s]
	const float omega_pitch_rad = 1.57f; 						// pitch rotation velocity [rad/s]
	const float omega_pitch = omega_pitch_rad/units.t(1.0f); 	// pitch rotation velocity [lattice units]
	const uint lbm_dt = 1u; 									// revoxelize rotor every dt time steps
	const float d_pitch = omega_pitch*(float)lbm_dt; 			// pitch angle change per dt time steps

	// ###################################################################################### define geometry ######################################################################################
	Mesh* robot = read_stl(get_exe_path()+"../stl/ironcub.stl");	// load robot mesh
	// Mesh* left_turbine = read_stl(get_exe_path()+"../stl/left_turb.stl");		// load left turbine mesh

	const float3 robot_center = robot->get_center();

	// scale robot to fit into simulation box
	const float robot_size = robot->get_bounding_box_size().y; 
	const float scale = lbm_length/robot_size;	
	robot->scale(scale);
	// left_turbine->scale(scale);

	// move robot to desired position											
	const float3 offset = float3(0.0f, -0.5f*lbm_length, 0.0f);	// offset to center of simulation box
	robot->translate(lbm.center() - robot_center + offset);		// robot translation
	// left_turbine->translate(lbm.center() - robot_center + offset);		// robot translation

	// rotate robot to desired attitude
	const float3x3 rotation = float3x3(float3(0, 0, 1), radians(0.0f))*float3x3(float3(0, 1, 0), radians(0.0f))*float3x3(float3(1, 0, 0), radians(180.0f-alpha));
	robot->rotate(rotation);
	// left_turbine->rotate(rotation);

	// voxelize robot mesh
	lbm.voxelize_mesh_on_device(robot, TYPE_S|TYPE_X);	// voxelize robot mesh on GPU and mark voxels as solid (TYPE_S) and fixed (TYPE_X) (TYPE_X is required for FORCE_FIELD)
	// lbm.voxelize_mesh_on_device(left_turbine, TYPE_S|TYPE_Y);	// voxelize robot mesh on GPU and mark voxels as solid (TYPE_S) and fixed (TYPE_X) (TYPE_X is required for FORCE_FIELD)

	// ########################################################################  set boundary conditions ###########################################################################################
	const uint Nx=lbm.get_Nx(), Ny=lbm.get_Ny(), Nz=lbm.get_Nz(); parallel_for(lbm.get_N(), [&](ulong n) { uint x=0u, y=0u, z=0u; lbm.coordinates(n, x, y, z);
		if(lbm.flags[n]!=TYPE_S) lbm.u.y[n] = lbm_u;									// set inflow velocity to lbm_u
		if(x==0u||x==Nx-1u||y==0u||y==Ny-1u||z==0u||z==Nz-1u) lbm.flags[n] = TYPE_E;	// set equilibrium boundaries on all box sides
	}); 

	// ####################################################################### run simulation, export images and data ##############################################################################

	// Get the current time
    std::time_t current_time = std::time(nullptr);

    // Convert the current time to a struct tm (time information)
    struct std::tm time_info;

	#ifdef _WIN32
	localtime_s(&time_info, &current_time);
	#else
	localtime_r(&time_info, &current_time);
	#endif
	std::string date_str = std::to_string(time_info.tm_year + 1900) + '_' + std::to_string(time_info.tm_mon + 1) + '_' + std::to_string(time_info.tm_mday);
	std::string time_str = std::to_string(time_info.tm_hour) + '_' + std::to_string(time_info.tm_min) + '_' + std::to_string(time_info.tm_sec);
	std::string test_name = date_str + "_" + time_str;
	
	lbm.graphics.visualization_modes = VIS_FLAG_SURFACE|VIS_Q_CRITERION;
	lbm.run(0u); 			// initialize simulation
	lbm.write_status(get_exe_path()+"export/"+test_name+"/");		// write simulation status to file
	

	// set up data export
	#if defined(FP16S)
		const string data_path = get_exe_path()+"export/"+test_name+"/data/FP16S/";
	#elif defined(FP16C)
		const string data_path = get_exe_path()+"export/"+test_name+"/data/FP16C/";
	#else // FP32
		const string data_path = get_exe_path()+"export/"+test_name+"/data/FP32/";
	#endif // FP32
	const uint prec = 6u;																	// precision of data output
	write_file(data_path+"forces.dat",  "#      t\t      CdA\t      ClA\t      CsA\n");		// initialize forces data file
	write_file(data_path+"torques.dat", "#      t\t      CrAl\t      CpAl\t      CyAl\n");	// initialize torques data file

	// MAN SIMULATION LOOP
	while(lbm.get_t()<=units.t(si_T)) {
		#if defined(GRAPHICS) && !defined(INTERACTIVE_GRAPHICS)
			if(lbm.graphics.next_frame(units.t(si_T), video_length)) {
				// set up camera position and write frame to file for 60 Hz video acquisition
				lbm.graphics.set_camera_centered(-30.0f, 20.0f, 100.0f, 1.25f);	// camera position: (Rx, Ry, FOV, zoom)
				lbm.graphics.write_frame(get_exe_path()+"export/"+test_name+"/png/");
			}
		#endif // GRAPHICS && !INTERACTIVE_GRAPHICS
		if(lbm.get_t()>=units.t(si_t_start_rot) && lbm.get_t()<=units.t(si_t_end_rot)) {
			// rotate robot mesh and revoxelize it every lbm_dt time steps during rotation
			lbm.voxelize_mesh_on_device(robot, TYPE_S, robot->get_center(), float3(0.0f), float3(omega_pitch, 0.0f, 0.0f)); // revoxelize mesh on GPU
			lbm.run(lbm_dt); 																								// run dt time steps
			robot->rotate(float3x3(float3(1.0f, 0.0f, 0.0f), d_pitch)); 													// rotate mesh
		} else {
			// run simulation without robot rotation
			lbm.run(lbm_dt); // run 1 time step
		}
		#if defined(FORCE_FIELD)
			// compute force and torques on robot
			lbm.calculate_force_on_boundaries();
			lbm.F.read_from_device();
			const float3 lbm_force = lbm.calculate_force_on_object(TYPE_S|TYPE_X); // compute total force on object (TYPE_S)
			const float3 lbm_torque = lbm.calculate_torque_on_object(robot_center, TYPE_S|TYPE_X); // compute total torque on object (TYPE_S)
			// compute force areas and torque coefficients on robot in SI units
			const float CdA  =  units.si_F(lbm_force.y)/(0.5f*si_rho*sq(si_u));
			const float ClA  =  units.si_F(lbm_force.z)/(0.5f*si_rho*sq(si_u));
			const float CsA  = -units.si_F(lbm_force.x)/(0.5f*si_rho*sq(si_u));
			const float CrAl =  units.si_T(lbm_torque.y)/(0.5f*si_rho*sq(si_u));
			const float CpAl = -units.si_T(lbm_torque.x)/(0.5f*si_rho*sq(si_u));
			const float CyAl =  units.si_T(lbm_torque.z)/(0.5f*si_rho*sq(si_u));
			// write force and torque data to file
			write_line(data_path+"forces.dat", to_string(lbm.get_t())+"\t"+to_string(units.si_t(lbm.get_t()), prec)+"\t"+to_string(CdA, prec)+"\t"+to_string(ClA, prec)+"\t"+to_string(CsA, prec)+"\n");
			write_line(data_path+"torques.dat", to_string(lbm.get_t())+"\t"+to_string(units.si_t(lbm.get_t()), prec)+"\t"+to_string(CrAl, prec)+"\t"+to_string(CpAl, prec)+"\t"+to_string(CyAl, prec)+"\n");
		#endif
	}

	// write simulation status to file and exit
	lbm.write_status(get_exe_path()+"export/"+test_name+"/");
} /**/