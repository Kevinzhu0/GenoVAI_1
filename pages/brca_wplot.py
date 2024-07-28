from dash import dcc, html, dash_table, Output, Input, callback
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import os
import plotly.express as px

dash.register_page(__name__, name='BRCA_wplot')
data_path = os.path.join(os.path.dirname(__file__), '../dataset/Cleaned_BRCA_Merged_Data_test.csv')
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    columns_to_display = ['Hugo_Symbol', 'One_Consequence', 'age_at_initial_pathologic_diagnosis', 'vital_status'] + \
                         [col for col in df.columns if col not in ['Unnamed: 0', 'Hugo_Symbol', 'One_Consequence',
                                                                   'age_at_initial_pathologic_diagnosis',
                                                                   'vital_status']]
    df = df[columns_to_display]
else:
    df = pd.DataFrame()

# 创建datatable tooltips工具提示数据
tooltips = []
for i in range(len(df)):
    tooltips.append({
        'Hugo_Symbol': {
            'value': f"Barcode: {df.loc[i, 'bcr_patient_barcode']}, Hugo_Symbol: {df.loc[i, 'Hugo_Symbol']},"
                     f"One_Consequence: {df.loc[i, 'One_Consequence']}, Age: {df.loc[i, 'age_at_initial_pathologic_diagnosis']},"
                     f"Vital Status: {df.loc[i, 'vital_status']}, Gender: {df.loc[i, 'gender']}",
            'type': 'markdown'
        }
    })

prediction_metrics_options = [
    {'label': 'a', 'value': 'A'},
    {'label': 'b', 'value': 'B'},
    {'label': 'c', 'value': 'C'},
    {'label': 'd', 'value': 'D'},
    {'label': 'e', 'value': 'E'},
    {'label': 'BRCA Gene Mutation Waterfall Plot', 'value': 'brca_waterfall'}
]

layout = dbc.Container([
    html.H2("BRCA Gene Mutation Analysis"),
    html.Div(
        children=[
            html.P("""
            You can use the filters in the BRCA_Mutational&Clinical_Merged_Dataset datatable below to select the Hugo_Symbol: gene name, One_Consequence: the ‘type’ of mutation, age_at_initial_pathologic_diagnosis, and other fields you want to display. The visualizations below will update accordingly.
            If you would like to learn more insights related to the visualizations, you can click the "Insights" button below each graph. 
        """)
        ],
        className='mt-3'
    ),
    html.Div(id='datatable-container', children=[
        html.Div(style={'height': '400px', 'overflowY': 'scroll'}, children=[
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[{"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns],
                data=df.to_dict('records'),
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                tooltip_data=tooltips,
                tooltip_duration=None,  # 保持工具提示一直可见
            ),
        ]),
        html.Div(id='datatable-interactivity-container')
    ]),
    dcc.Dropdown(
        id='visualization-dropdown',
        options=prediction_metrics_options,
        value=[option['value'] for option in prediction_metrics_options],
        multi=True,
        className='mt-3',
        style={'margin-bottom': '30px'}
    ),
    dcc.Dropdown(
        id='figures-per-row-dropdown',
        options=[{'label': '1', 'value': 1}, {'label': '2', 'value': 2}],
        value=1,
        multi=False,
        className='mt-3',
        style={'margin-bottom': '30px'}
    ),
    dbc.Row(id='visualization-brca_waterfall')
], fluid=True)


@callback(
    Output('visualization-brca_waterfall', 'children'),
    [Input('visualization-dropdown', 'value'),
     Input('figures-per-row-dropdown', 'value'),
     Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")
     ],
    prevent_initial_call=False
)
def update_graphs(selected_vis, figures_per_row, rows, derived_virtual_selected_rows):
    # data_path = os.path.join(os.path.dirname(__file__), '../dataset/Cleaned_BRCA_Merged_Data_test.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        columns_to_display = ['Hugo_Symbol', 'One_Consequence', 'age_at_initial_pathologic_diagnosis', 'vital_status'] + \
                             [col for col in df.columns if col not in ['Unnamed: 0', 'Hugo_Symbol', 'One_Consequence',
                                                                       'age_at_initial_pathologic_diagnosis',
                                                                       'vital_status']]
        df = df[columns_to_display]
    else:
        df = pd.DataFrame()

    if 'age_at_initial_pathologic_diagnosis' not in df.columns or 'vital_status' not in df.columns or 'One_Consequence' not in df.columns:
        return []

    figs = []
    for vis in selected_vis:
        if vis == 'brca_waterfall':
            if derived_virtual_selected_rows is None:
                derived_virtual_selected_rows = []
            dff = df if rows is None else pd.DataFrame(rows)
            top_genes = dff['Hugo_Symbol'].value_counts().head(20).index
            filtered_df = dff[dff['Hugo_Symbol'].isin(top_genes)]
            waterfall_data = filtered_df.groupby(['Hugo_Symbol', 'One_Consequence']).size().reset_index(
                name='Count')
            waterfall_fig = px.bar(waterfall_data, x='Hugo_Symbol', y='Count', color='One_Consequence',
                                   title='BRCA Gene Mutation Waterfall Plot')
            waterfall_fig.update_layout(xaxis_title='Gene', yaxis_title='Count')
            line_data = dff.groupby('age_at_initial_pathologic_diagnosis').size().reset_index(name='Mutation Count')
            line_fig = px.line(line_data, x='age_at_initial_pathologic_diagnosis', y='Mutation Count',
                               title='Mutation Count by Age at Initial Pathologic Diagnosis')
            line_fig.update_layout(xaxis_title='Age at Initial Pathologic Diagnosis', yaxis_title='Mutation Count')
            figs.append(waterfall_fig)
            figs.append(line_fig)

    rows = []
    for i in range(0, len(figs), figures_per_row):
        row = dbc.Row([
            dbc.Col([
                dcc.Graph(figure=figs[i], id={'type': 'dynamic-graph', 'index': i}),
                html.Button('Insights', id={'type': 'insight-btn', 'index': i},
                            style={'background-color': '#007bff', 'color': 'white', 'border': 'none',
                                   'padding': '5px 10px', 'text-align': 'center', 'text-decoration': 'none',
                                   'display': 'inline-block', 'font-size': '12px', 'margin': '4px 2px',
                                   'cursor': 'pointer', 'border-radius': '12px'}),
                html.Div(id={'type': 'insight-content', 'index': i}, style={'margin-top': '10px'})
            ], width=int(12 / figures_per_row)) if i < len(figs) else None,
            dbc.Col([
                dcc.Graph(figure=figs[i + 1], id={'type': 'dynamic-graph', 'index': i + 1}),
                html.Button('Insights', id={'type': 'insight-btn', 'index': i + 1},
                            style={'background-color': '#007bff', 'color': 'white', 'border': 'none',
                                   'padding': '5px 10px', 'text-align': 'center', 'text-decoration': 'none',
                                   'display': 'inline-block', 'font-size': '12px', 'margin': '4px 2px',
                                   'cursor': 'pointer', 'border-radius': '12px'}),
                html.Div(id={'type': 'insight-content', 'index': i + 1}, style={'margin-top': '10px'})
            ], width=int(12 / figures_per_row)) if i + 1 < len(figs) and figures_per_row > 1 else None
        ], className="mb-4")
        rows.append(row)
    return rows
