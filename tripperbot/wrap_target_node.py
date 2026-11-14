import rclpy
from rclpy.node import Node

from rclpy.signals import SignalHandlerOptions

from std_msgs.msg import Bool
from geometry_msgs.msg import TwistStamped

from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange

from enum import Enum, auto

class WrapTarget(Node):
    """ 
    Drives tripperbot in two stages:
        1. Tripperbot moves forward until it detects pulled=True
        2. Tripperbot moves in a circle for duration wrap_duration  
    """
    def __init__(self):
        super().__init__('wrap_target')

        self.subscription = self.create_subscription(
            Bool,
            'pulled',
            self.listener_callback,
            10
        )
        self.subscription

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
            1.0, # meters
            ParameterDescriptor(
                description='Radius in meters of the circle that trippebot will follow.',
                floating_point_range=[FloatingPointRange(from_value=0.1, to_value=3.0)]
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
            'wrap_duration',
            60.0 # seconds
            )

        # Read parameter values
        self.r = self.get_parameter('radius').value
        self.cmd_vel.twist.linear.x = self.get_parameter('velocity').value
        self.cmd_vel.twist.angular.z = 0.0 # for initially deiving straight
        self.wrap_duration = self.get_parameter('wrap_duration').value

        self.get_logger().info(f'Radius: {self.r}, Velocity: {self.cmd_vel.twist.linear.x}')

        self.timer_period = 0.1 # s
        self.i = 1 # timer tick
        
        self.current_state = TripperbotState.ADVANCE
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def parameter_callback(self):
        # Controls new parameters

        x = self.get_parameter('velocity').value
        z = x / self.r

        if z > 2.84:
            self.get_logger().error(f'Angular velocity exceeds maximum of 2.84 rad/s (w=v/r); velocity={x} radius={self.r} angular velocity={z}')
            return

        else:
            if self.pulled is True:
                self.cmd_vel.twist.angular.z = z

            self.cmd_vel.twist.linear.x = x

        return

    def move(self):
        self.cmd_vel.header.stamp = self.get_clock().now().to_msg()
        self.cmd_vel.header.frame_id = 'base_link'
        self.publisher.publish(self.cmd_vel)
        return

    def finish(self):
        self.stop_msg = TwistStamped()
        self.stop_msg.header.stamp = self.get_clock().now().to_msg()
        self.stop_msg.header.frame_id = 'base_link'
        self.stop_msg.twist.linear.x = 0.0
        self.stop_msg.twist.angular.z = 0.0
        self.publisher.publish(self.stop_msg)

    def listener_callback(self, msg):
        self.pulled = msg.data
        return

    def timer_callback(self):
        # Report change in parameter
        if self.get_parameter('velocity').value != self.cmd_vel.twist.linear.x:
            self.parameter_callback()

        match self.current_state:
            case TripperbotState.ADVANCE:
                # Toggle driving action on trigger pull
                if self.pulled is True:
                    self.get_logger().info('Trigger pulled!')
                    self.cmd_vel.twist.angular.z = self.cmd_vel.twist.linear.x / self.r
                    self.current_state = TripperbotState.WRAP
                
                self.move()

            case TripperbotState.WRAP:
                # Increment timer
                self.i += 1
                if self.i > self.wrap_duration/self.timer_period:
                    self.get_logger().info('Timer exceeded')
                    self.current_state = TripperbotState.FINISH

                self.move()

            case TripperbotState.FINISH:
                self.finish()

        return

class TripperbotState(Enum):
    ADVANCE = auto()
    WRAP = auto()
    FINISH = auto()

def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    wrap_target = WrapTarget()
    try:
        rclpy.spin(wrap_target)
    except KeyboardInterrupt:
        wrap_target.get_logger().info('Keyboard interrupt')
        wrap_target.finish()
    finally:
        wrap_target.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
