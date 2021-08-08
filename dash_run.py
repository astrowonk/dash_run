import base64
import datetime
import io
import gzip
from gpxrun import GpxRun
from gpxcsv import make_new_file_name
from numpy import nan_to_num, NaN

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from layout import layout


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


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    url_base_pathname='/gpxrun/',
    title='GPX Run Workout Analysis',
    meta_tags=[{
        'name': 'description',
        'content': 'GPX File Workout Pace and Distance Analysis'
    }, {
        'name':
        'keywords',
        'content':
        'gpx, workout, pace, distance, gps, Apple Watch, Garmin, calibration'
    }, {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }])

server = app.server

app.layout = html.Div(layout)


def decimal_minutes_to_minutes_seconds(decimal_minutes):
    """Take decimal minutes and return minutes and decimmal seconds"""
    minutes = int(decimal_minutes)
    decimal_seconds = (decimal_minutes - minutes) * 60
    return minutes, decimal_seconds


def make_dataframe(
    content_string,
    filename,
    distance_input,
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


def parse_contents(contents, filename, distance_input):
    content_type, content_string = contents.split(',')
    if distance_input:
        dist = float(distance_input)
    else:
        dist = NaN
    df = make_dataframe(content_string, filename, dist)
    data_dict = df.to_dict(orient='records')[0]

    df = df.reset_index().transpose().reset_index().tail(-1)
    df.columns = ['Label', 'Value']
    df['Label'] = df['Label'].apply(clean_header_names)
    theMarkdown = f"""
     #### GPS Based Mile Pace: {data_dict['pace_mile_string']}
     #### Submitted Distance Error: {(100 * (dist - data_dict['total_distance_miles']) / dist):.2f}%
     
     * GPS Based Distance: 
          - {data_dict['total_distance_miles']:.2f} miles
          - {data_dict['total_distance_meters']:.2f} meters
     * Submitted Distance: 
          - {dist:.2f} miles
          - {dist * 1609.34:.2f} meters
     * Total Time: {GpxRun.decimal_minutes_to_formatted_string(data_dict['total_time_minutes'])}"

     """

    return html.Div([
        dcc.Markdown(theMarkdown,
                     style={
                         'font-family': 'monospace',
                         'font-size': 18
                     }),
        html.H4('Splits'),
        html.Ul(
            [
                html.
                Li(f"{clean_header_names(key).replace(' Split','')}: {GpxRun.decimal_minutes_to_formatted_string(val):>9}"
                   ) for key, val in data_dict.items() if 'split' in key
            ],
            style={
                'font-family': 'monospace',
                'font-size': 18
            },
        ),
        html.Hr(),  # horizontal line
    ])


@app.callback(
    Output('upload-data', 'children'),
    Input('upload-data', 'filename'),
)
def update_upload_text(file_name):
    if file_name:
        return html.Div(file_name)
    return html.Div(['Drag and Drop or ', html.A('Select a GPX File')])


@app.callback(
    Output('output-data-upload', 'children'),
    Input('submit_button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('distance_input', 'value'),
)
def update_output(_, content, name, distance_input):
    if content:
        return parse_contents(content, name, distance_input)


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True,
)
def func(n_clicks, contents, filename):
    _, content_string = contents.split(',')

    return dcc.send_data_frame(
        make_dataframe(content_string, filename, None,
                       return_full=True).to_csv,
        make_new_file_name(filename, 'csv'))


if __name__ == '__main__':
    app.run_server(debug=True)
