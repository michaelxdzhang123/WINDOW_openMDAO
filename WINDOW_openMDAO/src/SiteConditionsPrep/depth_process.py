"""Summary
"""
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines, max_n_substations
import numpy as np
from abc import ABC, abstractmethod


class AbstractWaterDepth(ExplicitComponent, ABC):

    """Summary
    
    Attributes:
        bathymetry_path (TYPE): Description
        n_turbines (TYPE): Description
    """
    
    def __init__(self, n_turbines, bathymetry_path):
        """Summary
        
        Args:
            n_turbines (TYPE): Description
            bathymetry_path (TYPE): Description
        """
        super(AbstractWaterDepth, self).__init__()
        self.n_turbines = n_turbines
        self.bathymetry_path = bathymetry_path

    def setup(self):
        """Summary
        """
        # if self.n_turbines > 4:
        #     self.add_input('layout', shape=(max_n_turbines, 2))
        # else:
        #     self.add_input('layout', shape=(max_n_substations, 2))  

        self.add_input('layout', shape=(self.n_turbines, 2))             
        self.add_input('n_turbines', val=0)

        self.add_output('water_depths', shape=self.n_turbines)
        #self.declare_partals(of='water_depths', wrt='layout', method='fd')

    def compute(self, inputs, outputs):
        """Summary
        
        Args:
            inputs (TYPE): Description
            outputs (TYPE): Description
        """
        layout = inputs['layout']
        n_turbines = int(inputs['n_turbines'])
        depths = self.depth_model(layout[:n_turbines])
        # dif = max_n_turbines - n_turbines
        # if dif:
        #     depths = np.append(depths, np.empty(dif).fill(np.nan))
        # depths = depths.reshape(max_n_turbines)
        outputs['water_depths'] = depths

    @abstractmethod
    def depth_model(self, layout):
        """Summary
        
        Args:
            layout (TYPE): Description
        """
        pass
