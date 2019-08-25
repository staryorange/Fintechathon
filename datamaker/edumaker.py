import numpy as np
import pandas as pd
import flask
import pyecharts.charts as charts

a=np.arange(100).reshape(100,1)
b=np.random.randint(0,10,[100,29])
data=np.concatenate((a,b),axis=1)

data=pd.DataFrame(data)
data.to_csv('edu.csv')
