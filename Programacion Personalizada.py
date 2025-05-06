import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import math
import random
import matplotlib.pyplot as plt
import plotly.express as px
import time as tm

## Funciones necesarias

def reprogamar(pedidos, rates, df, modificaciones):
  for pedido in modificaciones['agregados']:
      agregar_pedido(pedido.producto, pedido.cantidad, str(pedido.hora_pedido)[:5])

  for pedido in modificaciones['eliminados']:
      quitar_pedido(pedido)

  #ingresa pedidos en espacios disponibles y retorna los no acomodados
  df,no_acomodados = reprogramar_pedidos(df,pedidos,rates)

  if no_acomodados != []:
    df=quitar_y_poner(df,pedidos,rates,no_acomodados)

  return df

def time_a_timedelta(hora):
    fecha_base = datetime(2024, 11, 27)
    time_delta = datetime.combine(fecha_base, hora)
    return time_delta

def timedelta_a_time(hora):

    total_segundos = int(hora.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    tiempo_time = time(horas, minutos, segundos)

    return tiempo_time

def datetime_a_minutos(hora):
  hora = hora.hour * 3600 + hora.minute * 60
  return hora

def obtener_prioridades(Pedidos,Df,not_acomodados):

  df_scheduling = Df.copy()
  df_pedidos = Pedidos.copy()
  df_scheduling['Inicio']=df_scheduling['Inicio'].apply(time_a_timedelta)
  df_scheduling['Fin.1']=df_scheduling['Fin.1'].apply(time_a_timedelta)
  df_scheduling['Tiempo_total'] = df_scheduling['Fin.1'] - df_scheduling['Inicio']
  df_scheduling['Tiempo_total'] = df_scheduling['Tiempo_total'].apply(timedelta_a_time)
  df_scheduling['Tiempo_total'] = df_scheduling['Tiempo_total'].apply(datetime_a_minutos)


  df_pedidos = df_pedidos.drop(not_acomodados)
  df_prioridades = pd.merge(df_scheduling, df_pedidos, left_index=True, right_index=True)
  df_prioridades['Valor'] = df_prioridades['Cantidad']/df_prioridades['Tiempo_total']
  df_prioridades = df_prioridades.sort_values(by='Valor',ascending=False)
  prioridades = df_prioridades.index.tolist()
  valores = df_prioridades['Valor'].to_list()

  return prioridades,valores

def crear_fila_2(id,maquina,inicio,posible_final,tiempo_completar,quitar,valor,produccion):

  maquina_t=None

  if maquina == 's1':
    maquina_t = 't1'
  elif maquina == 's2':
    maquina_t = 't2'
  elif maquina == 's3':
    maquina_t = 't3'
  elif maquina == 's4':
    maquina_t = 't4'



  duracion = posible_final
  tiempo_completar = tiempo_completar + posible_final


  hora = (pd.Timestamp("1970-01-01") + pd.Timedelta(duracion)).time()
  tiempo_completar = (pd.Timestamp("1970-01-01") + pd.Timedelta(tiempo_completar)).time()

  indicador = True
  hora_ = timedelta(hours = hora.hour,minutes=hora.minute,seconds=hora.second)
  inicio_= timedelta(hours = inicio.hour,minutes=inicio.minute,seconds=inicio.second)
  
 
  denominador = hora_- inicio_
  total_segundos = int(denominador.total_seconds())
  minutos = total_segundos  // 60
  valor_reemplazo = produccion/minutos

  if valor_reemplazo > valor:
    df.loc[id] = [maquina,inicio,hora,maquina_t,hora,tiempo_completar]
    df.drop(quitar,inplace=True)
    pedidos.drop(quitar,inplace=True)
    indicador = True
    print(f'El pedido {id} fue reemplazado por {quitar}')
  else:
    print(f'El pedido {id} no es posible reemplazarse ya que el pedido {quitar} es mejor ({valor_reemplazo} < {valor})')
    indicador = False

  return indicador


def crear_fila(id,maquina,inicio,posible_final,tiempo_completar,acomodado):

  maquina_t=None

  if maquina == 's1':
    maquina_t = 't1'
  elif maquina == 's2':
    maquina_t = 't2'
  elif maquina == 's3':
    maquina_t = 't3'
  elif maquina == 's4':
    maquina_t = 't4'

  if not acomodado:

      duracion = posible_final
      tiempo_completar = tiempo_completar + posible_final


      hora = (pd.Timestamp("1970-01-01") + pd.Timedelta(duracion)).time()
      tiempo_completar = (pd.Timestamp("1970-01-01") + pd.Timedelta(tiempo_completar)).time()


      df.loc[id] = [maquina,inicio,hora,maquina_t,hora,tiempo_completar]


def quitar_pedido(id_pedido):
  df.drop(id_pedido,inplace=True)
  pedidos.drop(id_pedido, inplace=True)

def obtener_intervalos_libres(df):

  dict_libres = {}

  for maquina in df['Máquina ST'].unique():

      df_filtrado = df[df['Máquina ST'] == maquina]
      df_filtrado = df_filtrado.sort_values(by='Inicio')

      intervalos_libres_s= []
      intervalos_libres_t= []


      inicio_dia = datetime.strptime('07:00', '%H:%M').time()
      fin_dia = datetime.strptime('18:00', '%H:%M').time()

      if df_filtrado.iloc[0]['Inicio'] > inicio_dia:
        intervalos_libres_s.append((inicio_dia, df_filtrado.iloc[0]['Inicio']))
      if df_filtrado.iloc[0]['Inicio.1'] > inicio_dia:
        intervalos_libres_t.append((inicio_dia, df_filtrado.iloc[0]['Inicio.1']))


      for i in range(len(df_filtrado) - 1):

        fin_actual = df_filtrado.iloc[i]['Fin']
        inicio_siguiente = df_filtrado.iloc[i + 1]['Inicio']
        if inicio_siguiente > fin_actual:
            intervalos_libres_s.append((fin_actual, inicio_siguiente))

        fin_actual = df_filtrado.iloc[i]['Fin.1']
        inicio_siguiente = df_filtrado.iloc[i + 1]['Inicio.1']
        if inicio_siguiente > fin_actual:
            intervalos_libres_t.append((fin_actual, inicio_siguiente))

      if df_filtrado.iloc[-1]['Fin'] < fin_dia:
        intervalos_libres_s.append((df_filtrado.iloc[-1]['Fin'], fin_dia))

      if df_filtrado.iloc[-1]['Fin.1'] < fin_dia:
        intervalos_libres_t.append((df_filtrado.iloc[-1]['Fin.1'], fin_dia))

      dict_libres[maquina] = [intervalos_libres_s, intervalos_libres_t]

  return dict_libres

def reprogramar_pedidos(df,pedidos,rates):
  no_acomodados = []
  for id_pedido in pedidos.index:

    if id_pedido not in df.index:

      acomodado = False

      hora = pedidos.loc[id_pedido,'Hora pedido']
      producto = pedidos.loc[id_pedido,'Producto']
      cantidad = pedidos.loc[id_pedido,'Cantidad']

      dict_libres = obtener_intervalos_libres(df)

      posibles=[]

      for maquina in dict_libres.keys():
        if dict_libres[maquina][0] != []:
          for inicio,final in dict_libres[maquina][0]:
            if hora <= inicio:
              rate = rates.loc[maquina,str(producto)]
              time = cantidad/rate
              minutos,horas = math.modf(time)
              minutos = minutos*60
              tiempo_completar = timedelta(hours=horas, minutes=minutos)
              hr=inicio.hour
              mins = inicio.minute
              tiempo_inicio = timedelta(hours=hr, minutes=mins)

              posible_final = tiempo_inicio+tiempo_completar

              if posible_final <= timedelta(hours=final.hour, minutes=final.minute):



                for inicio_t,final_t in dict_libres[maquina][1]:
                  final_t = timedelta(hours=final_t.hour, minutes=final_t.minute)
                  inicio_t = timedelta(hours=inicio_t.hour, minutes=inicio_t.minute)

                  if posible_final <= final_t and posible_final>=inicio_t:


                    index_maquina_t = rates.index.get_loc(maquina)
                    maquina_t= int(index_maquina_t + (len(rates.index)/2))
                    rate = rates.iloc[maquina_t][str(producto)]
                    time = cantidad/rate
                    minutos,horas = math.modf(time)
                    minutos = minutos*60
                    tiempo_completar_t = timedelta(hours=horas, minutes=minutos)


                    if posible_final + tiempo_completar_t <= final_t:


                      crear_fila(id_pedido,maquina,inicio,posible_final,tiempo_completar_t,acomodado)
                      acomodado = True



      if acomodado == False:

        no_acomodados.append(id_pedido)
  return df,no_acomodados

def quitar_y_poner(df,pedidos,rates,no_acomodados):

  print(no_acomodados)
  prioridades,valores = obtener_prioridades(pedidos,df,no_acomodados)



  for id_pedido in no_acomodados: # Recorrer los no acomodados

    acomodado = False

    for prioridad,valor in zip(prioridades,valores): # Recorrer las prioridades

      temp_df = df.copy()
      temp_df = temp_df.drop(prioridad)

      hora = pedidos.loc[id_pedido,'Hora pedido']
      producto = pedidos.loc[id_pedido,'Producto']
      cantidad = pedidos.loc[id_pedido,'Cantidad']



      dict_libres = obtener_intervalos_libres(temp_df)

      posibles=[]

      for maquina in dict_libres.keys():
        if dict_libres[maquina][0] != []:
          for inicio,final in dict_libres[maquina][0]:
            if hora <= inicio:
              rate = rates.loc[maquina,str(producto)]
              time = cantidad/rate
              minutos,horas = math.modf(time)
              minutos = minutos*60
              tiempo_completar = timedelta(hours=horas, minutes=minutos)
              hr=inicio.hour
              mins = inicio.minute
              tiempo_inicio = timedelta(hours=hr, minutes=mins)

              posible_final = tiempo_inicio+tiempo_completar
              t1 = tiempo_completar - tiempo_inicio

              if posible_final <= timedelta(hours=final.hour, minutes=final.minute):
                for inicio_t,final_t in dict_libres[maquina][1]:
                  final_t = timedelta(hours=final_t.hour, minutes=final_t.minute)
                  inicio_t = timedelta(hours=inicio_t.hour, minutes=inicio_t.minute)

                  if posible_final <= final_t and posible_final>=inicio_t:

                    index_maquina_t = rates.index.get_loc(maquina)
                    maquina_t= int(index_maquina_t + (len(rates.index)/2))
                    rate = rates.iloc[maquina_t][str(producto)]
                    time = cantidad/rate
                    minutos,horas = math.modf(time)
                    minutos = minutos*60
                    tiempo_completar_t = timedelta(hours=horas, minutes=minutos)

                    if posible_final + tiempo_completar_t <= final_t:

                      if acomodado == False:

                        indicador = crear_fila_2(id_pedido,maquina,inicio,posible_final,tiempo_completar_t,prioridad,valor,producto)
                        acomodado = indicador
                        print(indicador)


                        if acomodado == True:
                          prioridades.remove(prioridad)


    if acomodado == False:
      print(f'El pedido {id_pedido} no pudo ser actualizado')
      pedidos.drop(id_pedido,inplace=True)

  return df


def agregar_pedido(producto,cantidad,hora):

  global id_count

  hora = pd.to_datetime(hora, format='%H:%M').time()
  id_nuevo  = id_count + 1
  pedidos.loc[id_nuevo] = [producto,cantidad,hora]
  id_count += 1

def generar_gantt(name):


  df = pd.read_csv(name, index_col=0)

  # Convertir tiempo a formato datetime para graficar
  df["Inicio"] = pd.to_datetime(df["Inicio"], format="%H:%M").apply(lambda t: datetime.combine(datetime.today(), t.time()))
  df["Fin"] = pd.to_datetime(df["Fin"], format="%H:%M").apply(lambda t: datetime.combine(datetime.today(), t.time()))
  df["Inicio.1"] = pd.to_datetime(df["Inicio.1"], format="%H:%M").apply(lambda t: datetime.combine(datetime.today(), t.time()))
  df["Fin.1"] = pd.to_datetime(df["Fin.1"], format="%H:%M").apply(lambda t: datetime.combine(datetime.today(), t.time()))

  # Extraer el índice como columna para usarlo como identificador de color
  df = df.reset_index().rename(columns={"index": "id_pedido"})

  # Agregar el id_pedido a ambas partes del DataFrame para mantener el color único
  df_st = df[["id_pedido", "Máquina ST", "Inicio", "Fin"]].rename(columns={"Máquina ST": "Máquina"})
  df_t = df[["id_pedido", "Maquina T", "Inicio.1", "Fin.1"]].rename(columns={"Maquina T": "Máquina", "Inicio.1": "Inicio", "Fin.1": "Fin"})

  # Combinar los datos
  df_plotly = pd.concat([df_st, df_t])
  highlight_colors = px.colors.qualitative.Bold 
  machine_order = ["s1", "s2", "s3", "s4", "t1", "t2", "t3", "t4"]

  # Crear gráfico de Gantt interactivo con color basado en id_pedido
  fig = px.timeline(
      df_plotly,
      x_start="Inicio",
      x_end="Fin",
      y="Máquina",
      color="id_pedido",  # Colores únicos por pedido
      title="Diagrama de Gantt de los Pedidos",
      labels={"Máquina": "Máquinas", "id_pedido": "Pedido"},
      color_discrete_sequence=highlight_colors,
      category_orders={"Máquina": machine_order}
  )

  # Mejorar diseño
  fig.update_layout(xaxis_title="Hora", yaxis_title="Máquinas", showlegend=True)

  # Exportar el gráfico a un archivo HTML
  return fig

def generar_gantt_2(df_):
  df = df_.copy()

  # Convertir tiempo a formato datetime para graficar
  df["Inicio"] = df["Inicio"].apply(lambda t: datetime.combine(datetime.today(), t))
  df["Fin"] = df["Fin"].apply(lambda t: datetime.combine(datetime.today(), t))
  df["Inicio.1"] = df["Inicio.1"].apply(lambda t: datetime.combine(datetime.today(), t))
  df["Fin.1"] = df["Fin.1"].apply(lambda t: datetime.combine(datetime.today(), t))

  # Extraer el índice como una columna
  df = df.reset_index().rename(columns={"index": "id_pedido"})

  # Agregar el id_pedido a ambas partes del DataFrame para mantener el color único
  df_st = df[["id_pedido", "Máquina ST", "Inicio", "Fin"]].rename(columns={"Máquina ST": "Máquina"})
  df_t = df[["id_pedido", "Maquina T", "Inicio.1", "Fin.1"]].rename(columns={"Maquina T": "Máquina", "Inicio.1": "Inicio", "Fin.1": "Fin"})

  # Combinar los datos
  df_plotly = pd.concat([df_st, df_t])

  highlight_colors = px.colors.qualitative.Bold  # Ejemplo de esquema con colores vibrantes

  machine_order = ["s1", "s2", "s3", "s4", "t1", "t2", "t3", "t4"]


  # Crear gráfico de Gantt interactivo con color basado en id_pedido
  fig = px.timeline(
      df_plotly,
      x_start="Inicio",
      x_end="Fin",
      y="Máquina",
      color="id_pedido",  # Colores únicos por pedido
      title="Diagrama de Gantt De los Pedidos",
      labels={"Máquina": "Máquinas", "id_pedido": "Pedido"},
      color_discrete_sequence=highlight_colors,
      category_orders={"Máquina": machine_order}
  )

  # Mejorar diseño
  fig.update_layout(xaxis_title="Hora", yaxis_title="Máquinas", showlegend=True)

  # Exportar el gráfico a un archivo HTML
  return fig
  

### -----------Terminan funciones necesarias-----------##
###-------------Clase de simulación------------###
rango_horas = [7,13]
num_productos = 3
rango_cantidad = [50, 401, 50]

class Pedido:
    def __init__(self, id, producto, cantidad, hora_pedido):
        self.id = id
        self.producto = producto
        self.cantidad = cantidad
        self.hora_pedido = hora_pedido

    def __str__(self):
        return f"Pedido {self.id}: {self.producto} ({self.cantidad} unidades) a las {self.hora_pedido} horas."

class GestorPedidos:
    #lista de objetos Pedido
    def __init__(self, pedidos):
        self.pedidos_originales = pedidos
        self.pedidos = pedidos
        self.next_id = max(pedido.id for pedido in pedidos) + 1 #Id para el siguiente pedido

    def agregar_pedidos(self, lam=2):

        # Agregar ´pedidos a la lista con una distribición de poisson

        n_nuevos = np.random.poisson(lam) #Numero de pedidos nuevos
        nuevos_pedidos = [] #lista con nuevos pedidos (contiene objetos de la clase Pedido)

        for _ in range(n_nuevos):
            producto = random.randint(1,num_productos)
            cantidad = random.randrange(*rango_cantidad)
            hora = time(np.random.randint(*rango_horas))
            nuevo_pedido = Pedido(self.next_id, producto, cantidad, hora)
            self.pedidos.append(nuevo_pedido)
            nuevos_pedidos.append(nuevo_pedido)
            self.next_id += 1

        return nuevos_pedidos

    def eliminar_pedidos(self, prob = 0.1):

        #eliminar pedidos con una pribabiulidad uniforme de 0.1

        num_pedidos_iniciales = len(self.pedidos)

        id_pedidos_eliminados = [] #lista con los ids de los pedidos eliminados

        pedidos_nuevos = [] # reinicio lista de pedidos

        for pedido in self.pedidos:
            if random.uniform(0,1) > prob: pedidos_nuevos.append(pedido)
            else: id_pedidos_eliminados.append(pedido.id)

        self.pedidos =  pedidos_nuevos

        num_pedidos_eliminados = num_pedidos_iniciales - len(self.pedidos)

        return id_pedidos_eliminados

    def simular_cambio(self, lam=2, prob=0.1):

        #simular una iteración en la que la lista de pedidos puede ser modificada al agregar o quitar pediodos con su respectiva dist. probabilidad

        eliminados = self.eliminar_pedidos(prob=prob)
        agregados = self.agregar_pedidos(lam=lam)


        return {"agregados": agregados, "eliminados": eliminados}


    def mostrar_pedidos(self):
        """
        Muestra la lista actual de pedidos.
        """
        for pedido in self.pedidos:
            print(pedido)


    def to_dataframe(self):
        """
        Exporta la lista actual de pedidos a un DataFrame de pandas.
        """
        data = [{
            "id_pedido": pedido.id,
            "producto": pedido.producto,
            "cantidad": pedido.cantidad,
            "hora_pedido": pedido.hora_pedido
        } for pedido in self.pedidos]
        return pd.DataFrame(data)

###_________Leer datos iniciales____________###



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

##-----Finaliza lectura de datos iniciales-------##
lamb = 2
proba = 0.2
##______Estructura de la página______####

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.title('Reprogramación Personalizada')
col1,col2 = st.columns(2)

with col1:
  st.subheader('Schedule inicial')
  st.dataframe(df)
  
with col2:
  st.subheader('Pedidos')
  pedidos = st.data_editor(pedidos,num_rows='dynamic',key='jeje',)
  pedidos['Producto'] = pedidos['Producto'].apply(lambda x: int(x))
  print(pedidos['Producto'])


st.subheader('Cronograma')
st.plotly_chart(generar_gantt('df.csv'))
produccion1 = pedidos['Cantidad'].sum()
st.write('La producción inicial es de:',str(produccion1))
st.button('¡Simular!',on_click=click_button)

if st.session_state.clicked == True:

    progress_text = "Simulación en progeso, por favor espere"
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        tm.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    tm.sleep(1)
    my_bar.empty()

    df,no_acomodados = reprogramar_pedidos(df,pedidos,rates)
    df=quitar_y_poner(df,pedidos,rates,no_acomodados)

    col1,col2 = st.columns(2)

    with col1:
        st.subheader('Schedule Reprogramado')
        st.dataframe(df)
    
    with col2:
        st.subheader('Pedidos Reprogramados')
        st.dataframe(pedidos,key='9')

    st.subheader('Cronograma Reprogramado')
    st.plotly_chart(generar_gantt_2(df),key='p')
    
    with st.expander('Comparación con cronograma inicial'):
       st.plotly_chart(generar_gantt('df.csv'),key='final_')
       
    produccion = pedidos['Cantidad'].sum()
    st.write('La producción total es de:',str(produccion))



