import dash
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

lista_asistencias = pd.read_excel(
    "./dashboard/registro_asistencia_salon4.xlsx")
lista_oficial = pd.read_excel("./dashboard/Estudiantes.xlsx")


# ---------. Obtener dias totales de clases.


# Convertir la columna 'fecha_registro' al formato de fecha
lista_asistencias['fecha_registro'] = pd.to_datetime(
    lista_asistencias['fecha_registro'], dayfirst=True)

# Obtener el total de días de clase
total_dias_clase = lista_asistencias['fecha_registro'].dt.date.nunique()

# Imprimir el total de días de clase
print("Total de días de clase:", total_dias_clase)


# ---------------. Obtener cant de estuiantes inasistentes

# Crear una lista de estudiantes que registraron asistencia con el bot
frecuencia_asistencias = lista_asistencias['correo_estudiante'].value_counts()


cantidad_dias_registrados = len(lista_asistencias)

# Calcular la lista de inasistencias
inasistencias = lista_asistencias[~lista_asistencias['correo_estudiante'].isin(
    frecuencia_asistencias.index)]

# Calcular la cantidad de inasistencias
cantidad_inasistencias = len(inasistencias)

#print(lista_asistencias)

# Obtener estudiantes inasistentes y calcular porcentaje de asistencias e inasistencias mensuales
asistencias = []
inasistencias = {}

for mes in range(1, 13):  # Iterar sobre los meses del año
    asistieron = 0

    # Filtrar registros por mes y año
    registros_mes = lista_asistencias[(pd.to_datetime(lista_asistencias["fecha_registro"]).dt.month == mes) & (
        pd.to_datetime(lista_asistencias["fecha_registro"]).dt.year == 2023)]

    for _, estudiante in lista_oficial.iterrows():
        correo_estudiante = estudiante["correo_estudiante"]
        if correo_estudiante not in registros_mes["correo_estudiante"].values:
            if correo_estudiante in inasistencias:
                inasistencias[correo_estudiante] += 1
            else:
                inasistencias[correo_estudiante] = 1
        else:
            asistieron += 1

    asistencias.append(asistieron)

# Calcular porcentaje de asistencias e inasistencias mensuales
total_estudiantes = len(lista_oficial)
porcentaje_asistencias = [
    (asistencias[i] / total_estudiantes) * 100 for i in range(len(asistencias))]
porcentaje_inasistencias = [(inasistencias.get(estudiante, 0) / total_estudiantes)
                             * 100 for estudiante in lista_oficial["correo_estudiante"]]

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

paises = lista_asistencias["pais"].unique()


app = Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(
    className='container',
    children=[
        html.Header(
            className='header',
            children=[
                html.Link(
                    rel='stylesheet',
                    href='https://bootswatch.com/4/flatly/bootstrap.min.css'
                ),
                html.Div(className="Header", children=[
                    html.H1(children='Dashboard de asistencia', style={
                        'textAlign': 'center', 'marginTop': '50px'}),
                ])
            ]
        ),

        html.Div(
            children=[
                dcc.Graph(
                    figure=go.Figure(
                        data=[
                            go.Scatter(x=meses, y=porcentaje_asistencias,
                                       name="Asistencias"),
                            go.Scatter(x=meses, y=porcentaje_inasistencias,
                                       name="Inasistencias"),
                        ],
                        layout=go.Layout(
                            xaxis={"title": "Mes"},
                            yaxis={"title": "Porcentaje"},
                            title="Asistencias e Inasistencias Mensuales",
                            showlegend=True,
                        ),
                    )
                ),
            ]
        ),

        html.Label('Selecciona un país:'),
        dcc.Dropdown(
            id='dropdown-paises',
            options=[{'label': pais, 'value': pais} for pais in paises],
            value=paises[0]  # Valor inicial
        ),

        dbc.Row(
            children=[
                dbc.Col(
                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Bar(x=meses, y=porcentaje_asistencias, marker=dict(color='#84b6f4'))
                            ],
                            layout=go.Layout(
                                title='Asistencias mensuales',
                                xaxis=dict(title='Meses'),
                                yaxis=dict(title='Asistencia')
                            )
                        ),
                        style={'height': '350px', 'width': '100%'}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Bar(x=meses, y=porcentaje_inasistencias, marker=dict(color='#ff6961'))
                            ],
                            layout=go.Layout(
                                title='Inasistencias mensuales',
                                xaxis=dict(title='Meses'),
                                yaxis=dict(title='Inasistencia')
                            )
                        ),
                        style={'height': '350px', 'width': '100%'}
                    ),
                    width=6
                ),
            ],
            className='chart',
            style={'display': 'flex', 'marginTop': '30px'}
        ),

        dbc.Row(
            children=[
                dbc.Col(
                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Pie(
                                    labels=['Asistencias', 'Inasistencias'],
                                    values=[sum(porcentaje_asistencias), sum(porcentaje_inasistencias)],
                                    marker=dict(colors=['#77dd77', '#ff6961']),
                                    textinfo='label+percent',
                                    hoverinfo='none',
                                    textposition='outside'
                                )
                            ],
                            layout=go.Layout(
                                title='Porcentaje de Asistencias vs Inasistencias',
                                showlegend=False,
                            )
                        ),
                        style={'height': '350px'}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=go.Figure(
                            data=[
                                go.Histogram(
                                    x=lista_asistencias['salon'],
                                    nbinsx=10,
                                    marker=dict(color='#83072D')
                                )
                            ],
                            layout=go.Layout(
                                title='Asistenecia por salones',
                                xaxis=dict(title=''),
                                yaxis=dict(title='Frecuencia')
                            )
                        ),
                        style={'height': '350px'}
                    ),
                    width=6
                ),
            ],
            className='chart',
            style={'display': 'flex', 'justify-content': 'center'}
        )
    ]
)

@app.callback(
    Output('grafico-lineas', 'figure'),
    Input('dropdown-paises', 'value')
)

def actualizar_grafico(pais):
    datos_filtrados = lista_asistencias[lista_asistencias['pais'] == pais]
    
    figura = go.Figure(
        data=[
            go.Scatter(x=datos_filtrados['meses'], y=datos_filtrados['asistencias'],
                       name="Asistencias"),
            go.Scatter(x=datos_filtrados['meses'], y=datos_filtrados['inasistencias'],
                       name="Inasistencias"),
        ],
        layout=go.Layout(
            xaxis={"title": "Mes"},
            yaxis={"title": "Cantidad"},
            title=f"Asistencias e Inasistencias Mensuales - {pais}",
            showlegend=True,
        ),
    )
    
    return figura


if __name__ == '__main__':
    app.run_server(port=8080, debug = False)
