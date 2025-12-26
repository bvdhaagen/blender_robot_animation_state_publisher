import bpy
import json
import os
import math
import csv
from mathutils import Vector, Matrix, Euler

print("=== CALCULATE JOINT ANGLES FROM IK ===")

obj = bpy.context.active_object
if not obj or obj.type != 'ARMATURE':
    print("❌ Selecteer een armature!")
else:
    print(f"🤖 Armature: {obj.name}")
    print(f"📊 Aantal frames: {bpy.context.scene.frame_start} tot {bpy.context.scene.frame_end}")
    
    bones = obj.pose.bones
    scene = bpy.context.scene
    
    home = os.path.expanduser("~")
    export_dir = os.path.join(home, "bart", "Desktop", "blender_ros_exports")
    
    # Maak export directory aan als deze niet bestaat
    os.makedirs(export_dir, exist_ok=True)
    
    # DATA 1: Bone matrices (voor back-up/analyse)
    print("\n📁 Exporting bone matrices...")
    
    frames_data = []
    
    for frame in range(scene.frame_start, min(scene.frame_end + 1, 101)):  # Max 100 frames
        scene.frame_set(frame)
        
        frame_matrices = {}
        
        for bone in bones:
            matrix = bone.matrix  # Wereld space
            
            matrix_list = []
            for row in matrix:
                matrix_list.append([float(v) for v in row])
            
            frame_matrices[bone.name] = matrix_list
        
        frames_data.append({
            "frame": frame,
            "matrices": frame_matrices
        })
    
    # Export matrices als JSON
    output_path = os.path.join(export_dir, "ik_bone_matrices.json")
    with open(output_path, 'w') as f:
        json.dump({
            "armature": obj.name,
            "bones": [b.name for b in bones],
            "frames": frames_data
        }, f, indent=2)
    
    print(f"✅ Bone matrices exported: {output_path}")
    
    # DATA 2: DIRECT EULER ANGLES (in graden)
    print("\n📐 Calculating Euler angles from matrices...")
    
    euler_order = 'XYZ'
    angles_data = []
    
    for frame in range(scene.frame_start, min(scene.frame_end + 1, 101)):
        scene.frame_set(frame)
        
        frame_angles = {}
        
        for bone in bones:
            matrix = bone.matrix
            euler_rad = matrix.to_euler(euler_order)
            
            euler_deg = (
                math.degrees(euler_rad.x),
                math.degrees(euler_rad.y),
                math.degrees(euler_rad.z)
            )
            
            frame_angles[bone.name] = {
                "x_deg": round(euler_deg[0], 4),
                "y_deg": round(euler_deg[1], 4),
                "z_deg": round(euler_deg[2], 4)
            }
        
        angles_data.append({
            "frame": frame,
            "angles": frame_angles
        })
    
    # Export angles in degrees als JSON
    angles_json_path = os.path.join(export_dir, "joint_angles_degrees.json")
    with open(angles_json_path, 'w') as f:
        json.dump({
            "armature": obj.name,
            "euler_order": euler_order,
            "units": "degrees",
            "frames": angles_data
        }, f, indent=2)
    
    print(f"✅ Joint angles JSON exported: {angles_json_path}")
    
    # EXPORT 1: Volledige CSV met alle hoeken (X, Y, Z voor elke bot)
    print("\n📋 Creating full CSV with all angles...")
    
    csv_path_full = os.path.join(export_dir, "joint_angles_full.csv")
    
    if angles_data:
        # Maak kolomnamen
        column_names = ["frame"]
        bone_names = []
        
        # Haal alle botnamen op uit de eerste frame
        first_frame_angles = angles_data[0]["angles"]
        for bone_name in first_frame_angles.keys():
            bone_names.append(bone_name)
            column_names.extend([f"{bone_name}_x", f"{bone_name}_y", f"{bone_name}_z"])
        
        # Schrijf CSV
        with open(csv_path_full, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Schrijf header
            writer.writerow(column_names)
            
            # Schrijf data voor elke frame
            for frame_data in angles_data:
                frame_num = frame_data["frame"]
                angles = frame_data["angles"]
                
                row = [frame_num]
                
                for bone_name in bone_names:
                    if bone_name in angles:
                        bone_angles = angles[bone_name]
                        row.extend([bone_angles["x_deg"], bone_angles["y_deg"], bone_angles["z_deg"]])
                    else:
                        row.extend([0, 0, 0])  # Standaard waarden als bot niet bestaat
                
                writer.writerow(row)
        
        print(f"✅ Full CSV exported: {csv_path_full}")
    
    # EXPORT 2: CSV met alleen Z-hoeken (voor 2D robotarmen)
    print("\n📋 Creating simplified CSV with Z-angles only...")
    
    csv_path_simple = os.path.join(export_dir, "joint_angles_z_only.csv")
    
    if angles_data:
        # Maak kolomnamen
        column_names = ["frame"]
        bone_names = []
        
        # Haal alle botnamen op uit de eerste frame
        first_frame_angles = angles_data[0]["angles"]
        for bone_name in first_frame_angles.keys():
            # Maak kortere namen voor CSV
            short_name = bone_name.replace(".", "_")
            bone_names.append((bone_name, short_name))
            column_names.append(f"{short_name}_z")
        
        # Schrijf CSV
        with open(csv_path_simple, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Schrijf header
            writer.writerow(column_names)
            
            # Schrijf data voor elke frame
            for frame_data in angles_data:
                frame_num = frame_data["frame"]
                angles = frame_data["angles"]
                
                row = [frame_num]
                
                for bone_name, short_name in bone_names:
                    if bone_name in angles:
                        bone_angles = angles[bone_name]
                        row.append(bone_angles["z_deg"])
                    else:
                        row.append(0)  # Standaard waarde als bot niet bestaat
                
                writer.writerow(row)
        
        print(f"✅ Simplified CSV exported: {csv_path_simple}")
    
    # EXPORT 3: CSV met X,Y,Z apart per bot (één kolom per as)
    print("\n📋 Creating separated CSV (X, Y, Z per bone)...")
    
    csv_path_separated = os.path.join(export_dir, "joint_angles_separated.csv")
    
    if angles_data:
        # Maak kolomnamen per as
        axes = ["x", "y", "z"]
        column_names = ["frame"]
        
        # Haal alle botnamen op uit de eerste frame
        first_frame_angles = angles_data[0]["angles"]
        bone_names = list(first_frame_angles.keys())
        
        # Voeg kolommen toe per as
        for axis in axes:
            for bone_name in bone_names:
                short_name = bone_name.replace(".", "_")
                column_names.append(f"{short_name}_{axis}")
        
        # Schrijf CSV
        with open(csv_path_separated, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Schrijf header
            writer.writerow(column_names)
            
            # Schrijf data voor elke frame
            for frame_data in angles_data:
                frame_num = frame_data["frame"]
                angles = frame_data["angles"]
                
                row = [frame_num]
                
                # Voeg eerst alle X waarden toe, dan alle Y, dan alle Z
                for axis in axes:
                    for bone_name in bone_names:
                        if bone_name in angles:
                            bone_angles = angles[bone_name]
                            row.append(bone_angles[f"{axis}_deg"])
                        else:
                            row.append(0)
                
                writer.writerow(row)
        
        print(f"✅ Separated CSV exported: {csv_path_separated}")
    
    # Show sample van eerste frame
    print("\n🎯 SAMPLE OUTPUT (Frame 1, first 3 joints):")
    if angles_data:
        first_frame = angles_data[0]
        print(f"Frame: {first_frame['frame']}")
        
        for i, (bone_name, angles) in enumerate(list(first_frame['angles'].items())[:3]):
            print(f"  {bone_name}:")
            print(f"    X: {angles['x_deg']:.2f}°")
            print(f"    Y: {angles['y_deg']:.2f}°")
            print(f"    Z: {angles['z_deg']:.2f}°")
    
    print("\n📁 Export directory:", export_dir)
    print("✅ DONE! Check your files in the blender_ros_exports folder.")