import glob
import carla
import sys
import os

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import time
import numpy
import logging

actor_list = []

def print_all_blueprints(world : carla.World, filter : str = '*') -> None:
    '''
    print all blueprints that are available in carla
    '''
    bp_lib = world.get_blueprint_library().filter(filter)
    logging.info('get all blueprints from the library')
    for bp in bp_lib:
        print(f' - {bp.id:40s} {bp.tags}')


def get_blueprint(world : carla.World, filter : str = '*') -> carla.ActorBlueprint:
    return world.get_blueprint_library().filter(filter)[0]
def get_spawn_points(world : carla.World):
    return world.get_map().get_spawn_points()

def spawn_blueprint(world : carla.World, blueprint : carla.ActorBlueprint, spawn_point : int) -> None:
    global actor_list
    spawn_points = world.get_map().get_spawn_points()
    sel_point = spawn_points[spawn_point]

    new_actor = world.spawn_actor(blueprint, sel_point)
    actor_list.append(new_actor)

def highlight_spawn_points(world : carla.World) -> None:
    spawn_points = get_spawn_points(world)
    for i, spawn_point in enumerate(spawn_points):
        world.debug.draw_string(spawn_point.location, str(i), life_time=10000)

if __name__ == '__main__':
    try:
        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(2)
        world = client.get_world()
        print_all_blueprints(world, filter="*prop*")

        spawn_blueprint(world, get_blueprint(world, "static.prop.streetfountain"), 24)
        time.sleep(100)

    finally:
        logging.info('terminated')
        for a in actor_list:
            a.destroy()