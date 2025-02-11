#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu" at 11:34, 11/07/2021                                                               %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Nguyen_Thieu2                                  %
#       Github:     https://github.com/thieu1995                                                        %
# ------------------------------------------------------------------------------------------------------%

from mealpy.evolutionary_based.GA import BaseGA
from mealpy.utils.visualize import *
from numpy import sum, mean, sqrt


## Define your own fitness function
# Multi-objective but single fitness/target value. By using weighting method to convert from multiple objectives to single target

def obj_function(solution):
    f1 = (sum(solution ** 2) - mean(solution)) / len(solution)
    f2 = sum(sqrt(abs(solution)))
    f3 = sum(mean(solution ** 2) - solution)
    return [f1, f2, f3]


## Setting parameters
verbose = True
epoch = 100
pop_size = 50

lb1 = [-10, -5, -15, -20, -10, -15, -10, -30]
ub1 = [10, 5, 15, 20, 50, 30, 100, 85]

optimizer = BaseGA(obj_function, lb1, ub1, "min", verbose, epoch, pop_size, obj_weight=[0.2, 0.5, 0.3])
best_position, best_fitness, g_best_fit_list, c_best_fit_list = optimizer.train()
print(best_position)

## Drawing trajectory of some agents in the first and second dimensions
# Need a little bit more pre-processing
pos_list = []
list_legends = []
dimension = 2
y_label = f"x{dimension + 1}"
for i in range(0, 5, 2):  # Get the third dimension of position of the first 3 solutions
    x = [pop[0][0][dimension] for pop in optimizer.history_list_pop]
    pos_list.append(x)
    list_legends.append(f"Agent {i + 1}.")
    # pop[0]: Get the first solution
    # pop[0][0]: Get the position of the first solution
    # pop[0][0][0]: Get the first dimension of the position of the first solution
export_trajectory_chart(pos_list, list_legends=list_legends, y_label=y_label)

# Parameter for this function
# data: is the list of array, each element is the position value of selected dimension in all generations
# title: title of the figure, default = "Trajectory of some first agents after generations"
# list_legends: list of line's name, default = None
# list_styles: matplotlib API, default =  None
# list_colors: matplotlib API, default = None
# x_label: string, default = "#Iteration"
# y_label: string, default = "X1"
# filename: string, default = "1d_trajectory"
# exts: matplotlib API, default = (".png", ".pdf") --> save figure in format of png and pdf
# verbose: show the figure on Python IDE, default = True

