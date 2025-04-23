import time
import numpy as np
from vicon_dssdk import ViconDataStream

def connect_vicon(server_ip):
    vicon = ViconDataStream.Client()
    vicon.Connect(server_ip)
    if not vicon.IsConnected():
        raise Exception(f"Unable to connect to Vicon server at {server_ip}")
    vicon.EnableSegmentData()
    vicon.SetStreamMode(ViconDataStream.Client.StreamMode.EClientPull)
    vicon.SetAxisMapping(
        ViconDataStream.Client.AxisMapping.EForward,
        ViconDataStream.Client.AxisMapping.ELeft,
        ViconDataStream.Client.AxisMapping.EUp
    )
    return vicon

def get_position(vicon, marker):
    if not vicon.GetFrame():
        return None, True
    pos, occluded = vicon.GetSegmentGlobalTranslation(marker, marker)
    if occluded:
        return None, True
    return np.array(pos) / 1000.0, False
