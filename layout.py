import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

markdown_style = {
    "width": "100%",
    'margin': '10px',
}

with open("intro.md", "r") as myfile:
    intro_text = myfile.readlines()

main_text = """
### GPX Based Workout Summary

This web app calculates pace and distance of a workout from a GPX file using the time and GPS latitude/longitude. It is powered by [gpxrun](https://github.com/astrowonk/gpxrun) and [gpxcsv](https://pypi.org/project/gpxcsv/) and built on the [Dash](https://dash.plotly.com) framework.

Submitting a GPX file (or gzipped GPX file) will compute the *GPS* based pace and distance. You may optionally submit the distance in miles that is reported by Apple Fitness or whatever device you have. This will be used to compute the GPS based error of your fitness tracker/device.

Dowload Full CSV will return the full `gpx_data` dataframe from the `GpxRun` class. This is augmented from the [gpxcsv](https://pypi.org/project/gpxcsv/) GPX file with additional columns such as cummulative distance, rolling average speed/pace, etc.

__No data or files submitted are stored or preserved on the server. See the About tab for more information__.

"""
left_col = html.Div([
    dcc.Markdown(main_text, style=markdown_style),
    dcc.Upload(
        id='upload-data',
        children=['Drag and Drop or ',
                  html.A('Select a File')],
        style={
            'width': '100%',
            'height': '70px',
            'lineHeight': '70px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '15px',
            'textAlign': 'center',
            'margin': '10px'
        },
        #  Allow multiple files to be uploaded
        multiple=False),
    html.Div([
        dbc.FormGroup([
            html.Label('Enter Device Reported Distance in Miles (optional):'),
            dbc.Input(
                id='distance_input',
                style={'width': '100%'},
                persistence=True,
                persistence_type='memory',
                placeholder='Enter Pedometer/Watch workout distance in miles',
                debounce=True,
            ),
            dbc.Button("Download Full CSV",
                       id="btn_csv",
                       style={'width': '100%'}),
        ]),
    ])
])

right_col = html.Div([
    dcc.Loading(
        children=[
            dcc.Download(id="download-dataframe-csv"),
            html.Div(id='output-data-upload')
        ],
        id='loading-output-1',
        type='circle',
    ),
    html.Div(id='distance-comparison-div')
])

main_tab_content = html.Div(
    [dbc.Row([
        dbc.Col(left_col),
        dbc.Col(right_col),
    ])])
about_tab_content = html.Div(dcc.Markdown(
    intro_text,
    style=markdown_style,
))
tabs = dbc.Tabs([
    dbc.Tab(main_tab_content, label="Home"),
    dbc.Tab(about_tab_content, label="About"),
])

layout = dbc.Container(
    [dcc.Store(id='summary_data', storage_type='memory'), tabs])
