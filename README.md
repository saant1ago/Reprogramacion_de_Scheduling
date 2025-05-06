# 🚀 Proyecto de Reprogramación de Pedidos con Streamlit

Este proyecto implementa una aplicación interactiva en **Streamlit** para visualizar, modificar y reprogramar pedidos en un entorno de producción. El objetivo es optimizar la asignación de pedidos a máquinas, considerando restricciones de tiempo, capacidad y prioridades.
## 💻 Funcionalidades principales

- Visualización de cronogramas y pedidos actuales
- Simulación de llegada y eliminación de pedidos con distribuciones de Poisson
- Reprogramación automática de pedidos según prioridades
- Generación de diagramas de Gantt interactivos usando **Plotly**
- Modificación manual de datos vía editores interactivos en Streamlit

## 🚀 Cómo ejecutar el proyecto

1. Clona este repositorio:
    ```bash
    git clone https://github.com/tu-usuario/nombre-del-repo.git
    cd nombre-del-repo
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3. Corre la aplicación:
    ```bash
    streamlit run app.py
    ```

4. Asegúrate de tener los archivos `pedidos.csv`, `df.csv` y `rates.csv` en el mismo directorio.

## 📦 Requisitos

- Python 3.x
- pandas
- numpy
- streamlit
- matplotlib
- plotly

## 🛠️ Estructura de las páginas

- `Estructuras_de_datos.py`: muestra datos base cargados.
- `Programacion Personalizada.py`: permite al usuario modificar manualmente pedidos y reprogramarlos.
- `Reprogramacion.py`: ejecuta simulaciones automáticas y ajusta la programación.

## Imágenes

<img width="547" alt="Image" src="https://github.com/user-attachments/assets/f8c657ac-5a8e-4207-bb60-b0936829cf05" />
<img width="547" alt="Image" src="https://github.com/user-attachments/assets/fc1577b1-5930-4aa5-884e-93a03f512c89" />
<img width="547" alt="Image" src="https://github.com/user-attachments/assets/098e9178-1a9d-46e9-a878-4167bdc99024" />

## 📄 Licencia

MIT

## 📬 Contacto

- Santiago Juárez Roaro  
