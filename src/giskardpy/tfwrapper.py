import rospy
from geometry_msgs.msg import PoseStamped
from tf2_geometry_msgs import do_transform_pose
from tf2_py._tf2 import ExtrapolationException
from tf2_ros import Buffer, TransformListener

tfBuffer = None
tf_listener = None

def init(tf_buffer_size=2):
    """
    If you want to specify the buffer size, call this function manually, otherwise don't worry about it.
    :param tf_buffer_size:
    :type tf_buffer_size: int
    """
    global tfBuffer, tf_listener
    tfBuffer = Buffer(rospy.Duration(tf_buffer_size))
    tf_listener = TransformListener(tfBuffer)
    rospy.sleep(0.1)

def transform_pose(target_frame, pose):
    """
    Transforms a pose stamped into a different target frame.
    :param target_frame:
    :type target_frame: str
    :param pose:
    :type pose: PoseStamped
    :return: Transformed pose of None on loop failure
    :rtype: PoseStamped
    """
    global tfBuffer
    if tfBuffer is None:
        init()
    try:
        transform = tfBuffer.lookup_transform(target_frame,
                                              pose.header.frame_id,  # source frame
                                              pose.header.stamp,
                                              rospy.Duration(1.0))
        new_pose = do_transform_pose(pose, transform)
        return new_pose
    except ExtrapolationException as e:
        rospy.logwarn(e)

def lookup_transform(target_frame, source_frame):
    """
    :param target_frame:
    :type target_frame: str
    :param source_frame:
    :type source_frame: str
    :return: Transform from target_frame to source_frame
    :rtype: PoseStamped
    """
    p = PoseStamped()
    p.header.frame_id = source_frame
    p.pose.orientation.w = 1.0
    return transform_pose(target_frame, p)

