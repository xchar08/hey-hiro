#!/usr/bin/env python3
import sys
import time
import json
import argparse
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils.power_switch import PowerSwitch
from cflib.utils import uri_helper

def reset_drone(uri):
    cflib.crtp.init_drivers()
    cf = Crazyflie(rw_cache="./cache")
    try:
        with SyncCrazyflie(uri, cf=cf):
            print(f"[{uri}] Sending stop command...")
            cf.commander.send_stop_setpoint()
            time.sleep(2)
    except Exception as e:
        print(f"[{uri}] Error during reset: {e}")
    finally:
        cf.close_link()
        print(f"[{uri}] Power cycling...")
        PowerSwitch(uri).stm_power_cycle()
        print(f"[{uri}] Reset complete.")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Reset one or multiple drones via URI or JSON configuration."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--uri", help="Drone URI to reset (single drone mode)")
    group.add_argument("--config", help="Path to JSON file with drone configurations (reset all)")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.uri:
        # Reset a single drone
        reset_drone(args.uri)
    else:
        # Reset all drones specified in the JSON file
        try:
            with open(args.config, "r") as f:
                drones = json.load(f)
        except Exception as e:
            print(f"Error reading config: {e}")
            sys.exit(1)
        for drone in drones:
            uri = drone.get("uri")
            if uri:
                reset_drone(uri)
            else:
                print("Skipping entry without a 'uri' field.")
    print("Reset process complete.")

if __name__ == "__main__":
    main()
