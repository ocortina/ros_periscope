import rclpy
import numpy as np
import transforms3d as tf
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry.msgs.msg import TransformStamped, PoseWithCovarianceStamped


class DynamicFrameBroadcaster(Node):

    def __init__(self):
        super().__init__('dynamic_drone_frame_tf2_broadcaster')
        self.tf_broadcaster = TransformBroadcaster(self)

        # Subscribe to a drone_posecov topic and call broadcast_drone_pose
        # callback function on each message
        self.subscription = self.create_subscription(PoseWithCovarianceStamped, 
                                                     'drone_posecov',
                                                     self.broadcast_drone_pose,
                                                     10)
        self.subscription  # prevent unused variable warning
    
    
    def broadcast_drone_pose(self, msg):
        """
        Updates drone pose state.        

        Args:
            msg (PoseWithCovarianceStamped): ros message of type PoseWithCovariance,
                                             containing drone pose info.
        
        Returns:
            None                                     
        """
        
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'drone'
        
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation.x = msg.pose.pose.position.x
        t.transform.rotation.y = msg.pose.pose.position.y
        t.transform.rotation.z = msg.pose.pose.position.z
        t.transform.rotation.w = msg.pose.pose.position.w
        
        self.tf_broadcaster.sendTransform(t)
        
        #quaternion = [msg.pose.pose.position.x,
        #              msg.pose.pose.position.y, 
        #              msg.pose.pose.position.z, 
        #              msg.pose.pose.position.w]
        #
        #angles = tf.euler.quat2euler(quaternion, axes="sxyz")
        #
        #self.drone_phi   = angles[0]  
        #self.drone_theta = angles[1]
        #self.drone_psi   = angles[2]


