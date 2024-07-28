from dash import dcc, html
import dash
import dash_bootstrap_components as dbc

# dash.register_page(__name__, name='nlp')
layout = dbc.Container([
    html.Label('Select Visualization:', style={'margin-bottom': '15px'}),
    dcc.Dropdown(
        id='visualization-dropdown',
        value=[],  # 默认值为空
        multi=True,
        className='mt-3',
        style={'margin-bottom': '30px'}
    ),
    html.Label('Number of figures per row:', style={'margin-bottom': '15px'}),
    dcc.Dropdown(
        id='figures-per-row-dropdown',
        options=[{'label': '1', 'value': 1}, {'label': '2', 'value': 2}],
        value=1,
        multi=False,
        className='mt-3',
        style={'margin-bottom': '30px'}
    ),
    dbc.Row(id='visualization-nlp')
], fluid=True)
