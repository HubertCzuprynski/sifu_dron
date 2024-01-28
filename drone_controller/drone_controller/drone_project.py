import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist, Pose


class DroneController(Node):
    def __init__(self):
        super().__init__('drone_controller')
        
        #subskrybent
        self.gt_pose_sub = self.create_subscription( Pose, '/drone/gt_pose',
            self.pose_callback, 1)
        self.gt_pose = None

        #jak ma lecieć
        self.command_pub = self.create_publisher(Twist, '/drone/cmd_vel', 10)
        #czas callbacku
        timer_period = 1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        #pozycje gdzie ma lecieć (cel)
        self.goals = [[15.0, -15.0],[15.0, 15.0], [-15.0, 15.0], [-15.0, -15.0]]
        self.next_goal = 0
    
    def pose_callback(self, data):
        self.gt_pose = data
        print(f"{data}")

    
    def timer_callback(self):
        #pozycje i lot do celu
        x = 0
        y = 0
        if self.gt_pose is not None:
            x = self.gt_pose.position.x
            y = self.gt_pose.position.y
        dx = abs(x*2 - self.goals[self.next_goal][0])
        dy = abs(y*2 - self.goals[self.next_goal][1])
        if dx < .5 and dy < .5:
            print("Osiągnąłeś cel, lecimy dalej")
            self.next_goal += 1
            if self.next_goal > len(self.goals) -1:
                self.next_goal = 0
        #wiadomosc jako Twist i publikacja
        msg = Twist()
        msg.linear.z = 10
        msg.linear.x = self.goals[self.next_goal][0]
        msg.linear.y = self.goals[self.next_goal][1]
        #selfpub
        self.command_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = DroneController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
