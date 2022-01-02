# 郑淋文
# 时间: 2021/12/19 21:05

from docplex.mp.model import Model
import numpy as np


def consturct_lagrangian_relaxation_u_kt(mu_kt,res,max_H,lftn,activities,cost,req,est_s,lst_s,duration,mandatory,ae,we,be,b,projPred,u_kt):
    M = lftn
    # 创建模型
    md1 = Model()
    # 资源种类
    k = [i for i in range(0, res)]
    h = [i for i in range(1, max_H + 1)]
    d = [i for i in range(0, lftn + 1)]

    act = [i for i in range(0, activities)]
    it = [(i, j) for i in act for j in d]
    kt = [(i, j) for i in k for j in d]
    # x_it = md1.continuous_var_dict(it, name='x')
    # y_kth = md1.continuous_var_cube(k, d, h, name='y')
    x_it = md1.binary_var_dict(it, name='x')
    z_kt = md1.integer_var_dict(kt, name='z')
    # y_kth = md1.binary_var_cube(k, d, h, name='y')

    # 目标函数
    md1.minimize(md1.sum(
        (mu_kt[kk, t]*md1.sum(req[i][kk] * x_it[i, tt] for i in list(range(1, activities)) for tt
        in list(range(max(est_s[i], t - duration[i] + 1), min(t, lst_s[i]) + 1))) for kk in k for t in d))+\
    md1.sum(cost[kk]* z_kt[kk, t]*z_kt[kk,t]-mu_kt[kk,t]*z_kt[kk,t] for kk in k for t in d))

    # 虚开始活动的开始时间为1
    md1.add_constraint(x_it[0, 0] == 1)

    # z_kt约束
    for kk in k:
        for t in d:
            md1.add_constraint(z_kt[kk, t] == round(mu_kt[kk, t] / (2 * cost[kk])))

    # 必须执行的活动
    md1.add_constraints(
        md1.sum(x_it[i, t] for t in list(range(est_s[i], lst_s[i] + 1))) == 1 for i in mandatory
    )

    # 触发可选活动集合
    for ii in ae:
        md1.add_constraint(
            md1.sum(x_it[i, t] for i in we[ae.index(ii)] for t in
                    list(range(est_s[i], lst_s[i] + 1))) ==
            md1.sum(x_it[ii, tt] for tt in list(range(est_s[ii], lst_s[ii] + 1))))

    # 依赖活动
    for a in be:
        for i in b[be.index(a)]:
            md1.add_constraint(
                md1.sum(x_it[i, t] for t in list(range(est_s[i], lst_s[i] + 1))) == \
                md1.sum(x_it[a, tt] for tt in list(range(est_s[a], lst_s[a] + 1))))

    # 优先关系
    for j in list(range(1, activities)):
        for i in projPred[j]:
            md1.add_constraint(
                md1.sum((t + duration[i]) * x_it[i, t] for t in
                        list(range(est_s[i], lst_s[i] + 1))) \
                <= md1.sum(
                    tt * x_it[j, tt] for tt in list(range(est_s[j], lst_s[j] + 1))) + \
                M * (1 - md1.sum(
                    x_it[j, tt] for tt in list(range(est_s[j], lst_s[j] + 1)))))




    # 时间参数设定
    md1.parameters.timelimit = 600
    solution = md1.solve()
    # 获取目标函数值
    d1 = md1.objective_value
    # 解的状态
    a = solution.solve_status
    # 计算时间
    cputime = solution.solve_details.time


    # x_it 的取值
    opt_x_it = np.zeros((activities, lftn+1))
    opt_z_kt = np.zeros((res,lftn+1))
    # opt_y_kth = np.zeros((res, lftn+1, max_H+1))

    # print(x_it)
    # 获取执行活动以及对应的开始时间
    x_it_value = solution.get_value_dict(x_it)
    z_kt_value = solution.get_value_dict(z_kt)
    # y_kth_value = solution.get_value_dict(y_kth)
    # print(y_kth_value)

    for key, value in x_it_value.items():
        if value == 1:
            opt_x_it[key[0],key[1]] = 1

    for key, value in z_kt_value.items():
        if value > 0:
            opt_z_kt[key[0],key[1]] = value

    act_time = []
    for key, value in x_it_value.items():
        if value == 1:
            act_time.append(key)
    # 进度计划
    schedule = [0 for x in range(0, activities)]
    # 执行活动
    vl = []
    for i in range(len(act_time)):
        vl.append(act_time[i][0])
        schedule[act_time[i][0]] = act_time[i][1]
    # 执行列表
    implement = [0]*activities
    for i in vl:
        implement[i] = 1





    return d1, opt_x_it, opt_z_kt,mu_kt, vl, schedule, implement





