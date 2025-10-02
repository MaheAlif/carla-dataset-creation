import carla
import random
import json
import os
import cv2
import numpy as np
import pygame
import wave
import time

# --- Configuration ---
NUM_NPC_VEHICLES = 50
NUM_NPC_PEDESTRIANS = 30
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
OUTPUT_FOLDER = 'driving_session'

class CarlaRecorder:
    def __init__(self):
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.blueprint_library = self.world.get_blueprint_library()
        self.actor_list = []
        self.player = None
        
        # Data storage
        self.bgr_frames = [] # --- MODIFIED: Store frames in BGR format for OpenCV
        self.player_actions = []
        self.recording = False  # Add recording state
        self.frames_captured = 0  # Counter for debugging
        self.recording_count = 0  # Sequential naming counter
        self.recording_start_time = None  # Track when recording starts
        self._load_existing_recordings()  # Check for existing recordings

        # Pygame setup
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('CARLA Manual Recording')
        self.clock = pygame.time.Clock()
        
        # --- NEW: Camera control attributes ---
        self.camera_view_mode = '1st_person'
        self.transform_1st_person = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.transform_3rd_person = carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15))

    def _spawn_player(self):
        print("Spawning player vehicle...")
        vehicle_bp = self.blueprint_library.find('vehicle.tesla.model3')
        spawn_point = random.choice(self.world.get_map().get_spawn_points())
        self.player = self.world.spawn_actor(vehicle_bp, spawn_point)
        self.actor_list.append(self.player.id)  # Store ID for cleanup
        print(f"Player spawned with ID: {self.player.id}")
        self._setup_sensors()

    def _setup_sensors(self):
        camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
        camera_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT))
        camera_bp.set_attribute('fov', '110')
        # --- MODIFIED: Start with the 1st person transform ---
        self.camera = self.world.spawn_actor(camera_bp, self.transform_1st_person, attach_to=self.player)
        self.actor_list.append(self.camera.id)  # Store ID for cleanup
        self.camera.listen(lambda image: self._camera_callback(image))
        print("Note: Generating silent audio track as a placeholder.")
        
    def _camera_callback(self, image):
        # --- FIXED: Only process when needed ---
        # Convert CARLA's BGRA raw data to a BGR numpy array
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4)) # BGRA
        bgr_frame = array[:, :, :3] # Slice to BGR
        
        # ONLY store frames when actively recording (this was the bug!)
        if self.recording:
            self.bgr_frames.append(bgr_frame.copy())  # Make a copy to avoid reference issues
            self.frames_captured += 1
            if self.frames_captured % 20 == 0:  # Print every second (20 FPS)
                print(f"📹 Frames captured: {self.frames_captured} ({self.frames_captured/20.0:.1f}s)")
        
        # Always display (for visual feedback) - but don't store
        rgb_frame = bgr_frame[:, :, ::-1] # BGR to RGB
        surface = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
        self.display.blit(surface, (0, 0))

    def _spawn_npcs(self):
        print(f"Spawning {NUM_NPC_VEHICLES} vehicles and {NUM_NPC_PEDESTRIANS} pedestrians...")
        
        # Get traffic manager with normal settings (based on generate_traffic.py)
        tm_port = 8000
        tm = self.client.get_trafficmanager(tm_port)
        tm.set_global_distance_to_leading_vehicle(2.5)  # Normal following distance
        tm.set_synchronous_mode(True)
        
        # Spawn Vehicles (using batch approach from generate_traffic.py)
        vehicle_bps = self.blueprint_library.filter('vehicle.*')
        spawn_points = self.world.get_map().get_spawn_points()
        random.shuffle(spawn_points)
        
        # Spawn vehicles one by one (more reliable than batch)
        spawned_vehicles = 0
        for n, transform in enumerate(spawn_points):
            if n >= NUM_NPC_VEHICLES:
                break
            try:
                bp = random.choice(vehicle_bps)
                if bp.has_attribute('color'):
                    color = random.choice(bp.get_attribute('color').recommended_values)
                    bp.set_attribute('color', color)
                if bp.has_attribute('driver_id'):
                    driver_id = random.choice(bp.get_attribute('driver_id').recommended_values)
                    bp.set_attribute('driver_id', driver_id)
                
                # Spawn vehicle
                npc = self.world.try_spawn_actor(bp, transform)
                if npc:
                    self.actor_list.append(npc.id)  # Store actor ID for cleanup
                    npc.set_autopilot(True, tm_port)
                    spawned_vehicles += 1
            except Exception as e:
                print(f"⚠️ Vehicle spawn failed: {e}")
                continue
        
        print(f"✅ Spawned {spawned_vehicles} vehicles with normal autopilot")

        # Spawn Pedestrians (simplified approach)
        walker_bps = self.blueprint_library.filter('walker.pedestrian.*')
        spawned_walkers = 0
        
        # Spawn pedestrians
        walker_batch = []
        walker_spawn_points = []
        for i in range(NUM_NPC_PEDESTRIANS):
            spawn_point = carla.Transform()
            loc = self.world.get_random_location_from_navigation()
            if loc is not None:
                spawn_point.location = loc
                walker_spawn_points.append(spawn_point)
                bp = random.choice(walker_bps)
                if bp.has_attribute('is_invincible'):
                    bp.set_attribute('is_invincible', 'false')
                walker_batch.append(carla.command.SpawnActor(bp, spawn_point))
        
        walker_ids = []
        for response in self.client.apply_batch_sync(walker_batch, True):
            if response.error:
                continue
            else:
                walker_ids.append(response.actor_id)
                self.actor_list.append(response.actor_id)
                spawned_walkers += 1
        
        # Spawn walker controllers
        controller_batch = []
        walker_controller_bp = self.blueprint_library.find('controller.ai.walker')
        for walker_id in walker_ids:
            controller_batch.append(carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker_id))
        
        for response in self.client.apply_batch_sync(controller_batch, True):
            if not response.error:
                self.actor_list.append(response.actor_id)
        
        # Start walker controllers
        all_actors = self.world.get_actors(self.actor_list)
        for actor in all_actors:
            if 'controller.ai.walker' in actor.type_id:
                actor.start()
                actor.go_to_location(self.world.get_random_location_from_navigation())
                actor.set_max_speed(random.uniform(1.0, 2.0))  # Normal walking speed
                
        print(f"✅ Spawned {spawned_walkers} pedestrians with normal behavior")
        print("🚗 Normal traffic spawned - vehicles should be moving!")

    def _load_existing_recordings(self):
        """Check for existing recordings and set the counter appropriately"""
        if not os.path.exists(OUTPUT_FOLDER):
            return
        
        existing_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith('recording_drive-') and f.endswith('.mp4')]
        if existing_files:
            # Extract numbers from filenames and find the highest
            numbers = []
            for filename in existing_files:
                try:
                    num = int(filename.split('recording_drive-')[1].split('.mp4')[0])
                    numbers.append(num)
                except:
                    continue
            
            if numbers:
                self.recording_count = max(numbers)
                print(f"📁 Found {len(existing_files)} existing recordings. Next will be #{self.recording_count + 1}")
        
    def _parse_input(self, clock):
        # (This function remains mostly unchanged, but we add camera toggle logic)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Signal to exit loop
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False # Signal to exit loop
                # --- NEW: Recording toggle logic ---
                if event.key == pygame.K_r:
                    try:
                        if not self.recording:
                            # Start recording
                            self.recording_count += 1
                            self.recording = True
                            self.recording_start_time = time.time()  # Record start time
                            print(f"🔴 RECORDING STARTED - Session {self.recording_count}")
                            print(f"⏰ Start time: {time.strftime('%H:%M:%S', time.localtime(self.recording_start_time))}")
                            # CRITICAL: Clear frame storage before starting
                            self.bgr_frames.clear()  # Use clear() method
                            self.player_actions.clear()  # Use clear() method
                            self.frames_captured = 0
                            print(f"📹 Frame buffer cleared - ready to record fresh frames")
                        else:
                            # Stop recording and save immediately
                            self.recording = False
                            recording_end_time = time.time()
                            duration = recording_end_time - self.recording_start_time
                            print(f"⏹️ RECORDING STOPPED - Session {self.recording_count}")
                            print(f"⏰ Actual recording duration: {duration:.2f} seconds")
                            print(f"📹 Total frames captured: {len(self.bgr_frames)}")
                            print(f"🎬 Expected video duration: {len(self.bgr_frames)/20.0:.2f} seconds")
                            self._save_current_session()
                    except Exception as e:
                        print(f"❌ Error with recording: {e}")
                        self.recording = False
                # --- NEW: Camera toggle logic ---
                if event.key == pygame.K_c:
                    if self.camera_view_mode == '1st_person':
                        self.camera.set_transform(self.transform_3rd_person)
                        self.camera_view_mode = '3rd_person'
                        print("Camera view: 3rd Person")
                    else:
                        self.camera.set_transform(self.transform_1st_person)
                        self.camera_view_mode = '1st_person'
                        print("Camera view: 1st Person")
        
        keys = pygame.key.get_pressed()
        control = carla.VehicleControl()
        
        # Forward/Backward controls
        if keys[pygame.K_w]:
            control.throttle = 1.0
        if keys[pygame.K_s]:
            control.brake = 1.0
        
        # Reverse control
        if keys[pygame.K_x]:
            control.reverse = True
            control.throttle = 0.8  # Apply some throttle in reverse
        else:
            control.reverse = False
            
        # Steering controls
        if keys[pygame.K_a]:
            control.steer = -0.5
        if keys[pygame.K_d]:
            control.steer = 0.5
            
        # Handbrake
        if keys[pygame.K_SPACE]:
            control.hand_brake = True
        
        self.player.apply_control(control)
        
        # Only record actions when recording is active
        if self.recording and self.recording_start_time is not None:
            try:
                current_time = time.time()
                timestamp = current_time - self.recording_start_time  # Time since recording started
                
                action_data = {
                    'timestamp': round(timestamp, 3),  # Time in seconds since recording started
                    'absolute_time': time.strftime('%H:%M:%S', time.localtime(current_time)),  # Human readable time (fixed format)
                    'steer': control.steer, 
                    'throttle': control.throttle, 
                    'brake': control.brake,
                    'reverse': control.reverse,
                    'hand_brake': control.hand_brake
                }
                
                # Only log actions that have actual input (to reduce noise)
                if (control.steer != 0.0 or control.throttle != 0.0 or control.brake != 0.0 or 
                    control.reverse or control.hand_brake):
                    print(f"⚡ Action @ {timestamp:.2f}s: ", end="")
                    if control.throttle > 0: print("ACCELERATE ", end="")
                    if control.brake > 0: print("BRAKE ", end="")
                    if control.steer < 0: print("LEFT ", end="")
                    if control.steer > 0: print("RIGHT ", end="")
                    if control.reverse: print("REVERSE ", end="")
                    if control.hand_brake: print("HANDBRAKE ", end="")
                    print()  # New line
                
                self.player_actions.append(action_data)
            except Exception as e:
                print(f"❌ Error recording action: {e}")
                # Continue without crashing
        
        return True # Signal to continue loop

    def _final_summary(self):
        """Print summary of all recordings when exiting"""
        if self.recording_count > 0:
            print(f"\n📊 SESSION SUMMARY:")
            print(f"   Total recordings: {self.recording_count}")
            print(f"   Saved to folder: {OUTPUT_FOLDER}/")
            print(f"   Files created:")
            for i in range(1, self.recording_count + 1):
                print(f"     - recording_drive-{i}.mp4")
                print(f"     - actions_drive-{i}.json") 
                print(f"     - audio_drive-{i}.wav")
        else:
            print("⚠️ No recordings were made.")

    def _save_current_session(self):
        """Save the current recording session with sequential naming"""
        if not self.bgr_frames:
            print("⚠️ No frames in current session! Recording was not active.")
            return
            
        actual_duration = len(self.bgr_frames) / 20.0
        print(f"\n💾 Saving Session {self.recording_count}...")
        print(f"📊 Frame count: {len(self.bgr_frames)}")
        print(f"🎬 Video duration: {actual_duration:.2f} seconds")
        print(f"🎮 Action count: {len(self.player_actions)}")
        
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Sequential naming
        video_filename = f'recording_drive-{self.recording_count}.mp4'
        actions_filename = f'actions_drive-{self.recording_count}.json'
        audio_filename = f'audio_drive-{self.recording_count}.wav'
        
        # Save video
        video_path = os.path.join(OUTPUT_FOLDER, video_filename)
        print(f"📹 Saving video: {video_filename}")
        
        height, width, _ = self.bgr_frames[0].shape
        frame_rate = 20.0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(video_path, fourcc, frame_rate, (width, height))
        
        frames_written = 0
        for frame in self.bgr_frames:
            out.write(frame)
            frames_written += 1
        out.release()
        
        print(f"✅ Video saved: {frames_written} frames @ {frame_rate}fps = {frames_written/frame_rate:.2f}s")

        # Save actions with metadata
        actions_path = os.path.join(OUTPUT_FOLDER, actions_filename)
        print(f"🎮 Saving actions: {actions_filename}")
        
        # Create comprehensive action data with metadata
        action_metadata = {
            'session_id': self.recording_count,
            'total_duration': len(self.bgr_frames) / 20.0,  # Duration in seconds
            'frame_rate': 20,
            'total_frames': len(self.bgr_frames),
            'total_actions': len(self.player_actions),
            'recording_start_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.recording_start_time)) if self.recording_start_time else None,
            'actions': self.player_actions
        }
        
        with open(actions_path, 'w') as f:
            json.dump(action_metadata, f, indent=4)
            
        # Save placeholder audio
        audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
        print(f"🔊 Saving audio: {audio_filename}")
        sample_rate = 16000
        duration = len(self.bgr_frames) / 20.0
        num_samples = int(duration * sample_rate)
        silent_data = np.zeros(num_samples, dtype=np.int16)

        with wave.open(audio_path, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
            wf.writeframes(silent_data.tobytes())

        print(f"✅ Session {self.recording_count} saved successfully!")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Total actions recorded: {len(self.player_actions)}")
        print(f"   Files: {video_filename}, {actions_filename}, {audio_filename}\n")

    def game_loop(self):
        try:
            self._spawn_player()
            self._spawn_npcs()
            
            print("\nReady to record! Controls:")
            print("- W: Throttle")
            print("- S: Brake") 
            print("- A/D: Steer left/right")
            print("- X: Reverse")
            print("- SPACE: Handbrake")
            print("- R: Start/Stop recording")
            print("- C: Toggle camera view")
            print("- ESC: Quit")
            print("\n⚠️ Press 'R' to start recording when ready!")
            print("💡 Each recording session will be saved separately!")
            
            running = True
            while running:
                self.clock.tick_busy_loop(20)
                running = self._parse_input(self.clock)
                pygame.display.flip()
        finally:
            # If there's an active recording when quitting, save it
            if self.recording and self.bgr_frames:
                print("💾 Saving final recording session...")
                self._save_current_session()
            self._final_summary()
            self._cleanup()

    def _cleanup(self):
        print("Destroying actors...")
        if self.actor_list:
            # All actors in the list are now IDs
            destroy_commands = []
            for actor_id in self.actor_list:
                destroy_commands.append(carla.command.DestroyActor(actor_id))
            
            if destroy_commands:
                self.client.apply_batch(destroy_commands)
        
        pygame.quit()
        print("Cleanup complete.")

if __name__ == '__main__':
    recorder = None
    try:
        recorder = CarlaRecorder()
        recorder.game_loop()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if recorder and recorder.actor_list:
            recorder._cleanup()
        else:
            pygame.quit()