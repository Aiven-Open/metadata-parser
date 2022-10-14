"""Parsing MySQL service"""

import pymysql


def explore_mysql(service, service_name, service_map):
    """Explores an MySQL service"""
    nodes = []
    edges = []

    host = service["connection_info"]["mysql_params"][0]["host"]
    port = service["connection_info"]["mysql_params"][0]["port"]

    # Get the avnadmin password
    # this is in case someone creates the service
    # and then changes avnadmin password
    avnadmin_pwd = list(
        filter(lambda x: x["username"] == "avnadmin", service["users"])
    )[0]["password"]

    service_conn_info = service["service_uri_params"]

    try:
        conn = pymysql.connect(
            host=service_conn_info["host"],
            port=int(service_conn_info["port"]),
            database=service_conn_info["dbname"],
            user="avnadmin",
            password=avnadmin_pwd,
            connect_timeout=2,
        )
    except pymysql.Error as err:
        conn = None
        print("Error connecting to: " + service_name + str(err))
        nodes, edges = create_connection_error_node(service_name)

    if conn is not None:
        cur = conn.cursor()

        # Getting databases

        new_nodes, new_edges = explore_mysql_databases(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        # Getting tables

        new_nodes, new_edges = explore_mysql_tables(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        # Get users

        new_nodes, new_edges = explore_mysql_users(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        # Get User Priviledges

        # tobedone  get user priviledges to tables

        # Get Columns

        new_nodes, new_edges = explore_mysql_columns(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

    return host, port, nodes, edges, service_map


def create_connection_error_node(service_name):
    """Creates an error node in case of connection errors"""
    nodes = []
    edges = []
    nodes.append(
        {
            "id": "mysql~" + service_name + "~connection-error",
            "service_type": "mysql",
            "type": "connection-error",
            "label": "connection-error",
        }
    )
    edges.append(
        {
            "from": service_name,
            "to": "mysql~" + service_name + "~connection-error",
            "label": "connection-error",
        }
    )
    return nodes, edges


def explore_mysql_databases(cur, service_name):
    """Retrieves MySQL databases"""

    nodes = []
    edges = []

    cur.execute(
        """
            select catalog_name, schema_name
            from information_schema.schemata;
            """
    )

    databases = cur.fetchall()
    for database in databases:
        # print(database)
        nodes.append(
            {
                "id": "mysql~" + service_name + "~database~" + database[1],
                "service_type": "mysql",
                "type": "database",
                "label": database[1],
            }
        )
        edges.append(
            {
                "from": service_name,
                "to": "mysql~" + service_name + "~database~" + database[1],
                "label": "database",
            }
        )
    return nodes, edges


def explore_mysql_tables(cur, service_name):
    """Retrieves MySQL tables"""

    nodes = []
    edges = []

    cur.execute(
        """
            select TABLE_SCHEMA,TABLE_NAME, TABLE_TYPE
            from information_schema.tables
            where table_schema not in
            ('information_schema','sys','performance_schema','mysql');
            """
    )

    tables = cur.fetchall()
    for table in tables:
        nodes.append(
            {
                "id": "mysql~"
                + service_name
                + "~database~"
                + table[0]
                + "~table~"
                + table[1],
                "service_type": "mysql",
                "type": "table",
                "label": table[1],
                "table_type": table[2],
            }
        )
        edges.append(
            {
                "from": "mysql~" + service_name + "~database~" + table[0],
                "to": "mysql~"
                + service_name
                + "~database~"
                + table[0]
                + "~table~"
                + table[1],
                "label": "table",
            }
        )
    return nodes, edges


def explore_mysql_users(cur, service_name):
    """Retrieves MySQL users"""

    nodes = []
    edges = []

    cur.execute(
        """
            select USER, HOST, ATTRIBUTE
            from information_schema.USER_ATTRIBUTES;
            """
    )

    users = cur.fetchall()
    # print(users)
    for user in users:
        nodes.append(
            {
                "id": "mysql~" + service_name + "~user~" + user[0],
                "service_type": "mysql",
                "type": "user",
                "label": user[0],
            }
        )
        edges.append(
            {
                "from": "mysql~" + service_name + "~user~" + user[0],
                "to": service_name,
                "label": "user",
            }
        )
    return nodes, edges


def explore_mysql_columns(cur, service_name):
    """Retrieves MySQL columns"""

    nodes = []
    edges = []

    cur.execute(
        """
            select TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,IS_NULLABLE,DATA_TYPE
            from information_schema.columns where table_schema
            not in ('information_schema', 'sys','mysql','performance_schema');
            """
    )

    columns = cur.fetchall()
    for column in columns:
        nodes.append(
            {
                "id": "mysql~"
                + service_name
                + "~database~"
                + column[0]
                + "~table~"
                + column[1]
                + "~column~"
                + column[2],
                "service_type": "mysql",
                "type": "table column",
                "data_type": column[4],
                "is_nullable": column[3],
                "label": column[2],
            }
        )
        edges.append(
            {
                "from": "mysql~"
                + service_name
                + "~database~"
                + column[0]
                + "~table~"
                + column[1]
                + "~column~"
                + column[2],
                "to": "mysql~"
                + service_name
                + "~database~"
                + column[0]
                + "~table~"
                + column[1],
                "label": "column",
            }
        )
    return nodes, edges
