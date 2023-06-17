import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# Read the Excel file into a DataFrame
df = pd.read_excel('../demo_dataset_new.xlsx')

# Extract the author names from the DataFrame
author_list = df['Author Name'].tolist()

# Define a function to extract the author names from each entry
def extract_authors(entry):
    authors = entry.split(', ')
    if len(authors) > 1 and authors[-1].endswith(','):
        # Split the last name and remove the trailing comma
        last_name = authors[-1][:-1]
        authors = authors[:-1] + [last_name]
    authors = [author.strip() for author in authors]
    return authors
# Create an empty graph
G = nx.Graph()

# Iterate over each entry in the author_list
for entry in author_list:
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
                    

# Generate the layout of the graph
# pos = nx.kamada_kawai_layout(G_top)
# pos = nx.spring_layout(G_top)
# pos = nx.fruchterman_reingold_layout(G_top)
# pos = nx.spectral_layout(G_top)
pos = nx.circular_layout(G_top)


# Extract node positions and edge coordinates
node_x = []
node_y = []
node_size = []
for node, position in pos.items():
    node_x.append(position[0])
    node_y.append(position[1])
    node_size.append(co_occurrences[node])

edge_x = []
edge_y = []
for edge in G_top.edges():
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
        sizeref=max(node_size) / 10,  # Scale the marker size
        sizemin=5
    ))

# Create a list of node labels
node_labels = list(G_top.nodes())

# Create node text
node_text = [f"{node}<br>Co-occurrences: {co_occurrences[node]}" for node in G_top.nodes()]

# Update node trace with labels and text
node_trace.text = node_labels
node_trace.hovertext = node_text

# Create figure
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Top 5 Author Co-occurrence Graph',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                     ))

# Show the figure
fig.show()
    
