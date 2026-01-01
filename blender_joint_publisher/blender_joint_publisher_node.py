#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import pandas as pd
import numpy as np
import os
from pathlib import Path
import time
import sys
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

class BlenderJointPublisher(Node):
    def __init__(self):
        super().__init__('blender_joint_publisher')
        
        # Parameters
        self.declare_parameter('csv_file', '')
        self.declare_parameter('publish_rate', 2.0)  # Hz
        self.declare_parameter('loop', True)
        self.declare_parameter('frame_column', 'frame')
        self.declare_parameter('joint_prefix', '')
        
        # Get parameters
        csv_file_param = self.get_parameter('csv_file').get_parameter_value().string_value
        self.publish_rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self.loop = self.get_parameter('loop').get_parameter_value().bool_value
        frame_column = self.get_parameter('frame_column').get_parameter_value().string_value
        joint_prefix = self.get_parameter('joint_prefix').get_parameter_value().string_value
        
        # Default CSV path if not specified
        if not csv_file_param:
            home = str(Path.home())
            csv_file_param = os.path.join(home, 'bart', 'Desktop', 'blender_ros_exports', 'robot_demo_organic.csv')
        
        self.csv_path = csv_file_param
        self.frame_column = frame_column
        
        # Joint configuration - matching your CSV columns
        self.joint_config = {
            'joint_1': {'csv_column': 'joint_1', 'is_degree': True},
            'joint_2': {'csv_column': 'joint_2', 'is_degree': True},
            'joint_3': {'csv_column': 'joint_3', 'is_degree': True},
            'joint_4': {'csv_column': 'joint_4', 'is_degree': True},
            'joint_5': {'csv_column': 'joint_5', 'is_degree': True},
            'joint_6': {'csv_column': 'joint_6', 'is_degree': True},
            'joint_7': {'csv_column': 'joint_7', 'is_degree': True},
            'Slider 22': {'csv_column': 'Slider 22', 'is_degree': True},
            'Slider 23': {'csv_column': 'Slider 23', 'is_degree': True}
        }
        
        # Apply prefix if specified
        if joint_prefix:
            self.joint_config = {f"{joint_prefix}{name}": config 
                                for name, config in self.joint_config.items()}
        
        self.joint_names = list(self.joint_config.keys())
        
        # Load CSV data
        self.data = self.load_csv_data()
        if self.data is None or self.data.empty:
            self.get_logger().error(f"Failed to load CSV from {self.csv_path}")
            sys.exit(1)
        
        self.current_frame = 0
        self.total_frames = len(self.data)
        
        # Setup publisher with QoS profile
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.publisher = self.create_publisher(
            JointState, 
            '/joint_states', 
            qos_profile
        )
        
        # Create timer for publishing
        timer_period = 1.0 / self.publish_rate
        self.timer = self.create_timer(timer_period, self.publish_next_frame)
        
        # Statistics
        self.start_time = self.get_clock().now()
        self.frames_published = 0
        
        self.get_logger().info(f"Blender Joint Publisher initialized")
        self.get_logger().info(f"  CSV file: {self.csv_path}")
        self.get_logger().info(f"  Total frames: {self.total_frames}")
        self.get_logger().info(f"  Publish rate: {self.publish_rate} Hz")
        self.get_logger().info(f"  Joint names: {self.joint_names}")
        self.get_logger().info(f"  Loop mode: {self.loop}")
    
    def load_csv_data(self):
        """Load CSV file with error handling and column mapping"""
        try:
            if not os.path.exists(self.csv_path):
                self.get_logger().error(f"CSV file not found: {self.csv_path}")
                
                # Try to find the file with common variations
                home = str(Path.home())
                possible_paths = [
                    self.csv_path,
                    os.path.join(home, 'Desktop', 'blender_ros_exports', 'joint_angles_z_only.csv'),
                    os.path.join(home, 'bart', 'Desktop', 'joint_angles_z_only.csv'),
                    'joint_angles_z_only.csv'
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        self.csv_path = path
                        self.get_logger().info(f"Found CSV at: {path}")
                        break
                else:
                    self.get_logger().error("Could not find CSV file in any known location")
                    return None
            
            # Read CSV
            data = pd.read_csv(self.csv_path)
            
            # Clean column names
            data.columns = data.columns.str.strip()
            
            self.get_logger().info(f"CSV columns: {list(data.columns)}")
            self.get_logger().info(f"First few rows:\n{data.head(3)}")
            
            # Verify required columns exist
            missing_columns = []
            for joint_name, config in self.joint_config.items():
                csv_col = config['csv_column']
                if csv_col not in data.columns:
                    missing_columns.append(csv_col)
            
            if missing_columns:
                self.get_logger().warn(f"Missing columns in CSV: {missing_columns}")
                self.get_logger().info("Available columns will be used, others set to 0")
            
            return data
            
        except Exception as e:
            self.get_logger().error(f"Error loading CSV: {e}")
            return None
    
    def get_joint_values_from_row(self, row):
        """Extract joint values from a DataFrame row"""
        joint_values = []
        
        for joint_name in self.joint_names:
            config = self.joint_config[joint_name]
            csv_col = config['csv_column']
            is_degree = config['is_degree']
            
            if csv_col in row.index:
                try:
                    value = float(row[csv_col])
                    
                    # Convert from degrees to radians if needed
                    if is_degree:
                        value = np.deg2rad(value)
                    
                    joint_values.append(value)
                except (ValueError, TypeError):
                    joint_values.append(0.0)
                    self.get_logger().debug(f"Invalid value for {joint_name}, using 0")
            else:
                # Column not found, use default value
                joint_values.append(0.0)
        
        return joint_values
    
    def publish_next_frame(self):
        """Publish the next frame from the CSV"""
        if self.current_frame >= self.total_frames:
            if self.loop:
                self.get_logger().info("Looping back to frame 0")
                self.current_frame = 0
            else:
                self.get_logger().info("All frames published, stopping timer")
                self.timer.cancel()
                return
        
        row = self.data.iloc[self.current_frame]
        
        # Get frame number
        if self.frame_column in row.index:
            frame_number = int(row[self.frame_column])
        else:
            frame_number = self.current_frame
        
        # Get joint values
        joint_values = self.get_joint_values_from_row(row)
        
        # Create JointState message
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"
        msg.name = self.joint_names
        msg.position = joint_values
        msg.velocity = [0.0] * len(joint_values)
        msg.effort = [0.0] * len(joint_values)
        
        # Publish
        self.publisher.publish(msg)
        
        # Log progress
        self.frames_published += 1
        if self.frames_published % 10 == 0 or self.current_frame == 0:
            elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
            fps = self.frames_published / elapsed if elapsed > 0 else 0
            
            # Show first 3 joint values as sample
            sample_values = joint_values[:9]
            sample_names = self.joint_names[:9]
            sample_str = ', '.join([f'{n}:{v:.3f}' for n, v in zip(sample_names, sample_values)])
            
            self.get_logger().info(
                f"Frame {frame_number} ({self.current_frame+1}/{self.total_frames}) | "
                f"FPS: {fps:.1f} | {sample_str}"
            )
        
        # Move to next frame
        self.current_frame += 1
    
    def destroy_node(self):
        """Cleanup before shutdown"""
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        fps = self.frames_published / elapsed if elapsed > 0 else 0
        
        self.get_logger().info(f"Publisher shutting down")
        self.get_logger().info(f"  Total frames published: {self.frames_published}")
        self.get_logger().info(f"  Average FPS: {fps:.2f}")
        self.get_logger().info(f"  Total time: {elapsed:.2f} seconds")
        
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    
    node = BlenderJointPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt received")
    except Exception as e:
        node.get_logger().error(f"Error in main: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
