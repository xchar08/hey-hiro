import numpy as np

def demo(controller, pos, filtered_alt, now):
    if not hasattr(controller, "circle_initialized"):
        controller.circle_center = controller.desired.copy()
        controller.circle_start = now
        controller.circle_radius = controller.params.get("circle_radius", 5)
        controller.circle_period = controller.params.get("circle_period", 20)
        controller.circle_initialized = True
    t_elapsed = now - controller.circle_start
    theta = (t_elapsed / controller.circle_period) * 2 * np.pi
    desired = controller.circle_center.copy()
    desired[0] += controller.circle_radius * np.cos(theta)
    desired[1] += controller.circle_radius * np.sin(theta)
    return desired
