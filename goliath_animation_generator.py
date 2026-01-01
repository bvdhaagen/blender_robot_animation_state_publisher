import numpy as np
import pandas as pd
import math

class OrganicKeyframeAnimator:
    def __init__(self, total_frames=400, global_osc_factor=1.0):
        self.total_frames = total_frames
        self.frames = np.arange(total_frames)
        self.global_osc_factor = global_osc_factor  # Global multiplier
        
        # Initialize all joints to zero
        self.data = {
            'frame': self.frames,
            'joint_1': np.zeros(total_frames),
            'joint_2': np.zeros(total_frames),
            'joint_3': np.zeros(total_frames),
            'joint_4': np.zeros(total_frames),
            'joint_5': np.zeros(total_frames),
            'joint_6': np.zeros(total_frames),
            'joint_7': np.zeros(total_frames),
            'Slider 22': np.full(total_frames, -0.022),
            'Slider 23': np.full(total_frames, 0.022)
        }
        
        # Keyframes: {frame_number: {joint: value}}
        self.keyframes = {}
        
        # Individual oscillation factors per joint (multipliers)
        self.osc_factors = {
            'joint_1': 1.0,    # Base rotation - most oscillation
            'joint_2': 0.8,    # Shoulder - less oscillation
            'joint_3': 0.6,    # Elbow - even less (needs to be stable)
            'joint_4': 1.1,    # Wrist 1 - can oscillate
            'joint_5': 1.2,    # Wrist 2 - can oscillate more (looks natural)
            'joint_6': 2,    # Gripper rotation - most oscillation (flair!)
            'joint_7': 0.3,    # Linear rail - minimal oscillation
            'Slider 22': 0.1,  # Gripper - tiny oscillation
            'Slider 23': 0.1   # Gripper - tiny oscillation
        }
        
        # Oscillation parameters for each joint (frequency, amplitude, phase)
        self.osc_params = {
            'joint_1': {'freq': 0.08, 'base_amp': 3.0, 'phase': 0},
            'joint_2': {'freq': 0.12, 'base_amp': 2.0, 'phase': math.pi/4},
            'joint_3': {'freq': 0.10, 'base_amp': 1.5, 'phase': math.pi/2},
            'joint_4': {'freq': 0.15, 'base_amp': 4.0, 'phase': 3*math.pi/4},
            'joint_5': {'freq': 0.20, 'base_amp': 5.0, 'phase': math.pi},
            'joint_6': {'freq': 0.25, 'base_amp': 4.0, 'phase': 5*math.pi/4},
            'joint_7': {'freq': 0.05, 'base_amp': 0.5, 'phase': 0},
            'Slider 22': {'freq': 0.3, 'base_amp': 0.001, 'phase': 0},
            'Slider 23': {'freq': 0.3, 'base_amp': 0.001, 'phase': math.pi},
        }
    
    def set_global_oscillation_factor(self, factor):
        """Set global oscillation multiplier (0.0 = none, 1.0 = normal, 2.0 = double)"""
        self.global_osc_factor = max(0.0, factor)
        print(f"🌍 Global oscillation factor set to: {self.global_osc_factor}")
        return self
    
    def set_joint_oscillation_factor(self, joint_name, factor):
        """Set oscillation factor for specific joint"""
        if joint_name in self.osc_factors:
            self.osc_factors[joint_name] = max(0.0, factor)
            print(f"🔧 Joint '{joint_name}' oscillation factor set to: {factor}")
        else:
            print(f"⚠️  Joint '{joint_name}' not found. Available joints: {list(self.osc_factors.keys())}")
        return self
    
    def set_all_joints_oscillation(self, factor):
        """Set oscillation factor for all joints"""
        for joint in self.osc_factors:
            self.osc_factors[joint] = max(0.0, factor)
        print(f"⚙️  All joints oscillation factor set to: {factor}")
        return self
    
    def set_oscillation_amplitude(self, joint_name, amplitude):
        """Directly set oscillation amplitude for a joint"""
        if joint_name in self.osc_params:
            self.osc_params[joint_name]['base_amp'] = amplitude
            print(f"📏 Joint '{joint_name}' base amplitude set to: {amplitude}")
        return self
    
    def set_oscillation_frequency(self, joint_name, frequency):
        """Set oscillation frequency (speed of oscillation)"""
        if joint_name in self.osc_params:
            self.osc_params[joint_name]['freq'] = frequency
            print(f"📈 Joint '{joint_name}' frequency set to: {frequency}")
        return self
    
    def add_keyframe(self, frame, joints):
        """Add a precise keyframe at specific frame"""
        self.keyframes[frame] = joints.copy()
        print(f"📌 Added keyframe at frame {frame}:")
        for joint, value in joints.items():
            if joint not in ['Slider 22', 'Slider 23']:
                print(f"  {joint}: {value:.1f}")
            else:
                print(f"  {joint}: {value:.4f}")
    
    def get_oscillation(self, joint_name, frame, speed_factor=1.0):
        """Get organic oscillation for a joint at given frame"""
        if joint_name not in self.osc_params:
            return 0
        
        params = self.osc_params[joint_name]
        joint_factor = self.osc_factors.get(joint_name, 1.0)
        
        # Calculate base oscillation
        base_osc = params['base_amp'] * math.sin(frame * params['freq'] + params['phase'])
        
        # Apply all factors
        final_osc = base_osc * joint_factor * self.global_osc_factor * speed_factor
        
        return final_osc
    
    def generate_movement(self):
        """Generate organic movement between keyframes"""
        print("\n" + "="*60)
        print("GENERATING ORGANIC KEYFRAME MOVEMENT")
        print("="*60)
        
        print(f"🌍 Global oscillation factor: {self.global_osc_factor}")
        print("🔧 Per-joint oscillation factors:")
        for joint, factor in self.osc_factors.items():
            if factor > 0:
                print(f"  {joint}: {factor}")
        
        # Sort keyframes by frame number
        sorted_frames = sorted(self.keyframes.keys())
        
        if not sorted_frames:
            print("No keyframes defined! Using default movement.")
            return self._create_default_movement()
        
        # Add start and end keyframes if not present
        if 0 not in self.keyframes:
            self.keyframes[0] = {joint: 0 for joint in ['joint_1', 'joint_2', 'joint_3', 
                                                       'joint_4', 'joint_5', 'joint_6', 'joint_7']}
            self.keyframes[0]['Slider 22'] = -0.022
            self.keyframes[0]['Slider 23'] = 0.022
        
        if self.total_frames-1 not in self.keyframes:
            self.keyframes[self.total_frames-1] = self.keyframes[0].copy()
        
        sorted_frames = sorted(self.keyframes.keys())
        
        print(f"\n📊 Keyframes: {sorted_frames}")
        
        # Process each segment between keyframes
        for i in range(len(sorted_frames) - 1):
            start_frame = sorted_frames[i]
            end_frame = sorted_frames[i + 1]
            segment_frames = range(start_frame, end_frame + 1)
            
            print(f"\n➡️  Segment {i+1}: Frame {start_frame} to {end_frame} "
                  f"({len(segment_frames)} frames)")
            
            for frame in segment_frames:
                t = (frame - start_frame) / (end_frame - start_frame) if start_frame != end_frame else 0
                
                # Cosine easing for smoother interpolation
                ease_t = (1 - math.cos(t * math.pi)) / 2
                
                for joint in ['joint_1', 'joint_2', 'joint_3', 'joint_4', 
                             'joint_5', 'joint_6', 'joint_7', 'Slider 22', 'Slider 23']:
                    
                    # Get start and end values
                    start_val = self.keyframes[start_frame].get(joint, 0)
                    end_val = self.keyframes[end_frame].get(joint, start_val)
                    
                    # Smooth interpolation
                    base_value = start_val + (end_val - start_val) * ease_t
                    
                    # Add organic oscillation
                    oscillation = 0
                    
                    # Check if we're in a precision zone
                    is_precision_zone = False
                    precision_frames = 10
                    
                    for keyframe in sorted_frames:
                        if abs(frame - keyframe) < precision_frames:
                            is_precision_zone = True
                            break
                    
                    if not is_precision_zone and self.osc_factors[joint] > 0:
                        # Calculate movement speed
                        movement_distance = abs(end_val - start_val)
                        segment_length = max(1, end_frame - start_frame)
                        speed = movement_distance / segment_length
                        
                        # Adjust oscillation based on speed
                        # Faster movement = less oscillation, slower = more
                        speed_factor = max(0.1, 1.0 - speed * 0.1)
                        
                        # Get oscillation with speed factor
                        oscillation = self.get_oscillation(joint, frame, speed_factor)
                        
                        # For sliders, only oscillate if they're actually moving
                        if joint in ['Slider 22', 'Slider 23'] and movement_distance < 0.001:
                            oscillation = 0
                    
                    self.data[joint][frame] = base_value + oscillation
        
        # Apply smoothing
        self._apply_smoothing()
        
        return pd.DataFrame(self.data)
    
    def _apply_smoothing(self):
        """Apply smoothing to all joints"""
        print("\n🔄 Applying smoothing...")
        
        def moving_average(data, window_size=5):
            smoothed = np.copy(data)
            for i in range(len(data)):
                start = max(0, i - window_size // 2)
                end = min(len(data), i + window_size // 2 + 1)
                smoothed[i] = np.mean(data[start:end])
            return smoothed
        
        # Smooth based on oscillation factors (more oscillation = more smoothing)
        for joint in ['joint_1', 'joint_2', 'joint_3', 'joint_4', 
                     'joint_5', 'joint_6', 'joint_7']:
            factor = self.osc_factors[joint]
            window_size = max(3, int(factor * 5))  # More oscillation = more smoothing
            self.data[joint] = moving_average(self.data[joint], window_size)
    
    def _create_default_movement(self):
        """Create default movement if no keyframes"""
        print("Creating default movement with keyframes...")
        
        self.add_keyframe(0, {
            'joint_1': 0, 'joint_2': 0, 'joint_3': 20,
            'joint_4': 0, 'joint_5': 0, 'joint_6': 0, 'joint_7': 0,
            'Slider 22': -0.022, 'Slider 23': 0.022
        })
        
        self.add_keyframe(100, {
            'joint_1': 30, 'joint_2': -60, 'joint_3': 30,
            'joint_4': 15, 'joint_5': 45, 'joint_6': -30, 'joint_7': 5,
            'Slider 22': -0.003, 'Slider 23': 0.003
        })
        
        # Your precise pickup
        self.add_keyframe(200, {
            'joint_1': 0, 'joint_2': -84, 'joint_3': 31.2,
            'joint_4': 0, 'joint_5': 55, 'joint_6': -90, 'joint_7': 0,
            'Slider 22': -0.003, 'Slider 23': 0.003
        })
        
        self.add_keyframe(210, {
            'joint_1': 0, 'joint_2': -84, 'joint_3': 31.2,
            'joint_4': 0, 'joint_5': 45, 'joint_6': -90, 'joint_7': 0,
            'Slider 22': -0.022, 'Slider 23': 0.022
        })
        
        self.add_keyframe(399, {
            'joint_1': 0, 'joint_2': 0, 'joint_3': 20,
            'joint_4': 0, 'joint_5': 0, 'joint_6': 0, 'joint_7': 0,
            'Slider 22': -0.022, 'Slider 23': 0.022
        })
        
        return self.generate_movement()

# ----------------- MAIN EXECUTION WITH OSCILLATION CONTROL -----------------
if __name__ == "__main__":
    print("🤖 ORGANIC KEYFRAME ANIMATION SYSTEM WITH OSCILLATION CONTROL")
    print("=" * 70)
    
    # Create animator with default settings
    animator = OrganicKeyframeAnimator(total_frames=400)
    
    # ====== OSCILLATION CONTROL EXAMPLES ======
    print("\n⚙️  Setting oscillation factors (you can adjust these):")
    
    # Example 1: Set global oscillation factor
    animator.set_global_oscillation_factor(1.0)  # 0.0 = no oscillation, 2.0 = double
    
    # Example 2: Adjust specific joints
    animator.set_joint_oscillation_factor('joint_1', 1.5)   # More base rotation oscillation
    animator.set_joint_oscillation_factor('joint_3', 0.3)   # Less elbow oscillation (more stable)
    animator.set_joint_oscillation_factor('joint_6', 2.0)   # More gripper rotation flair!
    animator.set_joint_oscillation_factor('joint_7', 0.2)   # Minimal rail oscillation
    
    # Example 3: Set all joints at once
    # animator.set_all_joints_oscillation(0.5)  # Half oscillation for all
    
    # Example 4: Direct amplitude control
    # animator.set_oscillation_amplitude('joint_1', 5.0)  # Larger swings
    
    # Example 5: Frequency control
    # animator.set_oscillation_frequency('joint_1', 0.15)  # Faster oscillation
    
    # ====== DEFINE KEYFRAMES ======
    print("\n📌 Defining keyframes...")
    
    # Home position
    animator.add_keyframe(0, {
        'joint_1': 0, 'joint_2': 0, 'joint_3': 20,
        'joint_4': 0, 'joint_5': 0, 'joint_6': 0, 'joint_7': 0,
        'Slider 22': -0.022, 'Slider 23': 0.022
    })
    
    # Approach position (frame 180)
    animator.add_keyframe(180, {
        'joint_1': 0, 'joint_2': -75, 'joint_3': 30,
        'joint_4': -5, 'joint_5': 80, 'joint_6': -85, 'joint_7': 0,
        'Slider 22': -0.003, 'Slider 23': 0.003
    })
    
    # PRECISE PICKUP (frame 200) - YOUR SPEC
    animator.add_keyframe(200, {
        'joint_1': 0, 'joint_2': -84, 'joint_3': 31.2,
        'joint_4': 0, 'joint_5': 65, 'joint_6': -90, 'joint_7': 0,
        'Slider 22': -0.003, 'Slider 23': 0.003
    })
    
    # Hold with gripper closed (frame 210)
    animator.add_keyframe(210, {
        'joint_1': 0, 'joint_2': -84, 'joint_3': 31.2,
        'joint_4': 0, 'joint_5': 65, 'joint_6': -90, 'joint_7': 0,
        'Slider 22': -0.022, 'Slider 23': 0.022
    })
    
    # Lift (frame 230)
    animator.add_keyframe(230, {
        'joint_1': 0, 'joint_2': -70, 'joint_3': 35,
        'joint_4': 10, 'joint_5': 70, 'joint_6': -70, 'joint_7': 2,
        'Slider 22': -0.022, 'Slider 23': 0.022
    })
    
    # Transport (frame 300)
    animator.add_keyframe(300, {
        'joint_1': -45, 'joint_2': -50, 'joint_3': 40,
        'joint_4': -20, 'joint_5': 40, 'joint_6': 30, 'joint_7': 6,
        'Slider 22': -0.022, 'Slider 23': 0.022
    })
    
    # Place (frame 350)
    animator.add_keyframe(350, {
        'joint_1': -45, 'joint_2': -80, 'joint_3': 32,
        'joint_4': -15, 'joint_5': 85, 'joint_6': -75, 'joint_7': 6,
        'Slider 22': -0.003, 'Slider 23': 0.003
    })
    
    # Return home (frame 399)
    animator.add_keyframe(399, {
        'joint_1': 0, 'joint_2': 0, 'joint_3': 20,
        'joint_4': 0, 'joint_5': 0, 'joint_6': 0, 'joint_7': 0,
        'Slider 22': -0.022, 'Slider 23': 0.022
    })
    
    # ====== GENERATE MOVEMENT ======
    demo_df = animator.generate_movement()
    
    # ====== VALIDATE ======
    print("\n" + "="*60)
    print("VALIDATION")
    print("="*60)
    
    # Check ranges
    print("\n📊 Joint ranges:")
    joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6', 'joint_7']
    for joint in joints:
        vals = demo_df[joint]
        osc_range = vals.max() - vals.min()
        print(f"{joint}: {vals.min():6.1f} to {vals.max():6.1f} (range: {osc_range:5.1f})")
    
    # Check oscillation amounts
    print("\n🌀 Oscillation amounts (peak-to-peak):")
    for joint in joints:
        # Calculate actual oscillation by comparing to linear interpolation
        # Simple approximation: look at variation in adjacent frames
        diffs = np.abs(np.diff(demo_df[joint]))
        avg_osc = np.mean(diffs)
        print(f"{joint}: avg change/frame = {avg_osc:.3f}")
    
    # ====== SAVE CSV ======
    def save_oscillation_csv(df, filename="oscillation_demo.csv"):
        df[''] = ''
        columns = ['frame', '', 'joint_1', 'joint_2', 'joint_3', 'joint_4', 
                   'joint_5', 'joint_6', 'joint_7', 'Slider 22', 'Slider 23']
        df = df[columns]
        df.to_csv(filename, index=False)
        return filename
    
    filename = save_oscillation_csv(demo_df, "keyframe_demo_precise.csv")
    
    print("\n" + "="*60)
    print("✅ CSV GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📁 File: {filename}")
    print(f"📊 Frames: {len(demo_df)}")
    print(f"⏱️  Duration: {len(demo_df)/24:.1f}s at 24Hz")
    
    print("\n🎛️  Oscillation Controls Used:")
    print(f"   Global factor: {animator.global_osc_factor}")
    print("   Per-joint factors:")
    for joint, factor in animator.osc_factors.items():
        if factor != 1.0:
            print(f"     {joint}: {factor}")
    
    print("\n💡 How to adjust oscillation:")
    print("   1. animator.set_global_oscillation_factor(0.5)  # Half oscillation")
    print("   2. animator.set_joint_oscillation_factor('joint_6', 2.0)  # Double for joint 6")
    print("   3. animator.set_all_joints_oscillation(0.0)  # No oscillation")
    print("   4. animator.set_oscillation_amplitude('joint_1', 10.0)  # Bigger swings")
    print("\n🎯 Ready for RViz testing!")
