import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load cleaned data
df = pd.read_csv('mobile_sales_clean.csv')

# App initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
def serve_layout():
    return dbc.Container([
        html.H1('Mobile Sales Dashboard', className='text-center mb-4'),
        dbc.Row([
            dbc.Col([
                html.Label('Select Year:'),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': y, 'value': y} for y in sorted(df['Year'].unique())],
                    value=sorted(df['Year'].unique())[0],
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label('Select Brand:'),
                dcc.Dropdown(
                    id='brand-dropdown',
                    options=[{'label': b, 'value': b} for b in sorted(df['Brand'].unique())] + [{'label': 'All', 'value': 'All'}],
                    value='All',
                    clearable=False
                )
            ], width=3),
        ], className='mb-4'),
        dbc.Row([
            dbc.Col(dcc.Graph(id='monthly-sales'), width=6),
            dbc.Col(dcc.Graph(id='top-models'), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='revenue-by-age'), width=6),
            dbc.Col(dcc.Graph(id='payment-methods'), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='geo-sales'), width=12),
        ]),
    ], fluid=True)

app.layout = serve_layout

# Callbacks
@app.callback(
    [Output('monthly-sales', 'figure'),
     Output('top-models', 'figure'),
     Output('revenue-by-age', 'figure'),
     Output('payment-methods', 'figure'),
     Output('geo-sales', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('brand-dropdown', 'value')]
)
def update_dashboard(selected_year, selected_brand):
    dff = df[df['Year'] == selected_year]
    if selected_brand != 'All':
        dff = dff[dff['Brand'] == selected_brand]

    # Monthly Sales
    monthly = dff.groupby('Month').agg({'TotalRevenue': 'sum', 'UnitsSold': 'sum'}).reset_index()
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=monthly['Month'], y=monthly['TotalRevenue'], name='Revenue'))
    fig_monthly.add_trace(go.Bar(x=monthly['Month'], y=monthly['UnitsSold'], name='Units Sold'))
    fig_monthly.update_layout(barmode='group', title='Monthly Revenue & Units Sold', xaxis_title='Month')

    # Top Models
    top_models = dff.groupby('MobileModel').agg({'UnitsSold': 'sum'}).sort_values('UnitsSold', ascending=False).head(10).reset_index()
    fig_models = px.bar(top_models, x='UnitsSold', y='MobileModel', orientation='h', title='Top 10 Mobile Models')

    # Revenue by Age Group
    if 'AgeGroup' in dff.columns:
        age_group = dff.groupby('AgeGroup').agg({'TotalRevenue': 'sum'}).reset_index()
        fig_age = px.bar(age_group, x='AgeGroup', y='TotalRevenue', title='Revenue by Age Group')
    else:
        fig_age = go.Figure()

    # Payment Methods
    payment = dff['PaymentMethod'].value_counts().reset_index()
    payment.columns = ['PaymentMethod', 'Count']
    fig_payment = px.pie(payment, names='PaymentMethod', values='Count', title='Payment Method Distribution')

    # Geo Sales (Top 10 Locations)
    if 'Location' in dff.columns:
        geo = dff['Location'].value_counts().head(10).reset_index()
        geo.columns = ['Location', 'Count']
        fig_geo = px.bar(geo, x='Location', y='Count', title='Top 10 Locations by Sales')
    else:
        fig_geo = go.Figure()

    return fig_monthly, fig_models, fig_age, fig_payment, fig_geo

if __name__ == '__main__':
    app.run(debug=True)
