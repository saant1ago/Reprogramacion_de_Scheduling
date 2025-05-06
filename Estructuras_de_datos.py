import streamlit as st
import numpy as np
import pandas as pd

pedidos = pd.read_csv('pedidos.csv')
pedidos.set_index('id_pedido',inplace=True)
pedidos['Hora pedido'] = pd.to_datetime(pedidos['Hora pedido'], format='%H:%M').dt.time

df=pd.read_csv('df.csv')
df.set_index('id_pedido',inplace=True)
formato_horas = '%H:%M'
columnas_a_convertir = ['Inicio', 'Fin', 'Inicio.1', 'Fin.1']
id_count = len(df)
for columna in columnas_a_convertir:
    df[columna] = pd.to_datetime(df[columna], format=formato_horas).dt.time

rates=pd.read_csv('rates.csv')
rates=rates.set_index('Máquinas')

st.header('Estructuras de Datos')

with st.expander('Schedule Inicial'):
    st.dataframe(df)

with st.expander('Pedidos'):
    st.dataframe(pedidos)

with st.expander('Rates de Máquinas'):
    st.dataframe(rates)