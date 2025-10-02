#!/usr/bin/env python3
# filepath: e:\CARLA_Latest\PythonAPI\examples\simple_drive.py

"""
Simple CARLA script to spawn a Tesla and drive it manually
Controls: WASD to drive, ESC to quit
"""

import carla
import pygame
import weakref
import numpy as np
from carla import ColorConverter as cc

class CameraManager(object):
    def __init__(self, parent_actor, hud_dim):
        self.sensor = None
        self.surface = None
        self._parent = parent_actor
        
        # Camera positions (same as manual_control.py)
        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        bound_z = 0.5 + self._parent.bounding_box.extent.z
        
        Attachment = carla.AttachmentType
        self._camera_transforms = [
            # Third person view
            (carla.Transform(carla.Location(x=-2.0*bound_x, y=0.0, z=2.0*bound_z), carla.Rotation(pitch=8.0)), Attachment.SpringArmGhost),
            # Driver's view  
            (carla.Transform(carla.Location(x=0.8*bound_x, y=0.0, z=1.3*bound_z)), Attachment.Rigid),
        ]
        self.transform_index = 0  # Start with third person view
        
        # Setup RGB camera
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.camera.rgb')
        bp.set_attribute('image_size_x', str(hud_dim[0]))
        bp.set_attribute('image_size_y', str(hud_dim[1]))
        bp.set_attribute('fov', '110')
        
        self.sensor = world.spawn_actor(
            bp,
            self._camera_transforms[self.transform_index][0],
            attach_to=self._parent,
            attachment_type=self._camera_transforms[self.transform_index][1])
        
        # Setup callback
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
    
    def toggle_camera(self):
        """Switch between third person and driver view"""
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.sensor.destroy()
        
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.camera.rgb')
        bp.set_attribute('image_size_x', '1200')
        bp.set_attribute('image_size_y', '800')
        bp.set_attribute('fov', '110')
        
        self.sensor = world.spawn_actor(
            bp,
            self._camera_transforms[self.transform_index][0],
            attach_to=self._parent,
            attachment_type=self._camera_transforms[self.transform_index][1])
        
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
    
    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))
    
    def destroy(self):
        if self.sensor is not None:
            self.sensor.destroy()
    
    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        
        # Convert CARLA image to pygame surface
        image.convert(cc.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]  # Remove alpha channel
        array = array[:, :, ::-1]  # BGR to RGB
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

class KeyboardControl(object):
    def __init__(self, world):
        self._control = carla.VehicleControl()
        self._steer_cache = 0.0
        world.player.set_autopilot(False)
    
    def parse_events(self, world, clock):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return True
                elif event.key == pygame.K_TAB:
                    world.camera_manager.toggle_camera()
        
        # Get pressed keys and parse vehicle controls
        keys = pygame.key.get_pressed()
        self._parse_vehicle_keys(keys, clock.get_time())
        world.player.apply_control(self._control)
        return False
    
    def _parse_vehicle_keys(self, keys, milliseconds):
        # Throttle control
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._control.throttle = min(self._control.throttle + 0.1, 1.0)
        else:
            self._control.throttle = 0.0
        
        # Brake control  
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._control.brake = min(self._control.brake + 0.2, 1.0)
        else:
            self._control.brake = 0.0
        
        # Steering control (smooth like manual_control.py)
        steer_increment = 5e-4 * milliseconds
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self._steer_cache > 0:
                self._steer_cache = 0
            else:
                self._steer_cache -= steer_increment
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self._steer_cache < 0:
                self._steer_cache = 0
            else:
                self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        self._control.steer = round(self._steer_cache, 1)
        self._control.hand_brake = keys[pygame.K_SPACE]
        
        # Reverse gear
        if keys[pygame.K_q]:
            self._control.gear = 1 if self._control.reverse else -1
        self._control.reverse = self._control.gear < 0

class World(object):
    def __init__(self, carla_world):
        self.world = carla_world
        self.player = None
        self.camera_manager = None
        self.restart()
    
    def restart(self):
        # Get Tesla Model 3 blueprint
        blueprint_library = self.world.get_blueprint_library()
        bp = blueprint_library.filter('vehicle.tesla.model3')[0]
        bp.set_attribute('role_name', 'hero')
        
        # Spawn at a random location
        spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = spawn_points[0] if spawn_points else carla.Transform()
        
        if self.player is not None:
            self.destroy()
        
        self.player = self.world.try_spawn_actor(bp, spawn_point)
        
        if self.player is None:
            raise RuntimeError('Could not spawn vehicle')
        
        # Setup camera manager
        self.camera_manager = CameraManager(self.player, (800, 600))
        print(f"Spawned Tesla Model 3 at {spawn_point.location}")
        print("Controls: WASD=drive, TAB=switch camera, SPACE=handbrake, Q=reverse, ESC=quit")
    
    def render(self, display):
        self.camera_manager.render(display)
    
    def destroy(self):
        if self.camera_manager is not None:
            self.camera_manager.destroy()
        if self.player is not None:
            self.player.destroy()

def main():
    pygame.init()
    pygame.font.init()
    
    try:
        # Connect to CARLA
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        
        # Setup display
        display = pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Tesla Model 3 - CARLA")
        
        # Create world and controller
        world = World(client.get_world())
        controller = KeyboardControl(world)
        
        clock = pygame.time.Clock()
        
        while True:
            clock.tick_busy_loop(60)
            
            # Handle input
            if controller.parse_events(world, clock):
                break
            
            # Render
            world.render(display)
            pygame.display.flip()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'world' in locals():
            world.destroy()
        pygame.quit()

if __name__ == '__main__':
    main()