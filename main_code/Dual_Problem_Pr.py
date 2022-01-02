import numpy as np

from main_code.Subproblem import consturct_lagrangian_relaxation
from main_code.Subproblem_pr import consturct_lagrangian_relaxation_Pr
from main_code.local_search import local_search
from main_code.updateRelation import update_Relation


class Main_Pr():
    def __init__(self,k,d,act,H):

        # 松弛优先关系的拉格朗日乘子
        self.lamd = []
        # 初始步长
        self.step_size = 2
        self.beta = 2
        self.max_non_improv = 5
        self.non_improv = 0
        # 梯度
        self.sg = np.zeros((k,d))
        # 迭代次数
        self.iter_time = 0
        self.best_ub = 10731
        self.best_lb = 0
        self.best_x_it = np.zeros((act,d))
        self.best_y_kth = np.zeros((k,d,H))
        self.subgradient_act_pred = []


    def solve_subgradient(self, max_iter,res, max_H, lftn, activities, cost,
                           req, est_s, lst_s,  duration, mandatory, ae, we, be, b, pred,
                           nrpr, nrsu, su, choiceList, resNo, u_kt
                          ):
        # 乘子初始化
        for i in list(range(1, activities)):
            temp = [2] * nrpr[i]
            self.lamd.append(temp)
        self.lamd.insert(0, [])
        # 次梯度初始化
        for i in list(range(1, activities)):
            temp = [0] * nrpr[i]
            self.subgradient_act_pred.append(temp)
        self.subgradient_act_pred.insert(0,[0])
        # print(nrpr[4])
        # print(self.subgradient_act_pred)

        while self.iter_time < max_iter or self.beta>0.01:
        # while self.iter_time < max_iter:
            iter = self.iter_time
            print('第', iter+1, '次迭代')

            # 子问题松弛优先关系
            opt_objvalue, opt_x_it, opt_y_kth, mu_kt, opt_vl, opt_schedule, opt_implement = consturct_lagrangian_relaxation_Pr(
                self.lamd, res, max_H, lftn, activities, cost,  req, est_s, lst_s,  duration, mandatory, ae, we, be, b, pred, nrpr,u_kt)
            # print(opt_objvalue)
            # print(opt_vl)
            # 更新下界
            if opt_objvalue > self.best_lb:
                self.best_lb = opt_objvalue
                self.lamd = mu_kt
                self.best_x_it = opt_x_it
                self.best_y_kth = opt_y_kth
                self.non_improv = 0
            else:
                self.non_improv += 1
            # 下界达到一定次数未更新
            if self.non_improv >= self.max_non_improv:
                self.beta /= 2
                self.non_improv = 0

            M = lftn
            # 更新次梯度
            for j in list(range(1, activities)):
                # 活动j的开始时间
                s_j = 0
                s_jj = 0
                for t in range(est_s[j],lst_s[j]+1):
                    s_j += t*opt_x_it[j,t]
                    s_jj += opt_x_it[j,t]
                for i in range(nrpr[j]):
                    jinqian = pred[j][i]
                    s_i = 0
                    for t in range(est_s[jinqian],lst_s[jinqian]):
                        s_i += (t+duration[jinqian])*opt_x_it[jinqian, t]
                self.subgradient_act_pred[j][i] = s_i-s_j-M*(1-s_jj)

            # 更新拉格朗日乘子
            for i in range(activities):
                for j in range(nrpr[i]):
                    # 保证乘子>=0
                    self.lamd[i][j] = max(0, self.lamd[i][j]+self.step_size*self.subgradient_act_pred[i][j])


            # 更新项目结构
            new_nr_pr, new_nr_su, new_pr, new_s = update_Relation(nrpr, nrsu, su, pred, choiceList, opt_implement, activities)

            # 满足原问题约束的可行解作为原问题的上界【根据执行的活动，进行局部改进，调整】
            best_schedule, current_ub = local_search(opt_schedule,new_nr_su, new_s, new_nr_pr, new_pr, activities, opt_implement, duration, lftn, cost, resNo,req,ae, we, be, b)
            # if current_ub < self.best_ub:
            #     self.best_ub = current_ub


            # 更新步长
            dist = 0
            for i in range(activities):
                for j in range(nrpr[i]):
                    dist += pow(self.subgradient_act_pred[i][j], 2)

            self.step_size = self.beta * (self.best_ub - self.best_lb) / dist

            self.iter_time += 1
            print('best_lb', self.best_lb)
            print('best_ub', self.best_ub)
            gap = (self.best_ub-self.best_lb)/self.best_lb
            print('gap', gap)
            print('-------------------------')
        gap = (self.best_ub - self.best_lb) / self.best_lb

        return self.best_lb, self.best_ub, gap
        # print('best_lb', self.best_lb)
        # print('best_ub', self.best_ub)
        # print('gap', gap)














