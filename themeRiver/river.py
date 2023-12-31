from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)

df = pd.read_excel('demo_dataset_new.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
min_month = df['Date'].dt.to_period('M').min()
max_month = df['Date'].dt.to_period('M').max()

while(max_month.month not in [1, 4, 7, 10]):
    max_month = max_month - 1

while(min_month.month not in [1, 4, 7, 10]):
    min_month = min_month + 1
    
# keep the data in the range of min_month and max_month
dframe = df[(df['Date'].dt.to_period('M') >= min_month) & (df['Date'].dt.to_period('M') < max_month)]

fields_of_struct = []
for i in range(len(dframe)):
    try:
        fields_of_struct.append(dframe.iloc[i]['Fields Of Study'].split(','))
    except:
        fields_of_struct.append("lack of data")
dframe['field_list'] = fields_of_struct
dframe = dframe.explode('field_list')
dframe['field_list'] = dframe['field_list'].apply(lambda x: x.strip() if x != None else x)
dframe['field_list'] = dframe['field_list'].apply(lambda x: ''.join([i for i in x if i.isalpha() or i == " "]) if x != None else x)

####################
# drop the line whose field_list starts with "oratory"
dframe = dframe[dframe['field_list'] != 'oratory was in fact a way of establishing selfworth among Native Americans']
####################

dframe_field_group = dframe.groupby('field_list')
dframe_field_group.head()

field_genres = []
field_counts = []
field_months = []

for field in dframe_field_group:
    for month in pd.date_range(min_month.to_timestamp(), max_month.to_timestamp(), freq='M'):
        field_genres.append(field[0])
        field_counts.append(len(field[1][field[1]['Date'].dt.to_period('M') == month.to_period('M')]))
        field_months.append(month)

field_df = pd.DataFrame({'fields': field_genres, 'counts': field_counts, 'months': field_months})

field_trace_dict = {}
field_all_traces = field_df['fields'].unique()
total_traces = len(field_all_traces)

for field in field_all_traces:
    field_trace_dict[field] = go.Scatter(x=field_df[field_df['fields'] == field]['months'], 
                                         y=field_df[field_df['fields'] == field]['counts'], 
                                         name=field,
                                         mode='none',
                                         stackgroup= total_traces,
                                         line_shape='spline')
    
fig = go.Figure()
for field in field_trace_dict.keys():
    fig.add_trace(field_trace_dict[field])

fig.update_layout(
    xaxis=dict(
        type="date"
    )
)

# Generate a list of months between min_month and max_month
months = pd.period_range(start=min_month, end=max_month, freq='M')
mi = min_month.to_timestamp().toordinal()
ma = max_month.to_timestamp().toordinal()
num_months = len(months)
step = (ma - mi) // (num_months - 1) * 3 
ma = mi + (num_months - 1) // 3 * step

# initialize the marks
marks = {}
for month in months:
    if months.get_loc(month) % 3 == 0:
        marks[months.get_loc(month) * step // 3 + mi] = str(month)

app.layout = html.Div(
    children=[
        html.Div(className='row',
                children=[
                    html.Div(className='four columns div-user-controls',
                            children=[
                                html.H2('Theme River'),
                                html.Div(style={'margin-top': '20px'}),
                                dcc.RangeSlider(
                                    min=mi,
                                    max=ma,
                                    step=1,
                                    marks=marks,
                                    value=[mi, ma],
                                    id='my-range-slider'
                                )
                            ]
                    ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='output-container-range-slider',
                                           animate=True,
                                           config={'displayModeBar': False},
                                )
                            ]
                    )
                ]
        ),
    ]
)


@callback(
    Output('output-container-range-slider', 'figure'),
    [Input('my-range-slider', 'value')])

def update_output(value):
    min_month = pd.Timestamp.fromordinal(value[0]).to_period('M')
    max_month = pd.Timestamp.fromordinal(value[1] + 30).to_period('M')

    dframe = df[(df['Date'].dt.to_period('M') >= min_month) & (df['Date'].dt.to_period('M') <= max_month)]
    
    fields_of_struct = []
    for i in range(len(dframe)):
        try:
            fields_of_struct.append(dframe.iloc[i]['Fields Of Study'].split(','))
        except:
            fields_of_struct.append("lack of data")
    dframe['field_list'] = fields_of_struct
    dframe = dframe.explode('field_list')
    dframe['field_list'] = dframe['field_list'].apply(lambda x: x.strip() if x != None else x)
    dframe['field_list'] = dframe['field_list'].apply(lambda x: ''.join([i for i in x if i.isalpha() or i == " "]) if x != None else x)

    ####################
    # drop the line whose field_list starts with "oratory"
    dframe = dframe[dframe['field_list'] != 'oratory was in fact a way of establishing selfworth among Native Americans']
    ####################

    dframe_field_group = dframe.groupby('field_list')
    dframe_field_group.head()

    field_genres = []
    field_counts = []
    field_months = []

    for field in dframe_field_group:
        for month in pd.date_range(min_month.to_timestamp(), max_month.to_timestamp(), freq='M'):
            field_genres.append(field[0])
            field_counts.append(len(field[1][field[1]['Date'].dt.to_period('M') == month.to_period('M')]))
            field_months.append(month)

    field_df = pd.DataFrame({'fields': field_genres, 'counts': field_counts, 'months': field_months})

    field_trace_dict = {}
    field_all_traces = field_df['fields'].unique()
    total_traces = len(field_all_traces)

    for field in field_all_traces:
        field_trace_dict[field] = go.Scatter(x=field_df[field_df['fields'] == field]['months'], 
                                            y=field_df[field_df['fields'] == field]['counts'], 
                                            name=field,
                                            mode='none',
                                            stackgroup= total_traces,
                                            line_shape='spline')
        
    fig = go.Figure()
    for field in field_trace_dict.keys():
        fig.add_trace(field_trace_dict[field])

    fig.update_layout(
        xaxis=dict(
            type="date"
        )
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
