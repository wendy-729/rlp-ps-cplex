import random
def change_al(schedule,nrsu, su, nrpr, pred, actNo, implement, duration, lftn, cost,resNo,req):
    # 生成活动列表
    al = [index for index, value in sorted(enumerate(schedule), key=lambda x: x[1])]
    # 改变活动列表
    for a in range(1, len(al)):
        i = al[a]
        if implement[i] == 1:
            for b in range(a+1, len(al)):
                j = al[b]
                if implement[j] == 1:
                    # i的紧后活动
                    if j not in su[i]:
                        al[a] = j
                        al[b] = i
                        break
    return al
def change_implement(ae,we,be,b, implement):
    new_implement = implement
    for i in range(len(ae)):
        act = ae[i]
        if new_implement[act]==1:
            index = random.randint(0, len(we[i])-1)
            while new_implement[we[i][index]]==1:
                index = random.randint(0, len(we[i])-1)
            new_implement[we[i][index]]=1
            for j in range(len(we[i])):
                if j != index:
                    new_implement[we[i][j]]=0

            # 更新依赖活动的状态
            for d in range(len(be)):
                if new_implement[be[d]]==1:
                    for dd in range(len(b[d])):
                        new_implement[b[d][dd]]=1
                else:
                    for dd in range(len(b[d])):
                        new_implement[b[d][dd]]=0
        else:
            # 以前触发但是现在未触发，即可选活动中有执行活动，但是该选择未触发
            if len(set(we[i]))!=0:
                for j in range(len(we[i])): 
                    new_implement[we[i][j]] = 0
                # 更新依赖活动
                for d in range(len(be)):
                    if new_implement[be[d]] == 1:
                        for dd in range(len(b[d])):
                            new_implement[b[d][dd]] = 1
                    else:
                        for dd in range(len(b[d])):
                            new_implement[b[d][dd]] = 0
    return new_implement



