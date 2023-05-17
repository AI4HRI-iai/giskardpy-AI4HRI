from collections import defaultdict

import rospy
from py_trees import Status

import giskardpy.identifier as identifier
from giskardpy.data_types import JointStates
from giskardpy.tree.behaviors.plugin import GiskardBehavior
from giskardpy.utils import logging
from giskardpy.utils.decorators import record_time


class Sleeper(GiskardBehavior):

    def __init__(self, name, sleep_time: float = 0.01):
        super().__init__(name)
        self.sleep_time = sleep_time

    def update(self):
        rospy.sleep(self.sleep_time)
        return Status.RUNNING
