import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import logging
import random
import time
import numpy as np
import cv2

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

IM_WIDTH, IM_HEIGHT = 1920, 1080
IM_FPS = 10

def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("sensor", i3)
    cv2.waitKey(1)
    return i3/255.0

def main():
    actor_list = []

    try:
        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(2)

        world = client.get_world()

        bp_lib = world.get_blueprint_library()
        logging.info('get all blueprints from the library')
        logging.debug(f'{bp_lib}')

        spawn_points = world.get_map().get_spawn_points()
        logging.info('get all spawn points for the map')
        logging.debug(f'{spawn_points}')

        bp = bp_lib.filter('model3')[0]
        sel_point = random.choice(spawn_points)
        vehicle = world.spawn_actor(bp, sel_point)
        logging.info('spawn vehicle')
        logging.debug(f'spawn vehicle {bp} to spawn point {sel_point}')

        bp_sensor = bp_lib.find('sensor.camera.rgb')
        bp_sensor.set_attribute('image_size_x', f'{IM_WIDTH}')
        bp_sensor.set_attribute('image_size_y', f'{IM_HEIGHT}')
        bp_sensor.set_attribute('fov', '110')
        bp_sensor.set_attribute('sensor_tick', f'{1/IM_FPS}')
        attach_point = carla.Transform(carla.Location(x=2.5, z=0.7))
        sensor = world.spawn_actor(bp_sensor, attach_point, attach_to=vehicle)
        actor_list.append(sensor)
        sensor.listen(lambda scene: process_img(scene))
        logging.info('spawn sensor and attach to vehicle')
        logging.debug(f'sensor {IM_HEIGHT}x{IM_WIDTH} FOV 110, at {IM_FPS} fps; attached to vehicle {vehicle}')

        vehicle.apply_control(carla.VehicleControl(throttle=1., steer=0))
        actor_list.append(vehicle)
        logging.info('add control to vehicle and add vehicle to actor list')

        time.sleep(10000)

    finally:
        logging.info('destroy all actors that have been spawned')
        for actor in actor_list:
            actor.destroy()

if __name__ == '__main__':
    main()