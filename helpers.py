import numpy as np


def vertical_levels():
    """
    Gets levels with greater density near surface.
    
    Returns
    -------
    list
        List of altitudes in meters.
    """
    delta_z = 30
    z_previous = 0
    v_levels_keep = [z_previous]
    for _ in range(61):
        if z_previous <= 1000:
            factor = 1.1
        elif (z_previous > 1000) & (z_previous <= 3000):
            factor = 1.05
        else:
            factor = 1.019
        delta_z = int((delta_z * factor))
        z_previous += delta_z
        v_levels_keep.append(z_previous)
    return np.array(v_levels_keep)