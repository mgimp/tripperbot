import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool

class WrapTarget(Node):
    def __init__(self):
        super().__init__('wrap_target')

        self.subscription = self.create_subscription(
            Bool,
            'pulled',
            self.listener_callback,
            10
        )
        self.subscription

        self.pulled = False

        # Declare parameters with default values
        """ 
        Example parameter use
            ros2 run tripperbot wrap_target --ros-args -p radius:=0.5 -p velocity:=0.15
        To change parameter while running
            ros2 param set /wrap_target velocity:=0.17
        """
        self.declate_parameter('radius', 1) # meters
        self.declare_parameter('velocity', 0.22) # m/s (max speed is 0.22m/s)

        # Read parameter values
        self.r = get_parameter('radius').value
        self.v = get_parameter('velocity').value

        self.get_logger().info(f'Radius: {self.r}, Velocity: {self.v}')

        self.trigger = False
        self.a # angular speed m/s
        self.publish_rate = 0.5 # Hz
        self.drive_duration # seconds

        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def idle(self):
        return

    # TODO: drive()
    def drive(self):
        # turn speed = velocity / radius
        self.get_logger().info(f'Velocity: {self.v}, Turn Rate: {self.v/self.r}')
        pass

    def listener_callback(self, msg):
        self.pulled = msg.data

    def timer_callback(self):

        # Report change in parameter
        if get_parameter('velocity').value is not self.v:

            self.v = get_parameter('velocity').value
            self.get_logger().info(f'Radius: {self.r}, Velocity: {self.v}')

        if self.pulled is True:
            self.trigger = True
            self.get_logger().info('Trigger pulled!')

        if self.trigger is True:
            self.drive()

        else: return

def main(args=None):
    rclpy.init()
    wrap_target = WrapTarget()
    rclpy.spin(wrap_target)
    wrap_target.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
