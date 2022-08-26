import base64
import io
import gzip
from gpxrun import GpxRun
from gpxcsv import make_new_file_name
from numpy import nan_to_num, NaN
import pandas as pd
from database import DatabaseInterface

import config
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from hashlib import sha256

from layout import layout

dbi = DatabaseInterface(database_name=config.db_name)

import os
parent_dir = os.getcwd().split('/')[-1]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    url_base_pathname=f'/dash/{parent_dir}/',
    title='GPX Run Workout Analysis',
    meta_tags=[{
        'name':
        'description',
        'content':
        'GPX File Workout Pace and Distance Analysis, GPX to CSV Converter'
    }, {
        'name':
        'keywords',
        'content':
        'gpx, workout, pace, distance, gps, Apple Watch, Garmin, calibration, gps converter, csv'
    }, {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)

server = app.server

app.layout = html.Div(layout)


def clean_header_names(x):
    return x.replace('_', ' ').title()


def make_table_from_df2(_df, columns=None):
    if _df.empty:
        return html.Table()
    if columns is None:
        columns = _df.columns
    data_dict = _df[columns].to_dict(orient='records')

    col_names = list(data_dict[0].keys())
    header_column_cells = [
        html.Th(clean_header_names(x)) for x in col_names
        if not x.endswith('_HREF')
    ]
    table_header = [html.Thead(html.Tr(header_column_cells))]
    table_body = [html.Tbody([make_row2(x, col_names) for x in data_dict])]
    return dbc.Table(table_header + table_body)


def make_row2(data_dict_entry, col_names):
    def process_cell_links(col_name, link_names):
        """Add links to tables in the right way."""
        if (thehref := f"{col_name}_HREF") in link_names:
            return dcc.Link(str(data_dict_entry[col_name]),
                            href=str(data_dict_entry[thehref]))
        elif isinstance(data_dict_entry[col_name], float):
            return f"{(nan_to_num(data_dict_entry[col_name])):.2f}"
        return str(data_dict_entry[col_name])

    link_names = [x for x in col_names if x.endswith('_HREF')]
    return html.Tr([
        html.Td(process_cell_links(x, link_names)) for x in col_names
        if not x.endswith('_HREF')
    ])


def decimal_minutes_to_minutes_seconds(decimal_minutes):
    """Take decimal minutes and return minutes and decimmal seconds"""
    minutes = int(decimal_minutes)
    decimal_seconds = (decimal_minutes - minutes) * 60
    return minutes, decimal_seconds


def make_dataframe(
    content_string,
    filename,
    return_full=False,
):
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith('.gpx.gz'):
            gprun = GpxRun(io.StringIO(
                gzip.decompress(decoded).decode('utf-8')),
                           silent=True)
            if not return_full:
                return gprun.summary_data
            else:
                return gprun.gpx_data
        elif filename.endswith('.gpx'):
            # Assume that the user uploaded a GPX file
            gprun = GpxRun(io.StringIO(decoded.decode('utf-8')), silent=True)
            if not return_full:
                return gprun.summary_data
            else:
                return gprun.gpx_data
    except Exception as e:
        print(e)


def parse_contents(contents, filename):
    _, content_string = contents.split(',')

    df = make_dataframe(content_string, filename)
    data_dict = df.to_dict(orient='records')[0]

    df = df.reset_index().transpose().reset_index().tail(-1)
    df.columns = ['Label', 'Value']
    df['Label'] = df['Label'].apply(clean_header_names)
    theMarkdown = f"""
     __Start Time: {data_dict['start_time'].strftime('%a %b %d %H:%m:%S %Z')}__ {data_dict.get('type','').title()}
 
    ##### GPS Based Mile Pace: {data_dict['pace_mile_string']}


     Total Time: {GpxRun.decimal_minutes_to_formatted_string(data_dict['total_time_minutes'])}
     * GPS Based Distance: 
          - {data_dict['total_distance_miles']:.2f} miles
          - {data_dict['total_distance_meters']:.2f} meters


     """

    return html.Div([
        dcc.Markdown(theMarkdown, className='markdown-text'),
        html.P('Splits'),
        html.Ul(
            [
                html.
                Li(f"{clean_header_names(key).replace(' Split','')}: {GpxRun.decimal_minutes_to_formatted_string(val):>9}"
                   ) for key, val in data_dict.items() if 'split' in key
            ],
            style={'font-size': 14},
        ),
        html.Hr(),  # horizontal line
        dbc.Button(
            "Download Full CSV",
            id="btn_csv",
            style={'width': '100%'},
        ),
        dbc.Tooltip(
            "The CSV will contain all original gpx data created by gpxcsv with additional computed columns from GpxRun",
            target='btn_csv',
            placement='bottom',
        )
    ]), data_dict


@app.callback(
    Output('upload-data', 'children'),
    Input('upload-data', 'filename'),
)
def update_upload_text(file_name):
    if file_name:
        return html.Div(file_name)
    return html.Div(['Drag and Drop or ', html.A('Select a GPX File')])


@app.callback(
    [Output('output-data-upload', 'children'),
     Output('summary_data', 'data')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
)
def update_output(content, name):
    if content:
        return parse_contents(content, name)
    else:
        return [html.Div(['No file selected.']), {}]


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True,
)
def func(n_clicks, contents, filename):
    if not n_clicks:
        #the download is triggering without the button being clicked for unknown reasons
        return dash.no_update
    _, content_string = contents.split(',')
    ctx = dash.callback_context
    print([ctx.triggered[0]['prop_id'], ctx.triggered[0]['value'], ctx.inputs])
    return dcc.send_data_frame(
        make_dataframe(content_string, filename, return_full=True).to_csv,
        make_new_file_name(filename, 'csv'))


@app.callback(Output('distance-comparison-div', 'children'),
              Input('submit-distance-button', 'n_clicks'),
              State('distance-input', 'value'), State('summary_data', 'data'),
              State('data-opt-in', 'checked'))
def update_comparison_div(n_clicks, distance_input, data, opt_in):
    if not n_clicks:
        return dash.no_update
    if data is None:
        return dash.no_update
    if not distance_input:
        return []
    if distance_input:
        dist = float(distance_input)
    else:
        dist = NaN

    temp_df = pd.DataFrame([{
        'Distance (meters)': dist * 1609.344,
        'Source': 'Submitted'
    }, {
        'Distance (meters)':
        data.get('total_distance_miles', 0) * 1609.344,
        'Source':
        "GPS"
    }])
    error = f"{(100 * (dist - data['total_distance_miles']) / dist):.2f}%"
    thank_you_message = ''
    if opt_in:
        thank_you_message = "Thank you for sharing your summary data!"

    return html.Div([
        html.H4(f"Computed Distance Error: {error}"),
        make_table_from_df2(temp_df),
        html.P(thank_you_message),
    ],
                    style={'margin': '15px'})


@app.callback(Output('dummy', 'children'),
              Input('distance-comparison-div', 'children'),
              State('distance-input', 'value'), State('summary_data', 'data'),
              State('upload-data', 'contents'), State('upload-data',
                                                      'filename'),
              State('device-type', 'value'), State('data-opt-in', 'checked'),
              State('device-model', 'value'))
def save_hashed_stat_data(_, distance_input, data, contents, filename,
                          device_type, data_opt_in, device_model):
    if not data_opt_in:
        return dash.no_update
    if not distance_input:
        return dash.no_update
    print("This is the test save hashed stats method")
    _, content_string = contents.split(',')

    # I want the hash to be the same if it's submited as a gzip or as a plain gpx file
    # so I decode it and gunzip it (if need be) before then hashing it.

    decoded = base64.b64decode(content_string)

    if filename.endswith('.gpx.gz'):
        true_content = gzip.decompress(decoded)
    elif filename.endswith('.gpx'):
        # Assume that the user uploaded a GPX file
        true_content = decoded

    dist = float(distance_input)
    m = sha256()
    m.update(true_content)
    hashed_data = m.hexdigest()
    device_model = device_model.replace(';', '').replace('"', '')
    dbi.insert_summary_data(hashed_data, data.get('total_distance_miles', 0),
                            dist, device_type + '+' + device_model)
    return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)
