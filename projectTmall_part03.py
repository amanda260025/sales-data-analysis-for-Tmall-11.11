# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 11:12:55 2020

@author: Administrator
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool

'''
(1)数据计算
'''

data_zk=result3_data2[result3_data2['zkl']<0.95]# 删除未打折数据
result4_zkld=data_zk.groupby('店名_y')['zkl'].mean()#按照店名_y和店名_x的结果一样（同一个id下对应的店名一样）
#筛选出不同品牌的平均折扣情况

n_dz=data_zk['店名_y'].value_counts()
n_zs=result3_data2['店名_y'].value_counts()
result4_dzspbl=pd.DataFrame({'打折商品总数':n_dz,'商品总数':n_zs})

result4_dzspbl['参与打折商品比例']=result4_dzspbl['打折商品总数']/result4_dzspbl['商品总数']
result4_dzspbl.dropna(inplace=True)

result4_sum=result2_data.copy()
result4_data=pd.merge(pd.DataFrame(result4_zkld),result4_dzspbl,left_index=True,right_index=True,how='inner')

result4_data=pd.merge(result4_data,result4_sum,left_index=True,right_index=True,how='inner')

'''
(2)作图
'''

from bokeh.models.annotations import Span
from bokeh.models.annotations import Label
from bokeh.models.annotations import BoxAnnotation

bokeh_data5=result4_data[['zkl','sum','参与打折商品比例']]
bokeh_data5.columns=['zkl','amount','pre']#列名要改成全英文
bokeh_data5['size']=bokeh_data5['amount']*0.03
source3=ColumnDataSource(bokeh_data5)

x_mean=bokeh_data5['pre'].mean()
y_mean=bokeh_data5['zkl'].mean()

hover=HoverTool(tooltips=[('品牌','@index'),
                          ('折扣率','@zkl'),
                          ('商品总数','@amount'),
                          ('参与打折商品比例','@pre')])

output_file('project08_pic4.html')
p=figure(plot_width=900,plot_height=600,title='各个商品打折套路解析',
         tools=[hover,'box_select,reset,wheel_zoom,pan,crosshair'])

p.circle_x(x='pre',y='zkl',source=source3,size='size',fill_color='red',line_color='black',fill_alpha=0.6,line_dash=[8,3])


x=Span(location=x_mean,dimension='height',line_color='green',line_alpha=0.7)
y=Span(location=y_mean,dimension='width',line_color='green',line_alpha=0.7)
p.add_layout(x)
p.add_layout(y)

bg1=BoxAnnotation(bottom=y_mean,right=x_mean,fill_alpha=0.1,fill_color='olive')
label1=Label(x=0.1,y=0.8,text='少量少打折',text_font_size='10pt')
p.add_layout(bg1)
p.add_layout(label1)

bg2=BoxAnnotation(bottom=y_mean,left=x_mean,fill_alpha=0.1,fill_color='firebrick')
label2=Label(x=0.7,y=0.8,text='大量少打折',text_font_size='10pt')
p.add_layout(bg2)
p.add_layout(label2)

bg3=BoxAnnotation(top=y_mean,right=x_mean,fill_alpha=0.1,fill_color='firebrick')
label3=Label(x=0.1,y=0.55,text='少量大打折',text_font_size='10pt')
p.add_layout(bg3)
p.add_layout(label3)


bg4=BoxAnnotation(top=y_mean,left=x_mean,fill_alpha=0.1,fill_color='olive')
label4=Label(x=0.7,y=0.55,text='大量大打折',text_font_size='10pt')
p.add_layout(bg4)
p.add_layout(label4)

show(p)