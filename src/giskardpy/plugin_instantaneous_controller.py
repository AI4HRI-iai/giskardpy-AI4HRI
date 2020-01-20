from copy import copy

from py_trees import Status

import giskardpy.identifier as identifier
from giskardpy.plugin import GiskardBehavior
from giskardpy.symengine_controller import InstantaneousController


class ControllerPlugin(GiskardBehavior):
    def __init__(self, name):
        super(ControllerPlugin, self).__init__(name)
        self.path_to_functions = self.get_god_map().safe_get_data(identifier.data_folder)
        self.nWSR = self.get_god_map().safe_get_data(identifier.nWSR)
        self.soft_constraints = None
        self.qp_data = {}
        self.get_god_map().safe_set_data(identifier.qp_data, self.qp_data)  # safe dict on godmap and work on ref

    def initialise(self):
        super(ControllerPlugin, self).initialise()
        self.init_controller()

    def setup(self, timeout=0.0):
        return super(ControllerPlugin, self).setup(5.0)

    def init_controller(self):
        new_soft_constraints = self.get_god_map().safe_get_data(identifier.soft_constraint_identifier)
        if self.soft_constraints is None or set(self.soft_constraints.keys()) != set(new_soft_constraints.keys()):
            self.soft_constraints = copy(new_soft_constraints)
            self.controller = InstantaneousController(self.get_robot(),
                                                      u'{}/{}/'.format(self.path_to_functions,
                                                                       self.get_robot().get_name()))
            self.controller.set_controlled_joints(self.get_robot().controlled_joints)
            self.controller.update_soft_constraints(self.soft_constraints)
            self.controller.compile()

            self.qp_data[identifier.weight_keys[-1]], \
            self.qp_data[identifier.b_keys[-1]], \
            self.qp_data[identifier.bA_keys[-1]], \
            self.qp_data[identifier.xdot_keys[-1]] = self.controller.get_qpdata_key_map()

    def update(self):
        last_cmd = self.get_god_map().safe_get_data(identifier.cmd)
        self.get_god_map().safe_set_data(identifier.last_cmd, last_cmd)

        expr = self.controller.get_expr()
        expr = self.god_map.get_values(expr)

        next_cmd, \
        self.qp_data[identifier.H[-1]], \
        self.qp_data[identifier.A[-1]], \
        self.qp_data[identifier.lb[-1]], \
        self.qp_data[identifier.ub[-1]], \
        self.qp_data[identifier.lbA[-1]], \
        self.qp_data[identifier.ubA[-1]], \
        self.qp_data[identifier.xdot_full[-1]] = self.controller.get_cmd(expr, self.nWSR)
        self.get_god_map().safe_set_data(identifier.cmd, next_cmd)

        return Status.RUNNING
