from collections import OrderedDict


class SingleJointState(object):
    def __init__(self, name='', position=0.0, velocity=0.0, effort=0.0):
        self.name = name
        self.position = position
        self.velocity = velocity
        self.effort = effort


class MultiJointState(object):
    #TODO emulate dict?
    def __init__(self):
        self._states = OrderedDict()

    def get(self, name):
        return self._states[name]

    def set(self, state):
        self._states[state.name] = state

    def keys(self):
        return self._states.keys()

    def values(self):
        return self._states.values()

    def items(self):
        return self._states.items()


class Point(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class Quaternion(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w


class Transform(object):
    def __init__(self, translation=Point(), rotation=Quaternion()):
        self.translation = translation
        self.rotation = rotation


class Stamped(object):
    def __init__(self, reference_name=''):
        self.reference_name = reference_name


class PointStamped(Point, Stamped):
    pass


class QuaternionStamped(Quaternion, Stamped):
    pass


class TransformStamped(Transform, Stamped):
    pass


class Trajectory(object):
    def __init__(self):
        self._points = OrderedDict()

    def get_exact(self, time):
        return self._points[time]

    def get_closest(self, time):
        pass

    def get_sub_trajectory(self, start_time, end_time):
        pass

    def set(self, time, point):
        if len(self._points) > 0 and self._points.keys()[-1] > time:
            raise KeyError("Cannot append a trajectory point that is before the current end time of the trajectory.")
        self._points[time] = point
