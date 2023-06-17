from dash import Dash, html
import pandas as pd

app = Dash(__name__)

# time range to be passed
value1 = 737615
value2 = 738505

value1 = pd.Timestamp.fromordinal(value1).to_period('M').to_timestamp().strftime('%Y-%m-%d')
value2 = pd.Timestamp.fromordinal(value2 + 30).to_period('M').to_timestamp().strftime('%Y-%m-%d')

with open('abstractBarChartRace.html', 'r') as file:
    src_doc = file.read().replace('%value1%', value1).replace('%value2%', value2)

app.layout = html.Div(
    children=[
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='four columns div-user-controls',
                    children=[
                        html.H2('Bar Chart Race')
                    ]
                ),
                html.Div(
                    className='eight columns div-for-charts bg-grey',
                    children=[
                        html.Iframe(
                            srcDoc = src_doc,
                            style={
                                'width': '100%',
                                'height': '800px',
                                'border': 'none',
                                'transform': 'scale(0.7) translateY(-20%)'
                            }
                        )
                    ]
                )
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
