def newProjectData1(su,pred,choiceList,actNo,mandatory):
    # new_projRelation=projRelation
    # new_nrpr=nrpr
    # new_nrsu=nrsu
    new_pred=pred
    new_su=su
    for i in range(1,actNo-1):
        if i in mandatory:
            flag1=0
            # 紧前活动
            jinqian=pred[i]

            for j in jinqian:
                if j in choiceList:
                    flag1+=1
                if flag1==len(jinqian):
                    # print('s[0]',s[0])
                    if i not in su[0]:
                        # print('hh')
                        # new_projRelation[1,new_nrsu[1]+2]=i
                        # new_projRelation[1,1]+=1
                        # new_nrsu[0]+=1
                        new_su[0].append(i)
                        # new_nrpr[i]+=1
                        new_pred[i].append(0)
                        break
                else:
                    continue
            # 紧后活动
            flag2=0
            jinhou=su[i]
            for j in jinhou:
                if j in choiceList:
                    flag2+=1
                if flag2==len(jinhou):
                    if actNo-1 not in jinhou:
                        # new_projRelation[i,new_nrsu[i]+2]=actNo
                        # new_projRelation[i,1]+=1
                        # new_nrsu[i]+=1
                        new_su[i].append(actNo-1)
                        # new_nrpr[actNo-1]+=1
                        new_pred[actNo-1].append(i)
                        break
                else:
                    continue
    return new_su, new_pred