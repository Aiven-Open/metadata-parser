import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

from colour import Color
from textwrap import dedent as d
import json
from networkx.readwrite.gml import read_gml
from networkx.algorithms.components import node_connected_component

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Aiven Network"

YEAR=[2010, 2022]
ACCOUNT=None
TYPESTOFILTER=None

list_of_nodes = []
list_of_types = []

##############################################################################################################################################################
def network_graph(NodeToFilter, TypesToFilter):
    
    edge_x = []
    edge_y = []

    global list_of_nodes
    global list_of_types
    G = read_gml('graph_data.gml')
    not_services =  (n for n in G if G.nodes[n].get('type') != 'service')
    
    if(NodeToFilter and NodeToFilter != 'All'):
        conn = node_connected_component(G.to_undirected().subgraph(not_services),NodeToFilter)
        G = G.subgraph(conn)
    if TypesToFilter:
        sel_nodes =  (n for n in G if G.nodes[n].get('type') in TypesToFilter)
        G = G.subgraph(sel_nodes)
    pos = nx.nx_pydot.pydot_layout(G)
    #pos = nx.layout.spring_layout(G)

    list_of_nodes = []
    list_of_types = []
    list_of_nodes.append( {"label": "All", "value": "All"})
    for node in G.nodes():
        
        G.nodes[node]["pos"]=pos[node]
        title=G.nodes[node].get("title") if G.nodes[node].get("title") else '{"type":"unknown","id":"dunno","label":"dunno"}'
        node_det = json.loads(title.replace('<br>','').replace("'",'"').replace('True','true').replace('False','false'))
        list_of_types.append(G.nodes[node].get("type"))
        if node_det.get("type") != "service":
            list_of_nodes.append({"label": node_det.get('id').replace('~',' -> '), "value": node_det.get('id')})
            
        
    list_of_types = list(sorted(set(list_of_types)))
    

    traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
    ############################################################################################################################################################

    index = 0
    for edge in G.edges:
        #print(edge)
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        weight = 1
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': weight},
                           marker=dict(color="#dddddd"),
                           #line_shape='spline',
                           opacity=1)
        traceRecode.append(trace)
        index = index + 1
    ###############################################################################################################################################################
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 20, 'color': 'LightSkyBlue'})

    index = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        #print(G.nodes[node])
        title=G.nodes[node].get("title") if G.nodes[node].get("title") else '{"type":"unknown","id":"dunno","label":"dunno"}'
        hovertext = title #.replace(",",",<br>").replace("{","{<br>").replace("}","<br>}")
        #print(G.nodes[node]['title'].replace('<br>','').replace("'",'"'))
        text = json.loads(title.replace('<br>','').replace("'",'"').replace('True','true').replace('False','false'))["label"]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        #node_trace['marker'] = tuple(["img/dashboard"])
        index = index + 1

    traceRecode.append(node_trace)
    ################################################################################################################################################################
    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'},
                                    opacity=0)

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_json = json.loads(G.edges[edge]["title"].replace('<br>','').replace("'",'"').replace('True','true').replace('False','false'))
        #print(edge_json)
        hovertext = {"from": edge_json['from'], "to" : edge_json['to'] , "type" : edge_json['label']}
        hovertext = G.edges[edge]["title"]
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(middle_hover_trace)
    #################################################################################################################################################################
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Interactive Graph Visualization', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=1000,
                            clickmode='event+select',
                            annotations=[
                                dict(
                                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                    showarrow=True,
                                    arrowhead=1,
                                    arrowsize=1,
                                    arrowwidth=1,
                                    opacity=1
                                ) for edge in G.edges]
                            )}
    return figure

######################################################################################################################################################################
# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'white-space': 'pre-line',
        'word-wrap': 'break-word'
    }
}

app.layout = html.Div([
    #########################Title
    html.Div(
             className="row",
             style={'textAlign': "center"},
             children=[
                 html.Div(
                    className="row",
                    children=[
                        html.H1("Aiven Network Graph"),
                        html.Div(
                            className="twelve columns",
                            children=[
                                dcc.Markdown(d("""
                                **Node To Search**
                                Input the Node Id to visualize.
                                """)),
                                dcc.Dropdown(id="input1", options=[{"label": "All","value": "All"}], placeholder="Select a node",),
                                #dcc.Input(id="input1", type="text", placeholder="Account"),
                                html.Div(id="output")
                            ],
                            style={'height': '100px', "width":"1500px"}
                        )
                    ]
                ),
             ]
        ),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(ACCOUNT, TYPESTOFILTER))],
            ),

            #########################################right side two output component
            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Select Node Types**

                            To filter particular services/node types.
                            """)),
                            dcc.Checklist(id='checkbox', options=[{"label": "All","value": "All"}])
                        ],
                        style={'height': '500px', "width":"300px"}),
                        
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Hover Data**
                            
                            Mouse over values in the graph.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ],
                        style={'height': '800px', "width":"300px"})
                ]
            )
        ]
    )
])


@app.callback(
    dash.dependencies.Output('checkbox', 'options'),
    dash.dependencies.Input('input1', 'search_value')
    )
def update_checkbox(input1):
    global list_of_types
    #print(list_of_nodes)
    if input1 == None:
        input1 = ''
    if list_of_types == None:
        list_of_types = [{"label": "All","value": "All"}]

    return [{"label":o, "value":o} for o in list_of_types]

@app.callback(
    dash.dependencies.Output('input1', 'options'),
    dash.dependencies.Input('input1', 'search_value')
    )
def update_drowpdown(input1):
    global list_of_nodes
    #print(list_of_nodes)
    if input1 == None:
        input1 = ''
    if list_of_nodes == None:
        list_of_nodes = [{"label": "All","value": "All"}]
    
    return list_of_nodes

###################################callback for left side components
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('input1', 'value'), dash.dependencies.Input('checkbox', 'value')])

def update_output(input1, chkvalue):
    ACCOUNT = input1
    TYPESTOFILTER = chkvalue
    return network_graph(input1, chkvalue)
    # to update the global variable of YEAR and ACCOUNT
################################callback for right side components
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    #print(hoverData)
    if hoverData:
        hoverData = hoverData["points"][0].get("hovertext")
        if hoverData:
            hoverData = hoverData.replace('<br>','').replace("'",'"').replace('True','true').replace('False','false')
            hoverData = json.loads(hoverData)
    return json.dumps(hoverData, indent=2)




if __name__ == '__main__':
    app.run_server(debug=True)