import os
import io
import json
import base64
from urllib.parse import urlencode, unquote
from werkzeug.utils import secure_filename
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, session, make_response
import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px

"""
A web-based exploratory data analysis tool that allows users to upload a CSV or Excel file and visualize its contents using interactive charts and tables.

The app uses the Flask web framework and the Dash visualization library to provide a user-friendly interface. It allows users to filter data based on categorical and date columns and to aggregate numeric data by different categories. It also provides key performance indicators (KPIs) for the selected categories.

The app saves uploaded files as pickled data frames, which can be accessed and modified as needed.

This code defines the Flask server and Dash app for the exploratory data analysis tool. The Flask server handles file uploads and serves the Dash app, which provides the interactive data visualization.

Author: Fabio Carvalho
GitHub: github.com/hipnologo
""" 

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
DEBUG = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_dataframe(df):
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    
    cat_unique_values = {}
    for col in categorical_cols + date_cols:
        cat_unique_values[col] = df[col].unique().tolist()
    
    if DEBUG == True:
        print(f"numeric_cols: {numeric_cols}")  # Debugging
        print(f"categorical_cols: {categorical_cols}")  # Debugging
        print(f"date_cols: {date_cols}")  # Debugging
        print(f"cat_unique_values: {cat_unique_values}")  # Debugging

    return numeric_cols, categorical_cols, date_cols, cat_unique_values

def load_dataframe(session_id):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], f'df_{session_id}')
    pkl_files = [f for f in os.listdir(directory) if f.endswith('.pkl')]
    if pkl_files:
        df = pd.read_pickle(os.path.join(directory, pkl_files[0]))
        return df
    else:
        return None

# Initialize the Dash app with the Flask server
dash_app = dash.Dash(__name__, server=app, routes_pathname_prefix='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

dash_app.layout = lambda: serve_layout()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename.endswith('.csv'):
                df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename), engine='openpyxl')

            # Generate the session_id and save it in the Flask session
            session_id = base64.b64encode(os.urandom(32)).decode('utf-8')
            session['session_id'] = session_id
            
            # Create the directory if it doesn't exist
            directory = os.path.join(app.config['UPLOAD_FOLDER'], f'df_{session_id}')
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Save the pickled dataframe
            pd.to_pickle(df, os.path.join(directory, f'{filename}.pkl'))
            numeric_cols, categorical_cols, date_cols, cat_unique_values = process_dataframe(df)
            
            return redirect(url_for('dash_app_page', _external=True, _scheme='http', session_id=session_id,
                        numeric_cols=urlencode({'param': json.dumps(numeric_cols)})[6:],
                        categorical_cols=urlencode({'param': json.dumps(categorical_cols)})[6:],
                        date_cols=urlencode({'param': json.dumps(date_cols)})[6:],
                        cat_unique_values=urlencode({'param': json.dumps(cat_unique_values)})[6:]))

    return render_template('index.html')
    
@app.route('/dashboard/')
def dash_app_page():
    return dash_app.index()

# Define the Dash app layout
def serve_layout():
    session_id = session.get('session_id')
    if DEBUG == True:
        print(f"Session ID: {session_id}")  # Debugging
    if session_id is not None:
        session_id = unquote(session_id)

    if session_id is None:
        return html.Div('Invalid session ID. Please upload a file first.')

    # Load the dataset
    df = load_dataframe(session_id)

    # Process the DataFrame
    numeric_cols, categorical_cols, date_cols, cat_unique_values = process_dataframe(df)

    # Debugging
    if DEBUG == True:
        print(f"serve_layout - numeric_cols: {numeric_cols}")
        print(f"serve_layout - categorical_cols: {categorical_cols}")
        print(f"serve_layout - date_cols: {date_cols}")
        print(f"serve_layout - cat_unique_values: {cat_unique_values}")

    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='session-id', storage_type='memory', data=session_id),
        dcc.Store(id='numeric-cols', storage_type='memory', data=numeric_cols),
        dcc.Store(id='categorical-cols', storage_type='memory', data=categorical_cols),
        dcc.Store(id='date-cols', storage_type='memory', data=date_cols),
        dcc.Store(id='cat-unique-values', storage_type='memory', data=cat_unique_values),

        html.H1('Exploratory Data Analysis Tool'),
        html.Div(id='kpi-container'),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='categorical-column',
                    options=[{'label': col, 'value': col} for col in categorical_cols],
                    placeholder='Select a categorical column'
                ),
                dcc.Input(id='categorical-search', placeholder='Search values...', type='text', debounce=True),
                dcc.Dropdown(id='categorical-filter', multi=True, placeholder='Select values to filter'),
            ], className='col-md-4'),
            html.Div([
                dcc.Dropdown(
                    id='date-column',
                    options=[{'label': col, 'value': col} for col in date_cols],
                    placeholder='Select a date column'
                ),
                dcc.DatePickerRange(id='date-range-filter'),
            ], className='col-md-4'),
            html.Div([
                dcc.Dropdown(
                    id='aggregation-column',
                    options=[{'label': col, 'value': col} for col in numeric_cols],
                    placeholder='Select a column for aggregation'
                ),
            ], className='col-md-4'),
            html.Div([
                dcc.Dropdown(
                    id='x-axis-dropdown',
                    options=[{'label': col, 'value': col} for col in numeric_cols],
                    placeholder='Select a numeric column for x-axis'
                ),
                dcc.Dropdown(
                    id='y-axis-dropdown',
                    options=[{'label': col, 'value': col} for col in numeric_cols],
                    placeholder='Select a numeric column for y-axis'
                ),
            ], className='col-md-4'),
            dbc.Button("Export Data", id="export-button", color="primary"), # Export button
            dcc.Graph(id='chart'), # Show the chart
        ], className='row'),
        html.Br(),
        dash_table.DataTable(
            id='data-table',
            style_data={'whiteSpace': 'normal'},
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
            }],
            style_table={'overflowX': 'auto'},
            page_action='native',
            page_size=15,
        )
    ])

@dash_app.callback(
    Output('chart', 'figure'),
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('data-table', 'data'),
     Input('data-table', 'columns')])
def update_chart(x_axis_col, y_axis_col, data, columns):
    df = pd.DataFrame(data, columns=[col['id'] for col in columns])
    numeric_cols, categorical_cols, _, _ = process_dataframe(df)

    if x_axis_col in categorical_cols and y_axis_col in numeric_cols:
        fig = px.bar(df, x=x_axis_col, y=y_axis_col, title="Bar Chart")
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2f}")
    elif x_axis_col in numeric_cols and y_axis_col in numeric_cols:
        fig = px.scatter(df, x=x_axis_col, y=y_axis_col, title="Scatter Plot")
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.2f}")
    else:
        fig = {}
    return fig

@dash_app.callback(
    [Output('categorical-filter', 'options'),
     Output('categorical-filter', 'value')],
    [Input('categorical-column', 'value'),
     Input('categorical-search', 'value')],
    [State('cat-unique-values', 'data')])
def update_categorical_filter(selected_column, search_value, cat_unique_values):
    if DEBUG == True:
        print(f"selected_column: {selected_column}") # Debugging
        print(f"search_value: {search_value}") # Debugging
        print(f"cat_unique_values: {cat_unique_values}") # Debugging
        
    if selected_column is None:
        return [], []
    options = [{'label': value, 'value': value} for value in cat_unique_values[selected_column]
               if search_value.lower() in value.lower()]
    return options, []

@dash_app.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns'),
     Output('kpi-container', 'children')], 
    [Input('categorical-filter', 'value'),
     Input('date-range-filter', 'start_date'),
     Input('date-range-filter', 'end_date'),
     Input('aggregation-column', 'value'),
     Input('export-button', 'n_clicks')],
    [State('categorical-column', 'value'),
     State('date-column', 'value'),
     State('session-id', 'data')]) 
def update_data_table(cat_filter_values, start_date, end_date, n_clicks, agg_col, cat_col, date_col, session_id):
    df = load_dataframe(session_id)
    if DEBUG == True:
        print(f"df: {df.head()}") # Debugging
    if cat_col and cat_filter_values:
        df = df[df[cat_col].isin(cat_filter_values)]
    if date_col and start_date and end_date:
        df = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
    if agg_col:
        df = df.groupby([cat_col, date_col]).agg({agg_col: 'sum'}).reset_index()
    columns = [{'name': col, 'id': col} for col in df.columns]
    data = df.to_dict('records')
    kpi_container = []
    if cat_col:
        grouped = df.groupby(cat_col).sum()
        for col in df.select_dtypes(include=['number']).columns:
            kpi_container.append(html.Div([
                html.H4(f'Sum of {col} by {cat_col}'),
                dbc.Table.from_dataframe(grouped[col].reset_index(), striped=True, bordered=True, hover=True)
            ], style={'display': 'inline-block', 'padding': '0 30px'}))
    # Export data to CSV
    if n_clicks:
        csv = df.to_csv(index=False)
        buf = io.StringIO(csv)
        resp = make_response(buf.getvalue())
        resp.headers["Content-Disposition"] = "attachment; filename=data.csv"
        resp.headers["Content-Type"] = "text/csv"
        return data, columns, kpi_container, resp
    else:
        return data, columns, kpi_container

if __name__ == '__main__':
    app.run(debug=True)
