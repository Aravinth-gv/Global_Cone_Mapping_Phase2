import numpy as np

def transform_to_global(perception, telemetry):
    telemetry_times=telemetry["timestamp"].to_numpy()
    tx=telemetry["x"].to_numpy()
    ty=telemetry["y"].to_numpy()
    tyaw=telemetry["yaw_rad"].to_numpy()

    perception=perception.copy()

    perception["vehicle_x"]=np.interp(perception["timestamp"],telemetry_times,tx)
    perception["vehicle_y"]=np.interp(perception["timestamp"],telemetry_times,ty)
    perception["yaw"]=np.interp(perception["timestamp"],telemetry_times,tyaw)

    perception["vehicle_frame_x"]=-perception["rel_x_sensor"]
    perception["vehicle_frame_y"]=-perception["rel_y_sensor"]

    c=np.cos(perception["yaw"])
    s=np.sin(perception["yaw"])

    perception["global_x"]=(
        perception["vehicle_x"]
        +c*perception["vehicle_frame_x"]
        -s*perception["vehicle_frame_y"]
    )

    perception["global_y"]=(
        perception["vehicle_y"]
        +s*perception["vehicle_frame_x"]
        +c*perception["vehicle_frame_y"]
    )

    return perception