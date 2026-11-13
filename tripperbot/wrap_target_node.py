import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from geometry_msgs.msg import TwistStamped

from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange

class WrapTarget(Node):
    def __init__(self):
        super().__init__('wrap_target')

        self.tubscription = self.create_subscription(
            Bool,
            'pulled',
            self.listener_callback,
            10
        )
        self.tubscription

        self.publisher = self.create_publisher(
            TwistStamped,
            'cmd_vel',
            10
        )

        self.cmd_vel = TwistStamped()

        self.pulled = False

        # Declare parameters with default values
        """ 
        Example parameter use
            ros2 run tripperbot wrap_target --ros-args -p radius:=0.5 -p velocity:=0.15
        To change parameter while running
            ros2 param set /wrap_target velocity:=0.17
        """
        self.declare_parameter(
            'radius',
            1, # meters
            ParameterDescriptor(
                description='Radius in meters of the circle that trippebot will follow.',
                floating_point_range=[FloatingPointRange(from_value=0.5, to_value=3)]
                                )
            ) 
        self.declare_parameter(
            'velocity',
            0.22, # m/s (max speed is 0.22m/s)
            ParameterDescriptor(
                description='Tripper bot speed in m/s.',
                floating_point_range=[FloatingPointRange(from_value=0.01, to_value=0.22)]
                )
            )
        self.declare_parameter(
            'drive_duration',
            60 # seconds
            )

        # Read parameter values
        self.r = self.get_parameter('radius').value
        self.cmd_vel.twist.linear.x = self.get_parameter('velocity').value
        self.cmd_vel.twist.angular.z = self.cmd_vel.twist.linear.x / self.r # max turn velocity 2.84 rad/s
        self.drive_duration = self.get_parameter('drive_duration').value

        self.get_logger().info(f'Radius: {self.r}, Velocity: {self.cmd_vel.twist.linear.x}')

        self.trigger = False
        self.publish_rate = 0.5 # Hz

        self.timer_period = 0.5 # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.i = 0 # timer tick
        self.t = 0 # time, seconds

    def paramter_callback(self):
        # Controls new parameters

        x = self.get_parameter('velocity').value
        z = x / self.r

        if z > 2.84:
            self.get_logger().error(f'Angular velocity exceeds maximum of 2.84 rad/s (w=v/r); velocity={x} radius={self.r} angular velocity={z}')
            return

        else:
            self.cmd_vel.twist.linear.x = x
            self.cmd_vel.twist.angular.z = z

        return

    def drive(self):
        self.publisher(self.cmd_vel)
        return

    def listener_callback(self, msg):
        self.pulled = msg.data
        return

    def timer_callback(self):
        # Increment timer
        self.i += 1
        if self.i % self.timer_period == 0:
            self.t += 1

        # Report change in parameter
        if self.get_parameter('velocity').value is not self.cmd_vel.twist.linear.x:
            self.paramter_callback()

        # Toggle driving action on trigger pull
        if self.pulled is True:
            self.trigger = True
            self.get_logger().info('Trigger pulled!')

        # Stop action if exceeded drive duration
        if self.t > self. drive_duration:
            self.destroy_node()

        # Drive!
        if self.trigger is True:
            self.drive()
            return

        else: return

def main(args=None):
    rclpy.init()
    wrap_target = WrapTarget()
    rclpy.spin(wrap_target)
    wrap_target.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
