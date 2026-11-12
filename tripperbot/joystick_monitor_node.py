import rclpy
from rclpy.node import Node

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

        self.subscription = self.create_subscription(
            Int32MultiArray,
            'user_pins',
            self.listener_callback,
            10
        )
        self.subscription

        self.publisher_ = self.create_publisher(
            Bool, 
            'pulled', 
            10
        )

        self.pins = []
        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def listener_callback(self, msg_in):
        self.pins = msg_in.data

    def timer_callback(self):
        if self.pins is None:  # Wait until first message is received
            return

        msg_out = Bool()

        # Test if joystick has left resting position
        neutral = 1024 / 2 - 1                                      # Value of joystick at resting position
        if abs(self.pins[0] - neutral) > + 100 or abs(self.pins[1] - neutral) > 100:  
            msg_out.data = True
        else: msg_out.data = False

        self.publisher_.publish(msg_out)                            # Actually publishes msg_out
        # self.get_logger().info('Publishing : "%s"' % msg_out.data)  # Print to console

def main(args=None):
    rclpy.init(args=args)

    joystick_monitor = JoystickMonitor()    # Initialize class

    rclpy.spin(joystick_monitor)            # Start node and hand off to ROS

    joystick_monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
