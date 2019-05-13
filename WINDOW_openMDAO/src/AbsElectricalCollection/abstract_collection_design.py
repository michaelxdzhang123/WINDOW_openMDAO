from builtins import range
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines, max_n_substations, max_n_turbines_p_branch, max_n_branches
import numpy as np


class AbstractElectricDesign(ExplicitComponent):

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 2))
        self.add_input('n_turbines_p_cable_type', shape=3)
        self.add_input('substation_coords', shape=(max_n_substations, 2))
        self.add_input('n_substations', val=0)
        self.add_input('n_turbines', val=0)

        self.add_output('topology', shape=(max_n_substations, max_n_branches, max_n_turbines_p_branch, 2))
        self.add_output('cost_p_cable_type', shape=3)
        self.add_output('length_p_cable_type', shape=3)

        # self.declare_partials(of=['topology', 'cost_p_cable_type', 'length_p_cable_type'], wrt=['layout', 'n_turbines_p_cable_type', 'substation_coords', 'n_substations', 'n_turbines'], method='fd')

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        layout = np.hstack((np.arange(n_turbines).reshape(n_turbines,1), inputs["layout"]))[:n_turbines]
        n_substations = int(inputs['n_substations'])
        n_turbines_p_cable_type = [int(num) for num in inputs['n_turbines_p_cable_type']]
        substation_coords = np.hstack((np.arange(n_substations).reshape(n_substations,1), inputs['substation_coords']))[:n_substations]
        # print(substation_coords)
        cost, topology_dict, cable_lengths = self.topology_design_model(layout, substation_coords, n_turbines_p_cable_type)
        if type(topology_dict) is dict:
            topology_list = []
            for n in range(1, len(topology_dict) + 1):
                topology_list.append(topology_dict[n])

            ### Start Python 2+3 compatibility code
            from future.standard_library import install_aliases
            install_aliases()
            ### End Python 2+3 compatibility code
            from itertools import zip_longest

            def find_shape(seq):
                try:
                    len_ = len(seq)
                except TypeError:
                    return ()
                shapes = [find_shape(subseq) for subseq in seq]
                return (len_,) + tuple(max(sizes) for sizes in zip_longest(*shapes, fillvalue=1))

            def fill_array(arr, seq):
                if arr.ndim == 1:
                    try:
                        len_ = len(seq)
                    except TypeError:
                        len_ = 0
                    arr[:len_] = seq
                    arr[len_:] = np.nan
                else:
                    for subarr, subseq in zip_longest(arr, seq, fillvalue=()):
                        fill_array(subarr, subseq)

            topology = np.empty((max_n_substations, max_n_branches, max_n_turbines_p_branch, 2))
            fill_array(topology, topology_list)

        else:
            topology = topology_dict
        outputs['cost_p_cable_type'] = cost
        outputs['topology'] = topology
        outputs['length_p_cable_type'] = cable_lengths

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type, n_substations):
        # Define your own model in a subclass of AbstractElectricDesign and redefining this method.
        pass
