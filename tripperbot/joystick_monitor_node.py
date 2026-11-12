import rclpy
from rclpy import Node

from std_msgs.msg import Int32MultiArray, Bool

# /user_pins varies between [0, 1023] on each pin
# layout:
#   dim: []
#   data_offset: 0
# data:
# - 501 (Y, parallel to the pins)
# - 507 (X, perpendicular to the pins)

# Tutorial pubsub: https://docs.ros.org/en/foxy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html

class JoystickMonitor(Node):
    def __init__(self):
        super().__init__('joystick_monitor')

        # TODO: Edit subscriber node to read /user_pins
        # TODO: Remove subscriber callback
        self.subscription = self.create_subscription(
            Int32MultiArray,
            '/user_pins',
            self.listener_callback,
            10
        )
        self.subscription

        # TODO: Edit publisher to report a boolean 'tripped' value
        self.publisher_ = self.create_publisher(
            Bool, 
            'pulled', 
            10
        )

        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Bool()

        msg.data = True                                         # TODO: adjust to be the result of /user_pins data

        self.publisher_.publish(msg)                            # Actually publishes msg
        self.get_logger().info('Publishing : "%s"' % msg.data)  # Print to console

    # TODO: Write a function to asses whether joystick is tripped or not tripped and change reported boolean depending on the result

def main(args=None):
    rclpy.init(args=args)

    joystick_monitor = JoystickMonitor()    # Initialize class

    rclpy.spin(joystick_monitor)            # Start node and hand off to ROS

    joystick_monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
