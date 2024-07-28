# data_exploration.py
from dash import dcc, html, callback, Input, Output, State, no_update
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
import dash_ag_grid as dag
import plotly.express as px

dash.register_page(__name__, name='Data Exploration')

layout = dbc.Container([
    html.H2("Data Exploration and Visualization"),
    html.P(
        "On this page, you can upload your dataset using the 'Drag and Drop or Select Files' feature below. "
        "Once uploaded, the data will be displayed in a table where you can explore it. "
        "You can then select features for the X and Y axes and choose a chart type to generate various visualizations. "
        "Click the 'Generate Visualization' button to create the visualization. The supported chart types include "
        "Scatter Plot, Box Plot, Heatmap, Bar Chart, Line Chart, Pie Chart, Scatter Matrix, Histogram, and Area Chart."
    ),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='exploration-data-preview'),
    html.Div(id='visualization-options'),
    html.Button('Generate Visualization', id='generate-visualization-button', n_clicks=0, className='btn btn-primary',
                style={'margin-top': '20px'}),
    dcc.Loading(
        html.Div(id='generated-visualization'),
        type='cube'
    )
], fluid=True)


@callback(
    Output('exploration-data-preview', 'children'),
    Output('visualization-options', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def preview_data(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            return html.Div(['There was an error processing this file.']), no_update

        feature_options = [{'label': col, 'value': col} for col in df.columns]

        return (
            html.Div([
                html.H5(filename),
                dag.AgGrid(
                    id='data-grid',
                    rowData=df.to_dict('records'),
                    columnDefs=[{'field': col} for col in df.columns],
                    defaultColDef={'filter': True, 'sortable': True, 'floatingFilter': True},
                    style={'height': '400px', 'width': '100%'}
                )
            ]),
            html.Div([
                html.Label('Select X-axis:'),
                dcc.Dropdown(id='x-axis-dropdown', options=feature_options, multi=False,
                             style={'margin-bottom': '10px'}),
                html.Label('Select Y-axis:'),
                dcc.Dropdown(id='y-axis-dropdown', options=feature_options, multi=False,
                             style={'margin-bottom': '10px'}),
                html.Label('Select Chart Type:'),
                dcc.Dropdown(id='chart-type-dropdown', options=[
                    {'label': 'Scatter Plot', 'value': 'scatter'},
                    {'label': 'Box Plot', 'value': 'box'},
                    {'label': 'Heatmap', 'value': 'heatmap'},
                    {'label': 'Bar Chart', 'value': 'bar'},
                    {'label': 'Line Chart', 'value': 'line'},
                    {'label': 'Pie Chart', 'value': 'pie'},
                    {'label': 'Scatter Matrix', 'value': 'scatter_matrix'},
                    {'label': 'Histogram', 'value': 'histogram'},
                    {'label': 'Area Chart', 'value': 'area'},
                ], multi=False, style={'margin-bottom': '10px'})
            ])
        )


@callback(
    Output('generated-visualization', 'children'),
    Input('generate-visualization-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('x-axis-dropdown', 'value'),
    State('y-axis-dropdown', 'value'),
    State('chart-type-dropdown', 'value'),
    prevent_initial_call=True
)
def generate_visualization(n_clicks, contents, filename, x_axis, y_axis, chart_type):
    if contents is not None and n_clicks > 0 and x_axis and y_axis and chart_type:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            return html.Div(['There was an error processing this file.'])

        if chart_type == 'scatter':
            fig = px.scatter(df, x=x_axis, y=y_axis)
        elif chart_type == 'box':
            fig = px.box(df, x=x_axis, y=y_axis)
        elif chart_type == 'heatmap':
            fig = px.density_heatmap(df, x=x_axis, y=y_axis)
        elif chart_type == 'bar':
            fig = px.bar(df, x=x_axis, y=y_axis)
        elif chart_type == 'line':
            fig = px.line(df, x=x_axis, y=y_axis)
        elif chart_type == 'pie':
            fig = px.pie(df, names=x_axis, values=y_axis)
        elif chart_type == 'scatter_matrix':
            fig = px.scatter_matrix(df, dimensions=[x_axis, y_axis])
        elif chart_type == 'histogram':
            fig = px.histogram(df, x=x_axis, y=y_axis)
        elif chart_type == 'area':
            fig = px.area(df, x=x_axis, y=y_axis)

        return dcc.Graph(figure=fig)

    return no_update
