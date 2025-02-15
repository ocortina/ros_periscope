import rclpy
import numpy as np
import transforms3d as tf
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import Vector3Stamped, TransformStamped, PoseWithCovarianceStamped


class DynamicGimbalPoseBroadcaster(Node):
    def __init__(self, x, y, z):
        super().__init__('dynamic_gimbal_frame_tf2_Broadcaster')
        
        #self._subscription = self.create_subscription(Vector3Stamped,
        #                                             "/ZR30/get_gimbal_attitude",
        #                                             self.gimbal_pose_callback,
        #                                             10)


        self._publisher = self.create_publisher(PoseWithCovarianceStamped,
                                                'gimbal_posecov',
                                                10)
        
        self.__pwcs = PoseWithCovarianceStamped()
        
        # Initialize timer for publishing transform
        self.__timer = self.create_timer(0.1, self.publish_gimbal_tf2)
        
        # Declare the transforms broadcaster
        self.__tf_broadcaster = TransformBroadcaster(self)
        
        # Declare the transform to broadcast
        self.__trans = TransformStamped()
        
        # Parent frame
        self.__trans.header.frame_id = 'drone'
        
        # Child frame
        self.__trans.child_frame_id = 'gimbal'   
        
        self.__trans.transform.translation.x = self.__pwcs.pose.pose.position.x = float(x)
        self.__trans.transform.translation.y = self.__pwcs.pose.pose.position.y = float(y)
        self.__trans.transform.translation.z = self.__pwcs.pose.pose.position.z = float(z)
        
        #self.__initial_pose()
    
    def publish_gimbal_tf2(self):
        self.__trans.header.stamp = self.__pwcs.header.stamp = self.get_clock().now().to_msg()
        self.__tf_broadcaster.sendTransform(self.__trans)
        
        self.__pwcs.header.frame_id = "gimbal"
        self._publisher.publish(self.__pwcs)
        
        
    def __initial_pose(self):   
        """
        This method is intended to be used just for debugging purposes
        
        Returns:
            None
        """ 
        self.__trans.transform.rotation.w = self.__pwcs.pose.pose.orientation.w = 1.0
        self.__trans.transform.rotation.x = self.__pwcs.pose.pose.orientation.x = 0.0
        self.__trans.transform.rotation.y = self.__pwcs.pose.pose.orientation.y = 0.0
        self.__trans.transform.rotation.z = self.__pwcs.pose.pose.orientation.z = 0.0
            
        self.__pwcs.pose.covariance = np.zeros(36)
        
            
    def gimbal_pose_callback(self, msg):
        """
        Creates transform based on euler angles of gimbal.

        Args:
            msg (Vector3Stamped): Gimbal orientation (euler) angles (x,y,z). 
                                   
        Returns:
            None
            
        """
        
        q = tf.euler.euler2quat(np.deg2rad(msg.vector.x), 
                                np.deg2rad(-msg.vector.y), 
                                np.deg2rad(msg.vector.z), 
                                'rxyz')
        
        self.__trans.transform.rotation.w = self.__pwcs.pose.pose.orientation.w = float(q[0])
        self.__trans.transform.rotation.x = self.__pwcs.pose.pose.orientation.x = float(q[1])
        self.__trans.transform.rotation.y = self.__pwcs.pose.pose.orientation.y = float(q[2])
        self.__trans.transform.rotation.z = self.__pwcs.pose.pose.orientation.z = float(q[3])
        
        self.__pwcs.pose.covariance = np.zeros(36)


def main():
    rclpy.init()
    node = DynamicGimbalPoseBroadcaster(x=0, y=0, z=0.238)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()