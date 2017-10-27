from WakeModel.jensen import JensenWakeFraction, JensenWakeDeficit
from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder
import numpy as np
from time import time, clock
from Power.power_models import PowerPolynomial
from input_params import turbine_radius
from WakeModel.WakeMerge.RSS import WakeMergeRSS
from src.api import AEPWorkflow

real_angle = 30.0
artificial_angle = 10.0
n_windspeedbins = 10
n_cases = int((360.0 / artificial_angle) * (n_windspeedbins + 1.0))

direction = []
weibull_scale = []
weibull_shape = []
dir_probability = []
with open('weibull_windrose.dat', 'r') as windrose:
    for line in windrose:
        columns = line.split()
        direction.append(float(columns[0]))
        weibull_scale.append(float(columns[1]))
        weibull_shape.append(float(columns[2]))
        dir_probability.append(float(columns[3]))


class WorkingGroup(Group):
    def __init__(self, power_model, fraction_model, deficit_model, merge_model):
        super(WorkingGroup, self).__init__()
        self.power_model = power_model
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output('layout', val=read_layout('horns_rev.dat'))
        # indep2.add_output('layout', val=np.array([[0, 0.0, 0.0], [1, 560.0, 560.0], [2, 1120.0, 1120.0],
        #                                           [3, 0.0, 1120.0], [4, 1120.0, 0.0]]))#, [5, 0.0, 1120.0],
                                                  # [6, 0.0, 1120.0], [7, 0.0, 1120.0], [8, 0.0, 1120.0],
                                                  # [9, 0.0, 1120.0]]))
        indep2.add_output('weibull_shapes', val=weibull_shape)
        indep2.add_output('weibull_scales', val=weibull_scale)
        indep2.add_output('dir_probabilities', val=dir_probability)
        indep2.add_output('wind_directions', val=direction)  # Follows windrose convention N = 0 deg, E = 90 deg,
        #  S = 180 deg, W = 270 deg
        indep2.add_output('cut_in', val=4.0)
        indep2.add_output('cut_out', val=25.0)
        indep2.add_output('r', val=turbine_radius)
        indep2.add_output('n_turbines', val=80)
        aep = self.add_subsystem('AEP', AEPWorkflow(real_angle, artificial_angle, n_windspeedbins, self.power_model,
                                                    self.fraction_model, self.deficit_model, self.merge_model))

        # self.my_recorder = SqliteRecorder("data_out_try")
        # self.my_recorder.options['record_outputs'] = True
        # self.my_recorder.options['record_inputs'] = True
        # self.my_recorder.options['record_residuals'] = True

        # aep.add_recorder(self.my_recorder)

        self.connect('indep2.layout', 'AEP.original')
        self.connect('indep2.n_turbines', 'AEP.n_turbines')
        self.connect('indep2.r', 'AEP.r')
        self.connect('indep2.cut_in', 'AEP.cut_in')
        self.connect('indep2.cut_out', 'AEP.cut_out')
        self.connect('indep2.weibull_shapes', 'AEP.weibull_shapes')
        self.connect('indep2.weibull_scales', 'AEP.weibull_scales')
        self.connect('indep2.dir_probabilities', 'AEP.dir_probabilities')
        self.connect('indep2.wind_directions', 'AEP.wind_directions')


def read_layout(layout_file):
    layout_file = open(layout_file, 'r')
    layout = []
    i = 0
    for line in layout_file:
        columns = line.split()
        layout.append([i, float(columns[0]), float(columns[1])])
        i += 1

    return np.array(layout)


print clock(), "Before defining problem"
prob = Problem()
print clock(), "Before defining model"
prob.model = WorkingGroup(PowerPolynomial, JensenWakeFraction, JensenWakeDeficit, WakeMergeRSS)
print clock(), "Before setup"
prob.setup(check=False)

print clock(), "After setup"
# view_model(prob)
start = time()
print clock(), "Before 1st run"
prob.run_model()
print clock(), "After 1st run"
print time() - start, "seconds", clock()
print prob['AEP.AEP']
print sum(prob['AEP.windrose.probabilities'])
#
# print "second run"
# start = time()
# print clock(), "Before 2nd run"
# prob.run_model()
# print clock(), "After 2nd run"
# print time() - start, "seconds", clock()
# print prob['AEP.AEP']
#
#
# print "third run"
# start = time()
# print clock(), "Before 3rd run"
# prob.run_model()
# print clock(), "After 3rd run"
# print time() - start, "seconds", clock()
# print prob['AEP.AEP']


with open("angle_power.dat", "w") as out:
    for n in range(n_cases):
        out.write("{} {} {} {} {}\n".format(prob['AEP.open_cases.wind_directions'][n], prob['AEP.open_cases.freestream_wind_speeds'][n], prob['AEP.windrose.probabilities'][n], prob['AEP.farmpower.farm_power'][n], prob['AEP.energies'][n]))
print prob['AEP.AEP']
print sum(prob['AEP.windrose.probabilities'])