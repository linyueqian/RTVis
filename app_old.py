# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Incorporate data
df = pd.read_excel('demo_dataset_new.xlsx')

# Initialize the app
app = Dash(__name__)

# Create figure
fig = go.Figure()

# Add trace
fig.add_trace(
    go.Scatter(x=list(df['rank']), y=list(df.Counts))
)

# Set title
fig.update_layout(
    title_text="Time series with range slider and selectors"
)

# App layout
app.layout = html.Div([
    html.Div(children='Research Trend Visualization'),
    html.Hr(),
    dash_table.DataTable(id='data-table', page_size=6),
    dcc.Graph(figure=fig, id='controls-and-graph'),
    dcc.RangeSlider(
        id='rank-range-slider',
        value=[df['rank'].min(), df['rank'].max()],
        marks={str(rank): str(rank) for rank in df['rank'].unique()},
        step=None
    )
])


@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Output(component_id='data-table', component_property='data'),
    Input(component_id='rank-range-slider', component_property='value')
)

def update_graph(rank_range):
    filtered_df = df.loc[(df['rank'] >= rank_range[0]) & (df['rank'] <= rank_range[1])]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=list(filtered_df['rank']), y=list(filtered_df.Counts))
    )
    filtered_data = filtered_df.to_dict('records')
    return fig, filtered_data


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
