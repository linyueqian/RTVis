import pandas as pd
import networkx as nx
import datetime
import time
import plotly.graph_objects as go
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input

# Read the Excel file into a DataFrame
df = pd.read_excel('demo_dataset.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
# sort by df['Date]
df = df.sort_values(by='Date')
min_date_ymd = df['Date'].min().to_period('M').to_timestamp().strftime('%Y-%m-%d')
min_date_ym = df['Date'].min().to_period('M').to_timestamp().strftime('%Y-%m')
max_date_ymd = df['Date'].max().to_period('M').to_timestamp().strftime('%Y-%m-%d')
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
df['field_list'] = df['field_list'].apply(lambda x: x.strip() if x != None else x)
df['field_list'] = df['field_list'].apply(lambda x: ''.join([i for i in x if i.isalpha() or i == " "]) if x != None else x)

####################
# drop the line whose field_list starts with "oratory"
df = df[df['field_list'] != 'oratory was in fact a way of establishing selfworth among Native Americans']
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

river_fig = go.Figure()
river_fig.update_layout(plot_bgcolor='white')
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
def generate_node_fig(x_range):
    if x_range is None:
        df = pd.read_excel('demo_dataset.xlsx').fillna('')
    else:
        df = pd.read_excel('demo_dataset.xlsx').fillna('')
        df = df[(df['Date'] >= x_range[0]) & (df['Date'] <= x_range[1])]
    # Extract the author names from the DataFrame
    author_list = df['Author Name'].tolist()
    # Create an empty graph
    G = nx.Graph()

    # Iterate over each entry in the author_list
    for idx in range(len(author_list)):
        entry = str(author_list[idx])
        authors = extract_authors(entry)

        # Add edges between all pairs of authors in the entry
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                author1 = authors[i]
                author2 = authors[j]

                # Increment the weight of the edge if it already exists
                if G.has_edge(author1, author2):
                    G[author1][author2]['weight'] += 1
                else:
                    G.add_edge(author1, author2, weight=1)
                    
    # Calculate the co-occurrence counts for each author
    co_occurrences = {author: sum(weight['weight'] for weight in G[author].values()) for author in G.nodes()}

    # find the authors with the top 100 highest co-occurrence count
    least_co_occurrences = sorted(co_occurrences.items(), key=lambda x: x[1], reverse=True)[100][1]
    top_authors_nodes = []
    for node in G.nodes():
        if co_occurrences[node] > least_co_occurrences:
            top_authors_nodes.append(node)
            
    # turn the top_authors into a new graph
    G_top = nx.Graph()
    for entry in author_list:
        authors = extract_authors(entry)
        # Add edges between all pairs of authors in the entry
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                author1 = authors[i]
                author2 = authors[j]
                if author1 in top_authors_nodes and author2 in top_authors_nodes:
                    # Increment the weight of the edge if it already exists
                    if G_top.has_edge(author1, author2):
                        G_top[author1][author2]['weight'] += 1
                    else:
                        G_top.add_edge(author1, author2, weight=1)
    # remove the node if it is a single node in the current graph
    G = G_top.copy()
    for node in G_top.nodes():
        if len(list(G_top.neighbors(node))) <= 1:
            G.remove_node(node)

    # Generate the layout of the graph
    pos = nx.kamada_kawai_layout(G, scale=5)
    # pos = nx.force_atlas2_layout(G, iterations=1000)
    # pos = forceatlas2.forceatlas2_networkx_layout(G, pos=None, niter=1000)
    pos = nx.spring_layout(G, pos=pos)
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
            sizemode='diameter',
        ))

    # Create a list of node labels
    node_labels = list(G.nodes())

    # Create node text
    node_text = [f"{node}<br>Co-occurrences: {co_occurrences[node]}" for node in G.nodes()]

    # Update node trace with labels and text
    node_trace.text = node_labels
    node_trace.hovertext = node_text

    # Create figure
    node_fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        ))
    return node_fig

node_fig = generate_node_fig(None)
##############################################################################################################
# bar chart race
def convert_time_to_ordinal(time_str):
    time_str = time_str.split('.')[0]
    time_str = time_str.replace('T', ' ')
    time_str = time_str.replace('Z', '')
    time_str = time_str.replace(' ', '-')
    time_str = time_str.replace(':', '-')
    time_str = time_str.split('-')
    time_str = [int(x) for x in time_str]
    time_str = datetime.datetime(time_str[0], time_str[1], time_str[2], time_str[3], time_str[4], time_str[5])
    return int(time.mktime(time_str.timetuple()))
def extract_ymd(time_str):
    time_str = time_str.split('.')[0]
    time_str = time_str.replace('T', ' ')
    time_str = time_str.replace('Z', '')
    time_str = time_str.replace(' ', '-')
    time_str = time_str.replace(':', '-')
    time_str = time_str.split('-')
    time_str = [str(int(x)) for x in time_str]
    return time_str[0]+'-'+time_str[1]+'-'+time_str[2]
def generate_race_fig(x_range):
    if x_range is None:
        value1 = min_date_ymd
        value2 = max_date_ymd
        # print(value1, value2)
    else:
        value1, value2 = [extract_ymd(x) for x in x_range]
    with open('assets/abstractBarChartRace.html', 'r') as file:
        src_doc = file.read().replace('%value1%', value1).replace('%value2%', value2)
    return src_doc
src_doc = generate_race_fig(None)
##############################################################################################################
# show the figures using dash
app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.Div(
            className='figure',
            children=[
                dcc.Graph(id='node_fig', figure=node_fig)
            ]
        ),
        html.Div(
            className='figure',
            children=[
                html.Iframe(
                    id='race_fig',
                    srcDoc=src_doc,
                    style={
                        'width': '100%',
                        'height': '800px',
                        'border': 'none',
                        'transform': 'scale(0.7) translateY(-20%)'
                    }
                )
            ]
        ),
        html.Div(
            className='river',
            children=[
                dcc.Graph(id='river_fig', figure=river_fig)
            ]
        )
    ]
)

@app.callback(
    Output('node_fig', 'figure'),
    Output('river_fig', 'figure'),
    Output('race_fig', 'srcDoc'),
    Input('river_fig', 'relayoutData'))
    
def update_figure(relayoutData):
    # print(relayoutData)
    if relayoutData is None:
        node_fig = generate_node_fig(None)
        return node_fig, river_fig, src_doc
    else:
        if 'xaxis.range[0]' in relayoutData:
            x_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
            river_fig.update_layout(xaxis_range=x_range)
            node_fig = generate_node_fig(x_range)
            race_fig = generate_race_fig(x_range)
            return node_fig, river_fig, race_fig
        elif 'xaxis.autorange' in relayoutData:
            river_fig.update_layout(xaxis_range=None, yaxis_range=None)
            node_fig = generate_node_fig(None)
            race_fig = generate_race_fig(None)
            return node_fig, river_fig, race_fig
        else:
            node_fig = generate_node_fig(None)
            race_fig = generate_race_fig(None)
            return node_fig, river_fig, race_fig

# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
