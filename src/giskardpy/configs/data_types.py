from collections import defaultdict
from enum import Enum
from typing import Optional, List, Tuple, Dict, Union

from giskardpy.utils.utils import resolve_ros_iris


class CollisionCheckerLib(Enum):
    bpb = 1
    pybullet = 2
    none = 3


class SupportedQPSolver(Enum):
    gurobi = 1
    qp_oases = 2
    cplex = 3


class FrameToAddToWorld:
    def __init__(self, parent_link, child_link, transform, add_after_robot):
        self.child_link = child_link
        self.parent_link = parent_link
        self.transform = transform
        self.add_after_robot = add_after_robot


class ControlModes(Enum):
    open_loop = 1
    close_loop = 2
    stand_alone = 3


class GeneralConfig:
    control_mode: ControlModes = ControlModes.open_loop
    action_server_name: str = '~command'
    path_to_data_folder: str = resolve_ros_iris('package://giskardpy/data/')
    test_mode: bool = False
    debug: bool = False
    joint_limits: Dict[int, Dict[str, float]] = {
        'velocity': defaultdict(lambda: 1),
        'acceleration': defaultdict(lambda: 1e3),
        'jerk': defaultdict(lambda: 30)
    }


class QPSolverConfig:
    def __init__(self,
                 qp_solver: SupportedQPSolver = SupportedQPSolver.gurobi,
                 prediction_horizon: int = 9,
                 retries_with_relaxed_constraints: int = 5,
                 added_slack: float = 100,
                 sample_period: float = 0.05,
                 weight_factor: float = 100,
                 joint_weights: Optional[Dict[int, Dict[str, float]]] = None):
        self.qp_solver = qp_solver
        self.prediction_horizon = prediction_horizon
        self.retries_with_relaxed_constraints = retries_with_relaxed_constraints
        self.added_slack = added_slack
        self.sample_period = sample_period
        self.weight_factor = weight_factor
        if joint_weights is None:
            self.joint_weights = {
                'velocity': defaultdict(lambda: 0.001),
                'acceleration': defaultdict(float),
                'jerk': defaultdict(lambda: 0.001)
            }
        else:
            self.joint_weights = joint_weights


class CollisionAvoidanceConfig:
    class CollisionAvoidanceEntry:
        def __init__(self,
                     number_of_repeller: int = 1,
                     soft_threshold: float = 0.05,
                     hard_threshold: float = 0.0,
                     max_velocity: float = 0.2):
            self.number_of_repeller = number_of_repeller
            self.soft_threshold = soft_threshold
            self.hard_threshold = hard_threshold
            self.max_velocity = max_velocity

        @classmethod
        def init_50mm(cls):
            return cls(soft_threshold=0.05, hard_threshold=0.0)

        @classmethod
        def init_100mm(cls):
            return cls(soft_threshold=0.1, hard_threshold=0.0)

        @classmethod
        def init_25mm(cls):
            return cls(soft_threshold=0.025, hard_threshold=0.0)

    collision_checker: CollisionCheckerLib = CollisionCheckerLib.bpb

    _add_self_collisions: List[Tuple[str, str]] = []
    _ignored_self_collisions: List[Union[str, Tuple[str, str]]] = []

    _external_collision_avoidance: Dict[str, CollisionAvoidanceEntry] = defaultdict(CollisionAvoidanceEntry)
    _self_collision_avoidance: Dict[str, CollisionAvoidanceEntry] = defaultdict(CollisionAvoidanceEntry)

    def ignore_all_self_collisions_of_link(self, link_name):
        self._ignored_self_collisions.append(link_name)

    def ignore_self_collisions_of_pair(self, link_name1, link_name2):
        self._ignored_self_collisions.append((link_name1, link_name2))

    def add_self_collision(self, link_name1, link_name2):
        self._add_self_collisions.append((link_name1, link_name2))

    def set_default_external_collision_avoidance(self,
                                                 number_of_repeller: int = 1,
                                                 soft_threshold: float = 0.05,
                                                 hard_threshold: float = 0.0,
                                                 max_velocity: float = 0.2):
        self._external_collision_avoidance.default_factory = lambda: self.CollisionAvoidanceEntry(
            number_of_repeller=number_of_repeller,
            soft_threshold=soft_threshold,
            hard_threshold=hard_threshold,
            max_velocity=max_velocity
        )

    def overwrite_external_collision_avoidance(self,
                                               joint_name: str,
                                               number_of_repeller: Optional[int] = None,
                                               soft_threshold: Optional[float] = None,
                                               hard_threshold: Optional[float] = None,
                                               max_velocity: Optional[float] = None):
        if number_of_repeller is not None:
            self._external_collision_avoidance[joint_name].number_of_repeller = number_of_repeller
        if soft_threshold is not None:
            self._external_collision_avoidance[joint_name].soft_threshold = soft_threshold
        if hard_threshold is not None:
            self._external_collision_avoidance[joint_name].hard_threshold = hard_threshold
        if max_velocity is not None:
            self._external_collision_avoidance[joint_name].max_velocity = max_velocity

    def set_default_self_collision_avoidance(self,
                                             number_of_repeller: int = 1,
                                             soft_threshold: float = 0.05,
                                             hard_threshold: float = 0.0,
                                             max_velocity: float = 0.2):
        self._self_collision_avoidance.default_factory = lambda: self.CollisionAvoidanceEntry(
            number_of_repeller=number_of_repeller,
            soft_threshold=soft_threshold,
            hard_threshold=hard_threshold,
            max_velocity=max_velocity
        )

    def overwrite_self_collision_avoidance(self,
                                           link_name: str,
                                           number_of_repeller: Optional[int] = None,
                                           soft_threshold: Optional[float] = None,
                                           hard_threshold: Optional[float] = None,
                                           max_velocity: Optional[float] = None):
        if number_of_repeller is not None:
            self._self_collision_avoidance[link_name].number_of_repeller = number_of_repeller
        if soft_threshold is not None:
            self._self_collision_avoidance[link_name].soft_threshold = soft_threshold
        if hard_threshold is not None:
            self._self_collision_avoidance[link_name].hard_threshold = hard_threshold
        if max_velocity is not None:
            self._self_collision_avoidance[link_name].max_velocity = max_velocity


class BehaviorTreeConfig:
    tree_tick_rate: float = 0.1

    plugin_config = {
        'GoalReached': {
            'joint_convergence_threshold': 0.01,
            'window_size': 21
        },
        'VisualizationBehavior': {
            'enabled': True,
            'in_planning_loop': True
        },
        'PublishDebugExpressions': {
            'enabled': False,
            'expression_filter': None
        },
        'CollisionMarker': {
            'enabled': True,
            'in_planning_loop': False
        },
        'PlotTrajectory': {
            'enabled': True,
            'history': 5,
            'velocity_threshold': 0.0,
            'cm_per_second': 2.5,
            'height_per_derivative': 6,
            'normalize_position': True,
            'order': 4,
            'tick_stride': 0.5,
        },
        'PlotDebugExpressions': {
            'enabled': True,
            'history': 5,
            'cm_per_second': 2.5,
            'height_per_derivative': 6,
            'order': 2,
            'tick_stride': 0.5,
        },
        'WiggleCancel': {
            'amplitude_threshold': 0.55,
            'window_size': 21,
            'frequency_range': 0.4,
        },
        'TFPublisher': {
            'publish_attached_objects': True,
            'publish_world_objects': False,
            'tf_topic': '/tf',
        },
        'MaxTrajectoryLength': {
            'enabled': True,
            'length': 30
        },
        'LoopDetector': {
            'precision': 3
        },
        'SyncTfFrames': {
            'frames': [],
        },
        'PlotDebugTF': {
            'enabled': False,
        },
    }

    def set_goal_reached_parameters(self, joint_convergence_threshold=0.01, window_size=21):
        self.plugin_config['GoalReached'] = {
            'joint_convergence_threshold': joint_convergence_threshold,
            'window_size': window_size
        }

    def add_sync_tf_frame(self, parent_link, child_link, add_after_robot=False):
        # TODO make data structure
        self.plugin_config['SyncTfFrames']['frames'].append([parent_link, child_link, add_after_robot])


class RobotInterfaceConfig:
    def __init__(self, urdf: str, name: Optional[str] = None, joint_state_topic: str = '/joint_states'):
        self.urdf = urdf
        self.name = name
        self.joint_state_topic = joint_state_topic