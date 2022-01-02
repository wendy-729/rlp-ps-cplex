
import numpy as np
import csv


from pandas import DataFrame
from time import *
from docplex.mp.model import Model

# 设置线程数量
# sem=threading.Semaphore(1)
from main_code.backwardPass import backwardPass
from main_code.forwardPass import forwardPass
from main_code.initChoice import initChoice
from main_code.initCost import initCost
from main_code.initData import initData
from main_code.initfile import initfile
from main_code.newProjectData import newProjectData
from main_code.newProjectData1 import newProjectData1
from main_code.objValue import objValue

# 活动数量
act = [30]
M = 1e10
for actNumber in act:
    # 第几组数据
    for group in range(1, 2):
        # 第几个实例
        for project in range(3,4):

            # 写入实验结果的文件路径
            filename=r'C:\Users\ASUS\Desktop\Model_RCPSP_PS\J'+str(actNumber)+'\\'+'sch_rcpsp_ps.csv'

            with open(filename, 'a', newline='') as f:

                file = r'D:\研究生资料\RLP-PS汇总\实验数据集\PSPLIB\j' + str(actNumber) + '\\J' + str(
                    actNumber) + '_' + str(project) + '.RCP'
                # 初始化数据
                res, duration, su, pred, req, activities, provide_res = initData(file)
                # print(activities)
                # 处理紧前活动，从0开始编号
                projPred = []
                for i in range(1, len(pred)):
                    temp = pred[i]
                    temp = [i - 1 for i in temp]
                    projPred.append(temp)
                projPred.insert(0, [])
                # 紧后活动
                proSu = []
                for i in range(0, len(su)):
                    temp = su[i]
                    # print(temp)
                    temp1 = [j - 1 for j in temp]
                    proSu.append(temp1)
                # print('紧后活动集合', proSu)
                datafile = r'D:\研究生资料\RLP-PS汇总\实验数据集\J'
                # datafile = r'D:\研究生资料\RLP-PS汇总\示例'
                # 必须执行的活动
                # fp_mandatory=datafile+'\\mandatory\\'+ str(project) + '.txt'
                fp_mandatory = datafile + str(actNumber) + '\\' + str(
                    group) + '\\mandatory\\J' + str(actNumber) + '_' + str(project) + '.txt'

                mandatory = initfile(fp_mandatory)
                # 可选集合
                # fp_choice=datafile+'\\choice\\'  + str(project) + '.txt'
                fp_choice = datafile + str(actNumber) + '\\' + str(
                    group) + '\\choice\\J' + str(actNumber) + '_' + str(project) + '.txt'
                choice = initChoice(fp_choice)
                choice = np.array(choice)
                # print('可选集合', choice)

                # 所有可选活动
                # fp_choiceList=datafile+'\\choiceList\\' + str(project) + '.txt'
                fp_choiceList = datafile + str(actNumber) + '\\' + str(
                    group) + '\\choiceList\\J' + str(actNumber) + '_' + str(project) + '.txt'
                choiceList = initfile(fp_choiceList)
                # print(choiceList)

                # 依赖活动
                # fp_depend=datafile+'\\dependent\\'  + str(project) + '.txt'
                fp_depend = datafile + str(actNumber) + '\\' + str(
                    group) + '\\dependent\\J' + str(actNumber) + '_' + str(project) + '.txt'
                depend = initChoice(fp_depend)
                depend = np.array(depend)
                # print('依赖活动', depend)

                # 成本
                fp_cost = r'D:\研究生资料\RLP-PS汇总\实验数据集\cost.txt'
                Costs = initCost(fp_cost)
                cost = Costs[project - 1]


                # 触发活动
                ae = []
                for i in range(0, choice.shape[0]):
                    ae.append(choice[i][0])
                # print('触发活动', ae)

                # we 可选活动集合
                we = []
                for i in range(0, choice.shape[0]):
                    temp = choice[i][1:]
                    we.append(temp)
                # print('可选活动集合', we)

                # 触发依赖活动的可选活动
                be = []
                for i in range(0, depend.shape[0]):
                    be.append(depend[i][0])
                # print('触发依赖活动的可选活动', be)
                # 依赖活动
                b = []
                for i in range(0, depend.shape[0]):
                    temp = depend[i][1:]
                    b.append(temp)
                # print("依赖活动", b)
                # 考虑更新网络结构中的优先关系
                proSu, projPred = newProjectData1(proSu, projPred, choiceList, activities, mandatory)
                # print(projPred)

                # 考虑了所有活动的最早开始
                est_1, eft_1 = forwardPass(duration, su)
                lftn = est_1[activities - 1]
                # 最晚开始时间  考虑了所有活动
                lst_1, lft_1 = backwardPass(su, duration, lftn)
                data = {"est": est_1, "lst": lst_1}
                est_lst = DataFrame(data)
                est_lst['est'] = 0
                est_lst['lst'] = lftn
                # print(est_lst)
                # 创建模型
                md1 = Model()
                # 线程
                # md1.parameters.threads = 1
                # 资源种类
                k = [i for i in range(0, res)]
                d = [i for i in range(0, lftn + 1)]

                act = [i for i in range(0, activities)]
                it = [(i, j) for i in act for j in d]
                ik = [(i, j) for i in act for j in k]
                x_it = md1.binary_var_dict(it, name='x')
                # 目标函数
                md1.minimize(md1.sum(x_it[activities-1,t]*t for t in d))

                # 必须执行的活动
                md1.add_constraints(
                    md1.sum(x_it[i, t] for t in list(range(est_lst['est'][i], est_lst['lst'][i] + 1))) == 1 for i in
                    mandatory)

                # 触发可选活动集合
                for ii in ae:
                    md1.add_constraint(
                        md1.sum(x_it[i, t] for i in we[ae.index(ii)] for t in
                                list(range(est_lst['est'][i], est_lst['lst'][i] + 1))) ==
                        md1.sum(x_it[ii, tt] for tt in list(range(est_lst['est'][ii], est_lst['lst'][ii] + 1))))

                    # print('触发可选活动集合', ad)
                # 依赖活动
                for a in be:
                    for i in b[be.index(a)]:
                        md1.add_constraint(
                            md1.sum(x_it[i, t] for t in list(range(est_lst['est'][i], est_lst['lst'][i] + 1))) == \
                            md1.sum(x_it[a, tt] for tt in list(range(est_lst['est'][a], est_lst['lst'][a] + 1))))
                # 优先关系
                for j in list(range(1, activities)):
                    for i in projPred[j]:
                        md1.add_constraint(
                            md1.sum((t + duration[i]) * x_it[i, t] for t in
                                    list(range(est_lst['est'][i], est_lst['lst'][i] + 1))) \
                            <= md1.sum(
                                tt * x_it[j, tt] for tt in list(range(est_lst['est'][j], est_lst['lst'][j] + 1))) + \
                            M * (1 - md1.sum(
                                x_it[j, tt] for tt in list(range(est_lst['est'][j], est_lst['lst'][j] + 1)))))
                        # print('优先规则', pr)
                #  资源不能超过限制
                for kk in k:
                    for t in d:
                        md1.add_constraint(provide_res[kk] >=
                                           md1.sum(
                                               req[i][kk] * x_it[i, tt] for i in list(range(1, activities)) for tt
                                               in
                                               list(range(max(est_lst['est'][i], t - duration[i] + 1),
                                                          min(t, est_lst['lst'][i])+ 1) )
                                           ))

                # 所有活动的开始时间约束（避免一个活动的所有紧后活动都不执行，其开始时间等于截止日期
                for i in range(activities-1):
                    md1.add_constraint(md1.sum((t+duration[i]) * x_it[i,t] \
                                       for t in list(range(est_lst['est'][i],est_lst['lst'][i]+1))) <= md1.sum(x_it[activities-1,t]*t \
                                                                                            for t in list(range(est_lst['est'][activities-1]\
                                                                                                       ,est_lst['lst'][activities-1]+1))) )

                # 时间参数设定
                md1.parameters.timelimit = 600
                # cplex在长时间得到更好的可行解时，求解可行解优先而非最优性优先
                md1.parameters.emphasis.mip = 2
                md1.parameters.mip.display = 2
                md1.parameters.threads = 1

                solution = md1.solve()

                if solution==None:
                    continue

                # 获取目标函数值
                d1 = md1.objective_value
                print(d1)
                # 解的状态
                a = solution.solve_status

                # 计算时间
                cputime = solution.solve_details.time
                # 将实验结果写入文件
                results = str(project) + '\t' + str(d1) + '\t' + str(cputime) + '\t' + str(a.value)+'\t'
                # print(results)
                csv_results=[project, d1, cputime, a.value]
                # csv_results.append(project)
                # csv_results.append(d1)
                # csv_results.append(cputime)

                # 获取执行活动以及对应的开始时间
                x_it_value = solution.get_value_dict(x_it)
                act_time = []
                for key, value in x_it_value.items():
                    if value == 1:
                        act_time.append(key)
                # print(len(act_time))
                vl = []
                schedule = [0 for x in range(0, actNumber + 2)]
                for i in range(len(act_time)):
                    # print(i)
                    vl.append(act_time[i][0])
                    schedule[act_time[i][0]] = act_time[i][1]

                # print(schedule)

                # 计算资源占用量
                implement=[0]*activities
                for i in vl:
                    implement[i]=1
                # print(implement)
                objeactValue,u=objValue(implement, schedule, activities, res, duration, req, schedule[activities-1], cost)
                # print(objeactValue)
                results=results+str(objeactValue)
                csv_results.append(objeactValue)
                vl = [x + 1 for x in vl]
                # 执行列表
                for e in range(len(implement)):
                    results = results + str(implement[e]) + '\t'
                    csv_results.append(implement[e])
                # 进度计划
                for e in range(len(schedule)):
                    results = results + str(schedule[e]) + '\t'
                    csv_results.append(schedule[e])
                # 执行的活动
                for e in range(len(vl)):
                    results = results + str(vl[e]) + '\t'
                    csv_results.append(vl[e])

                results = results + '\n'

                # f.write(results)
                csv_writer = csv.writer(f)
                csv_writer.writerow(csv_results)
                # print(results)
                print(csv_results)
                print(project, 'is solved')
                del x_it, results, mandatory, choiceList, choice, depend, solution, cputime

