import requests as rq
from bs4 import BeautifulSoup as bs
from sklearn.cluster import KMeans as km
import numpy as np
import csv


def processing(url):
    r = rq.get(url, timeout=30)
    r.raise_for_status
    r.encoding = 'utf-8'
    h = r.text
    s = bs(h, 'html.parser')                                #爬下网页

    data = s.find_all('tr')                                   #获取所有大学信息
    au = []
    for tr in data:
        ltd = tr.find_all('td')                                 #获取单个大学信息
        if len(ltd) == 0:
            continue
        su = []
        for td in ltd:
            su.append(td.string)                            #将每个大学的具体信息存到su里
        au.append(su)                                        #将所有大学的信息存到au里
    return au



def get_u_name(url, k):
    au = processing(url)                                    #爬取并处理数据

    list0 = []
    for i in range(k):                                         #考虑排名榜上的前k个大学
        list0.append(au[i][1])                                 #返回前k个大学的排名为list
    return list0



def get_ranking(url):
    au = processing(url) 
    
    global list_u
    global dict_u
    for i in range(len(list_u)):
        for j in range(len(au)):
            if(list_u[i]==au[j][1]):                                     #如果大学名称相同
                dict_u[list_u[i]].append(j+1)                          #将此大学的某学科排名加入到字典中

                        
def save():
    global dict_u
    with open('test.csv', 'w', newline='') as csvfile:
        sw = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #打开csv文件并写入标题
        print("{:^15}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t".format("学校名称", "数学排名", "物理排名", "化学排名", "生物排名", "医学排名", "计算机排名", "电子工程排名"))
        sw.writerow(["{:^15}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t{:^10}\t".format("学校名称", "数学排名", "物理排名", "化学排名", "生物排名", "医学排名", "计算机排名", "电子工程排名")])
        for seq in dict_u.keys():
            #写入每个大学的排名
            sw.writerow(["{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t".format(seq, dict_u[seq][0], dict_u[seq][1], dict_u[seq][2], dict_u[seq][3], dict_u[seq][4], dict_u[seq][5], dict_u[seq][6])])
            print("{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t".format(seq, dict_u[seq][0], dict_u[seq][1], dict_u[seq][2], dict_u[seq][3], dict_u[seq][4], dict_u[seq][5], dict_u[seq][6]))

               
def cluster(nc):
    global list_u
    global dict_u
    clist = []
    for i in range(len(list_u)):
        clist.append(dict_u[list_u[i]])
    result = km(n_clusters=nc, max_iter=300, n_init=40, init='k-means++').fit_predict(np.array(clist))     #根据大学的不同学科情况进行聚类，聚类个数为nc个，最大迭代次数为300
    
    ny = [[] for i in range(nc)]                          #初始化数组
    for i in range(top_k):
        ny[result[i]].append(list_u[i])                   #按照类别将大学名称加入各类的list中
        
    for i in range(nc):                                     #输出各类的大学名称
        print(ny[i])

                
def correlation_matrix():
    nq = [[] for i in range(len(adict))]                 #初始化数组
    for seq in dict_u.keys():
        for i in range(len(nq)):
            nq[i].append(dict_u[seq][i])                 #提取字典中的数据存入list中，将原本的行数据存为列数据，将大学为单位的信息转为学科为单位的信息

    nq = np.array(nq)                                      #转为numpy矩阵，处理更方便
    ng = np.zeros((len(adict), len(adict)))           #初始化numpy矩阵

    for i in range(len(adict)):
        for j in range(len(adict)):
            ng[i][j] = np.dot(nq[i], nq[j].T)/((np.dot(nq[i], nq[i].T)*np.dot(nq[j], nq[j].T))**0.5)    #余弦计算

    print(np.round(ng, decimals=2))    #保留两位小数
    
    
    
def main():
    global adict
    global top_k
    global sub_r
    global list_u
    global dict_u
    global nc
    #爬取数据
    list_u = get_u_name(adict[sub_r], top_k)
    for i in range(len(list_u)):
        dict_u[list_u[i]] = []
    for j in adict.keys():
        get_ranking(adict[j])  #按照学科分别访问
        
    # 保存数据，csv
    save()
       
    #学校相似度分析，基于kmeans聚类分析
    cluster(nc)
    
    #学科相关性分析，基于余弦相似度计算
    correlation_matrix()
    
#参数设置
adict = {'数学':'http://www.zuihaodaxue.cn/subject-ranking/mathematics.html',
         '物理':'http://www.zuihaodaxue.cn/subject-ranking/physics.html',
         '化学':'http://www.zuihaodaxue.cn/subject-ranking/chemistry.html',
         '生物':'http://www.zuihaodaxue.cn/subject-ranking/biological-sciences.html',
         '医学':'http://www.zuihaodaxue.cn/subject-ranking/human-biological-sciences.html',
         '计算机':'http://www.zuihaodaxue.cn/subject-ranking/computer-science-engineering.html',
         '电子工程':'http://www.zuihaodaxue.cn/subject-ranking/electrical-electronic-engineering.html'}
top_k = 20                                                         #考虑前top20的大学
sub_r = '化学'                                                     #按化学学科排名
nc = 5                                                               #聚为5类
list_u = []
dict_u = {}


main()
    
