import numpy as np
def objValue(implement,schedule,actNo,resNo,duration,req,deadline,c):

    u=np.zeros((resNo,deadline))
    # print(deadline)
    u_kt2=0
    for i in range(actNo):
        if implement[i]==1:
            for k in range(resNo):
                for t in range(schedule[i],schedule[i]+duration[i]):
                    u[k][t]+=req[i][k]


    for k in range(resNo):
        for t in range(deadline):
            u_kt2+=c[k]*u[k][t]*u[k][t]
    return u_kt2, u