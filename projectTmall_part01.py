# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 15:47:34 2020

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
#工作路径

df=pd.read_excel('双十一淘宝美妆数据.xlsx',sheetname=0)
df.fillna(0,inplace=True)
df.index=df['update_time']
df['date']=df.index.day
#加载数据，提取销售日期

'''
(2)双十一当天在售的商品占比情况
'''
data1=df[['id','title','店名','date']]#筛选数据
d1=data1[['id','date']].groupby(by='id').agg(['min','max'])['date']#统计不同商品销售开始、结束日期
id_11=data1[data1['date']==11]['id']

d2=pd.DataFrame({'id':id_11,'双十一当天是否售卖':True})#筛选双十一当天售卖的商品id

id_date=pd.merge(d1,d2,left_index=True,right_on='id',how='left')
id_date.fillna(False,inplace=True)

m=len(d1)
m_11=len(id_11)
m_pre=m_11/m
print('双十一当天参与活动的商品为%i个，占比为%.2f%%'%(m_11,m_pre*100))  

'''
(3)商品销售节奏分类
'''
id_date['type']='待分类'
id_date['type'][(id_date['min']<11)&(id_date['max']>11)]='A'
id_date['type'][(id_date['min']<11)&(id_date['max']==11)]='B'
id_date['type'][(id_date['min']==11)&(id_date['max']>11)]='C'
id_date['type'][(id_date['min']==11)&(id_date['max']==11)]='D'
id_date['type'][id_date['双十一当天是否售卖']==False]='F'
id_date['type'][id_date['max']<11]='E'
id_date['type'][id_date['min']>11]='G'

result1=id_date['type'].value_counts()
result1=result1.loc[['A','B','C','D','E','F','G']]
#计算不同类别的商品数量

from bokeh.palettes import brewer

colori=brewer['Blues'][7]
plt.axis('equal')
plt.pie(result1,labels=result1.index,colors=colori,autopct='%.2f%%')

'''
(4)未参与双十一当天活动的商品去向如何
'''
id_not11=id_date[id_date['双十一当天是否售卖']==False]
date_not11=pd.merge(id_not11,df,on='id',how='left')
#找到双十一当天未参与活动的商品对应的原始数据

id_con1=id_date['id'][id_date['type']=='F'].values
#筛选出con1
data_con2=date_not11[['id','title','date']].groupby(by=['id','title']).count()
title_count=data_con2.reset_index()['id'].value_counts()
id_con2=title_count[title_count>1].index
#筛选出con2

data_con3=date_not11[date_not11['title'].str.contains('预售')]
id_con3=data_con3['id'].value_counts().index
#筛选出con3

print('未参与双十一当天活动商品中:%i个为暂时下架,%i个为重新上架,%i个为预售'%(len(id_con1),len(id_con2),len(id_con3)))


'''
(5)真正参与双十一当天活动商品及品牌情况
'''
data_11sale=id_11
id_11sale_final=np.hstack((data_11sale,id_con3))
result2_i=pd.DataFrame({'id':id_11sale_final})


x1=pd.DataFrame({'id':id_11})
x1_df=pd.merge(x1,df,on='id',how='left')
brand_11sale=x1_df.groupby('店名')['id'].count()
#不同品牌当天参与双十一活动的商品数量(按照id区别不同商品)


x2=pd.DataFrame({'id':id_con3})
x2_df=pd.merge(x2,df,on='id',how='left')
brand_presale=x2_df.groupby('店名')['id'].count()
#不同品牌预售的商品数量

result2_data=pd.DataFrame({'当天参与活动的商品数量':brand_11sale,
                           '预售商品数量':brand_presale})
result2_data['总量']=result2_data['当天参与活动的商品数量']+result2_data['预售商品数量']
result2_data.sort_values(by='总量',inplace=True,ascending=False)
#计算结果
'''
(6)堆叠图制作
'''
from bokeh.models import HoverTool
from bokeh.core.properties import value

lst_brand=result2_data.index.tolist()
lst_type=result2_data.columns.tolist()[:2]
colors=['red','green']

result2_data.index.name='brand'
result2_data.columns=['sale_on_11','presale','sum']#
#bokeh中columns和index的名字要改成英文
source=ColumnDataSource(data=result2_data)

hover=HoverTool(tooltips=[('品牌','@brand'),
                          ('双十一当天参与活动的商品数量','@sale_on_11'),
                          ('预售商品数量','@presale'),
                          ('真正参与双十一活动的商品总数','@sum')])
output_file('project08_pic1.html')
p=figure(x_range=lst_brand,plot_width=900,plot_height=350,title='各个品牌参与双十一活动的情况',
         tools=[hover,'reset,xwheel_zoom,pan,crosshair'])

p.vbar_stack(lst_type,x='brand',source=source,width=0.9,color=colors,alpha=0.7,
             legend=[value(x) for x in lst_type],
             muted_color='black',muted_alpha=0.2)
show(p)









