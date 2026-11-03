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

        self.subscription = self.create_subscription(
            Int32MultiArray,
            '/user_pins',
            self.listener_callback,
            10
        )
        self.subscription
    
        self.publisher_ = self.create_publisher(
            Bool, 
            'tripped', 
            10
        )

        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Bool()

    def listener_callback(self):
        pass

def main(args=None):
    rclpy.init(args=args)

    joystick_monitor = JoystickMonitor()

    rclpy.spin(joystick_monitor)

    joystick_monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
