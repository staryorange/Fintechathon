# !-*- coding: utf-8 -*-
import sys
import json
import argparse
# from imp import reload
import numpy as np

import pandas as pd
import warnings

warnings.filterwarnings('ignore')
# reload(sys)

# sys.setdefaultencoding('utf-8')
ap = argparse.ArgumentParser()
ap.add_argument("-area", required=False,
                help="地区")
ap.add_argument("-subject", required=True,
                help="文理专业")
ap.add_argument("-score", required=True,
                help="分数")
ap.add_argument("-ranking", default=-1, required=False,
                help="排名情况 ")
args = vars(ap.parse_args())

# print("请输入科类，分数（如：理科，680）：")
# /Users/maywond/Documents/programme/nodejs/XMU_EXAM_ALL/script/
data_history = pd.read_csv('fujian.csv')
_area = str(args['area'])
_subject = str(args['subject'])
_score = int(args['score'])
_ranking = int(args['ranking'])

# -----------------预处理排名，获得分数排名
if _ranking == -1:
    searchTablePath = 'rank/' + _area + '_' + _subject + '.csv'
    searchTable = pd.read_csv(searchTablePath, encoding='ansi', engine='python')
    if _score >= searchTable['分数'][0]:
        _ranking = searchTable['排名'][0]
    elif _score <= searchTable['分数'][len(searchTable['分数']) - 1]:
        _ranking = searchTable['排名'][len(searchTable['分数']) - 1]
    else:
        _ranking = searchTable[searchTable['分数'] == _score]['排名'].values  # --根据一分一段表查询，待优化，暂未考虑表中没有的情况
    _ranking = int(_ranking)

print(_ranking)


##按排名计算算概率,后期修改
def rate(data):
    alpha = 1
    beta = 2
    gama = 1
    factor = ((float(data['最低位次']) - _ranking) * float(data['录取人数']) * alpha)
    factor = np.log1p(factor) if factor > 0 else -np.log1p(-factor)
    factor = factor ** beta if factor > 0 else -factor ** beta
    ans = 60 + (gama * factor / np.e)
    ans = ans if ans < 100 else 100
    ans = ans if ans > 0 else 0
    return float('%.2f' % ans)


def calrecommend(data):
    omga = 1
    return float(data['rate']) * float(data['最低分']) * float(data['录取人数']) * omga / 1000


def top_n(df, n=3, column='recommend'):
    return df.sort_values(by=column, ascending=False)[:n]

def recommend(data):
    data['recommend'] = data.apply(calrecommend, axis=1)
    lis = data.sort_values(by='recommend', ascending=False)
    group_mean = data[['大学名称', 'rate']].groupby('大学名称').mean().reset_index()
    lis = pd.merge(lis, group_mean, how='left')
    lis = lis.fillna(0)
    lis = lis[lis['recommend'] != 0]
    lis=lis[['大学名称','专业名称','rate','recommend']]
    lis = lis.groupby('大学名称').apply(top_n)
    lis=lis[['专业名称','rate']].reset_index()
    if lis.shape[0] >= 60:
        lis = lis[:60]
    return lis[['大学名称', '专业名称', 'rate']]


rank_rate = 0
if _ranking < 1000:
    rank_rate = 0.08
elif _ranking < 10000:
    rank_rate = 0.1
elif _ranking < 50000:
    rank_rate = 0.08
elif _ranking < 100000:
    rank_rate = 0.03
else:
    rank_rate = 0.01

data_history = data_history.loc[(data_history['科类'] == _subject)
                                & (data_history['最低位次'] < _ranking * (1 + rank_rate))
                                & (data_history['最低位次'] > _ranking * (1 - rank_rate))]
data_history = data_history[['大学名称', '批次', '专业名称', '最低位次', '最低分', '录取人数']]

# -----------本一线分数
success = 1
if (_subject == "理科") & _score > 220:
    if _score < 493:
        data_history = data_history.loc[(data_history['批次'] == "本二批") | (data_history['批次'] == "高职专科")]
    elif _score < 393:
        data_history = data_history.loc[(data_history['批次'] == "高职专科")]
elif (_subject == "文科") & _score > 220:
    if _score < 550:
        data_history = data_history.loc[(data_history['批次'] == "本二批") | (data_history['批次'] == "高职专科")]
    elif _score < 464:
        data_history = data_history.loc[(data_history['批次'] == "高职专科")]
else:
    success = 0
# -----------------------
# print(data_history)
data_history['rate'] = data_history.apply(rate, axis=1)

recommend_list = recommend(data_history)
print("推荐院校：")
print(recommend_list)

array = []
_obj = {}
# print(type(lis.values))
_array = recommend_list.values
for i in range(len(recommend_list)):
    obj = {"rate": ("%.2f" % _array[i][1]), 'school': _array[i][0]}  # , 'major': _array[i][1]}
    array.append(obj)
if len(array) > 0:
    _obj = {"success": 1, "array": array}
else:
    _obj = {'success': 0, "array": []}
print(json.dumps(_obj, ensure_ascii=False))
