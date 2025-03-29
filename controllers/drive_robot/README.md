# ANYmal C in Webots

ANYmal C is a quadruped by Anybotics. Here 

## Prerequisites
Ensure you have Webots installed on your system. Additionally, install `urdf2webots`:
```bash
pip install urdf2webots
```

## Cloning the Repository
Clone the **ANYmal C Simple Description** repository:
```bash
git clone https://github.com/ANYbotics/anymal_c_simple_description.git
```

## Creating a Webots Project
1. Open Webots and create a new project.
2. Inside your Webots project directory, create a `protos` folder.
3. Copy the **URDF** folder from the cloned repository into your Webots project folder.

## Converting URDF to PROTO
Navigate to your Webots project folder and run:
```bash
python -m urdf2webots.importer \
    --input=anymal_c_simple_description/urdf/anymal.urdf \
    --output=protos/anymal.proto \
    --box-collision --normal
```

## Creating a Webots World
1. Create a new `.wbt` world file inside the `worlds` folder.
2. Use the following directory structure:

```
C:.
│   .gitignore
│   LICENSE.txt
│   
├───controllers
│   └───drive_robot
│           drive_robot.py
│
├───protos
│   │   anymal.proto
│   ├───anymal_textures
│   ├───icons
│   │       Astra.png
│   └───stretch_textures
└───worlds
        world.wbt
```

## Implementing the Robot Controller
Create a Python controller in `controllers/drive_robot/drive_robot.py`:
```python
from controller import Robot, Keyboard

robot = Robot()
timestep = int(robot.getBasicTimeStep())
keyboard = Keyboard()
keyboard.enable(timestep)

motor_names = [
    "LF_HAA", "LF_HFE", "LF_KFE",
    "RF_HAA", "RF_HFE", "RF_KFE",
    "LH_HAA", "LH_HFE", "LH_KFE",
    "RH_HAA", "RH_HFE", "RH_KFE"
]

motors = {name: robot.getDevice(name) for name in motor_names}
for motor in motors.values():
    motor.setPosition(0.0)

while robot.step(timestep) != -1:
    key = keyboard.getKey()
    if key == ord('W'):
        for motor in motors.values():
            motor.setPosition(0.5)
```

## Running the Simulation
1. Open Webots.
2. Load the `world.wbt` file.
3. Select the **ANYmal C** robot and assign `drive_robot` as its controller.
4. Run the simulation.

Your **ANYmal C** robot is now ready to be controlled in Webots!

