import dash
from dash import dcc, html,Input,Output ,State
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from lstm_model import lstm_prediction
import dash_bootstrap_components as dbc

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Roboto&display=swap"],
    meta_tags=[{'favicon.ico': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
)
app.title = "Stock GIKI"
server = app.server

# Helper function to create stock price visualization
def get_stock_price_fig(df):
    fig = px.line(df, x="Date", y=["Close", "Open"], title="Closing and Opening Price vs Date")
    return fig

# Helper function to create exponential moving average visualization
def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df, x="Date", y="EWA_20", title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import datetime as dt

# Initialize the app
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                # Sidebar
                dbc.Col(
                    [
                        html.Div(
                            "Stock GIKI",
                            className="display-4 text-white text-center py-3 bg-success",
                            style={"font-weight": "bold"},
                        ),
                        dbc.Form(
                            [
                                dbc.Label(
                                    "Input stock code:", className="text-white fw-semibold"
                                ),
                                dbc.Input(
                                    id="stock-code",
                                    type="text",
                                    placeholder="Enter stock code",
                                    className="mb-3",
                                ),
                                # Submit button commented out since it's not used
                            ]
                        ),
                        html.Div(
                            [
                                dbc.Label("Date Range (For Fetching Data):", className="text-white fw-semibold"),
                                dcc.DatePickerRange(
                                    id="date-picker-range",
                                    start_date=dt.datetime.now().strftime("%Y-%m-%d"),
                                    end_date=dt.datetime.now().strftime("%Y-%m-%d"),
                                    className="d-block mb-3",
                                ),
                                dbc.Label("Number of days (For Forecasting):", className="text-white fw-semibold"),
                                dbc.Input(
                                    id="num-days",
                                    type="number",
                                    placeholder="Enter number of days",
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "View Stock Data",
                                                id="stock-btn",
                                                color="warning",
                                                className="w-100 fw-bold",
                                            ),
                                            width=8,
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "View Stock Indicators",
                                                id="indicators-btn",
                                                color="info",
                                                className="w-100 fw-semibold",
                                            ),
                                            width=8,
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Predict Stock Price",
                                                id="forecast-btn",
                                                color="primary",
                                                className="w-100 fw-semibold",
                                            ),
                                            width=8,
                                        ),
                                    ],
                                    className="g-2 mb-3",
                                ),
                            ]
                        ),
                    ],
                    width=3,
                    className="bg-success vh-100 d-flex flex-column justify-content-between p-3",
                ),
                # Main Content Area
                dbc.Col(
                    [
                        html.Div(
                            id="content-container",
                            children=[
                                # Add a default content container that can be updated
                                html.Img(
                                    id="loading-image",
                                    src="https://images.unsplash.com/photo-1707761918029-1295034aa31e?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                                    style={
                                        "width": "100%",
                                        "height": "auto",
                                        "display": "block",
                                    },
                                ),
                            ],
                            className="content",
                        ),
                        # Add div containers for dynamic content
                        html.Div(id="graphs-content", className="content"),
                        html.Div(id="main-content", className="content"),
                        html.Div(id="forecast-content", className="content"),
                    ],
                    width=9,
                    className="bg-light",
                ),
            ]
        ),
    ],
)


# Callbacks
@app.callback(
    Output("content-container", "children"),
    [Input("stock-btn", "n_clicks"),
    Input("indicators-btn", "n_clicks"),
    Input("forecast-btn", "n_clicks")],
    prevent_initial_call=True,
)
def update_content(stock_click, indicators_click, forecast_click):
    # Replace the image with stock data or other content
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "stock-btn":
        return html.Div(
            id="graphs-content",
            className="content",
            children=html.H3("Stock Price Data Displayed Here!"),
        )
    elif button_id == "indicators-btn":
        return html.Div(
            id="main-content",
            className="content",
            children=html.H3("Indicators Data Displayed Here!"),
        )
    elif button_id == "forecast-btn":
        return html.Div(
            id="forecast-content",
            className="content",
            children=html.H3("Forecast Data Displayed Here! (Please Wait a bit)"),
        )



# Callbacks
@app.callback(
    [
        Output("graphs-content", "children"),
    ],
    [
        Input("stock-btn", "n_clicks"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    ],
    [State("stock-code", "value")],
)
def update_stock_visualizations(n, start_date, end_date, stock_code):
    if n is None or not stock_code:
        raise PreventUpdate

    df = yf.download(stock_code, start=start_date, end=end_date)
    df.reset_index(inplace=True)

    fig = get_stock_price_fig(df)
    candlestick_fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )])
    candlestick_fig.update_layout(title='Stock Price Movement', xaxis_rangeslider_visible=False)

    return [html.Div([
        dcc.Graph(figure=fig),
        dcc.Graph(figure=candlestick_fig),
    ])]

@app.callback(
    [Output("main-content", "children")],
    [Input("indicators-btn", "n_clicks")],
    [State("stock-code", "value"),
    State("date-picker-range", "start_date"),
    State("date-picker-range", "end_date")]
)
def update_indicators(n, stock_code, start_date, end_date):
    if n is None or not stock_code:
        raise PreventUpdate

    df = yf.download(stock_code, start=start_date, end=end_date)
    df.reset_index(inplace=True)

    fig = get_more(df)
    return [dcc.Graph(figure=fig)]

@app.callback(
    [Output("forecast-content", "children")],
    [Input("forecast-btn", "n_clicks")],
    [State("stock-code", "value"), State("num-days", "value")]
)
def update_forecast(n, stock_code, num_days):
    if n is None or not stock_code or not num_days:
        raise PreventUpdate

    try:
        num_days = int(num_days)
    except ValueError:
        return ["Please enter a valid number of days."]

    fig = lstm_prediction(stock_code, num_days)
    return [dcc.Graph(figure=fig)]

if __name__ == "__main__":
    app.run_server(debug=True)
