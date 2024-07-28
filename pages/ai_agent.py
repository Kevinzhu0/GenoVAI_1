from dash import callback
import dash
from dash import dcc, html, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import re
import base64
import io
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.load import dumps, loads
import dash_ag_grid as dag
import os
from langchain_groq import ChatGroq
from dotenv import find_dotenv, load_dotenv

dash.register_page(__name__, name='AI_Agent')
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
model = ChatGroq(api_key=GROQ_API_KEY, model="llama3-70b-8192")

layout = dbc.Container([
    html.H2("Plotly AI for Creating Graphs & Insights"),
    html.Div(
        children=[
            html.P("""
                On this page, users can upload their dataset for visualization by using the drag and drop or select files feature.
                After uploading the dataset, enter your instructions in the textbox below and click the Submit button.
                After a short wait, the desired visualization, the corresponding Python implementation code, and related insights will appear below.
            """)
        ],
        className='mt-3'
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
        multiple=True
    ),
    html.Div(id="output-grid"),
    dcc.Textarea(id='user-request', style={'width': '50%', 'height': 50, 'margin-top': 20},
                 placeholder="Please insert some prompts into AI Chatbox to create visualizations"),
    html.Br(),
    html.Button('Submit', id='my-button',
                style={'background-color': '#007bff', 'color': 'white', 'border': 'none',
                       'padding': '10px 20px', 'text-align': 'center', 'text-decoration': 'none',
                       'display': 'inline-block', 'font-size': '16px', 'margin': '4px 2px',
                       'cursor': 'pointer', 'border-radius': '12px'}),
    dcc.Loading(
        [html.Div(id='my-figure', children=''), dcc.Markdown(id='content', children='')],
        type='cube'
    ),
], fluid=True)


@callback(
    Output('output-grid', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)



def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)]
        return children

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    return html.Div([
        html.H5(filename),
        dag.AgGrid(
            rowData=df.to_dict("records"),
            columnDefs=[{"field": i} for i in df.columns],
            defaultColDef={"filter": True, "sortable": True, "floatingFilter": True}
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),
        dcc.Store(id='stored-file-name', data=filename),
        dcc.Store(id="store-it", data=[]),
        html.Hr()
    ])

@callback(
    Output('my-figure', 'children'),
    Output('content', 'children'),
    Output("store-it", "data"),
    Input('my-button', 'n_clicks'),
    State('user-request', 'value'),
    State('stored-data', 'data'),
    State('stored-file-name', 'data'),
    State("store-it", "data"),
    prevent_initial_call=True
)
def create_graph(_, user_input, file_data, file_name, chat_history):
    df = pd.DataFrame(file_data)
    df_5_rows = df.head()
    csv_string = df_5_rows.to_string(index=False)
    if len(chat_history) > 0:
        chat_history = loads(chat_history)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You're a data visualization expert and you use your favourite graphing library Plotly only. Suppose, that the data is provided as a {name_of_file} file. Here are the first 5 rows of the data set: {data}. Follow the user's indications when creating the graph."),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
        ]
    )
    chain = prompt | model
    response = chain.invoke(
        {
            "input": user_input,
            "data": csv_string,
            "name_of_file": file_name,
            "chat_history": chat_history
        },
    )
    result_output = response.content
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=result_output))
    history = dumps(chat_history)
    print(history)  # print chat_history
    code_block_match = re.search(r'```(?:[Pp]ython)?(.*?)```', result_output, re.DOTALL)
    if code_block_match:
        code_block = code_block_match.group(1).strip()
        cleaned_code = re.sub(r'(?m)^\s*fig\.show\(\)\s*$', '', code_block)
        fig = get_fig_from_code(cleaned_code)
        return dcc.Graph(figure=fig), result_output, history
    else:
        return no_update, result_output, history





def get_fig_from_code(code):
    local_variables = {}
    exec(code, {}, local_variables)
    return local_variables['fig']
