from controller import Robot, Motor, PositionSensor, Keyboard

# Create the Robot instance
robot = Robot()

# Get the time step of the current world
timestep = int(robot.getBasicTimeStep())

# Enable keyboard
keyboard = Keyboard()
keyboard.enable(timestep)

# Motor names from the PROTO file
motor_names = [
    "LF_HAA", "LF_HFE", "LF_KFE",  # Left Front leg
    "RF_HAA", "RF_HFE", "RF_KFE",  # Right Front leg
    "LH_HAA", "LH_HFE", "LH_KFE",  # Left Hind leg
    "RH_HAA", "RH_HFE", "RH_KFE"   # Right Hind leg
]

sensor_names = [
    "LF_HAA_sensor", "LF_HFE_sensor", "LF_KFE_sensor",
    "RF_HAA_sensor", "RF_HFE_sensor", "RF_KFE_sensor",
    "LH_HAA_sensor", "LH_HFE_sensor", "LH_KFE_sensor",
    "RH_HAA_sensor", "RH_HFE_sensor", "RH_KFE_sensor"
]

# Initialize motors and sensors
motors = {}
sensors = {}

for name in motor_names:
    motors[name] = robot.getDevice(name)
    # Use position control instead of velocity control
    motors[name].setPosition(0.0)

for name in sensor_names:
    sensors[name] = robot.getDevice(name)
    sensors[name].enable(timestep)

# Movement parameters
max_velocity = 1.0  # rad/s
step_height = 0.2   # Height to lift legs during step
step_length = 0.3   # Forward movement distance

# Default leg positions (standing stance)
default_positions = {
    "LF": {"HAA": 0.0, "HFE": -0.5, "KFE": 1.0},
    "RF": {"HAA": 0.0, "HFE": -0.5, "KFE": 1.0},
    "LH": {"HAA": 0.0, "HFE": -0.5, "KFE": 1.0},
    "RH": {"HAA": 0.0, "HFE": -0.5, "KFE": 1.0}
}

# Current target positions
target_positions = {}
for leg in ["LF", "RF", "LH", "RH"]:
    target_positions[leg] = default_positions[leg].copy()

def set_leg_position(leg_prefix, haa_pos, hfe_pos, kfe_pos, velocity=max_velocity):
    """Set position for a specific leg with velocity control"""
    motors[f"{leg_prefix}_HAA"].setPosition(haa_pos)
    motors[f"{leg_prefix}_HFE"].setPosition(hfe_pos)
    motors[f"{leg_prefix}_KFE"].setPosition(kfe_pos)
    
    motors[f"{leg_prefix}_HAA"].setVelocity(velocity)
    motors[f"{leg_prefix}_HFE"].setVelocity(velocity)
    motors[f"{leg_prefix}_KFE"].setVelocity(velocity)

def process_keyboard():
    """Process keyboard input and return movement commands"""
    key = keyboard.getKey()
    
    # Debug the key value
    if key != -1:
        print(f"Key pressed: {key} (ASCII: {chr(key) if 32 <= key <= 126 else 'non-printable'})")
    
    forward = 0.0
    turn = 0.0
    lift = False
    reset = False
    
    # Check for both uppercase and lowercase keys
    if key == ord("W") or key == ord("w"):
        forward = 1.0
        print("Moving forward")
    elif key == ord("S") or key == ord("s"):
        forward = -1.0
        print("Moving backward")
    elif key == ord("A") or key == ord("a"):
        turn = 1.0
        print("Turning left")
    elif key == ord("D") or key == ord("d"):
        turn = -1.0
        print("Turning right")
    elif key == ord("L") or key == ord("l"):
        lift = True
        print("Lifting legs")
    elif key == ord("R") or key == ord("r"):
        reset = True
        print("Resetting position")
    
    return forward, turn, lift, reset

def stand_position():
    """Set all legs to standing position"""
    for leg in ["LF", "RF", "LH", "RH"]:
        set_leg_position(
            leg,
            default_positions[leg]["HAA"],
            default_positions[leg]["HFE"],
            default_positions[leg]["KFE"]
        )
        # Update target positions
        target_positions[leg] = default_positions[leg].copy()

def trot_gait(phase, forward, turn):
    """Implement a trot gait (diagonal pairs move together)"""
    # Diagonal pairs: LF+RH and RF+LH
    if phase < 0.5:  # First diagonal pair (LF and RH)
        # Swing phase for LF and RH
        if phase < 0.25:
            # Lift leg
            lf_hfe = default_positions["LF"]["HFE"] - step_height
            rh_hfe = default_positions["RH"]["HFE"] - step_height
            
            # Adjust for forward/turning motion
            lf_haa = default_positions["LF"]["HAA"] - turn * 0.1
            rh_haa = default_positions["RH"]["HAA"] + turn * 0.1
            
            lf_kfe = default_positions["LF"]["KFE"] + forward * step_length
            rh_kfe = default_positions["RH"]["KFE"] + forward * step_length
        else:
            # Put leg down
            lf_hfe = default_positions["LF"]["HFE"]
            rh_hfe = default_positions["RH"]["HFE"]
            
            lf_haa = default_positions["LF"]["HAA"] - turn * 0.1
            rh_haa = default_positions["RH"]["HAA"] + turn * 0.1
            
            lf_kfe = default_positions["LF"]["KFE"] + forward * step_length
            rh_kfe = default_positions["RH"]["KFE"] + forward * step_length
        
        # Stance phase for RF and LH (keep planted)
        rf_haa = default_positions["RF"]["HAA"] + turn * 0.1
        rf_hfe = default_positions["RF"]["HFE"]
        rf_kfe = default_positions["RF"]["KFE"] - forward * step_length
        
        lh_haa = default_positions["LH"]["HAA"] - turn * 0.1
        lh_hfe = default_positions["LH"]["HFE"]
        lh_kfe = default_positions["LH"]["KFE"] - forward * step_length
        
    else:  # Second diagonal pair (RF and LH)
        # Swing phase for RF and LH
        if phase < 0.75:
            # Lift leg
            rf_hfe = default_positions["RF"]["HFE"] - step_height
            lh_hfe = default_positions["LH"]["HFE"] - step_height
            
            # Adjust for forward/turning motion
            rf_haa = default_positions["RF"]["HAA"] + turn * 0.1
            lh_haa = default_positions["LH"]["HAA"] - turn * 0.1
            
            rf_kfe = default_positions["RF"]["KFE"] + forward * step_length
            lh_kfe = default_positions["LH"]["KFE"] + forward * step_length
        else:
            # Put leg down
            rf_hfe = default_positions["RF"]["HFE"]
            lh_hfe = default_positions["LH"]["HFE"]
            
            rf_haa = default_positions["RF"]["HAA"] + turn * 0.1
            lh_haa = default_positions["LH"]["HAA"] - turn * 0.1
            
            rf_kfe = default_positions["RF"]["KFE"] + forward * step_length
            lh_kfe = default_positions["LH"]["KFE"] + forward * step_length
        
        # Stance phase for LF and RH (keep planted)
        lf_haa = default_positions["LF"]["HAA"] - turn * 0.1
        lf_hfe = default_positions["LF"]["HFE"]
        lf_kfe = default_positions["LF"]["KFE"] - forward * step_length
        
        rh_haa = default_positions["RH"]["HAA"] + turn * 0.1
        rh_hfe = default_positions["RH"]["HFE"]
        rh_kfe = default_positions["RH"]["KFE"] - forward * step_length
    
    # Apply positions
    set_leg_position("LF", lf_haa, lf_hfe, lf_kfe)
    set_leg_position("RF", rf_haa, rf_hfe, rf_kfe)
    set_leg_position("LH", lh_haa, lh_hfe, lh_kfe)
    set_leg_position("RH", rh_haa, rh_hfe, rh_kfe)
    
    # Update target positions
    target_positions["LF"] = {"HAA": lf_haa, "HFE": lf_hfe, "KFE": lf_kfe}
    target_positions["RF"] = {"HAA": rf_haa, "HFE": rf_hfe, "KFE": rf_kfe}
    target_positions["LH"] = {"HAA": lh_haa, "HFE": lh_hfe, "KFE": lh_kfe}
    target_positions["RH"] = {"HAA": rh_haa, "HFE": rh_hfe, "KFE": rh_kfe}

# Main control loop
phase = 0.0
phase_increment = 0.05
last_command_time = 0
moving = False

# Start in standing position
stand_position()
print("Controller started. Use WASD to move, L to lift legs, R to reset position.")

while robot.step(timestep) != -1:
    # Get keyboard input
    forward, turn, lift, reset = process_keyboard()
    
    current_time = robot.getTime()
    
    # Reset to default position if requested
    if reset:
        stand_position()
        moving = False
        phase = 0.0
        continue
    
    # Handle movement commands
    if forward != 0 or turn != 0:
        # Start or continue movement
        moving = True
        # Update phase for smooth gait
        phase = (phase + phase_increment) % 1.0
        # Apply trot gait
        trot_gait(phase, forward, turn)
        last_command_time = current_time
    elif lift:
        # Simple lift test
        moving = False
        for leg in ["LF", "RF", "LH", "RH"]:
            set_leg_position(leg, 0.0, -0.3, 0.6)
    elif moving and current_time - last_command_time > 0.5:
        # Stop movement after a short delay with no commands
        stand_position()
        moving = False
        phase = 0.0
    
    # Optional: Print a single sensor value for debugging (less console spam)
    if current_time % 1.0 < timestep / 1000.0:  # Print only once per second
        print(f"LF_HFE_sensor: {sensors['LF_HFE_sensor'].getValue()}")