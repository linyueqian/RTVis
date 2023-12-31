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
    dcc.Graph(id="bar-chart"),
    
])


@app.callback(
    Output("bar-chart", "figure"), 
    Output('bar-chart', 'clickData'),
    Input("bar-chart-x-dropdown", "value"),
    Input('bar-chart', 'clickData'),
    [State('bar-chart', 'figure')])

def update_bar_chart(top_n, click_data, figure):


    df = pd.read_csv('../demo_dataset.csv')
    df['Year'] = df['Date'].str[0:4].astype('int')
    gb = df.groupby(['Venue', 'Year']).sum(numeric_only=True)
    gb = gb.groupby(level=0).filter(lambda x: len(x) > 2 )
    first_n = gb.reset_index().groupby('Venue').sum(numeric_only=True).sort_values('Paper Citation Count', ascending=False).reset_index()['Venue'][0:top_n].tolist()
    df_clean = df[df['Venue'].isin(first_n)].sort_values('Paper Citation Count').reset_index().drop(['index'], axis=1)
    # mask = df["day"] == day
    # df_clean = pd.read_csv('./test.csv')
    
    fig=px.bar(df_clean, x="Year", y="Paper Citation Count", 
                color="Venue", barmode="group", hover_name = "Title")
    #fig update layout
    
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
    if click_data is not None:
        title = click_data['points'][0]['hovertext']
        title = title.replace(" ", "%20")
        webbrowser.open_new_tab("https://scholar.google.com/scholar?q="+title+"&btnG=&hl=en&as_sdt=0%2C5")
        click_data = None
        return fig, click_data
    return fig, click_data





if __name__ == "__main__":
    app.run_server(debug=True)
