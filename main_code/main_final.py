'''
改了计算活动最晚开始时间的方法
'''
import numpy as np


from pandas import DataFrame
from time import *
from docplex.mp.model import Model

# 设置线程数量
# sem=threading.Semaphore(1)
from main_code.backward import backward_update
from main_code.backwardPass import backwardPass
from main_code.forward import forwardManda
from main_code.forwardPass import forwardPass
from main_code.initChoice import initChoice
from main_code.initCost import initCost
from main_code.initData import initData
from main_code.initfile import initfile
from main_code.newProjectData import newProjectData
from main_code.newProjectData1 import newProjectData1

dtimes = [1.0]
noact = [38, 45, 51, 61, 93, 104, 112, 132, 157]
# 活动数量
act = [60]
M = 1e10
for actNumber in act:
    # 第几组数据
    for group in range(1, 2):
        # 第几个实例
        for project in range(7, 8):
            for dtime in dtimes:
                begin_time = time()
                # 写入实验结果的文件路径
                filename = r'C:\Users\ASUS\Desktop\cplex_feasible'+'\\J' + str(actNumber)+'delete_precedence_lower_'+str(dtime)+'_'+'.txt'
                # 大修路径
                # filename = r'D:\研究生资料\RLP-PS汇总\第五次投稿-Annals of Operations Research\ANOR大修\CPLEX\J'+ str(actNumber) +'\\' + 'sch_rlp_vl_' + str(actNumber + 2) + '_dtime_' + str(dtime) + '.txt'

                with open(filename, 'a', newline='') as f:
                    file = r'D:\研究生资料\RLP-PS汇总\实验数据集\PSPLIB\j' + str(actNumber) + '\\J' + str(
                        actNumber) + '_' + str(project) + '.RCP'
                    # 初始化数据
                    res, duration, su, pred, req, activities, provide_res, nrpr, nrsu = initData(file)

                    # 处理紧前活动，从0开始编号
                    projPred = []
                    for i in range(1, len(pred)):
                        temp = pred[i]
                        temp = [i - 1 for i in temp]
                        projPred.append(temp)
                    projPred.insert(0, [])

                    # 紧后活动从0开始编号
                    proSu = []

                    for i in range(0, len(su)):
                        temp = su[i]
                        temp1 = [j - 1 for j in temp]
                        proSu.append(temp1)
                    # print('紧后活动集合', proSu)
                    datafile = r'D:\研究生资料\RLP-PS汇总\实验数据集\J'

                    # 必须执行的活动
                    fp_mandatory = datafile + str(actNumber) + '\\' + str(
                        group) + '\\mandatory\\J' + str(actNumber) + '_' + str(project) + '.txt'

                    mandatory = initfile(fp_mandatory)
                    # 可选集合
                    fp_choice = datafile + str(actNumber) + '\\' + str(
                        group) + '\\choice\\J' + str(actNumber) + '_' + str(project) + '.txt'
                    choice = initChoice(fp_choice)
                    choice = np.array(choice)

                    # 所有可选活动
                    fp_choiceList = datafile + str(actNumber) + '\\' + str(
                        group) + '\\choiceList\\J' + str(actNumber) + '_' + str(project) + '.txt'
                    choiceList = initfile(fp_choiceList)

                    # 依赖活动
                    fp_depend = datafile + str(actNumber) + '\\' + str(
                        group) + '\\dependent\\J' + str(actNumber) + '_' + str(project) + '.txt'
                    depend = initChoice(fp_depend)
                    depend = np.array(depend)

                    # 成本
                    fp_cost = r'D:\研究生资料\RLP-PS汇总\实验数据集\cost.txt'
                    Costs = initCost(fp_cost)
                    cost = Costs[project - 1]

                    # 触发活动
                    ae = []
                    for i in range(0, choice.shape[0]):
                        ae.append(choice[i][0])
                    # we 可选活动集合
                    we = []
                    for i in range(0, choice.shape[0]):
                        temp = choice[i][1:]
                        we.append(temp)

                    # 触发依赖活动的可选活动
                    be = []
                    for i in range(0, depend.shape[0]):
                        be.append(depend[i][0])

                    # 依赖活动
                    b = []
                    for i in range(0, depend.shape[0]):
                        temp = depend[i][1:]
                        b.append(temp)
                    # 考虑更新网络结构中的优先关系
                    proSu, projPred = newProjectData1(proSu, projPred, choiceList, activities, mandatory)

                    # 考虑了所有活动的最早开始
                    est_1, eft_1 = forwardPass(duration, su)
                    lftn = int(dtime * est_1[activities - 1])

                    # 最晚开始时间  考虑了所有活动
                    lst_1, lft_1 = backwardPass(su, duration, lftn)
                    est_s = [0]*activities
                    lst_s = [lftn - duration[i] for i in range(activities)]

                    # est_s, eft_s = forwardManda(duration, proSu, mandatory, activities, projPred)
                    # # 所有活动都执行
                    # lst_s, lft_s = backward_update(proSu, duration, lftn, activities, mandatory)

                    # 计算资源占用量  所有活动都执行
                    u_kt = np.zeros((res, lftn), dtype=int)
                    dur = list(map(lambda x: x[0] - x[1], zip(lft_1, est_1)))

                    for i in range(0, activities):
                        for k in range(0, res):
                            for t in range(est_1[i], est_1[i] + dur[i]):
                                u_kt[k][t] = u_kt[k][t] + req[i][k]
                    max_h = []
                    for i in range(0, res):
                        h = max(u_kt[i])
                        max_h.append(h)
                    # 最大资源占用量
                    max_H = max(max_h)

                    # 创建模型
                    md1 = Model()

                    # 资源种类
                    k = [i for i in range(0, res)]
                    h = [i for i in range(1, max_H + 1)]
                    d = [i for i in range(0, lftn + 1)]

                    act = [i for i in range(0, activities)]
                    it = [(i, j) for i in act for j in d]
                    ik = [(i, j) for i in act for j in k]

                    x_it = md1.binary_var_dict(it, name='x')
                    y_kth = md1.binary_var_cube(k, d, h, name='y')

                    # 目标函数
                    md1.minimize(md1.sum(
                        cost[k] * (2 * (h) - 1) * y_kth[k, t, h] for h in list(range(1, max_H + 1)) for k in
                        list(range(0, res)) for t in d))

                    # 虚开始活动的开始时间为1
                    md1.add_constraint(x_it[0, 0] == 1)

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

                    # 资源占用量
                    for kk in k:
                        for t in d:
                            md1.add_constraint(md1.sum(y_kth[kk, t, h] for h in list(range(1, max_H + 1))) ==
                                               md1.sum(
                                                   req[i][kk] * x_it[i, tt] for i in list(range(1, activities)) for tt
                                                   in
                                                   list(range(max(est_s[i], t - duration[i] + 1),
                                                              min(t, lst_s[i])+1)))
                                               )


                    # 时间参数设定
                    md1.parameters.timelimit = 600
                    # cplex在长时间得到更好的可行解时，求解可行解优先而非最优性优先
                    # md1.parameters.emphasis.mip = 2
                    # md1.parameters.mip.display = 2
                    # md1.parameters.threads = 1

                    solution = md1.solve()

                    # 获取目标函数值
                    d1 = md1.objective_value
                    # 解的状态
                    a = solution.solve_status
                    # 计算时间
                    cputime = solution.solve_details.time
                    # 将实验结果写入文件
                    results = str(project) + '\t' + str(d1) + '\t' + str(cputime) + '\t' + str(a.value)+'\t'
                    print(results)


                    # # 获取执行活动以及对应的开始时间
                    # x_it_value = solution.get_value_dict(x_it)
                    #
                    # act_time = []
                    # for key, value in x_it_value.items():
                    #     if value == 1:
                    #         act_time.append(key)
                    # # print(act_time)
                    #
                    # vl = []
                    # schedule = [0 for x in range(0, actNumber + 2)]
                    # for i in range(len(act_time)):
                    #     vl.append(act_time[i][0])
                    #     schedule[act_time[i][0]] = act_time[i][1]
                    # vl = [x + 1 for x in vl]
                    # # print(vl)
                    # # print(schedule)
                    # # print(len(vl))
                    # # print(len(schedule))
                    # # 分成两个文件写入
                    #
                    #
                    # # 进度计划重新写一个文件
                    # for e in range(len(schedule)):
                    #     results = results + str(schedule[e]) + '\t'
                    # # 执行的活动
                    # for e in range(len(vl)):
                    #     results = results + str(vl[e]) + '\t'
                    # results = results + '\n'
                    #
                    # print(results)
                    # f.write(results)
                    # print(project, 'is solved')
                    # del x_it, y_kth, results, mandatory, choiceList, choice, depend, solution, cputime

