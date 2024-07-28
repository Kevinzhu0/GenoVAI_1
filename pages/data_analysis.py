from dash import callback
import dash
from dash import dcc, html, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import os
import base64
import time
from langchain_core.messages import HumanMessage
import plotly.graph_objects as go
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv

dash.register_page(__name__, path='/', name='Home')  # '/' is home page

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
chat_model = ChatOpenAI(model="gpt-4o", max_tokens=256)

visualization_options = [
    {'label': 'Age Distribution at Initial Diagnosis', 'value': 'age_dist'},
    {'label': 'Vital Status vs. Age', 'value': 'vital_status_vs_age'},
    {'label': 'Age at Initial Diagnosis vs. Mutation Type and Vital Status', 'value': 'mutation_vs_age_vs_status'},
    {'label': 'Top 10 Mutation Type Distribution in BRCA Patients', 'value': 'mutation_type_dist'},
    {'label': 'Gene Mutation Frequency by Chromosome', 'value': 'mutation_by_chr'},
    {'label': 'Age at Initial Diagnosis by Gender', 'value': 'age_by_gender'},
    {'label': 'Number of Mutations per Gene', 'value': 'mutations_per_gene'},
    {'label': 'Number of Mutations per Patient', 'value': 'mutations_per_patient'}
]

layout = dbc.Container([
    html.Div(
        children=[
            html.H4("Data Visualization Analysis Overview"),
            html.P("""
                This page provides several visualizations to analyze cancer genomic data. Below are the available visualizations and their purposes:
                """),
            html.Ul([
                html.Li(
                    "Age Distribution at Initial Diagnosis: Shows the distribution of ages at the initial pathologic diagnosis."),
                html.Li(
                    "Vital Status vs. Age: Compares the vital status (alive or dead) against the age at initial pathologic diagnosis."),
                html.Li(
                    "Age at Initial Diagnosis vs. Mutation Type and Vital Status: Analyzes the age at initial diagnosis with mutation type and vital status."),
                html.Li(
                    "Top 10 Mutation Type Distribution in BRCA Patients: Displays the distribution of the top 10 mutation types in BRCA patients."),
                html.Li("Gene Mutation Frequency by Chromosome: Shows the frequency of gene mutations by chromosome."),
                html.Li("Age at Initial Diagnosis by Gender: Compares the age at initial diagnosis by gender."),
                html.Li("Number of Mutations per Gene: Shows the number of mutations per gene."),
                html.Li("Number of Mutations per Patient: Displays the number of mutations per patient."),
            ]),
            html.P("""
                If you would like to learn more insights related to the visualizations, you can click the "Insights" button below each graph.
                """)
        ],
        className='mt-3'
    ),
    dcc.Dropdown(
        id='visualization-dropdown',
        options=visualization_options,
        value=[option['value'] for option in visualization_options],
        multi=True,
        className='mt-3',
        style={'margin-bottom': '30px'}
    ),
    dcc.Dropdown(
        id='figures-per-row-dropdown',
        options=[{'label': '1', 'value': 1}, {'label': '2', 'value': 2}],
        value=2,
        multi=False,
        className='mt-3',
        style={'margin-bottom': '30px'}
    ),
    dbc.Row(id='visualization-data_analysis')
], fluid=True)


@callback(
    Output('visualization-data_analysis', 'children'),
    [Input('visualization-dropdown', 'value'),
     Input('figures-per-row-dropdown', 'value'),
     ],
    prevent_initial_call=False
)
def update_graphs(selected_vis, figures_per_row):
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

    if 'age_at_initial_pathologic_diagnosis' not in df.columns or 'vital_status' not in df.columns or 'One_Consequence' not in df.columns:
        return []

    figs = []
    for vis in selected_vis:
        if vis == 'age_dist':
            hist_fig = px.histogram(df, x='age_at_initial_pathologic_diagnosis', nbins=30,
                                    title='Age Distribution at Initial Pathologic Diagnosis')
            hist_fig.update_layout(xaxis_title='Age', yaxis_title='Frequency')
            figs.append(hist_fig)
        elif vis == 'vital_status_vs_age':
            box_fig = px.box(df, x='vital_status', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                             title='Vital Status vs. Age')
            box_fig.update_layout(xaxis_title='Vital Status', yaxis_title='Age at Initial Pathologic Diagnosis')
            figs.append(box_fig)
        elif vis == 'mutation_vs_age_vs_status':
            box_fig = px.box(df, x='One_Consequence', y='age_at_initial_pathologic_diagnosis', color='vital_status',
                             title='Age at Initial Diagnosis vs. Mutation Type and Vital Status')
            box_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Age at Initial Pathologic Diagnosis')
            figs.append(box_fig)
        elif vis == 'mutation_type_dist':
            mutation_type_counts = df['One_Consequence'].value_counts().head(10)
            bar_fig = px.bar(mutation_type_counts, x=mutation_type_counts.index, y=mutation_type_counts.values,
                             title='Top 10 Mutation Type Distribution in BRCA Patients')
            bar_fig.update_layout(xaxis_title='Mutation Type', yaxis_title='Count')
            figs.append(bar_fig)
        elif vis == 'mutation_by_chr':
            mutation_by_chr = df['Chromosome'].value_counts()
            bar_fig = px.bar(mutation_by_chr, x=mutation_by_chr.index, y=mutation_by_chr.values,
                             title='Gene Mutation Frequency by Chromosome')
            bar_fig.update_layout(xaxis_title='Chromosome', yaxis_title='Mutation Count')
            figs.append(bar_fig)
        elif vis == 'age_by_gender':
            box_fig = px.box(df, x='gender', y='age_at_initial_pathologic_diagnosis', color='gender',
                             title='Age at Initial Diagnosis by Gender')
            box_fig.update_layout(xaxis_title='Gender', yaxis_title='Age at Initial Pathologic Diagnosis')
            figs.append(box_fig)
        elif vis == 'mutations_per_gene':
            top_genes = df['Hugo_Symbol'].value_counts().head(20).index
            filtered_df = df[df['Hugo_Symbol'].isin(top_genes)]
            mutations_per_gene_fig = px.histogram(filtered_df, x='Hugo_Symbol', color='One_Consequence',
                                                  title='Number of Mutations per Gene', category_orders={
                    'One_Consequence': filtered_df['One_Consequence'].value_counts().index[:5].tolist()},
                                                  labels={'Hugo_Symbol': 'Gene', 'count': 'Mutation Count'},
                                                  barmode='stack')
            mutations_per_gene_fig.update_layout(xaxis_title='Gene', yaxis_title='Mutation Count')
            figs.append(mutations_per_gene_fig)
        elif vis == 'mutations_per_patient':
            mutations_per_patient = df['bcr_patient_barcode'].value_counts().head(10)
            max_value = mutations_per_patient.max()
            y_axis_max = max(10, max_value + 1)
            mutations_per_patient_fig = px.bar(mutations_per_patient, x=mutations_per_patient.index,
                                               y=mutations_per_patient.values,
                                               title='Number of Mutations per Patient')
            mutations_per_patient_fig.update_layout(xaxis_title='Patient', yaxis_title='Mutation Count',
                                                    yaxis=dict(range=[0, y_axis_max]), xaxis={'tickangle': 45})
            figs.append(mutations_per_patient_fig)

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


@callback(
    Output({'type': 'insight-content', 'index': dash.dependencies.ALL}, 'children'),
    Input({'type': 'insight-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State({'type': 'dynamic-graph', 'index': dash.dependencies.ALL}, 'figure'),
    prevent_initial_call=True
)
def graph_insights(n_clicks, figures):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [no_update] * len(figures)
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    index = eval(button_id)['index']
    if not n_clicks[index]:
        return [no_update] * len(figures)
    fig_object = go.Figure(figures[index])
    image_path = f"images/fig{index}.png"
    fig_object.write_image(image_path)
    time.sleep(2)

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    base64_image = encode_image(image_path)
    result = chat_model.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": "What data insight can we get from this graph"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "auto", },
                    },
                ]
            )
        ]
    )
    insights = result.content if result else "No insights available."
    output = [html.Div(insights) if i == index else no_update for i in range(len(figures))]
    return output
