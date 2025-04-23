#!/usr/bin/env python3
import sys, time, json, threading, argparse, importlib
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from scripted_flight.controllers.vicon_flow_utils import connect_vicon
from scripted_flight.controllers.flow_deck import start_flow_logging
from scripted_flight.controllers.flight_controller import FlightController

def parse_args():
    parser = argparse.ArgumentParser(
        description="Elegant Vicon & Flow Deck Drone Controller with Demo and Formation Modes"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--uris", nargs="+", help="List of drone URIs")
    group.add_argument("--config", help="Path to JSON file with drone configurations")
    parser.add_argument("--vicon", default="192.168.10.1", help="Vicon server IP address")
    parser.add_argument("--marker", default="E2", help="Default Vicon marker for each drone")
    parser.add_argument("--leader", default="E1", help="Marker for the leader drone (e.g. 'E1')")
    parser.add_argument("--takeoff_height", type=float, default=1.0, help="Takeoff altitude (meters)")
    parser.add_argument("--hover_duration", type=float, default=10, help="Hover duration (seconds)")
    parser.add_argument("--control_rate", type=int, default=100, help="Control loop rate (Hz)")
    parser.add_argument("--demo", default="default", choices=["default", "hover", "circle", "surround", "v"],
                        help="Demo/Formation mode: 'hover', 'circle', 'surround', 'v', or 'default'")
    parser.add_argument("--demo_duration", type=float, default=20, help="Demo phase duration (seconds)")
    return parser.parse_args()

def load_config(args):
    if args.config:
        with open(args.config, "r") as f:
            return json.load(f)
    return [{"uri": uri, "marker": args.marker} for uri in args.uris]

def load_demo_pattern(demo_mode):
    if demo_mode == "hover":
        return importlib.import_module("scripted_flight.demos.hover_demo").demo
    if demo_mode == "circle":
        return importlib.import_module("scripted_flight.demos.circle_demo").demo
    if demo_mode in ("surround", "v"):
        module = importlib.import_module("scripted_flight.controllers.formation_manager")
        return module.surround_leader if demo_mode == "surround" else module.v_formation
    return None

def run_drone(drone_config, vicon, global_params):
    # Merge drone-specific parameters into a local copy of global parameters.
    local_params = global_params.copy()
    local_params.update(drone_config)  # now contains "drone_index" and "num_drones" if assigned
    cf = Crazyflie(rw_cache="./cache")
    try:
        with SyncCrazyflie(drone_config["uri"], cf=cf):
            deck_ready = threading.Event()
            cf.param.add_update_callback(
                group="deck", name="bcFlow2",
                cb=lambda _, val: deck_ready.set() if int(val) else sys.exit("Flow Deck not detected")
            )
            time.sleep(1)
            if not deck_ready.wait(timeout=5):
                sys.exit("Flow Deck not detected")
            lg, zrange = start_flow_logging(cf)
            local_params["zrange"] = zrange
            controller = FlightController(
                cf,
                vicon,
                drone_config.get("marker", local_params.get("marker", "E2")),
                local_params,
                local_params.get("pattern")
            )
            controller.run()
            lg.stop()
    except KeyboardInterrupt:
        cf.commander.send_stop_setpoint()
    finally:
        cf.commander.send_stop_setpoint()

def main():
    args = parse_args()
    drones = load_config(args)
    # Automatically assign each drone its index and total count
    num_drones = len(drones)
    for i, drone in enumerate(drones):
        drone["drone_index"] = i
        drone["num_drones"] = num_drones

    global_params = {
        "kp_xy": 0.2,
        "kp_z": 1.0,
        "takeoff_height": args.takeoff_height,
        "hover_duration": args.hover_duration,
        "demo_duration": args.demo_duration,
        "land_thresh": 0.1,
        "deadband_xy": 0.005,
        "deadband_z": 0.005,
        "max_vel_xy": 0.25,
        "max_vel_z": 0.6,
        "control_rate": args.control_rate,
        "marker": args.marker,
        "leader_marker": args.leader,
        "zrange": [0.0],
        "obstacle_markers": [],   # No obstacles by default
        "obstacle_threshold": 0.5,
        "warp_distance": 0.3
    }
    demo_pattern = load_demo_pattern(args.demo)
    if demo_pattern:
        global_params["pattern"] = demo_pattern
        global_params["demo_mode"] = args.demo
    else:
        global_params["demo_mode"] = "default"

    cflib.crtp.init_drivers()
    vicon = connect_vicon(args.vicon)
    threads = []
    for drone in drones:
        t = threading.Thread(target=run_drone, args=(drone, vicon, global_params))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print("All drones have completed their flights.")

if __name__ == "__main__":
    main()
