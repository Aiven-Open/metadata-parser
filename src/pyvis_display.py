import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from networkx.readwrite.gml import write_gml
from pyvis.network import Network

colors = {}
colors["service"] = "#ff0000"
colors["topic"] = "#00ff00"
colors["topic-acl"] = "#003300"
colors["database"] = "#0000ff"
colors["schema"] = "#000077"
colors["table"] = "#000033"
colors["view"] = "#000033"
colors["table column"] = "#000011"
colors["user"] = "#0000AA"
colors["flink table"] = "#AA0000"
colors["flink job"] = "#660000"
colors["flink table column"] = "#330000"
colors["external_endpoint"] = "#cc0000"
colors["kafka-connect"] = "#dd0000"
colors["external-postgresql"] = "#0000ff"
colors["external-postgresql-schema"] = "#0000ff"
colors["external-postgresql-table"] = "#0000ff"
colors["dashboard"] = "#0000cc"
colors["datasource"] = "#0000cc"
colors["index"] = "#0000cc"
colors["connection-error"] = "#0000cc"
colors["tag"] = "#0000cc"
colors["backup"] = "cccccc"
colors["consumer_group"] = "#0000cc"
colors["partition"] = "#0000cc"
colors["service_nodes"] = "#0000cc"
colors["service_nodes"] = "#0000cc"
colors["reference"] = "#0000cc"
colors["sql_reference"] = "#0000cc"


sizes = {}

sizes["service"] = 30
sizes["topic"] = 15
sizes["topic-acl"] = 15
sizes["database"] = 20
sizes["schema"] = 15
sizes["table"] = 15
sizes["view"] = 15
sizes["user"] = 15
sizes["flink table"] = 15
sizes["flink job"] = 25
sizes["flink table column"] = 10
sizes["table column"] = 10
sizes["external_endpoint"] = 30
sizes["kafka-connect"] = 25
sizes["external-postgresql"] = 30
sizes["external-postgresql-schema"] = 15
sizes["external-postgresql-table"] = 15
sizes["dashboard"] = 15
sizes["datasource"] = 15
sizes["index"] = 15
sizes["connection-error"] = 15
sizes["tag"] = 10
sizes["backup"] = 10
sizes["consumer_group"] = 10
sizes["partition"] = 10
sizes["service_node"] = 10
sizes["reference"] = 10
sizes["sql_reference"] = 10


images = {}
images["service"] = "img/monitor.png"
images["topic"] = "img/table.png"
images["topic-acl"] = "img/document.png"
images["acl"] = "img/document.png"
images["database"] = "img/database.png"
images["schema"] = "img/document.png"
images["table"] = "img/table.png"
images["view"] = "img/table.png"
images["user"] = "img/user.png"
images["flink table"] = "img/table.png"
images["flink job"] = "img/engineering.png"
images["flink table column"] = "img/layout.png"
images["table column"] = "img/layout.png"
images["external_endpoint"] = "img/ext-monitor.png"
images["kafka-connect"] = "img/engineering.png"
images["external-postgresql"] = "img/service.png"
images["external-postgresql-schema"] = "img/document.png"
images["external-postgresql-table"] = "img/table.png"
images["external-postgresql-database"] = "img/table.png"
images["dashboard"] = "img/dashboard.png"
images["datasource"] = "img/data-source.png"
images["index"] = "img/table.png"
images["connection-error"] = "img/warning.png"
images["tag"] = "img/tag.png"
images["backup"] = "img/database.png"
images["consumer_group"] = "img/user.png"
images["partition"] = "img/layout.png"
images["service_node"] = "img/servers.png"
images["reference"] = "img/reference.png"
images["sql_reference"] = "img/sql_reference.png"


def pyviz_graphy(nodes, edges):

    print()
    print("Calulating network graph")
    # g = Network(height='750px', width='100%')
    g = nx.DiGraph()
    for node in nodes:

        if isinstance(node, dict) and node["id"] is None:
            print(f"Ignoring node {node} - it has id None")
            continue
        img = (
            images.get(node["type"])
            if images.get(node["type"])
            else "unknown.png"
        )
        if node["type"] == "service":
            img = "img/services/" + node["service_type"] + ".svg"

        nodesize = sizes.get(node["type"]) if sizes.get(node["type"]) else 10
        nodecolor = (
            colors.get(node["type"]) if colors.get(node["type"]) else "#cccccc"
        )
        g.add_node(
            node["id"],
            color=nodecolor,
            title=str(node)
            .replace(",", ",<br>")
            .replace("{", "{<br>")
            .replace("}", "<br>}"),
            size=nodesize,
            label=node["label"],
            shape="image",
            image=img,
            type=node["type"] if node["type"] else "NoNodeType",
            service_type=node["service_type"],
            id=node["id"],
        )
        if node["id"] == None:
            print(node)

    for edge in edges:
        # print(str(edge))
        if edge["from"] is None or edge["to"] is None:
            print(f"Ignoring edge {edge} - one or both ends is None")
            continue
        g.add_edge(
            edge["from"],
            edge["to"],
            title=str(edge)
            .replace(",", ",<br>")
            .replace("{", "{<br>")
            .replace("}", "<br>}"),
            physics=False,
        )
        if edge["from"] == None or edge["to"] == None:
            print(edge)

    print()
    print("Writing DOT file")
    try:
        write_dot(g, "graph_data.dot")
    except Exception as err:
        print(f"Error writing DOT file: {err.__class__.__name__} {err}")

    print("Writing GML file")
    try:
        write_gml(g, "graph_data.gml")
    except Exception as err:
        print(f"Error writing GML file: {err.__class__.__name__} {err}")

    print("Writing NX file")
    try:
        nt = Network(height="1000px", width="1000px", font_color="#000000")
        nt.from_nx(g)
        # nt.show_buttons()
        nt.show_buttons()
        nt.show("nx.html")
        # print (g.nodes)
    except Exception as err:
        print(f"Error writing NX file: {err.__class__.__name__} {err}")

    ## All images are taken from https://www.flaticon.com/
