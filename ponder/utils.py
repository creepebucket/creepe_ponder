import math

from .formats import logger


def euler_to_quaternion(euler_angles):
    # 确保输入是一个包含三个元素的列表 [yaw, pitch, roll]
    if len(euler_angles) != 3:
        logger.critical("在将欧拉角转换为四元数时出现致命错误: 输入的欧拉角必须是一个包含三个元素的列表")

    # 将角度转换为弧度
    yaw, pitch, roll = map(math.radians, euler_angles)
    pitch += math.pi  # 转化为minecraft坐标系

    # 计算各个角的正弦和余弦值
    cy = math.cos(roll * 0.5)
    sy = math.sin(roll * 0.5)
    cp = math.cos(yaw * 0.5)
    sp = math.sin(yaw * 0.5)
    cr = math.cos(pitch * 0.5)
    sr = math.sin(pitch * 0.5)

    # 计算四元数
    q_w = cy * cp * cr + sy * sp * sr
    q_x = sy * cp * cr - cy * sp * sr
    q_y = cy * sp * cr + sy * cp * sr
    q_z = cy * cp * sr - sy * sp * cr

    return q_w, q_x, q_y, q_z
