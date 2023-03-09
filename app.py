"""Dash app to show the network"""
import json
from textwrap import dedent as d
import dash
from dash import dcc
from dash import html
import networkx as nx
import plotly.graph_objs as go


from networkx.readwrite.gml import read_gml
from networkx.algorithms.components import node_connected_component

# import the css template, and pass the css template into dash
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Aiven Network"

ACCOUNT = None
TYPESTOFILTER = None

LIST_OF_NODES = []
LIST_OF_TYPES = []

##################################################
##################################################
##################################################


def network_graph(node_to_filter, types_to_filter):
    """Manages the graph"""

    global LIST_OF_NODES
    global LIST_OF_TYPES
    graph = read_gml("graph_data.gml")
    not_services = (
        n for n in graph if graph.nodes[n].get("type") != "service"
    )

    if node_to_filter and node_to_filter != "All":
        conn = node_connected_component(
            graph.to_undirected().subgraph(not_services), node_to_filter
        )
        graph = graph.subgraph(conn)
    if types_to_filter:
        sel_nodes = (
            n for n in graph if graph.nodes[n].get("type") in types_to_filter
        )
        graph = graph.subgraph(sel_nodes)
    pos = nx.spring_layout(graph)
    # pos = nx.layout.spring_layout(G)

    LIST_OF_NODES = []
    LIST_OF_TYPES = []
    LIST_OF_NODES.append({"label": "All", "value": "All"})
    for node in graph.nodes():
        graph.nodes[node]["pos"] = pos[node]

        title = (
            graph.nodes[node].get("title")
            if graph.nodes[node].get("title")
            else '"{"type":"unknown","id":"dunno","label":"dunno"}"'
        )

        # node_det = json.loads('{"id":"here"}')
        node_det = json.loads(
            title.replace("<br>", "")
            .replace("'", '"')
            .replace("True", "true")
            .replace("False", "false")
            .replace("None", "[]")[1:-1]
        )
        LIST_OF_TYPES.append(
            graph.nodes[node].get("type")
            if graph.nodes[node].get("type")
            else "dunno"
        )
        if node_det.get("type") != "service":
            LIST_OF_NODES.append(
                {
                    "label": node_det.get("id").replace("~", " -> "),
                    "value": '"' + node_det.get("id") + '"',
                }
            )
            # print(node_det.get("id"))

    LIST_OF_TYPES = list(sorted(set(LIST_OF_TYPES)))

    trace_record = []  # contains edge_trace, node_trace, middle_node_trace
    ####################################################
    ####################################################

    index = 0
    for edge in graph.edges:
        # print(edge)
        x_0, y_0 = graph.nodes[edge[0]]["pos"]
        x_1, y_1 = graph.nodes[edge[1]]["pos"]
        weight = 1
        trace = go.Scatter(
            x=tuple([x_0, x_1, None]),
            y=tuple([y_0, y_1, None]),
            mode="lines",
            line={"width": weight},
            marker=dict(color="#dddddd"),
            # line_shape='spline',
            opacity=1,
        )
        trace_record.append(trace)
        index = index + 1
    ######################################################
    ######################################################

    node_trace = go.Scatter(
        x=[],
        y=[],
        hovertext=[],
        text=[],
        mode="markers+text",
        textposition="bottom center",
        hoverinfo="text",
        marker={"size": 20, "color": "LightSkyBlue"},
    )

    index = 0
    for node in graph.nodes():
        x_pos, y_pos = graph.nodes[node]["pos"]
        # print(graph.nodes[node])
        title = (
            graph.nodes[node].get("title")
            if graph.nodes[node].get("title")
            else '"{"type":"unknown","id":"dunno","label":"dunno"}"'
        )
        hovertext = title
        text = json.loads(
            title.replace("<br>", "")
            .replace("'", '"')
            .replace("True", "true")
            .replace("False", "false")
            .replace("None", "[]")[1:-1]
        )["label"]
        node_trace["x"] += tuple([x_pos])
        node_trace["y"] += tuple([y_pos])
        node_trace["hovertext"] += tuple([hovertext])
        node_trace["text"] += tuple([text])
        # node_trace['marker'] = tuple(["img/dashboard"])
        index = index + 1

    trace_record.append(node_trace)

    ########################################################

    middle_hover_trace = go.Scatter(
        x=[],
        y=[],
        hovertext=[],
        mode="markers",
        hoverinfo="text",
        marker={"size": 20, "color": "LightSkyBlue"},
        opacity=0,
    )

    index = 0
    for edge in graph.edges:
        x_0, y_0 = graph.nodes[edge[0]]["pos"]
        x_1, y_1 = graph.nodes[edge[1]]["pos"]

        edge_json = json.loads(
            graph.edges[edge]["title"]
            .replace("<br>", "")
            .replace("'", '"')
            .replace("True", "true")
            .replace("False", "false")
            .replace("None", "[]")[1:-1]
        )
        # print(edge_json)
        hovertext = {
            "from": edge_json["from"],
            "to": edge_json["to"],
            "type": edge_json.get("label")
            if edge_json.get("label")
            else "nolabel",
        }
        hovertext = graph.edges[edge]["title"]
        middle_hover_trace["x"] += tuple([(x_0 + x_1) / 2])
        middle_hover_trace["y"] += tuple([(y_0 + y_1) / 2])
        middle_hover_trace["hovertext"] += tuple([hovertext])
        index = index + 1

    trace_record.append(middle_hover_trace)
    ########################################################
    figure = {
        "data": trace_record,
        "layout": go.Layout(
            title="Interactive Graph Visualization",
            showlegend=False,
            hovermode="closest",
            margin={"b": 40, "l": 40, "r": 40, "t": 40},
            xaxis={
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
            },
            yaxis={
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
            },
            height=1000,
            clickmode="event+select",
            annotations=[
                dict(
                    ax=(
                        graph.nodes[edge[0]]["pos"][0]
                        + graph.nodes[edge[1]]["pos"][0]
                    )
                    / 2,
                    ay=(
                        graph.nodes[edge[0]]["pos"][1]
                        + graph.nodes[edge[1]]["pos"][1]
                    )
                    / 2,
                    axref="x",
                    ayref="y",
                    x=(
                        graph.nodes[edge[1]]["pos"][0] * 3
                        + graph.nodes[edge[0]]["pos"][0]
                    )
                    / 4,
                    y=(
                        graph.nodes[edge[1]]["pos"][1] * 3
                        + graph.nodes[edge[0]]["pos"][1]
                    )
                    / 4,
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=1,
                    opacity=1,
                )
                for edge in graph.edges
            ],
        ),
    }
    return figure


##########################################################
# styles: for right side hover/click component
styles = {
    "pre": {
        "border": "thin lightgrey solid",
        "overflowX": "scroll",
        "white-space": "pre-line",
        "word-wrap": "break-word",
    }
}

app.layout = html.Div(
    [
        # Title
        html.Div(
            className="row",
            style={"textAlign": "center"},
            children=[
                html.Div(
                    className="row",
                    children=[
                        html.H1("Aiven Network Graph"),
                        html.Div(
                            className="twelve columns",
                            children=[
                                dcc.Markdown(
                                    d(
                                        """
                                **Node To Search**
                                Input the Node Id to visualize.
                                """
                                    )
                                ),
                                dcc.Dropdown(
                                    id="input1",
                                    options=[{"label": "All", "value": "All"}],
                                    placeholder="Select a node",
                                ),
                                html.Div(id="output"),
                            ],
                            style={"height": "100px", "width": "1500px"},
                        ),
                    ],
                ),
            ],
        ),
        # define the row
        html.Div(
            className="row",
            children=[
                # middle graph component
                html.Div(
                    className="eight columns",
                    children=[
                        dcc.Graph(
                            id="my-graph",
                            figure=network_graph(ACCOUNT, TYPESTOFILTER),
                        )
                    ],
                ),
                # right side two output component
                html.Div(
                    className="two columns",
                    children=[
                        html.Div(
                            className="twelve columns",
                            children=[
                                dcc.Markdown(
                                    d(
                                        """
                                        **Select Node Types**

                                        To filter particular
                                        services/node types.
                                        """
                                    )
                                ),
                                dcc.Checklist(
                                    id="checkbox",
                                    options=[{"label": "All", "value": "All"}],
                                ),
                            ],
                            style={"height": "500px", "width": "300px"},
                        ),
                        html.Div(
                            className="twelve columns",
                            children=[
                                dcc.Markdown(
                                    d(
                                        """
                                        **Hover Data**
                                        Mouse over values in the graph.
                                        """
                                    )
                                ),
                                html.Pre(id="hover-data", style=styles["pre"]),
                            ],
                            style={"height": "800px", "width": "300px"},
                        ),
                    ],
                ),
            ],
        ),
    ]
)


@app.callback(
    dash.dependencies.Output("checkbox", "options"),
    dash.dependencies.Input("input1", "search_value"),
)
def update_checkbox(input1):
    """Updates the list of options in the checkbox"""
    global LIST_OF_TYPES
    # print(LIST_OF_NODES)
    if input1 is None:
        input1 = ""
    if LIST_OF_TYPES is None:
        LIST_OF_TYPES = [{"label": "All", "value": "All"}]

    return [{"label": o, "value": o} for o in LIST_OF_TYPES]


@app.callback(
    dash.dependencies.Output("input1", "options"),
    dash.dependencies.Input("input1", "search_value"),
)
def update_drowpdown(input1):
    """Updates the dropdown"""
    global LIST_OF_NODES
    # print(LIST_OF_NODES)
    if input1 is None:
        input1 = ""
    if LIST_OF_NODES is None:
        LIST_OF_NODES = [{"label": "All", "value": "All"}]

    return LIST_OF_NODES


# callback for left side components
@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [
        dash.dependencies.Input("input1", "value"),
        dash.dependencies.Input("checkbox", "value"),
    ],
)
def update_output(input1, chkvalue):
    """Updates the output"""
    global ACCOUNT
    global TYPESTOFILTER
    ACCOUNT = input1
    TYPESTOFILTER = chkvalue
    return network_graph(input1, chkvalue)
    # to update the global variable of TYPESTOFILTER and ACCOUNT


# callback for right side components
@app.callback(
    dash.dependencies.Output("hover-data", "children"),
    [dash.dependencies.Input("my-graph", "hoverData")],
)
def display_hover_data(hover_data):
    """Updates the hover info"""
    # print(hover_data)
    if hover_data:
        hover_data = hover_data["points"][0].get("hovertext")
        if hover_data:
            hover_data = (
                hover_data.replace("<br>", "")
                .replace("'", '"')
                .replace("True", "true")
                .replace("False", "false")
                .replace("None", "[]")[1:-1]
            )
            hover_data = json.loads(hover_data)
    return json.dumps(hover_data, indent=2)


if __name__ == "__main__":
    app.run_server(debug=True)
