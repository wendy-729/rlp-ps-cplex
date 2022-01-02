# 郑淋文
# 时间: 2021/12/19 21:28

import numpy as np


from main_code.Subproblem import consturct_lagrangian_relaxation
from main_code.Subproblem_pr import consturct_lagrangian_relaxation_Pr
from main_code.Subproblem_u_kt import consturct_lagrangian_relaxation_u_kt
from main_code.change_implement import change_implement
from main_code.local_search import local_search
from main_code.updateRelation import update_Relation


class Main_u_kt():
    def __init__(self,k,d,act,H):
        # 松弛资源约束的拉格朗日乘子
        self.lamd = np.zeros((k, d))
        self.lamd += 4
        # 初始步长
        self.step_size = 2
        self.beta = 2
        self.max_non_improv = 5
        self.non_improv = 0
        # 梯度
        self.sg = np.zeros((k,d))
        # 迭代次数
        self.iter_time = 0
        self.best_ub = 1e10
        self.best_lb = 0
        self.best_x_it = np.zeros((act,d))
        self.best_z_kt = np.zeros((k,d,H))
        self.subgradient_kt = np.zeros((k,d))


    def solve_subgradient(self, max_iter,res, max_H, lftn, activities, cost,
                           req, est_s, lst_s,  duration, mandatory, ae, we, be, b, pred,
                           nrpr, nrsu, su, choiceList, resNo, u_kt
                          ):

        while self.beta > 0.0001 and self.iter_time < max_iter:
            iter = self.iter_time
            print('第', iter+1, '次迭代')

            # 求解子问题
            opt_objvalue, opt_x_it, opt_z_kt, mu_kt, opt_vl, opt_schedule, opt_implement = consturct_lagrangian_relaxation_u_kt(self.lamd, res, max_H, lftn, activities, cost,
                                                                            req, est_s, lst_s,
                                                                            duration, mandatory, ae, we, be, b,
                                                                    pred,u_kt)

            # 更新下界
            if opt_objvalue > self.best_lb:
                self.best_lb = opt_objvalue
                self.lamd = mu_kt
                self.best_x_it = opt_x_it
                self.best_z_kt = opt_z_kt
                self.non_improv = 0

            else:
                self.non_improv += 1
            # 下界达到一定次数未更新
            if self.non_improv >= self.max_non_improv:
                self.beta /= 2
                self.non_improv = 0
            # 更新次梯度
            for kk in range(res):
                for tt in range(lftn+1):
                    sum_u_kt = 0
                    for i in range(activities):
                        max_t = max(tt-est_s[i], tt - duration[i] + 1)
                        min_t = min(tt, lst_s[i])
                        for ttt in range(max_t, min_t+1):
                            sum_u_kt += req[i][kk]*opt_x_it[i,ttt]

                    self.subgradient_kt[kk,tt] = sum_u_kt-opt_z_kt[kk,tt]


            # 更新拉格朗日乘子
            for kk in range(res):
                for tt in range(lftn+1):
                    # 保证乘子>=0
                    self.lamd[kk, tt] = max(0, self.lamd[kk, tt]+self.step_size*self.subgradient_kt[kk,tt])
                    # # lamd有上界【出现负无穷】
                    # upper = 0
                    # for h in range(1, u_kt[kk,tt]+1):
                    #     upper += 2*(h-1)*cost[kk]
                    # # print(upper)
                    # if self.lamd[kk, tt]>upper:
                    #     if upper>0:
                    #         self.lamd[kk, tt]=upper
                    #     else:
                    #         self.lamd[kk, tt]=0
            # print(self.lamd)


            # 改变执行列表
            # opt_implement = change_implement(ae, we, be, b, opt_implement)
            # 更新项目结构
            new_nrpr, new_nrsu, new_pred, new_su = update_Relation(nrpr, nrsu, su, pred, choiceList, opt_implement, activities)
            # 满足原问题约束的可行解作为原问题的上界【根据执行的活动，进行局部改进，调整】
            best_schedule, current_ub = local_search(opt_schedule, new_nrsu, new_su, new_nrpr, new_pred, activities, opt_implement, duration, lftn, cost, resNo,req,ae, we, be, b)
            if current_ub < self.best_ub:
                self.best_ub = current_ub

            # 更新步长
            dist = 0
            for kk in range(res):
                for tt in range(lftn+1):
                    dist += pow(self.subgradient_kt[kk, tt], 2)
            # self.step_size = self.beta*(opt_objvalue-self.best_lb)/dist
            self.step_size = self.beta * (self.best_ub - self.best_lb) / dist

            self.iter_time += 1
            print('best_lb', self.best_lb)
            print('best_ub', self.best_ub)
            gap = (self.best_ub-self.best_lb)/self.best_lb
            print('gap', gap)
            print('-------------------------')
        gap = (self.best_ub - self.best_lb) / self.best_lb
        # print(self.beta)

        return self.best_lb, self.best_ub, gap
        # print('best_lb', self.best_lb)
        # print('best_ub', self.best_ub)
        # print('gap', gap)












