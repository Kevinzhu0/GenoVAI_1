# model_training.py
from dash import dcc, html, callback, Input, Output, State, no_update
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report

# dash.register_page(__name__, name='Model Training')

layout = dbc.Container([
    html.H2("Model Training and Prediction"),
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
    html.Div(id='model-data-preview'),
    html.Div(id='model-training-options'),
    html.Button('Train Model', id='train-model-button', n_clicks=0, className='btn btn-primary',
                style={'margin-top': '20px'}),
    html.Div(id='model-training-results')
], fluid=True)


@callback(
    Output('model-data-preview', 'children'),
    Output('model-training-options', 'children'),
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
                dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True)
            ]),
            html.Div([
                html.Label('Select Features for Training:'),
                dcc.Dropdown(id='feature-dropdown', options=feature_options, multi=True,
                             style={'margin-bottom': '10px'}),
                html.Label('Select Target Variable:'),
                dcc.Dropdown(id='target-dropdown', options=feature_options, multi=False,
                             style={'margin-bottom': '10px'}),
                html.Label('Select Model:'),
                dcc.Dropdown(id='model-dropdown', options=[
                    {'label': 'Logistic Regression', 'value': 'logistic_regression'},
                    {'label': 'Random Forest', 'value': 'random_forest'},
                    {'label': 'Support Vector Machine', 'value': 'svm'}
                ], multi=False, style={'margin-bottom': '10px'})
            ])
        )


@callback(
    Output('model-training-results', 'children'),
    Input('train-model-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('feature-dropdown', 'value'),
    State('target-dropdown', 'value'),
    State('model-dropdown', 'value'),
    prevent_initial_call=True
)
def train_model(n_clicks, contents, filename, selected_features, target, model_name):
    if contents is not None and n_clicks > 0 and selected_features and target and model_name:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            return html.Div(['There was an error processing this file.'])

        X = df[selected_features]
        y = df[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if model_name == 'logistic_regression':
            model = LogisticRegression()
        elif model_name == 'random_forest':
            model = RandomForestClassifier()
        elif model_name == 'svm':
            model = SVC()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)

        report_df = pd.DataFrame(report).transpose()

        return html.Div([
            html.H5("Model Training Results"),
            dbc.Table.from_dataframe(report_df, striped=True, bordered=True, hover=True)
        ])
