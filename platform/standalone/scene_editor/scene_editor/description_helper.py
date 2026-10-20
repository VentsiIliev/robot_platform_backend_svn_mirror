#!/usr/bin/env python3
"""One-shot read-only robot_description subscriber; no GUI or ROS commands."""
import argparse
import json
import os
import time
import xml.etree.ElementTree as ET


def read_description(topic, timeout):
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
    from std_msgs.msg import String
    from ament_index_python.packages import get_package_share_directory, PackageNotFoundError

    rclpy.init(args=[])
    node = Node('scene_editor_description_'+str(os.getpid()),enable_rosout=False,start_parameter_services=False)
    received = []
    def receive(message):
        if message.data.strip() and not received:
            received.append(message.data)
    subscription = node.create_subscription(String,topic,receive,
                    QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,
                               reliability=ReliabilityPolicy.RELIABLE))
    try:
        deadline = time.monotonic()+timeout
        while not received and rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node,timeout_sec=min(.2,max(deadline-time.monotonic(),0)))
        if not received:
            return dict(success=False,unavailable=True,message=f'No robot description received on {topic} within {timeout:g} seconds.')
        xml = received[0]
        root = ET.fromstring(xml)
        packages = {}
        for mesh in root.iter('mesh'):
            uri = mesh.get('filename','')
            if uri.startswith('package://'):
                package = uri[len('package://'):].split('/',1)[0]
                if package not in packages:
                    try:
                        packages[package] = get_package_share_directory(package)
                    except PackageNotFoundError:
                        pass
        return dict(success=True,xml=xml,packages=packages)
    finally:
        node.destroy_subscription(subscription)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--description-topic',default='/robot_description')
    parser.add_argument('--timeout',type=float,default=5.)
    args = parser.parse_args()
    try:
        result = read_description(args.description_topic,args.timeout)
    except ImportError as exc:
        result = dict(success=False,unavailable=True,message='ROS Python environment unavailable: '+str(exc))
    except Exception as exc:
        result = dict(success=False,unavailable=False,message=str(exc) or type(exc).__name__)
    print(json.dumps(dict(protocol='scene-editor-description-v1',**result)),flush=True)


if __name__ == '__main__':
    main()
