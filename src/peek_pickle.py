import numpy as np
import cupy as cp
import pickle
import open3d as o3d
import scipy.cluster.hierarchy as hcluster
# from sklearn.cluster import AgglomerativeClustering
from manual_control_joystick import SemanticLidarSensor

MODEL3_BBOX = np.array([2.89588976,1.581725,1.24383003])
lim_l = cp.array(-1 * MODEL3_BBOX)
lim_r = cp.array(MODEL3_BBOX)


if __name__ == '__main__':
    vis = o3d.visualization.Visualizer()
    vis.create_window(
        window_name='point cloud segmentation visualization',
        width=1920,
        height=1080,
        left=480,
        top=270)
    vis.get_render_option().background_color = [0.05, 0.05, 0.05]
    vis.get_render_option().point_size = 1
    vis.get_render_option().show_coordinate_frame = True


    data = pickle.load(open('data.pkl', 'rb'))
    road_data = data[np.in1d(data['ObjTag'], np.array([6, 7]))]
    road_pts = cp.array([road_data['x'], -road_data['y'], road_data['z']]).T
    vehicle_data = data[np.in1d(data['ObjTag'], np.array([10]))]

    # convert numpy to cupy
    vehicle_pts_cos = cp.array(vehicle_data['CosAngle'])
    # vehicle_pts_sin = cp.sqrt(1 - vehicle_pts_cos ** 2)
    vehicle_pts = cp.array([vehicle_data['x'], -vehicle_data['y'], vehicle_data['z']]).T
    assert vehicle_pts.shape[0] == vehicle_pts_cos.shape[0], \
        f'pts{vehicle_pts.shape}!=cos{vehicle_pts_cos.shape}'

    cluster_thresh = 0.75
    clusters = cp.array(hcluster.fclusterdata(cp.asnumpy(vehicle_pts), cluster_thresh, criterion="distance")).astype(np.uint8)
    print(f'clusters: {clusters}')

    # filter point cloud within bounding box (own vehicle) and outside (other vehicles)
    bbox_mask = cp.all(cp.logical_and(lim_l <= vehicle_pts, vehicle_pts <= lim_r), axis=1)
    # in_box_pc = vehicle_pc[bbox_mask]
    out_box_pts = vehicle_pts[cp.logical_not(bbox_mask)]
    out_box_pts_cos = vehicle_pts_cos[cp.logical_not(bbox_mask)]

    # compute a repulsive force from other vehicles
    # ignore own vehicle
    distances = cp.sqrt(cp.sum(out_box_pts * out_box_pts, axis=1))

    # calculate a sum force
    threshold = 20
    force = 1e5 * (threshold - distances) / cp.sum(distances*distances*distances) / threshold
    sum_force = float(cp.sum(force*out_box_pts_cos))
    print(f'sum_force: {sum_force}')

    vehicle_labels = cp.logical_not(bbox_mask).astype(cp.uint8) * clusters # np.array(data['ObjTag'])
    vehicle_color = SemanticLidarSensor.VEHICLE_COLORS[vehicle_labels]
    road_color = SemanticLidarSensor.LABEL_COLORS[cp.array(road_data['ObjTag'])]


    point_list = o3d.geometry.PointCloud()
    point_list.points = o3d.utility.Vector3dVector(cp.asnumpy(cp.concatenate((road_pts, vehicle_pts), axis=0)))
    point_list.colors = o3d.utility.Vector3dVector(cp.asnumpy(cp.concatenate((road_color, vehicle_color), axis=0)))
    vis.add_geometry(point_list)
    vis.run()