import webbrowser
import dash
from dash import Dash, dcc, html, Input, Output
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px



# app = dash.Dash(__name__)





# Create the app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4('Top n citation venues'),
    dcc.Dropdown(
        id="bar-chart-x-dropdown",
        options=[3,4,5,6,7,8,9],
        value=5,
        clearable=False,
    )

])
df = pd.read_csv('../demo_dataset.csv')
df['Year'] = df['Date'].str[0:4].astype('int')
gb = df.groupby(['Venue', 'Year']).sum(numeric_only=True)
gb = gb.groupby(level=0).filter(lambda x: len(x) > 2 )
first_n = gb.reset_index().groupby('Venue').sum(numeric_only=True).sort_values('Paper Citation Count', ascending=False).reset_index()['Venue'][0:5].tolist()
df_clean = df[df['Venue'].isin(first_n)].sort_values('Paper Citation Count').reset_index().drop(['index'], axis=1)

# Define the bar chart
fig = dcc.Graph(
    id='bar-chart',
    figure=px.bar(df_clean, x="Year", y="Paper Citation Count", 
                 color="Venue", barmode="group", hover_name = "Title")
)

# Define the callback to handle bar clicks
@app.callback(
    Output('bar-chart', 'clickData'),
    Input('bar-chart', 'clickData'),
    [State('bar-chart', 'figure')]
)
def bar_click(click_data, figure):
    if click_data is not None:

        title = click_data['points'][0]['hovertext']
        #replace spaces in title with "%20"
        title = title.replace(" ", "%20")
        # print(title)
        webbrowser.open_new_tab("https://scholar.google.com/scholar?q="+title+"&btnG=&hl=en&as_sdt=0%2C5")

    # Return clickData to update the chart's clickData property
    return click_data

# Define the app layout with JavaScript
app.layout = html.Div(
    children=[
        fig,
        html.Script(
            """
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const bars = document.getElementsByClassName('bar');
                Array.from(bars).forEach(function(bar) {
                    bar.style.cursor = 'pointer';
                });
            });
            </script>
            """
        )
    ]
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
