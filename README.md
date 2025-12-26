# blender_robot_animator_state_publisher
A Blender Python script for exporting robot joint angles to CSV/JSON formats, specifically designed for ROS (Robot Operating System) and robot control applications.

📋 Features

    Export joint angles (Euler angles) from Blender armatures

    Support for multiple export formats: JSON, CSV

    Batch export of animation frames (max 100 frames by default)

    Three CSV variants for different use cases

    Automatic directory creation

    Compatible with Blender 5.0+

🚀 Installation

    Copy the script to your Blender script directory or use inline execution

    For use in Blender Script Editor:

        Open Blender

        Go to Scripting workspace

        Open a new text editor

        Paste the script code and save the file

        Click Run Script

🎯 Usage
Requirements in Blender before you run the script

    Change : your_user_name around line 21 of the script  >>   export_dir = os.path.join(home, "your_user_name", "Desktop", "blender_ros_exports")

    Armature: A robot model with armature (skeleton)

    Animation: Keyframes for the desired movement

    Selection: Select the armature in the 3D viewport

    Mode: Ensure Blender is in Pose Mode


Files created:

    ik_bone_matrices.json - Complete bone matrices data

    joint_angles_degrees.json - Joint angles in JSON format

    joint_angles_full.csv - All angles (X,Y,Z) for each joint

    joint_angles_z_only.csv - Only Z-angles (for 2D robot arms)

    joint_angles_separated.csv - Separate columns per axis
