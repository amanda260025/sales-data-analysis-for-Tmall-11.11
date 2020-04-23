# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 17:24:13 2020

@author: Administrator
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource

'''
(1)导入数据
'''

import os
os.chdir('C:\\Users\\Administrator\\Desktop')
df=pd.read_excel('双十一淘宝美妆数据.xlsx',sheetname=0)
df.fillna(0,inplace=True)
df.index=df['update_time']
df['date']=df.index.day
#加载数据，提取销售日期


'''
(2)针对每个商品，评估其打折情况
'''
data2=df[['id','title','店名','date','price']]#筛选数据
data2['period']=pd.cut(data2['date'],[4,10,11,14],labels=['双十一前',
'双十一当天','双十一过后'])

#查看数据是否有波动
price=data2[['id','price','period']].groupby(by=('id','price')).min()
#只能用min才能筛选出'双十一前'的字符串
price.reset_index(inplace=True)
id_count=price['id'].value_counts()

id_type1=id_count[id_count==1].index
id_type2=id_count[id_count!=1].index
#筛选出打折与不打折商品数量

'''
(3)计算打折商品的折扣率
'''

result3_data1 = data2[['id','price','period','店名']].groupby(['id','period']).min()
result3_data1.reset_index(inplace=True)
#筛选数据

result3_before11=result3_data1[result3_data1['period']=='双十一前']
result3_at11=result3_data1[result3_data1['period']=='双十一当天']
result3_data2=pd.merge(result3_at11,result3_before11,on='id')
#合并数据
result3_data2['zkl']=result3_data2['price_x']/result3_data2['price_y']
#计算折扣率

bokeh_data=result3_data2[['id','zkl']].dropna()

bokeh_data['zkl_range']=pd.cut(bokeh_data['zkl'],bins=np.linspace(0,1,21))

bokeh_data2=bokeh_data.groupby('zkl_range').count().iloc[:-1]

bokeh_data2['zkl_pre']=bokeh_data2['zkl']/bokeh_data2['zkl'].sum()
#计算折扣区间占比

from bokeh.models import HoverTool
output_file('project8_pic2.html')
source1=ColumnDataSource(bokeh_data2)
bokeh_data2.index.name='x_range'
bokeh_data2.index =bokeh_data2.index.astype(np.str)#将index转换为字符串型
lst_zkl=bokeh_data2.index.tolist()
hover=HoverTool(tooltips=[('折扣率','@zkl')])
p=figure(x_range=lst_zkl,plot_width=900,plot_height=350,title='商品折扣率统计',
         tools=[hover,'reset, xwheel_zoom,pan,crosshair'])
p.line(x='x_range',y='zkl_pre',source=source1,line_color='black',line_dash=[10,4])
p.circle(x='x_range',y='zkl_pre',source=source1,size=8,color='red',alpha=0.7)
#show(p)

'''
(3)按照品牌分析，不同品牌的打折力度
'''
from bokeh.transform import jitter
brands=result3_data2['店名_x'].dropna().unique().tolist()
bokeh_data3=result3_data2[['id','zkl','店名_x']].dropna()
bokeh_data3=bokeh_data3[bokeh_data3['zkl']<0.96]

source2=ColumnDataSource(bokeh_data3)

output_file('project08_pic3.html')
p2=figure(y_range=brands,plot_width=900,plot_height=700,title='不同品牌的折扣情况',
         tools=[hover,'box_select,reset, xwheel_zoom,pan,crosshair'])
p2.circle(x='zkl',y=jitter('店名_x',width=0.7,range=p2.y_range),
          source=source2,alpha=0.3)

show(p2)

