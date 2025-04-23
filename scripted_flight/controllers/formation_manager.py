import numpy as np
from scripted_flight.controllers.vicon_flow_utils import get_position

def surround_leader(controller, pos, filtered_alt, now):
    leader_marker = controller.params.get("leader_marker", "E1")
    leader_pos, occluded = get_position(controller.vicon, leader_marker)
    if occluded or leader_pos is None:
        return controller.desired
    idx = controller.params.get("drone_index", 0)
    num = controller.params.get("num_drones", 1)
    radius = controller.params.get("formation_radius", 0.5)
    angle = (2 * np.pi / num) * idx
    desired = leader_pos.copy()
    desired[0] += radius * np.cos(angle)
    desired[1] += radius * np.sin(angle)
    desired[2] = controller.desired[2]
    return desired

def v_formation(controller, pos, filtered_alt, now):
    leader_marker = controller.params.get("leader_marker", "E1")
    leader_pos, occluded = get_position(controller.vicon, leader_marker)
    if occluded or leader_pos is None:
        return controller.desired
    idx = controller.params.get("drone_index", 0)
    separation = controller.params.get("v_separation", 0.5)
    wing = -1 if idx % 2 == 0 else 1
    pair = idx // 2 + 1
    desired = leader_pos.copy()
    desired[0] += wing * pair * separation
    desired[1] += pair * separation
    desired[2] = controller.desired[2]
    return desired
