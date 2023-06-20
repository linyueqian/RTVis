from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from dash import dcc
from dash.dependencies import Input, Output, State
import webbrowser
import numpy as np



app = Dash(__name__)


app.layout = html.Div([
    html.H4('Top n citation venues'),
    dcc.Dropdown(
        id="bar-chart-x-dropdown",
        options=[3,4,5,6,7,8,9],
        value=5,
        clearable=False,
    ),
    dcc.Graph(id="bar-chart-x-graph"),
    
])


@app.callback(
    Output("bar-chart-x-graph", "figure"), 
    Input("bar-chart-x-dropdown", "value"))

def update_bar_chart(top_n):


    df = pd.read_csv('../demo_dataset.csv')
    df['Year'] = df['Date'].str[0:4].astype('int')
    gb = df.groupby(['Venue', 'Year']).sum(numeric_only=True)
    gb = gb.groupby(level=0).filter(lambda x: len(x) > 2 )
    first_n = gb.reset_index().groupby('Venue').sum(numeric_only=True).sort_values('Paper Citation Count', ascending=False).reset_index()['Venue'][0:top_n].tolist()
    df_clean = df[df['Venue'].isin(first_n)].sort_values('Paper Citation Count').reset_index().drop(['index'], axis=1)
    # mask = df["day"] == day
    # df_clean = pd.read_csv('./test.csv')
    fig = px.bar(df_clean, x="Year", y="Paper Citation Count", 
                 color="Venue", barmode="group", hover_name = "Title")
    # height = 10000
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Rockwell"
        ),
        legend=dict(
            x = -0.1,
            y = -1.5
        ),
        autosize = True
    )
    return fig

# def bar_click(click_data, figure):
#     if click_data is not None:
#         point_inds = click_data['points'][0]['pointIndex']
#         trace_index = click_data['points'][0]['curveNumber']
#         url = figure['data'][trace_index]['paper url'][point_inds]
#         webbrowser.open_new_tab(url)

#     # Return clickData to update the chart's clickData property
#     return click_data

if __name__ == "__main__":
    app.run_server(debug=True)
