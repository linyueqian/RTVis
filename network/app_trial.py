from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import dash
import webbrowser
import dash_bootstrap_components as dbc
from collections import Counter



# prepare the data for bar chart race
dframe = pd.read_csv('./assets/data/processed_data.csv')
df3 = pd.read_csv('./assets/data/commonWords.csv')
d = dict.fromkeys(df3['word'].tolist(), 0)
df3 = dframe.groupby('Date')
df3 = df3.apply(lambda x: x.sort_values(['Date'], ascending=[True]))
df3 = df3.reset_index(drop=True)

# Read the Excel file into a DataFrame
df = pd.read_csv('demo_dataset.csv')
df['Date'] = pd.to_datetime(df['Date'])
# sort by df['Date]
df = df.sort_values(by='Date')
min_date_ymd = df['Date'].min().to_period(
    'M').to_timestamp().strftime('%Y-%m-%d')
min_date_ym = df['Date'].min().to_period('M').to_timestamp().strftime('%Y-%m')
max_date_ymd = df['Date'].max().to_period(
    'M').to_timestamp().strftime('%Y-%m-%d')
max_date_ym = df['Date'].max().to_period('M').to_timestamp().strftime('%Y-%m')
min_month = df['Date'].dt.to_period('M').min()
max_month = df['Date'].dt.to_period('M').max()
############################################
# field theme river
fields_of_struct = []
for i in range(len(df)):
    try:
        fields_of_struct.append(df.iloc[i]['Fields Of Study'].split(','))
    except:
        fields_of_struct.append("lack of data")
df['field_list'] = fields_of_struct
df = df.explode('field_list')
df['field_list'] = df['field_list'].apply(
    lambda x: x.strip() if x != None else x)
df['field_list'] = df['field_list'].apply(lambda x: ''.join(
    [i for i in x if i.isalpha() or i == " "]) if x != None else x)

####################
# drop the line whose field_list starts with "oratory"
df = df[df['field_list'] !=
        'oratory was in fact a way of establishing selfworth among Native Americans']
####################

df_field_group = df.groupby('field_list')
# sort df_field_group alphabetically
df_field_group = sorted(df_field_group, key=lambda x: x[0], reverse=True)
field_genres = []
field_counts = []
field_months = []

for field in df_field_group:
    for month in pd.date_range(min_month.to_timestamp(), max_month.to_timestamp(), freq='M'):
        field_genres.append(field[0])
        field_counts.append(
            len(field[1][field[1]['Date'].dt.to_period('M') == month.to_period('M')]))
        field_months.append(month)

field_df = pd.DataFrame(
    {'fields': field_genres, 'counts': field_counts, 'months': field_months})

field_trace_dict = {}
field_all_traces = field_df['fields'].unique()
total_traces = len(field_all_traces)

for field in field_all_traces:
    field_trace_dict[field] = go.Scatter(x=field_df[field_df['fields'] == field]['months'],
                                         y=field_df[field_df['fields']
                                                    == field]['counts'],
                                         name=field,
                                         mode='none',
                                         stackgroup=total_traces,
                                         line_shape='spline')

river_fig = go.Figure()
river_fig.update_layout(plot_bgcolor='#FBFBFB',
                        paper_bgcolor='#FBFBFB', margin=dict(l=5, r=5, t=0, b=10))
# river_fig.update_xaxes(gridcolor='#F86F03')
river_fig.update_yaxes(gridcolor='#888')
for field in field_trace_dict.keys():
    river_fig.add_trace(field_trace_dict[field])


###########################################
# authors network
# Define a function to extract the author names from each entry
def extract_authors(entry):
    authors = entry.split(', ')
    if len(authors) > 1 and authors[-1].endswith(','):
        # Split the last name and remove the trailing comma
        last_name = authors[-1][:-1]
        authors = authors[:-1] + [last_name]
    authors = [author.strip() for author in authors]
    return authors

node_df = pd.read_csv('demo_dataset.csv').fillna('')
def generate_node_fig(x_range, top_n):
    df = node_df.copy()
    if x_range is not None:
        df = df[(df['Date'] >= x_range[0]) & (df['Date'] <= x_range[1])]
    # Extract the author names from the DataFrame
    author_list = df['Author Name'].tolist()
    # Create an empty graph
    G = nx.Graph()
    co_occurrences = Counter()
    edges = Counter()
    for idx in range(len(author_list)):
        entry = str(author_list[idx])
        authors = extract_authors(entry)
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                author1 = authors[i]
                author2 = authors[j]
                if author1 < author2:
                    edges[(author1, author2)] += 1
                else:
                    edges[(author2, author1)] += 1
                co_occurrences[author1] += 1
                co_occurrences[author2] += 1
    G.add_edges_from((a, b, {"weight": w}) for (a, b), w in edges.items())
    # find the authors with the top 100 highest co-occurrence count
    least_co_occurrences = sorted(co_occurrences.values(), reverse=True)[top_n]
    G = nx.Graph((a, b, {"weight": w}) for (a, b), w in edges.items() if co_occurrences[a] > least_co_occurrences and co_occurrences[b] > least_co_occurrences)

    # for node in G_top.nodes():
    #     if len(list(G_top.neighbors(node))) <= 1:
    #         G.remove_node(node)

    # Generate the layout of the graph
    pos = nx.spring_layout(G, scale=1, iterations=500)
    # pos = nx.force_atlas2_layout(G, iterations=1000)
    # pos = forceatlas2.forceatlas2_networkx_layout(G, pos=None, niter=1000)
    # pos = nx.spring_layout(G, pos=pos)
    # pos = nx.fruchterman_reingold_layout(G, pos=pos)
    # pos = nx.spring_layout(G_top)
    # pos = nx.fruchterman_reingold_layout(G_top)
    # pos = nx.spectral_layout(G_top)
    # pos = nx.circular_layout(G_top)

    # Extract node positions and edge coordinates
    node_x = []
    node_y = []
    node_size = []
    for node, position in pos.items():
        node_x.append(position[0])
        node_y.append(position[1])
        node_size.append(co_occurrences[node])
    # normalize the node size
    node_size = [size / max(node_size) * 100 for size in node_size]
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.3, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightblue',
            opacity=0.9,
            size=node_size,  # Update the marker size based on co-occurrences
            sizemode='area',
        ))

    # Create a list of node labels
    node_labels = list(G.nodes())

    # Create node text
    node_text = [
        f"{node}<br>Co-occurrences: {co_occurrences[node]}" for node in G.nodes()]

    # Update node trace with labels and text
    node_trace.text = node_labels
    node_trace.hovertext = node_text

    # Create figure
    node_fig = go.Figure(data=[edge_trace, node_trace],
                         layout=go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=5, t=5),
        plot_bgcolor='#fbfbfd',
        paper_bgcolor='#fbfbfd',
        xaxis=dict(showgrid=False, zeroline=False,
                   showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False,
                   showticklabels=False),
    ))
    return node_fig

node_fig_init = generate_node_fig(None, 50)
node_fig = node_fig_init
##############################################################################################################
# bar chart race
def extract_ymd(time_str):
    time = pd.to_datetime(time_str)
    time = time.date()
    return str(time)


def generate_race_fig(d, x_range, top_n_words):
    # read string from "/public/assets/data/barChartRace.csv" and keep it as csv format
    if x_range is None:
        value1 = min_date_ymd
        value2 = max_date_ymd
    else:
        value1, value2 = [extract_ymd(x) for x in x_range]
    
    # read df3 with lines start from value1 to value2
    df_temp = df3[(df3['Date'] >= value1) & (df3['Date'] <= value2)]
    
    df_temp = df_temp[df_temp['Abstract'].notna()]
    
    #connect all abstracts in the same date to one string
    df4 = df_temp.groupby('Date')['Abstract'].apply(lambda x: "%s" % ' '.join(x))
    df4 = pd.DataFrame(df4)
    #reset index
    df4 = df4.reset_index()

    #new df to create barcharrace
    df5 = pd.DataFrame(columns=['Date', 'Word', 'Count'])

    #for each abstract, call remove function to remove stopwords and punctuations
    for index, row in df4.iterrows():
        #for each word in the abstract, add 1 to the dictionary
        for word in row['Abstract'].split():
            #if wor in the dictionary, add 1
            if word in d:
                d[word] += 1
        #sort the dictionary by value
        d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
        #get the first 15 words and save to the dataframe use concat
        for i in range(15):
            df5 = pd.concat([df5, pd.DataFrame([[row['Date'], list(d.keys())[i], list(d.values())[i]]], columns=['Date', 'Word', 'Count'])])

    # convert df5 to csv string
    csv_string = df5.to_csv(index=False)
    csv_string = csv_string.replace('\n', '\\n')
    
    with open('assets/abstractBarChartRace.html', 'r') as file:
        src_doc = file.read()\
                    .replace('%value1%', value1)\
                    .replace('%value2%', value2)\
                    .replace('%csv_string%', csv_string)\
                    .replace('%top_n_words%', str(top_n_words))
    return src_doc

src_doc = generate_race_fig(d, None, top_n_words=8)
##############################################################################################################


def generate_bar_chart(top_n, click_data, x_range):
    if x_range is None:
        df = pd.read_csv('demo_dataset.csv')
    else:
        df = pd.read_csv('demo_dataset.csv')
        df = df[(df['Date'] >= x_range[0]) & (df['Date'] <= x_range[1])]
    df['Year'] = df['Date'].str[0:4].astype('int')
    gb = df.groupby(['Venue', 'Year']).sum(numeric_only=True)
    least_year = max(df['Year'].max() - df['Year'].min() - 1, 0)
    gb = gb.groupby(level=0).filter(lambda x: len(x) > least_year)
    first_n = gb.reset_index().groupby('Venue').sum(numeric_only=True).sort_values(
        'Paper Citation Count', ascending=False).reset_index()['Venue'][0:top_n].tolist()
    df_clean = df[df['Venue'].isin(first_n)].sort_values(
        'Paper Citation Count').reset_index().drop(['index'], axis=1)
    bar_fig = px.bar(df_clean, x="Year", y="Paper Citation Count",
                     color="Venue", barmode="group", hover_name="Title")
    bar_fig.update_layout(
        plot_bgcolor='#161617',
        paper_bgcolor='#161617',
        hoverlabel=dict(
            bgcolor="white",
            font_size=8,
            font_family='"SF Pro Text", "SF Pro Icons", "Helvetica Neue", Helvetica, Arial, sans-serif'
        ),
        xaxis=dict(
            linecolor='rgb(245, 245, 247)',
            tickfont=dict(color='rgb(245, 245, 247)'),
        ),
        yaxis=dict(
            linecolor='rgb(245, 245, 247)',
            tickfont=dict(color='rgb(245, 245, 247)'),
        ),
        font=dict(
            color='rgb(245, 245, 247)',
            family='"SF Pro Text", "SF Pro Icons", "Helvetica Neue", Helvetica, Arial, sans-serif'
        ),
        legend=dict(
            x=-0.1,
            y=-1.2
        ),
        margin=dict(
            l=5,
            r=5,
            b=0,
        ))
    if click_data is not None:
        title = click_data['points'][0]['hovertext']
        title = title.replace(" ", "%20")
        webbrowser.open_new_tab("https://scholar.google.com/scholar?q="+title+"&btnG=&hl=en&as_sdt=0%2C5")
        click_data = None
        return bar_fig, click_data
    return bar_fig, click_data
bar_fig, _ = generate_bar_chart(5, click_data=None, x_range=None)

# loading_modal = dbc.Modal(
#     [
#         dbc.ModalBody("Loading..."),
#     ],
#     id="loading-modal",
#     centered=True,
#     is_open=False,
# )

# def update_load_modal(load_trigger):
#     if load_trigger.get('children') == 1:
#         load_trigger['children'] = 0
#     else:
#         load_trigger['children'] = 1
#     return load_trigger
def update_node_fig(x_range, top_n_node):
    return generate_node_fig(x_range, top_n_node)

def update_river_fig(x_range, relayoutData):
    if x_range is not None:
        river_fig.update_layout(xaxis_range=x_range)
    elif 'xaxis.autorange' in relayoutData:
        river_fig.update_layout(xaxis_range=None, yaxis_range=None)
    return river_fig

def update_race_fig(x_range, top_n_words):
    return generate_race_fig(d, x_range, top_n_words)

def update_bar_chart(top_n_bar, click_data, x_range):
    return generate_bar_chart(top_n_bar, click_data, x_range)


##############################################################################################################
# show the figures using dash
external_stylesheets = ['assets/css/style.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Research Trend Visualization'
app.favicon = 'assets/favicon.ico'
app.layout = html.Div(
    children=[
        # loading_modal,
        # html.Div(id="load-trigger-1", children=1, style={"display": "none"}),
        html.Div(
            className='title',
            children=[
                html.A(
                    className='button-left',
                    href='https://github.com/linyueqian/RTVis',
                    children='Code'
                ),
                html.A(
                    className='button-right',
                    href='https://docs.rtvis.design',
                    children='Docs'
                ),
                html.H1('Research Trend Visualization'),
                html.P('Visualize research trends in a specific field')
            ]),
        html.Div(
            className='graph-container grey',
            # style={'width': '100%', 'height': '100%'},
            children=[
                html.Div(
                    className='figure grey',
                    children=[
                        html.H4([
                                "Top ",
                                dcc.Input(
                                    className="input",
                                    id="node-x-input",
                                    type="number",
                                    min=1,
                                    max=100,
                                    value=50,
                                    style={'display': 'inline-block', 'verticalAlign': 'middle',
                                           'margin': '0', 'padding': '0'}
                                ),
                                " authors' co-occurrences"
                            ]),
                        dcc.Graph(id='node_fig', figure=node_fig)
                    ]
                ),
                html.Div(
                    className='figure black',
                    children=[
                        html.Div([
                            html.H4([
                                "Top ",
                                dcc.Dropdown(
                                    className="dropdown",
                                    id="bar-chart-x-dropdown",
                                    options=[{'label': str(i), 'value': i}
                                             for i in [3, 4, 5, 6, 7, 8]],
                                    value=5,
                                    clearable=False,
                                    style={'display': 'inline-block', 'verticalAlign': 'middle',
                                           'margin': '0', 'padding': '0'}
                                ),
                                " citation venues"
                            ])
                        ]),
                        dcc.Graph(id="bar_fig", figure=bar_fig),
                    ]
                ),
                html.Div(
                    className='figure grey',
                    children=[
                        html.H4([
                            "Top ",
                            dcc.Input(
                                className="input",
                                id="race-x-input",
                                type="number",
                                min=5,
                                max=15,
                                value=8,
                                style={'display': 'inline-block', 'verticalAlign': 'middle',
                                    'margin': '0', 'padding': '0'}
                            ),
                            " common words in abstract part"
                        ]),
                        html.Iframe(
                            id='race_fig',
                            srcDoc=src_doc,
                            style={'width': '100%', 'height': '60vh', 'border': 'none'}
                        )
                    ]
                )]),
        html.Div(
            className='river',
            children=[
                dcc.Graph(id='river_fig', figure=river_fig)
            ]
        )
    ]
)

# @app.callback(
#     Output("loading-modal", "is_open"),
#     Input('river_fig', 'relayoutData'),
#     Input("bar-chart-x-dropdown", "value"),
#     Input('bar_fig', 'clickData'),
#     Input("node-x-input", "value"),
#     Input("race-x-input", "value"),
#     State('load-trigger-1', 'children'),
# )
# def toggle_loading_modal(relayoutData, top_n_bar, click_data, top_n_node, top_n_words, load_trigger):
#     if relayoutData is not None:
#         print("relayoutData is not None")
#         if load_trigger == 1:
#             return False
#         else: return True
@app.callback(
    Output('node_fig', 'figure'),
    Output('river_fig', 'figure'),
    Output('race_fig', 'srcDoc'),
    Output("bar_fig", "figure"),
    Output('bar_fig', 'clickData'),
    Input('river_fig', 'relayoutData'),
    Input("bar-chart-x-dropdown", "value"),
    Input('bar_fig', 'clickData'),
    Input("race-x-input", "value"),
    Input("node-x-input", "value"),
    State('bar_fig', 'figure'),
    State('node_fig', 'figure'),
    prevent_initial_call=True
)
def update_figure(relayoutData, top_n_bar, click_data, top_n_words, top_n_node, bar_fig, node_fig):

    x_range = None
    if relayoutData is not None:
        if 'xaxis.range[0]' in relayoutData:
            x_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
            node_fig = update_node_fig(x_range, top_n_node)
        elif 'xaxis.autorange' in relayoutData:
            x_range = None
            node_fig = update_node_fig(x_range, top_n_node)

    river_fig = update_river_fig(x_range, relayoutData)
    race_fig = update_race_fig(x_range, top_n_words)
    bar_fig, click_data = update_bar_chart(top_n_bar, click_data, x_range)

    return node_fig, river_fig, race_fig, bar_fig, click_data

@app.callback(
    Output('node_fig', 'figure'),
    Input('river_fig', 'relayoutData'),
    Input("node-x-input", "value"),
    State('node_fig', 'figure'),
)
def update_node_figure(relayoutData, top_n_node, node_fig):
    if relayoutData is not None:
        x_range = None
        if relayoutData is not None:
            if 'xaxis.range[0]' in relayoutData:
                x_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
            elif 'xaxis.autorange' in relayoutData:
                x_range = None

        node_fig = update_node_fig(x_range, top_n_node)
        return node_fig
    else:
        return node_fig
    


# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
