import psycopg2
import pymysql
import re
import requests
import json
import urllib.parse

SERVICE_MAP = {}

# This method parses all services to indentify internal IPs or hostnames
def populate_service_map(self, service_type, service_name, project):
    global SERVICE_MAP

    service = self.get_service(project=project, service=service_name)
    if service["state"]=="RUNNING":
        if service_type == 'kafka':
            SERVICE_MAP[service["service_uri_params"]["host"]]=service_name
            for url in service["connection_info"]["kafka"]:
                host = url.split(':')[0]
                SERVICE_MAP[host]=service_name
        if service_type == 'flink':
            SERVICE_MAP[service["service_uri_params"]["host"]]=service_name
            for url in service["connection_info"]["flink"]:
                host = url.split(':')[0]
                SERVICE_MAP[host]=service_name
        if service_type == 'pg':
            SERVICE_MAP[service["connection_info"]["pg_params"][0]["host"]]=service_name
            for component in service["components"]:
                if component["component"]=="pg":
                    SERVICE_MAP[component["host"]]=service_name
        if service_type == 'grafana':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'opensearch':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'elasticsearch':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'grafana':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name

        if service_type == 'mysql':
            SERVICE_MAP[service["connection_info"]["mysql_params"][0]["host"]]=service_name
        if service_type == 'kafka_connect':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'mirrormaker':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'clickhouse':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'cassandra':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name

        if service_type == 'redis':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name

        if service_type == 'm3db':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name

        if service_type == 'm3aggregator':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name

        if service_type == 'm3coordinator':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
        
        if service_type == 'influxdb':
            host=service["service_uri_params"]["host"]
            SERVICE_MAP[host]=service_name
    
    

def explore (self, service_type, service_name, project):
    edges = []
    nodes = []
    
    global SERVICE_MAP

    host = "no-host"
    service = self.get_service(project=project, service=service_name)
    print (service_name + " " + service_type)
    if service["state"]=="RUNNING":
        cloud=service["cloud_name"]
        plan=service["plan"]
        if service_type == 'kafka':
            (newnodes, newedges) = explore_kafka(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]
        if service_type == 'flink':
            (newnodes, newedges) = explore_flink(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=443
            
        if service_type == 'pg':
            #print (service)
            (newnodes, newedges) = explore_pg(self, service_name, project)
            host=service["connection_info"]["pg_params"][0]["host"]
            port=service["connection_info"]["pg_params"][0]["port"]
            
        if service_type == 'mysql':
            (newnodes, newedges) = explore_mysql(self, service_name, project)
            host=service["connection_info"]["mysql_params"][0]["host"]
            port=service["connection_info"]["mysql_params"][0]["port"]
        
        if service_type == 'grafana':
            (newnodes, newedges) = explore_grafana(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]
        
        if service_type == 'opensearch':
            (newnodes, newedges) = explore_opensearch(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]
        
        if service_type == 'elasticsearch':
            (newnodes, newedges) = explore_elasticsearch(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]

        if service_type == 'kafka_connect':
            (newnodes, newedges) = explore_kafka_connect(self, service_name, project, "kafka_connect")
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]
        
        if service_type == 'kafka_mirrormaker':
            (newnodes, newedges) = explore_mirrormaker(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=443
        
        if service_type == 'clickhouse':
            (newnodes, newedges) = explore_clickhouse(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]
        
        if service_type == 'cassandra':
            (newnodes, newedges) = explore_cassandra(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]

        if service_type == 'redis':
            (newnodes, newedges) = explore_redis(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]

        if service_type == 'm3db':
            (newnodes, newedges) = explore_m3db(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]

        if service_type == 'm3aggregator':
            (newnodes, newedges) = explore_m3aggregator(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]

        if service_type == 'm3coordinator':
            (newnodes, newedges) = explore_m3coordinator(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]
        
        if service_type == 'influxdb':
            (newnodes, newedges) = explore_influxdb(self, service_name, project)
            host=service["service_uri_params"]["host"]
            port=service["service_uri_params"]["port"]

        # Disabling this piece for now since it's taking looooong time
        integrations = self.get_service_integrations(service=service_name, project=project)
        for integration in integrations:
            if(integration["enabled"]==True):
                
                edges.append({"from":integration["source_service"], "to":integration["dest_service"], "main_type":"integration", "integration_type":integration["integration_type"], "label":integration["integration_type"], "integration_id":integration["service_integration_id"]})
        
        nodes.append({"id":service_name,"host":host, "port":port,"cloud":cloud, "plan":plan, "service_type":service_type, "type":"service", "label":service_name})

        # Looking for service tags

        tags = self.list_service_tags(service=service_name, project=project)
        
        for key, value in tags["tags"].items():            
            nodes.append({"id":"tag~id~"+key+"~value~"+value, "service_type": "tag", "type": "tag", "label":key+"="+value})
            edges.append({"from": service_name, "to": "tag~id~"+key+"~value~"+value, "label": "tag"})
        
        if newnodes != None:
            nodes = nodes + newnodes
        if newedges != None:
            edges = edges + newedges
        
    return nodes, edges

def explore_influxdb (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_elasticsearch (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_m3aggregator (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_m3coordinator (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_clickhouse (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_mirrormaker (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_m3db (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges


def explore_redis (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges

def explore_cassandra (self, service_name, project):
    nodes = []
    edges = []
    #TODO
    return nodes, edges


def explore_grafana(self, service_name, project):
    nodes = []
    edges = []
    service = self.get_service(project=project, service=service_name)
    users = service["users"]
    password = "fake"

    # Parse the users
    for user in users:
        # Create node per user
        nodes.append({"id":"grafana~"+service_name+"~user~"+user["username"],"user-type":user["type"], "service_type":"grafana", "type":"user", "label":user["username"]})
        # Create edge between user and service
        edges.append({"from":"grafana~"+service_name+"~user~"+user["username"], "to":service_name, "label": "user"})

        #Take the password of the avnadmin user for further ispection
        if user["username"]== "avnadmin":
            password = user["password"]
    # Define the base URL
    base_url = "https://"+service["service_uri_params"]["host"]+":443"

    # Get datasources
    datasources_map = {}
    datasources = requests.get(base_url+"/api/datasources", auth=("avnadmin", password))

    for datasource in json.loads(datasources.text):
        # Create a map of the datasources id -> name
        datasources_map[datasource["uid"]]=datasource["name"]
        # Create node per datasource
        nodes.append({"id":"grafana~"+service_name+"~datasource~"+datasource["name"],"datasource-type":datasource["type"], "service_type":"grafana", "type":"datasource", "label":datasource["name"], "tgt_url":datasource["url"]})
        # Create edge between datasource and service
        edges.append({"from":"grafana~"+service_name+"~datasource~"+datasource["name"], "to":service_name, "label": "datasource"})
        
        # Look for target host
        target_host = datasource["url"].replace("http://","").replace("https://","").split(':')[0]
        
        # Check if the host in the list of target hosts already
        dest_service = SERVICE_MAP.get(target_host)
        # If host doesn't exist yet
        if dest_service == None:
            # Create new node for external service host
            nodes.append({"id":"ext-src-"+target_host, "service_type": "ext-service", "type": "external-service", "label":target_host})
            # Create new edge between external service host and datasource
            edges.append({"from":"grafana~"+service_name+"~datasource~"+datasource["name"], "to":"ext-src-"+target_host, "label": "datasource"})
        else:
            # Create new edge between existing service host and datasource
            edges.append({"from":"grafana~"+service_name+"~datasource~"+datasource["name"], "to":dest_service, "label": "datasource"})
        
        # In case is PG
        if datasource["type"] == "postgres":
            if dest_service == None:
                # Creates a database node in the external service
                nodes.append({"id":"ext-src-"+dest_service+"~db~"+datasource["database"], "service_type": "ext-pg", "type": "database", "label":datasource["database"]})
                # Creates an edge between the database and the datasource
                edges.append({"from":"grafana~"+service_name+"~datasource~"+datasource["name"], "to":"ext-src-"+dest_service+"~db~"+datasource["database"], "label": "datasource"})
            else:
                # Creates an edge between the database and the datasource
                edges.append({"from":"grafana~"+service_name+"~datasource~"+datasource["name"], "to":"pg~"+dest_service+"~database~"+datasource["database"], "label": "datasource"})

    
    # getting dashboards
    dashboards = requests.get(base_url+"/api/search?dash-folder", auth=("avnadmin", password))

    for dashboard in json.loads(dashboards.text):
        # Creates a node for the dashboard 
        nodes.append({"id":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "service_type":"grafana", "type":"dashboard", "label":dashboard["title"]})
        # Creates an edge between service name and dashboard
        edges.append({"from":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "to":service_name, "label": "dashboard"})
        # gets the dashboard details

        dashboard_details = requests.get(base_url+"/api/dashboards/uid/"+dashboard["uid"], auth=("avnadmin", password))

        dash_details = json.loads(dashboard_details.text)
        # Adds edge between dashboard and creator
        edges.append({"from":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "to":"grafana~"+service_name+"~user~"+dash_details["meta"]["createdBy"], "type":"dashboard-creator", "label": "dashboard-creator"})
        
        # A dashboard can have rows defined or not
        if dash_details["dashboard"].get("rows") != None:
            for row in dash_details["dashboard"]["rows"]:
                # Looks for panels in the dashboard
                for panel in row["panels"]:

                    if isinstance(panel["datasource"], str):
                        datasource = panel["datasource"]
                        # Creates an edge between the dashboard and datasource
                        edges.append({"from":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "to":"grafana~"+service_name+"~datasource~"+datasource, "label": "dashboard datasource"})
                    else:
                        datasource = panel["datasource"]["uid"]
                        # Creates an edge between the dashboard and datasource
                        edges.append({"from":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "to":"grafana~"+service_name+"~datasource~"+datasources_map[datasource], "label": "dashboard datasource"})
                    #TODO explore all columns in a dashboard panel
        else:
            for panel in dash_details["dashboard"]["panels"]:
                if isinstance(panel["datasource"], str):
                    datasource = panel["datasource"]
                    # Creates an edge between the dashboard and datasource
                    edges.append({"from":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "to":"grafana~"+service_name+"~datasource~"+datasource, "label": "dashboard datasource"})
                elif isinstance(panel["datasource"], dict):
                    datasource = panel["datasource"]["uid"]
                    # Creates an edge between the dashboard and datasource
                    edges.append({"from":"grafana~"+service_name+"~dashboard~"+dashboard["title"], "to":"grafana~"+service_name+"~datasource~"+datasources_map[datasource], "label": "dashboard datasource"})
                #TODO explore all columns in a dashboard panel
    return nodes, edges

def explore_opensearch(self, service_name, project):
    nodes = []
    edges = []
    # Getting indexes
    indexes = self.get_service_indexes(project=project, service=service_name)
    for index in indexes:
        
        # CReating node for index
        nodes.append({"id":"opensearch~"+service_name+"~index~"+index["index_name"], "service_type":"opensearch", "type":"index", "label":index["index_name"], "health": index["health"], "replicas": index["number_of_replicas"], "shards": index["number_of_shards"]})
        # Creating edge between index and service
        edges.append({"from":"opensearch~"+service_name+"~index~"+index["index_name"], "to":service_name, "label": "index"})
    
    # TODO parse more stuff
    return nodes, edges

def explore_flink(self, service_name, project):
    nodes = []
    edges = []
    tables = self.list_flink_tables(service=service_name, project=project)
    tables_map = {}

    # Checking each table definition in Flink
    for table in tables:

        # Creating a node beween table and service
        nodes.append({"id":"flink~"+service_name+'~table~'+table["table_name"], "service_type": "flink", "type": "flink table", "table_id":table["table_id"],"label":table["table_name"]})
        # For each column in the table
        for column in table["columns"]:
            # Create node for the olumn
            nodes.append({"id":"flink~"+service_name+'~table~'+table["table_name"]+'~column~'+column["name"], "service_type": "flink", "type": "flink table column", "table_id":table["table_id"],"datatype":column["data_type"],"nullable":column["nullable"], "label":column["name"]})
            # Create edge between table and column
            edges.append({"from":"flink~"+service_name+'~table~'+table["table_name"]+'~column~'+column["name"], "to": "flink~"+service_name+'~table~'+table["table_name"], "label": "table_column"})
        
        # List the integrations
        integrations = self.get_service_integrations(service=service_name, project=project)
        src_name = ""
        i = 0
        # Look for an integration that has the same id as the table 
        # Probably we want to do once per flink service rather than doing it for every table
        while src_name == "":
            if integrations[i]["service_integration_id"]==table["integration_id"]:
                #print(integrations[i])
                src_name = integrations[i]["source_service"]
            i = i + 1
        # Creatind edge between table and service
        edges.append({"from":"flink~"+service_name+'~table~'+table["table_name"], "to": service_name, "label": "topic"})
        
        service = self.get_service(project=project, service=src_name)
        table_details = self.get_flink_table(service=service_name, project=project, table_id=table["table_id"])
        # TODO parse more details of the table (each column?)
        tables_map[table["table_id"]]=table["table_name"]

        # Creating the edge between table and target topic/table/index
        if service["service_type"]=='pg':
            edges.append({"from":"flink~"+service_name+'~table~'+table["table_name"], "to": src_name, "label": "flink pg src"})
            #TO_DO once flink returns the src table or topic name, link that one
        elif service["service_type"]=='opensearch':
            edges.append({"from":"flink~"+service_name+'~table~'+table["table_name"], "to": src_name, "label": "flink opensearch src"})
        else:
            edges.append({"from":"flink~"+service_name+'~table~'+table["table_name"], "to": src_name, "label": "flink kafka src"})
            #TO_DO once flink returns the src table or topic name, link that one
    # Parsing Jobs
    jobs = self.list_flink_jobs(service=service_name, project=project)
    for job in jobs:
        job_det = self.get_flink_job(service=service_name, project=project, job_id=job["id"])
        # Adding Job node
        nodes.append({"id":"flink~"+service_name+'~job~'+job_det["name"], "service_type": "flink", "type": "flink job", "job_id":job_det["jid"],"label":job_det["name"]})
        # Adding edges between Job node and service
        edges.append({"from":"flink~"+service_name+'~job~'+job_det["name"], "to": service_name, "label": "flink job"})
        # TODO: once the api returns the Flink tables used for the job, create edges between tables and jobs
    return nodes, edges

# Exploring Kafka Services
def explore_kafka(self, service_name, project):
    nodes = []
    edges = []
    topics = self.list_service_topics(service=service_name, project=project)
    topic_list = []

    # Exploring Topics
    for topic in topics:
    
        nodes.append({"id":"kafka~"+service_name+"~topic~"+topic["topic_name"], "service_type": "kafka", "type": "topic", "cleanup_policy":topic["cleanup_policy"], "label":topic["topic_name"]})
        edges.append({"from":"kafka~"+service_name+"~topic~"+topic["topic_name"], "to": service_name, "label": "topic"})
        topic_list.append(topic["topic_name"])

        for tag in topic["tags"]:
            nodes.append({"id":"tag~id~"+tag["key"]+"~value~"+tag["value"], "service_type": "tag", "type": "tag", "label":tag["key"]+"="+tag["value"]})
            edges.append({"from":"kafka~"+service_name+"~topic~"+topic["topic_name"], "to": "tag~id~"+tag["key"]+"~value~"+tag["value"], "label": "tag"})
    kafka = self.get_service(project=project, service=service_name)

    # Exploring Users
    for user in kafka["users"]:
        
        nodes.append({"id":"kafka~"+service_name+"~user~"+user["username"], "service_type": "kafka", "type": "user", "user_type":user["type"], "label":user["username"]})
        edges.append({"from":"kafka~"+service_name+"~user~"+user["username"], "to": service_name, "label": "user"})

    # Exploring ACLs
    for acl in kafka["acl"]:
        # Create node for ACL
        nodes.append({"id":"kafka~"+service_name+"~acl~"+acl["id"], "service_type": "kafka", "type": "topic-acl", "permission":acl["permission"], "label":acl["id"], "topic":acl["topic"], "username":acl["username"]})
        # Create edge between ACL and username
        edges.append({"from":"kafka~"+service_name+"~user~"+acl["username"], "to": "kafka~"+service_name+"~acl~"+acl["id"], "label": "user"})
        # Map topics that an ACL shows
        for topic in topic_list:
            strtomatch = acl["topic"]
            if strtomatch == '*':
                strtomatch = '.*'
            # Checking if the ACL string matches a topic (ACL strings are defined with Java RegExp and we're parsing them with Python, maybe something to improve here?)
            if(re.match(strtomatch, topic)):
                edges.append({"from":"kafka~"+service_name+"~acl~"+acl["id"], "to":"kafka~"+service_name+"~topic~"+topic, "label": "topic-acl"})
    
    # If the service has Kafka connect, we can explore it as well
    if(kafka["user_config"]["kafka_connect"]==True):
        (newnodes, newedges) = explore_kafka_connect(self, service_name, project, "kafka")
        nodes = nodes + newnodes
        edges = edges + newedges    

    return nodes, edges

# Exploring Kafka Services
def explore_kafka_connect(self, service_name, project, service_type):
    nodes = []
    edges = []
    # The service map allows to indetify if the source/target of a connector is within aiven or external
    global SERVICE_MAP 
    
    connectors = self.list_kafka_connectors(service=service_name, project=project)

    # Getting connectors
    for connector in connectors["connectors"]:
        # Checking connector properties
        properties = {"id":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "service_type": service_type, "type": "kafka-connect", "label":connector["config"]["name"], "class":connector["config"]["connector.class"]}

        ##########################################
        # Debezium PostgreSQL conector           #
        ##########################################
        if connector["config"]["connector.class"] == 'io.debezium.connector.postgresql.PostgresConnector':
            target_host = connector["config"]["database.hostname"]
            target_service = SERVICE_MAP.get(target_host)
            # Looks for the target service to be in Aiven, if None, creates a new node for the target service
            if target_service == None:
                target_service = "ext-pg-"+target_host
                # Create node for New service
                nodes.append({"id":"ext-pg-"+target_host, "service_type": "ext-pg", "type": "external-postgresql", "label":"ext-pg-"+target_host})
                tables = connector["config"]["table.include.list"].split(',')
                for table in tables:
                    # schema is the first part of the table 
                    schema = table.split('.')[0]
                    # table_name is the second part of the table 
                    table_name = table.split('.')[1]
                    # Create node for the schema
                    nodes.append({"id":"ext-pg-"+target_host+"~schema~"+schema, "service_type": "ext-pg-schema", "type": "external-postgresql-schema", "label":schema})
                    # Create node for the table
                    nodes.append({"id":"ext-pg-"+target_host+"~schema~"+schema+"~table~"+table_name, "service_type": "ext-pg-table", "type": "external-postgresql-table", "label":table_name})
                    # Create edge from schema to table
                    edges.append({"from":"ext-pg-"+target_host+"~schema~"+schema, "to":"ext-pg-"+target_host+"~schema~"+schema+"~table~"+table_name}) 
                    # Create edge from host to schema
                    edges.append({"from":"ext-pg-"+target_host, "to":"ext-pg-"+target_host+"~schema~"+schema}) 
                    # Create edge from connector to source table
                    edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":"ext-pg-"+target_host+"~schema~"+schema+"~table~"+table_name})
                    # Find the kafka instance that the connector is pushing/taking data from 
                    (serv_name, serv_type) = find_kafka_service_from_connect(self, service_name, service_type, project)
                    # Create edge from connector to target topic
                    edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":serv_type+"~"+serv_name+"~topic~"+connector["config"]["database.server.name"]+'.'+table, "label": "kafka-connect-connector"}) 
                SERVICE_MAP[target_host] = "ext-pg-"+target_host
            # Looks for the target is in Aiven, connecting it
            else:
                tables = connector["config"]["table.include.list"].split(',')
                for table in tables:
                    # schema is the first part of the table 
                    schema = table.split('.')[0]
                    # table_name is the second part of the table 
                    table_name = table.split('.')[1]
                    # Create an edge betwen the connector and the pg table
                    edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":"pg~"+target_service+"~schema~"+schema+"~table~"+table_name, "label": "table"}) 
                    # Create an edge betwen the connector and the kafka connect service
                    edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":service_name, "label": "kafka-connect-connector"})
                    # Find the kafka instance that the connector is pushing/taking data from 
                    (serv_name, serv_type) = find_kafka_service_from_connect(self, service_name, service_type, project)
                    # Create an edge betwen the connector and the source kafka topic            
                    edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":serv_type+"~"+serv_name+"~topic~"+connector["config"]["database.server.name"]+'.'+table, "label": "kafka-connect-connector"})

        #####################
        # Opensearch sink   #
        #####################
        if connector["config"]["connector.class"] == 'io.aiven.kafka.connect.opensearch.OpensearchSinkConnector':
            target_host = urllib.parse.urlparse(connector["config"]["connection.url"]).hostname
            print(target_host)
            target_service = SERVICE_MAP.get(target_host)
            
            # Looks for the target service to be in Aiven, if None, creates a new node for the target service
            if target_service == None:
                a=1
                print("NOT FOUUUUND!!!!!!!!!!!!!!!")
                #TODO What should we create in case we don't find the target Opensearch?
            else:
                # Add edge to source service
                edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":service_name, "label": "kafka-connect-connector"})
                for topic in connector["config"]["topics"].split(','):
                    # Find the kafka instance that the connector is pushing/taking data from 
                    (serv_name, serv_type) = find_kafka_service_from_connect(self, service_name, service_type, project)
                    #Add edge to source topic
                    edges.append({"from": serv_type+"~"+serv_name+"~topic~"+topic, "to":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "label": "kafka-connect-connector"})
                    # Add edge to destination opensearch index
                    edges.append({"from":service_type+"~"+service_name+"~connect~"+connector["config"]["name"], "to":"opensearch~"+target_service+"~index~"+topic, "label": "kafka-connect-connector"})

        nodes.append(properties)
        
    return nodes, edges

# Find the kafka instance that the connector is pushing/taking data from/to
def find_kafka_service_from_connect(self, service_name, service_type, project):
    serv_type = service_type
    serv_name = service_name
    if serv_type == 'kafka_connect':
        serv_type = 'kafka'
        integrations = self.get_service_integrations(service=service_name, project=project)
        for integration in integrations:
            if(integration["enabled"]==True and integration["integration_type"]=="kafka_connect"):
                serv_name = integration["source_service"]
    return serv_name, serv_type
    
def explore_mysql(self, service_name, project):
    nodes = []
    edges = []

    service = self.get_service(project=project, service=service_name)
    
    # Get the avnadmin password (this is in case someone creates the service and then changes avnadmin password)
    avnadmin_pwd = list(filter(lambda x: x["username"] == "avnadmin", service["users"]))[0]["password"]

    service_conn_info = service["service_uri_params"]
    
    try:
        conn = pymysql.connect(
            host=service_conn_info["host"], 
            port=int(service_conn_info["port"]), 
            database=service_conn_info["dbname"],
            user= "avnadmin",
            password=avnadmin_pwd,
            connect_timeout=2)
    except pymysql.Error as err:
        conn = None
        print("Error connecting to: " + service_name)
        nodes.append({"id":"mysql~"+service_name+"~connection-error", "service_type": "mysql", "type": "connection-error", "label":"connection-error"})
        edges.append({"from":service_name, "to":"mysql~"+service_name+"~connection-error", "label": "connection-error"})
    
    if conn != None:
        cur = conn.cursor()
        
        # Getting databases
        cur.execute("select catalog_name, schema_name from information_schema.schemata;")

        databases = cur.fetchall()
        for database in databases:
            #print(database)
            nodes.append({"id":"mysql~"+service_name+"~database~"+database[1], "service_type": "mysql", "type": "database", "label":database[1]})
            edges.append({"from":service_name, "to":"mysql~"+service_name+"~database~"+database[1], "label": "database"})
        
        # Getting tables
        cur.execute("select TABLE_SCHEMA,TABLE_NAME, TABLE_TYPE from information_schema.tables where table_schema not in ('information_schema','sys','performance_schema','mysql');")

        tables = cur.fetchall()
        for table in tables:
            nodes.append({"id":"mysql~"+service_name+"~database~"+table[0]+"~table~"+table[1], "service_type": "mysql", "type": "table", "label":table[1], "table_type":table[2]})
            edges.append({"from":"mysql~"+service_name+"~database~"+table[0], "to":"mysql~"+service_name+"~database~"+table[0]+"~table~"+table[1], "label": "table"}) 
        
        # Get users
        cur.execute("select USER, HOST, ATTRIBUTE from information_schema.USER_ATTRIBUTES;")

        users = cur.fetchall()
        #print(users)
        for user in users:
            nodes.append({"id":"mysql~"+service_name+"~user~"+user[0], "service_type": "mysql", "type": "user", "label":user[0]})
            edges.append({"from":"mysql~"+service_name+"~user~"+user[0], "to":service_name, "label": "user"})

        # Get User Priviledges
        
        ##TODO  get user priviledges to tables
        
        # Get Columns
        cur.execute("select TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,IS_NULLABLE,DATA_TYPE from information_schema.columns where table_schema not in ('information_schema', 'sys','mysql','performance_schema');")
        
        columns = cur.fetchall()
        for column in columns:
            nodes.append({"id":"mysql~"+service_name+"~database~"+column[0]+"~table~"+column[1]+"~column~"+column[2], "service_type": "mysql", "type": "table column", "data_type":column[4], "is_nullable":column[3], "label":column[2]})
            edges.append({"from":"mysql~"+service_name+"~database~"+column[0]+"~table~"+column[1]+"~column~"+column[2], "to":"mysql~"+service_name+"~database~"+column[0]+"~table~"+column[1], "label": "column"}) 

    return nodes, edges

def explore_pg(self, service_name, project):
    nodes = []
    edges = []
    service = self.get_service(project=project, service=service_name)
    
    # Get the avnadmin password (this is in case someone creates the service and then changes avnadmin password)
    avnadmin_pwd = list(filter(lambda x: x["username"] == "avnadmin", service["users"]))[0]["password"]

    service_conn_info = service["connection_info"]["pg_params"][0]
    # Build the connection string
    connstr = "postgres://avnadmin:"+ avnadmin_pwd + \
        "@" + service_conn_info["host"] + ":" + service_conn_info["port"] + \
        "/" + service_conn_info["dbname"] + \
        "?sslmode=" + service_conn_info["sslmode"]

    try:
        conn = psycopg2.connect(connstr, connect_timeout=2)
    except psycopg2.Error as err:
        conn = None
        print("Error connecting to: " + service_name)
        nodes.append({"id":"pg~"+service_name+"~connection-error", "service_type": "pg", "type": "connection-error", "label":"connection-error"})
        edges.append({"from":service_name, "to":"pg~"+service_name+"~connection-error", "label": "connection-error"})
    
    if conn != None:
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")

        databases = cur.fetchall()
        for database in databases:
            #print(database)
            nodes.append({"id":"pg~"+service_name+"~database~"+database[0], "service_type": "pg", "type": "database", "label":database[0]})
            edges.append({"from":service_name, "to":"pg~"+service_name+"~database~"+database[0], "label": "database"})
        
        cur.execute("select catalog_name, schema_name, schema_owner from information_schema.schemata;")

        namespaces = cur.fetchall()
        for namespace in namespaces:
            nodes.append({"id":"pg~"+service_name+"~schema~"+namespace[1], "service_type": "pg", "type": "schema", "label":namespace[1]})
            edges.append({"from":"pg~"+service_name+"~database~"+namespace[0], "to":"pg~"+service_name+"~schema~"+namespace[1], "label": "schema"}) 
        
        cur.execute("SELECT schemaname, tablename, tableowner FROM pg_tables where tableowner <> 'postgres';")

        tables = cur.fetchall()
        for table in tables:
            nodes.append({"id":"pg~"+service_name+"~schema~"+table[0]+"~table~"+table[1], "service_type": "pg", "type": "table", "label":table[1]})
            edges.append({"from":"pg~"+service_name+"~schema~"+table[0], "to":"pg~"+service_name+"~schema~"+table[0]+"~table~"+table[1], "label": "table"}) 
        
        cur.execute("SELECT * FROM pg_user;")

        users = cur.fetchall()
        #print(users)
        for user in users:
            nodes.append({"id":"pg~"+service_name+"~user~"+user[0], "service_type": "pg", "type": "user", "label":user[0]})
            edges.append({"from":"pg~"+service_name+"~user~"+user[0], "to":service_name, "label": "user"}) 

        cur.execute("SELECT grantee, table_schema, table_name, privilege_type,is_grantable FROM information_schema.role_table_grants;")
        
        role_table_grants = cur.fetchall()
        
        for role_table_grant in role_table_grants:
            edges.append({"from":"pg~"+service_name+"~user~"+role_table_grant[0], "to":"pg~"+service_name+"~schema~"+role_table_grant[1]+"~table~"+role_table_grant[2], "label": "grant", "privilege_type":role_table_grant[3], "is_grantable":role_table_grant[4]}) 

        cur.execute("select table_catalog, table_schema, table_name, column_name, data_type, is_nullable from information_schema.columns where table_schema not in ('information_schema', 'pg_catalog');")
        
        columns = cur.fetchall()
        for column in columns:
            nodes.append({"id":"pg~"+service_name+"~schema~"+column[1]+"~table~"+column[2]+"~column~"+column[3], "service_type": "pg", "type": "table column", "data_type":column[4], "is_nullable":column[5], "label":column[3]})
            edges.append({"from":"pg~"+service_name+"~schema~"+column[1]+"~table~"+column[2]+"~column~"+column[3], "to":"pg~"+service_name+"~schema~"+column[1]+"~table~"+column[2], "label": "column"}) 
        

        cur.close()
        conn.close()
    return nodes, edges

def explore_ext_endpoints(self, project):
    nodes = []
    edges = []
    ext_endpoints = self.get_service_integration_endpoints(project=project)

    for ext_endpoint in ext_endpoints:
        nodes.append({"id":"ext"+ext_endpoint["endpoint_name"], "service_type":ext_endpoint["endpoint_type"], "type":"external_endpoint", "label":ext_endpoint["endpoint_name"]})
    
    return nodes, edges