"""
****** Important! *******
If you run this app locally, un-comment line 113 to add the ThemeChangerAIO component to the layout
"""

from dash import Dash, dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import pandas as pd

# Import Dataset
df = pd.read_csv('data/pip_dataset.csv')
countries = pd.unique(df['country'])
years = df['year']
welfareType = df['welfare_type']

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

header = html.H4(
    "World Poverty Demographic", className="bg-primary text-white p-2 mb-2 text-center"
)

dropdownWelfare = html.Div(
    [
        dbc.Label("Select type"),
        dcc.Dropdown(
            ["consumption", "income"],
            "consumption",
            id="welfare_type",
            clearable=False,
        ),
    ],
    className="mb-4",
)

dropdownLevel = html.Div(
    [
        dbc.Label("Select level"),
        dcc.Dropdown(
            ["national", "rural", "urban"],
            "national",
            id="reporting_level",
            clearable=False,
        ),
    ],
    className="mb-4",
)

dropdownPpp = html.Div(
    [
        dbc.Label("Select ppp version"),
        dcc.Dropdown(
            [2011, 2017],
            2017,
            id="ppp_version",
            clearable=False,
        ),
    ],
    className="mb-4",
)

dropdownIndicator = html.Div(
    [
        dbc.Label("Select indicator (y-axis)"),
        dcc.Dropdown(
            ["headcount_ratio_international_povline", "headcount_ratio_lower_mid_income_povline", "headcount_ratio_upper_mid_income_povline"],
            "headcount_ratio_international_povline",
            id="indicator",
            clearable=False,
        ),
    ],
    className="mb-4",
)

checklist = html.Div(
    [
        dbc.Label("Select Countries"),
        dbc.Checklist(
            id="countries",
            options=[{"label": i, "value": i} for i in countries],
            value=["China"],
            inline=True,
        ),
    ],
    className="mb-4",
)

slider = html.Div(
    [
        dbc.Label("Select Years"),
        dcc.RangeSlider(
            years.min(),
            years.max(),
            5,
            id="years",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            value=[years.min(), years.max()],
            className="p-0",
        ),
    ],
    className="mb-4",
)

controls = dbc.Card(
    [dropdownWelfare, dropdownLevel, dropdownPpp, dropdownIndicator, slider, checklist],
    body=True,
)

table = html.Div(
    dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i, "deletable": True} for i in df.columns],
        data=df.to_dict("records"),
        page_size=10,
        editable=True,
        cell_selectable=True,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        row_selectable="multi",
    ),
    className="dbc-row-selectable",
)

tab1 = dbc.Tab([dcc.Graph(id="line-chart")], label="Line Chart")
tab2 = dbc.Tab([dcc.Graph(id="bar-chart")], label="Bar Chart")
tab3 = dbc.Tab([table], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

app.layout = dbc.Container(
    [
        header,
        dbc.Row(
            [
                dbc.Col(
                    [
                        controls,
                        ThemeChangerAIO(aio_id="theme")
                    ],
                    width=4,
                ),
                dbc.Col([tabs], width=8),
            ]
        ),
    ],
    fluid=True,
    className="dbc",
)

@callback(
    Output("line-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("table", "data"),
    Input("welfare_type", "value"),
    Input("reporting_level", "value"),
    Input("ppp_version", "value"),
    Input("indicator", "value"),
    Input("countries", "value"),
    Input("years", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
)
def update_line_chart(welfare, level, ppp, indicator, country, yrs, theme):
    if country == [] or indicator is None:
        return {}, {}, []

    print(welfare, level, ppp, indicator, country, yrs)
    # Filter the data frame based on user selected filter
    dff = df[df.ppp_version == int(ppp)]
    dff = dff[dff.welfare_type == welfare]
    dff = dff[dff.reporting_level == level]
    dff = dff[dff.year.between(yrs[0], yrs[1])]
    dff = dff[dff.country.isin(country)]
    data = dff.to_dict("records")

    print(dff)

    fig = px.line(
        dff,
        x="year",
        y=indicator,
        color="country",
        line_group="country",
        template=template_from_url(theme),
    )

    fig_bar = px.bar(
        dff,
        x="year",
        y=indicator,
        color="country",
        template=template_from_url(theme),
    )

    return fig, fig_bar, data


if __name__ == "__main__":
    app.run_server(debug=True)