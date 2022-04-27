import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from networkx.readwrite.gml import write_gml
from pyvis.network import Network

colors = {}
colors["service"]="#ff0000"
colors["topic"]="#00ff00"
colors["topic-acl"]="#003300"
colors["database"]="#0000ff"
colors["schema"]="#000077"
colors["table"]="#000033"
colors["table column"]="#000011"
colors["user"]="#0000AA"
colors["flink table"]="#AA0000"
colors["flink job"]="#660000"
colors["flink table column"]="#330000"
colors["external_endpoint"]="#cc0000"
colors["kafka-connect"]="#dd0000"
colors["external-postgresql"]="#0000ff"
colors["external-postgresql-schema"]="#0000ff"
colors["external-postgresql-table"]="#0000ff"
colors["dashboard"]="#0000cc"
colors["datasource"]="#0000cc"
colors["index"]="#0000cc"
colors["connection-error"]="#0000cc"
colors["tag"]="#0000cc"
colors["backup"]="#0000cc"


sizes = {}

sizes["service"]=30
sizes["topic"]=15
sizes["topic-acl"]=15
sizes["database"]=20
sizes["schema"]=15
sizes["table"]=15
sizes["user"]=15
sizes["flink table"]=15
sizes["flink job"]=25
sizes["flink table column"]=10
sizes["table column"]=10
sizes["external_endpoint"]=30
sizes["kafka-connect"]=25
sizes["external-postgresql"]=30
sizes["external-postgresql-schema"]=15
sizes["external-postgresql-table"]=15
sizes["dashboard"]=15
sizes["datasource"]=15
sizes["index"]=15
sizes["connection-error"]=15
sizes["tag"]=10
sizes["backup"]=10


images = {}
images["service"]="img/monitor.png"
images["topic"]="img/table.png"
images["topic-acl"]="img/document.png"
images["database"]="img/database.png"
images["schema"]="img/document.png"
images["table"]="img/table.png"
images["user"]="img/user.png"
images["flink table"]="img/table.png"
images["flink job"]="img/engineering.png"
images["flink table column"]="img/layout.png"
images["table column"]="img/layout.png"
images["external_endpoint"]="img/ext-monitor.png"
images["kafka-connect"]="img/engineering.png"
images["external-postgresql"]="img/service.png"
images["external-postgresql-schema"]="img/document.png"
images["external-postgresql-table"]="img/table.png"
images["external-postgresql-database"]="img/table.png"
images["dashboard"]="img/dashboard.png"
images["datasource"]="img/data-source.png"
images["index"]="img/table.png"
images["connection-error"]="img/warning.png"
images["tag"]="img/tag.png"
images["backup"]="img/database.png"

def pyviz_graphy(nodes, edges):

    #g = Network(height='750px', width='100%')
    g = nx.DiGraph()
    for node in nodes:
        img = images.get(node["type"]) if images.get(node["type"]) else 'unknown.png'
        if node["type"] == "service":
            img = "img/services/"+node["service_type"]+".svg"
        
        nodesize = sizes.get(node["type"]) if sizes.get(node["type"]) else 10
        nodecolor = colors.get(node["type"]) if colors.get(node["type"])  else "#cccccc"
        g.add_node(node["id"], color=nodecolor, 
            title=str(node).replace(",",",<br>").replace("{","{<br>").replace("}","<br>}"), 
            size=nodesize, label=node["label"], shape="image", image=img, type=node["type"] if node["type"] else 'NoNodeType', 
            service_type=node["service_type"], id=node["id"])
        if node["id"] == None:
            print(node)
    for edge in edges:
        g.add_edge(edge["from"], edge["to"], title=str(edge).replace(",",",<br>").replace("{","{<br>").replace("}","<br>}"), physics=False)
        if edge["from"] == None or edge["to"] == None:
            print(edge)
    
    
    
    write_dot(g, 'graph_data.dot')
    write_gml(g, 'graph_data.gml')
    nt = Network(height='1200px', width='1600px', font_color="#000000")
    nt.from_nx(g)
    
    #nt.show_buttons()
    nt.show_buttons()
    nt.show('nx.html')
    #print (g.nodes)

    '''
    not_services =  (n for n in g if g.nodes[n]['type'] != 'service')
    services =  (n for n in g if g.nodes[n]['type'] == 'service')
    
    g_connected = node_connected_component(g.to_undirected().subgraph(not_services),'pg~demo-pg~schema~public~table~pasta')
    #g_connected = (n for n in g_connected if g_connected[n]['type'] in ('service',''))
    g_subgraph = g.subgraph(g_connected)
    nt = Network(height='1200px', width='800px', font_color="#000000")
    nt.from_nx(g_subgraph)
    nt.show('filtered.html')
    content = '<table><tr><td ><div id = "mynetwork"></div></td><td ><div><table style="order-spacing: 0px; border-collapse: collapse; width: 100%; max-width: 100%; margin-bottom: 15px; background-color: transparent; text-align: left;">' \
              '<tr><th style="font-weight: bold; border: 1px solid #cccccc; padding: 8px;"><b>Img</b></th><th style="font-weight: bold; border: 1px solid #cccccc; padding: 8px;"><b>Node type</b></th><th style="font-weight: bold; border: 1px solid #cccccc; padding: 8px;"><b>Node Label</b></th><th style="font-weight: bold; border: 1px solid #cccccc; padding: 8px;"><b>Service type</b></td><th style="font-weight: bold; border: 1px solid #cccccc; padding: 8px;"><b>Service Name</b></th></tr>'
    for node in g_subgraph.nodes:
        
        content = content + '<tr><td style="border: 1px solid #cccccc; padding: 8px;"><img src="'+g_subgraph.nodes[node]["image"]+'" width="20px" ></img></td><td style="border: 1px solid #cccccc; padding: 8px;">'+g_subgraph.nodes[node]["type"]+'</td><td style="border: 1px solid #cccccc; padding: 8px;">'+g_subgraph.nodes[node]["label"]+'</td><td style="border: 1px solid #cccccc; padding: 8px;">'+g_subgraph.nodes[node]["service_type"]+'</td><td style="border: 1px solid #cccccc; padding: 8px;">'+g_subgraph.nodes[node]["id"].split('~')[1]+'</td></tr>'
    content = content + '</table></div></table>'
    file = open("filtered.html", "r")
    
        
    replacement = ""
    # using the for loop
    for line in file:
        line = line.strip()
        changes = line.replace('<div id = "mynetwork"></div>', content)
        replacement = replacement + changes + "\n"

    file.close()
    # opening the file in write mode
    fout = open("filtered.html", "w")
    fout.write(replacement)
    fout.close()
    '''