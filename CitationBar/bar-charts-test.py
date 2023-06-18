import webbrowser
import dash
import dash_core_components as dcc
from dash import html
from dash.dependencies import Input, Output, State

# Data for the bar chart
x = ['A', 'B', 'C']
y1 = [10, 15, 7]
y2 = [12, 9, 5]

# URLs corresponding to each bar
urls = ['https://example.com/page1', 'https://example.com/page2', 'https://example.com/page3']

# Create the app
app = dash.Dash(__name__)

# Define the bar chart
fig = dcc.Graph(
    id='bar-chart',
    figure={
        'data': [
            {
                'x': x,
                'y': y1,
                'name': 'Series 1',
                'customdata': urls,
                'hovertemplate': '<b>%{x}</b><br>Value: %{y}<extra></extra>',
                'type': 'bar'
            },
            {
                'x': x,
                'y': y2,
                'name': 'Series 2',
                'customdata': urls,
                'hovertemplate': '<b>%{x}</b><br>Value: %{y}<extra></extra>',
                'type': 'bar'
            }
        ],
        'layout': {
            'barmode': 'group'
        }
    }
)

# Define the callback to handle bar clicks
@app.callback(
    Output('bar-chart', 'clickData'),
    [Input('bar-chart', 'clickData')],
    [State('bar-chart', 'figure')]
)
def bar_click(click_data, figure):
    if click_data is not None:
        point_inds = click_data['points'][0]['pointIndex']
        trace_index = click_data['points'][0]['curveNumber']
        url = figure['data'][trace_index]['customdata'][point_inds]
        webbrowser.open_new_tab(url)

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
