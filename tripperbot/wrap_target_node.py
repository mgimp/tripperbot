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

        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def wrap(self):
        pass

    def listener_callback(self, msg):
        self.pulled = msg.data

    def timer_callback(self):
        if self.pulled is False:
            return

        if self.pulled is True:
            self.wrap()

def main(args=None):
    rclpy.init()
    wrap_target = WrapTarget()
    rclpy.spin(wrap_target)
    wrap_target.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
