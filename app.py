import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_auth

# BOOTSTRAP
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/custom.css'])
app.title = "GenoVAI"
auth = dash_auth.BasicAuth(
    app,
    {
        'test_app': 'smart_test',
        'user_login': 'login_pass'
    }
)

sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page["name"], className="ms-2", style={'white-space': 'normal', 'word-wrap': 'break-word'}),
            ],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className="bg-light",
    style={'width': '100%'}  # 确保 sidebar 本身宽度合适
)

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(html.Img(src=app.get_asset_url('GENOVAI Logo.png'), height='80px'), width="auto"),
        dbc.Col(html.H1("Cancer Genomic Data Visualization Tool", style={'fontSize': '18px', 'margin': '0'}), width=9),
    ], align="center", className="mb-4"),
    dbc.Row(
        [
            dbc.Col([
                sidebar
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, style={'position': 'fixed', 'height': '100vh', 'overflowY': 'auto'}
                # xs=4, sm=4, md=2, lg=2, xl=2, xxl=2,style={'position': 'fixed', 'height': '100vh', 'overflowY': 'auto'}
            ),
            dbc.Col(
                [
                    dash.page_container
                ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10, style={'margin-left': 'auto'})
            # xs=8, sm=8, md=10, lg=10, xl=10, xxl=10,, style={'margin-left': 'auto'}
            # Adjust margin to prevent content overlap
        ]
    )
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=False)


