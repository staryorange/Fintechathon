import pandas as pd
import warnings
import numpy
warnings.filterwarnings('ignore')

print("请输入科类，省排名（如：理科，1000）：")

s=list(input().split('，'))
sub=str(s[0])
paiming=int(s[1])


##数据预处理
data=pd.read_csv('data/data_2018.csv',encoding='gbk')
##去除没有位次信息和录取人数的字段
data=data.drop(data[data['最低位次']=='-'].index)
data=data.drop(data[data['录取人数']=='-'].index)
data['录取人数']=data['录取人数'].map(int)
data['最低位次']=data['最低位次'].map(int)
##每个学校最低录取排名
school_weici=data.groupby('大学名称')['最低位次'].max().reset_index()


##通过浮动省排名，获取data。省排名服从高斯分布。
##全部为主观定义区间，均可调节，使结果更平滑。
def get_data(n):
    if n <= 50:
        return 0, 150
    if n <= 100:
        return 0, 300
    if n <= 500:
        return 0.7 * n, 1.3 * n
    if n <= 1500:
        return 0.8 * n, 1.2 * n
    if n <= 5000:
        return 0.9 * n, 1.1 * n
    if n <= 10000:
        return 0.95 * n, 1.05 * n
    if n <= 20000:
        return 0.975 * n, 1.025 * n
    if n <= 30000:
        return 0.99 * n, 1.01 * n
h, l, = get_data(paiming)
data1 = data[(data['最低位次'].map(int) >= h) & (data['最低位次'].map(int) <= l) & (data['科类'] == sub)]



##计算该分段各学校招生人数，经softMax作学校热门程度指标
def softmax1(x):
    return 1/(1+numpy.exp(-(x*15)))      ##10，超参，可调节，改变热门程度输出范围
data2=data1.groupby('大学名称')['录取人数'].sum().reset_index()
all_num=data2['录取人数'].sum()
data2['学校热度']=(data2['录取人数']/all_num).map(softmax1)*50  ##40  热门指标占比，可调节



##计算排名与学校最低录取分排名差，经softMax作为被录取概率
def softmax2(x):
    return 1/(1+numpy.exp(-(x*0.0001)))    ##0.001，重要超参，可调节，调节排名差差距
data3=pd.merge(data2,school_weici,on='大学名称',how='left')
data3['排名差']=data3['最低位次']-paiming
data3['成绩概率']=(data3['排名差'].map(softmax2))*50    ##成绩录取概率占比，可调节
data3=data3[['大学名称','排名差','最低位次','成绩概率']]


result=pd.merge(data2,data3,on='大学名称',how='inner')
result['总成绩']=result['学校热度']+result['成绩概率']
result=result.sort_values('总成绩',ascending=False)

#print(result.sort_values('总成绩',ascending=False))
print(result)