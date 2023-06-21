from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import dash_bootstrap_components as dbc
from collections import Counter

# Read the Excel file into a DataFrame
df = pd.read_excel('../demo_dataset_new.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
# sort by df['Date]
df = df.sort_values(by='Date')
min_month = df['Date'].dt.to_period('M').min()
max_month = df['Date'].dt.to_period('M').max()
######
# field
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
for field in field_trace_dict.keys():
    river_fig.add_trace(field_trace_dict[field])
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

node_fig = generate_node_fig(None, 50)
app = Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='node_fig', figure=node_fig),
    dcc.Graph(id='river_fig', figure=river_fig),
])
@app.callback(
    Output('node_fig', 'figure'),
    Output('river_fig', 'figure'),
    Input('river_fig', 'relayoutData'))
    
def update_figure(relayoutData):
    if relayoutData is None:
        node_fig = generate_node_fig(None, 50)
        return node_fig, river_fig
    else:
        if 'xaxis.range[0]' in relayoutData:
            x_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']]
            river_fig.update_layout(xaxis_range=x_range)
            node_fig = generate_node_fig(x_range, 50)
            return node_fig, river_fig
        elif 'xaxis.autorange' in relayoutData:
            river_fig.update_layout(xaxis_range=None, yaxis_range=None)
            node_fig = generate_node_fig(None, 50)
            return node_fig, river_fig
        else:
            node_fig = generate_node_fig(None, 50)
            return node_fig, river_fig

# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
