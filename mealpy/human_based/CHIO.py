#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu Nguyen" at 19:24, 09/05/2020                                                        %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Thieu_Nguyen6                                  %
#       Github:     https://github.com/thieu1995                                                        %
#-------------------------------------------------------------------------------------------------------%

import numpy as np
from mealpy.optimizer import Optimizer


class OriginalCHIO(Optimizer):
    """
    The original version of: Coronavirus Herd Immunity Optimization (CHIO)
        (Coronavirus herd immunity Optimization)
    Link:
        https://link.springer.com/article/10.1007/s00521-020-05296-6
    """

    def __init__(self, problem, epoch=10000, pop_size=100, brr=0.06, max_age=150, **kwargs):
        """
        Args:
            problem ():
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
            brr (float): Basic reproduction rate, default=0.06
            max_age (int): Maximum infected cases age, default=150
            **kwargs ():
        """
        super().__init__(problem, kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.epoch = epoch
        self.pop_size = pop_size
        self.brr = brr
        self.max_age = max_age

    def initialization(self):
        self.pop = self.create_population(self.pop_size)
        _, self.g_best = self.get_global_best_solution(self.pop)

        self.immunity_type_list = np.random.randint(0, 3, self.pop_size)  # Randint [0, 1, 2]
        self.age_list = np.zeros(self.pop_size)  # Control the age of each position
        self.finished = False

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        pop_new = []
        is_corona_list = [False, ]*self.pop_size
        for i in range(0, self.pop_size):
            pos_new = self.pop[i][self.ID_POS].copy()
            for j in range(0, self.problem.n_dims):
                rand = np.random.uniform()
                if rand < (1.0 / 3) * self.brr:
                    idx_candidates = np.where(self.immunity_type_list == 1)  # Infected list
                    if idx_candidates[0].size == 0:
                        self.finished = True
                        print("Epoch: {}, i: {}, immunity_list: {}".format(epoch, i, self.immunity_type_list))
                        break
                    idx_selected = np.random.choice(idx_candidates[0])
                    pos_new[j] = self.pop[i][self.ID_POS][j] + np.random.uniform() * \
                                 (self.pop[i][self.ID_POS][j] - self.pop[idx_selected][self.ID_POS][j])
                    is_corona_list[i] = True
                elif (1.0 / 3) * self.brr <= rand < (2.0 / 3) * self.brr:
                    idx_candidates = np.where(self.immunity_type_list == 0)  # Susceptible list
                    idx_selected = np.random.choice(idx_candidates[0])
                    pos_new[j] = self.pop[i][self.ID_POS][j] + np.random.uniform() * \
                                 (self.pop[i][self.ID_POS][j] - self.pop[idx_selected][self.ID_POS][j])
                elif (2.0 / 3) * self.brr <= rand < self.brr:
                    idx_candidates = np.where(self.immunity_type_list == 2)  # Immunity list
                    fit_list = np.array([self.pop[item][self.ID_FIT][self.ID_TAR] for item in idx_candidates[0]])
                    idx_selected = idx_candidates[0][np.argmin(fit_list)]  # Found the index of best fitness
                    pos_new[j] = self.pop[i][self.ID_POS][j] + np.random.uniform() * \
                                 (self.pop[i][self.ID_POS][j] - self.pop[idx_selected][self.ID_POS][j])
            if self.finished:
                break
            pop_new.append([pos_new, None])
        pop_new = self.update_fitness_population(pop_new)

        for idx in range(0, self.pop_size):
            # Step 4: Update herd immunity population
            if self.compare_agent(pop_new[idx], self.pop[idx]):
                self.pop[idx] = pop_new[idx].copy()
            else:
                self.age_list[idx] += 1

            ## Calculate immunity mean of population
            fit_list = np.array([item[self.ID_FIT][self.ID_TAR] for item in self.pop])
            delta_fx = np.mean(fit_list)
            if (self.compare_agent(pop_new[idx], [None, [delta_fx, None]])) and (self.immunity_type_list[idx]==0) and is_corona_list[idx]:
                self.immunity_type_list[idx] = 1
                self.age_list[idx] = 1
            if (self.compare_agent([None, [delta_fx, None]], pop_new[idx])) and (self.immunity_type_list[idx] == 1):
                self.immunity_type_list[idx] = 2
                self.age_list[idx] = 0
            # Step 5: Fatality condition
            if (self.age_list[idx] >= self.max_age) and (self.immunity_type_list[idx] == 1):
                self.pop[idx] = self.create_solution()
                self.immunity_type_list[idx] = 0
                self.age_list[idx] = 0


class BaseCHIO(OriginalCHIO):
    """
        My version of: Coronavirus Herd Immunity Optimization (CHIO)
            (Coronavirus herd immunity Optimization)
        Noted:
            changed:
    """

    def __init__(self, problem, epoch=10000, pop_size=100, brr=0.06, max_age=150, **kwargs):
        """
        Args:
            problem ():
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
            brr (float): Basic reproduction rate, default=0.06
            max_age (int): Maximum infected cases age, default=150
            **kwargs ():
        """
        super().__init__(problem, epoch, pop_size, brr, max_age, **kwargs)

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        pop_new = []
        is_corona_list = [False, ] * self.pop_size
        for i in range(0, self.pop_size):
            pos_new = self.pop[i][self.ID_POS].copy()
            for j in range(0, self.problem.n_dims):
                rand = np.random.uniform()
                if rand < (1.0 / 3) * self.brr:
                    idx_candidates = np.where(self.immunity_type_list == 1)  # Infected list
                    if idx_candidates[0].size == 0:
                        rand_choice = np.random.choice(range(0, self.pop_size), int(0.33 * self.pop_size), replace=False)
                        self.immunity_type_list[rand_choice] = 1
                        idx_candidates = np.where(self.immunity_type_list == 1)
                    idx_selected = np.random.choice(idx_candidates[0])
                    pos_new[j] = self.pop[i][self.ID_POS][j] + np.random.uniform() * \
                                 (self.pop[i][self.ID_POS][j] - self.pop[idx_selected][self.ID_POS][j])
                    is_corona_list[i] = True
                elif (1.0 / 3) * self.brr <= rand < (2.0 / 3) * self.brr:
                    idx_candidates = np.where(self.immunity_type_list == 0)  # Susceptible list
                    if idx_candidates[0].size == 0:
                        rand_choice = np.random.choice(range(0, self.pop_size), int(0.33 * self.pop_size), replace=False)
                        self.immunity_type_list[rand_choice] = 0
                        idx_candidates = np.where(self.immunity_type_list == 0)
                    idx_selected = np.random.choice(idx_candidates[0])
                    pos_new[j] = self.pop[i][self.ID_POS][j] + np.random.uniform() * \
                                 (self.pop[i][self.ID_POS][j] - self.pop[idx_selected][self.ID_POS][j])
                elif (2.0 / 3) * self.brr <= rand < self.brr:
                    idx_candidates = np.where(self.immunity_type_list == 2)  # Immunity list
                    fit_list = np.array([self.pop[item][self.ID_FIT][self.ID_TAR] for item in idx_candidates[0]])
                    idx_selected = idx_candidates[0][np.argmin(fit_list)]  # Found the index of best fitness
                    pos_new[j] = self.pop[i][self.ID_POS][j] + np.random.uniform() * \
                                 (self.pop[i][self.ID_POS][j] - self.pop[idx_selected][self.ID_POS][j])
            if self.finished:
                break
            pop_new.append([pos_new, None])
        pop_new = self.update_fitness_population(pop_new)

        for idx in range(0, self.pop_size):
            # Step 4: Update herd immunity population
            if self.compare_agent(pop_new[idx], self.pop[idx]):
                self.pop[idx] = pop_new[idx].copy()
            else:
                self.age_list[idx] += 1

            ## Calculate immunity mean of population
            fit_list = np.array([item[self.ID_FIT][self.ID_TAR] for item in self.pop])
            delta_fx = np.mean(fit_list)
            if (self.compare_agent(pop_new[idx], [None, [delta_fx, None]])) and (self.immunity_type_list[idx] == 0) and is_corona_list[idx]:
                self.immunity_type_list[idx] = 1
                self.age_list[idx] = 1
            if (self.compare_agent([None, [delta_fx, None]], pop_new[idx])) and (self.immunity_type_list[idx] == 1):
                self.immunity_type_list[idx] = 2
                self.age_list[idx] = 0
            # Step 5: Fatality condition
            if (self.age_list[idx] >= self.max_age) and (self.immunity_type_list[idx] == 1):
                self.pop[idx] = self.create_solution()
                self.immunity_type_list[idx] = 0
                self.age_list[idx] = 0
