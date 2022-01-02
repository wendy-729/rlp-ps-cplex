def newProjectData1(su,pred,choiceList,actNo,mandatory):
    new_pred=pred
    new_su=su
    for i in range(1,actNo-1):
        if i in mandatory:
            flag1=0
            # 紧前活动
            jinqian=pred[i]
            for j in jinqian:
                if j in choiceList:
                    flag1 += 1
                if flag1 == len(jinqian):
                    if i not in su[0]:
                        new_su[0].append(i)
                        new_pred[i].append(0)
                        break
                else:
                    continue
            # 如果紧后活动全部是可选活动，则将actNo-1加入i的紧后
            flag2=0
            jinhou=su[i]
            for j in jinhou:
                if j in choiceList:
                    flag2+=1
                if flag2==len(jinhou):
                    if actNo-1 not in jinhou:
                        new_su[i].append(actNo-1)
                        new_pred[actNo-1].append(i)
                        break
                else:
                    continue
    return new_su, new_pred