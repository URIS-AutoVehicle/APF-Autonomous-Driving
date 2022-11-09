#!/usr/bin/env python

# Copyright (c) 2021 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Example script to generate traffic in the simulation"""

import glob
import os
import sys
import time
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from carla import VehicleLightState as vls

import argparse
import logging
import numpy
from numpy import random
random.seed(4)
def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []
def main():

    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=30,
        type=int,
        help='Number of vehicles (default: 30)')
    argparser.add_argument(
        '-w', '--number-of-walkers',
        metavar='W',
        default=0,
        type=int,
        help='Number of walkers (default: 10)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filterv',
        metavar='PATTERN',
        default='vehicle.*',
        help='Filter vehicle model (default: "vehicle.*")')
    argparser.add_argument(
        '--generationv',
        metavar='G',
        default='All',
        help='restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='Filter pedestrian type (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '--generationw',
        metavar='G',
        default='2',
        help='restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='Port to communicate with TM (default: 8000)')
    argparser.add_argument(
        '--asynch',
        action='store_true',
        help='Activate asynchronous mode execution')
    argparser.add_argument(
        '--hybrid',
        action='store_true',
        help='Activate hybrid mode for Traffic Manager')
    argparser.add_argument(
        '-s', '--seed',
        metavar='S',
        type=int,
        help='Set random device seed and deterministic mode for Traffic Manager')
    argparser.add_argument(
        '--seedw',
        metavar='S',
        default=0,
        type=int,
        help='Set the seed for pedestrians module')
    argparser.add_argument(
        '--car-lights-on',
        action='store_true',
        default=False,
        help='Enable automatic car light management')
    argparser.add_argument(
        '--hero',
        action='store_true',
        default=False,
        help='Set one of the vehicles as hero')
    argparser.add_argument(
        '--respawn',
        action='store_true',
        default=False,
        help='Automatically respawn dormant vehicles (only in large maps)')
    argparser.add_argument(
        '--no-rendering',
        action='store_true',
        default=False,
        help='Activate no rendering mode')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    vehicles_list = []
    walkers_list = []
    all_id = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(20.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    try:
        world = client.get_world()
        traffic_manager = client.get_trafficmanager(args.tm_port)
        # traffic_manager.global_percentage_speed_difference(-200)
        traffic_manager.set_hybrid_physics_mode(True)
        # traffic_manager.set_hybrid_physics_radius(70)
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        if args.respawn:
            traffic_manager.set_respawn_dormant_vehicles(True)
        if args.hybrid:
            traffic_manager.set_hybrid_physics_mode(True)
            traffic_manager.set_hybrid_physics_radius(70.0)

        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)

        settings = world.get_settings()
        # if not args.asynch:
        #     traffic_manager.set_synchronous_mode(False)
        #     if not settings.synchronous_mode:
        #         synchronous_master = True
        #         settings.synchronous_mode = True
        #         settings.fixed_delta_seconds = 0.05
        #     else:
        #         synchronous_master = False
        # else:
        #     print("You are currently in asynchronous mode. If this is a traffic simulation, \
        #     you could experience some issues. If it's not working correctly, switch to synchronous \
        #     mode by using traffic_manager.set_synchronous_mode(True)")

        if args.no_rendering:
            settings.no_rendering_mode = True
        world.apply_settings(settings)

        blueprints = get_actor_blueprints(world, args.filterv, args.generationv)
        blueprintsWalkers = get_actor_blueprints(world, args.filterw, args.generationw)

        if args.safe:
            blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
            blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 2]
            blueprints = [x for x in blueprints if not x.id.endswith('microlino')]
            blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
            blueprints = [x for x in blueprints if not x.id.endswith('cybertruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('t2')]
            blueprints = [x for x in blueprints if not x.id.endswith('sprinter')]
            blueprints = [x for x in blueprints if not x.id.endswith('firetruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('ambulance')]

        blueprints = sorted(blueprints, key=lambda bp: bp.id)

        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            pass#random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        # --------------
        # Spawn vehicles
        # --------------
        batch = []

        hero = args.hero
        for n, transform in enumerate(spawn_points):
            if n >= args.number_of_vehicles:
                break
            blueprint = blueprints[0]
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            if hero:
                blueprint.set_attribute('role_name', 'hero')
                hero = False
            else:
                blueprint.set_attribute('role_name', 'autopilot')

            #spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
             .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Set automatic vehicle lights update if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)






        print('spawned %d vehicles and %d walkers, press Ctrl+C to exit.' % (len(vehicles_list), len(walkers_list)))


        traffic_manager.global_percentage_speed_difference(-20)
        R=50
        print(vehicles_list)


        for actor in world.get_actors():
            if actor.attributes.get('role_name') == 'hero':
                player = actor
                break
        # carla.Rotation.__init__(player,pitch=0.0, yaw=0.0, roll=0.0)
        # print(player.get_transform().rotation)

        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()


            # actor_list = world.get_actors(vehicles_list)
            # for a in range(len(vehicles_list)):
            #     actor = actor_list.find(vehicles_list[a])
            #     #print('id: ', vehicles_list[a], actor.get_location().x, actor.get_velocity().x)
            #     print()
            #
            #     with open('C:/carla/WindowsNoEditor/PythonAPI/examples/src/data/location.txt', 'a+') as f:
            #         print ('id: ', vehicles_list[a], actor.get_location(), actor.get_velocity(),file=f)
            matrix = player.get_transform().get_matrix()
            actor_list = world.get_actors(vehicles_list)
            # ego = actor_list.find(vehicles_list[0])
            player_info = player.get_transform()
            inverse_matrix = numpy.linalg.inv(matrix)
            print('player', player_info.location, player.get_velocity())
            player_location = [[player_info.location.x], [player_info.location.y], [player_info.location.z],[1]]
            player_velocity = [[player.get_velocity().x], [player.get_velocity().y], [player.get_velocity().z], [0]]
            player_final_location = numpy.dot(inverse_matrix,player_location)
            player_final_velocity = numpy.dot(inverse_matrix,player_velocity)

            print('player', 'location:', player_final_location[0][0], player_final_location[1][0], player_final_location[2][0],  'velocity:', player_final_velocity[0][0], player_final_velocity[1][0], player_final_velocity[2][0])

            world.debug.draw_point(player_info.location, size=0.1, color=carla.Color(r=255, g=0, b=0), life_time=0)
            # world.debug.draw_string(player_info.location, '^', draw_shadow=False, color=carla.Color(r=255, g=0, b=0), life_time=0)
            vehicles = []
            # print(manual_control_joystick_copy.game_loop().location)
            for a in range(len(vehicles_list)):
                actor = actor_list.find(vehicles_list[a])
                #print('id: ', vehicles_list[1], ego.get_location(), ego.get_velocity())
                # print('id: ', vehicles_list[a], actor.get_location(), actor.get_velocity())
                # with open('C:/carla/WindowsNoEditor/PythonAPI/examples/src/data/location.txt', 'a+') as f:
                #     print('id: ', vehicles_list[a], actor.get_location(), actor.get_velocity(), file=f)
                if ((player.get_location().x-actor.get_location().x)**2+(player.get_location().y-actor.get_location().y)**2) <= (R**2):

                #     print('id: ', vehicles_list[a], actor.get_location(), actor.get_velocity(), len(vehicles))
                    vehicles.append(vehicles_list[a])
                    actor_location = [[actor.get_location().x], [actor.get_location().y], [actor.get_location().z], [1]]
                    actor_velocity =[[actor.get_velocity().x], [actor.get_velocity().y], [actor.get_velocity().z], [1]]
                    actor_final_location = numpy.dot(inverse_matrix, actor_location)
                    actor_final_velocity = numpy.dot(inverse_matrix, actor_velocity)
                    print('id: ', vehicles_list[a], 'location:', actor_final_location[0][0], actor_final_location[1][0], actor_final_location[2][0], 'velocity:', actor_final_velocity[0][0], actor_final_velocity[1][0], actor_final_velocity[2][0])

            print(len(vehicles))










    finally:

        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
        print('\ndestroying %d vehicles' % len(vehicles_list))



        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        # stop walker controllers (list is [controller, actor, controller, actor ...])

        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        time.sleep(0.5)

if __name__ == '__main__':

    try:
        main()


    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')




