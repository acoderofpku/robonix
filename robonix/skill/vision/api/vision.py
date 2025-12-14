import cv2
import numpy as np

def px2xy(point, camera_k, camera_d, z=1.0):
    """
    Convert pixel coordinates to camera coordinate system 2D coordinates
    
    Args:
        point: Pixel coordinates [x, y]
        camera_k: Camera intrinsic matrix K
        camera_d: Camera distortion parameters D
        z: Depth value
        
    Returns:
        Camera coordinate system 2D coordinates [x, y]
    """
    MK = np.array(camera_k, dtype=float).reshape(3, 3)
    MD = np.array(camera_d, dtype=float)
    point = np.array(point, dtype=float)
    pts_uv = cv2.undistortPoints(point, MK, MD) * z
    return pts_uv[0][0]

def remove_mask_outliers(data, lower_percentile=10, upper_percentile=90):
    """
    Remove outliers from depth data using percentile method
    
    Args:
        data: List of depth values or numpy array
        lower_percentile: Lower percentile threshold
        upper_percentile: Upper percentile threshold
        
    Returns:
        Filtered depth values. If no valid data remains after filtering,
        returns an empty list.
    """
    arr = np.array(data)
    
    # 检查是否为空或所有值都是非有限数（NaN, Inf）
    if arr.size == 0 or not np.any(np.isfinite(arr)):
        return []
    
    # 过滤掉 NaN 和 Inf
    finite_arr = arr[np.isfinite(arr)]
    
    # 如果过滤后数组为空
    if finite_arr.size == 0:
        return []

    lower = np.percentile(finite_arr, lower_percentile)
    upper = np.percentile(finite_arr, upper_percentile)
    filtered = finite_arr[(finite_arr >= lower) & (finite_arr <= upper)]
    
    # 如果过滤后仍无有效数据
    if filtered.size == 0:
        return []
    
    return filtered.tolist()


def get_mask_center_opencv(mask_points):
    """
    Calculate the center point of a mask using OpenCV moments
    
    Args:
        mask_points: Polygon point set, shape (n, 1, 2)
        
    Returns:
        Center point coordinates (cx, cy)
    """
    M = cv2.moments(mask_points)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return cx, cy 