import streamlit as st
import altair as alt
st.set_page_config(layout="wide")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight') 
import seaborn as sns
import datetime
import re

pd.options.mode.chained_assignment = None

df = pd.read_csv('Transactions.csv', dtype=str)
temp = df['Date created'].str.split(' - ', expand=True)
df['Date'] = pd.to_datetime(temp[0], format='%d/%m/%Y')
df['Offer SKU'] = df['Offer SKU'].replace(['0004925700', '0004928100', '0004928200', '0004928800', '0004555700', '0004933600'], ['0005346800', '0005347000', '0005346900', '0005347100', '0005310300', '0005347200'])

style = pd.read_csv('Style Listing Stock.csv', dtype=str, skiprows=2)
style = style[~style['Style'].isna()]
style = style[style['Style'] != 'Style']
style = style[~style['Category'].isna()]
style = style[['Style', 'Category', 'Department']]

fe = pd.read_csv('Fashione EAN 04-02-26.csv', dtype=str)
fe['Offer SKU'] = fe['PLU']
fe = pd.merge(fe, style, on='Style', how='left')
fe['Size'] = fe['Size'].replace('6', '06')
fe['Size'] = fe['Size'].replace('8', '08')
fe = fe[['Offer SKU', 'Style', 'Colour', 'Size', 'Category']]
fe['Category'] = fe['Category'].fillna('OTHER')

today = datetime.datetime.now()
prev_year = today.year - 7
next_year = today.year
first_date = datetime.date(today.year-2, 1, 1)
last_date = datetime.date(today.year, today.month, today.day)

d = st.date_input(
    "Select dates",
    (),
    first_date,
    last_date,
    format="DD.MM.YYYY",
    key=101,
)

d2 = ()

if(len(d) > 1):
    df = df[(df['Date'] >= pd.to_datetime(d[0])) & (df['Date'] <= pd.to_datetime(d[1]))]


    df = df[['Offer SKU', 'Type', 'Quantity', 'Amount']]
    df = pd.merge(df, fe, on='Offer SKU', how='left')
    sales = df[df['Type'] == 'Order amount']
    sales.dropna(subset=['Quantity'], inplace=True)
    sales['Quantity'] = sales['Quantity'].astype(int)
    sales.rename(columns={'Quantity': 'Sales'}, inplace=True)
    refunds = df[df['Type'] == 'Order amount refund']
    refunds.dropna(subset=['Quantity'], inplace=True)
    refunds['Quantity'] = refunds['Quantity'].astype(int)
    refunds.rename(columns={'Quantity': 'Refunds'}, inplace=True)
    
    sales_final = sales.groupby('Style')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
    sales_colour = sales.groupby(['Style', 'Colour', 'Size'])['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
    sales_size = sales.groupby(['Style', 'Size'])['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)

    refunds_final = refunds.groupby('Style')['Refunds'].sum().reset_index().sort_values(by='Refunds', ascending=False)
    refunds_colour = refunds.groupby(['Style', 'Colour', 'Size'])['Refunds'].sum().reset_index().sort_values(by='Refunds', ascending=False)
    refunds_size = refunds.groupby(['Style', 'Size'])['Refunds'].sum().reset_index().sort_values(by='Refunds', ascending=False)

    df_final = pd.merge(sales_final, refunds_final, on='Style', how='outer')
    df_colour = pd.merge(sales_colour, refunds_colour, on=['Style', 'Colour', 'Size'], how='outer')
#    df_size = pd.merge(sales_size, refunds_size, on=['Style', 'Size'], how='outer')

    style_arr = df_final['Style'].unique().tolist()
    style_arr = np.sort(style_arr).tolist()
    style_arr = style_arr
    style_options = st.selectbox('Select a style', options=style_arr)
    
    if (style_options != ''):
        df_final = df_final[df_final['Style'] == style_options]
        df_colour = df_colour[df_colour['Style'] == style_options]
#        df_size = df_size[df_size['Style'] == style_options]

        col1, _ = st.columns(2)
        col2, _ = st.columns(2)
#        col3, _ = st.columns(2)

        col1.dataframe(df_final.reset_index(drop=True), use_container_width=True)
        col2.dataframe(df_colour.reset_index(drop=True), use_container_width=True)
#        col3.dataframe(df_size.reset_index(drop=True), use_container_width=True)