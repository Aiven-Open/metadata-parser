"""Parsing PostgreSQL services"""

import psycopg2


def build_conn_string(avnadmin_pwd, service_conn_info):
    """Builds conntection string"""
    connstr = (
        "postgres://avnadmin:"
        + avnadmin_pwd
        + "@"
        + service_conn_info["host"]
        + ":"
        + service_conn_info["port"]
        + "/"
        + service_conn_info["dbname"]
        + "?sslmode="
        + service_conn_info["sslmode"]
    )
    return connstr


def explore_pg(self, service, service_name, project, service_map):
    """Explores an PG service"""
    nodes = []
    edges = []

    service = self.get_service(project=project, service=service_name)

    # Get the avnadmin password
    # this is in case someone creates the service
    # and then changes avnadmin password
    avnadmin_pwd = list(
        filter(lambda x: x["username"] == "avnadmin", service["users"])
    )[0]["password"]

    service_conn_info = service["connection_info"]["pg_params"][0]
    # Build the connection string
    connstr = build_conn_string(avnadmin_pwd, service_conn_info)

    try:
        conn = psycopg2.connect(connstr, connect_timeout=2)
    except psycopg2.Error as err:
        conn = None
        print("Error connecting to: " + service_name + str(err))
        nodes.append(
            {
                "id": "pg~" + service_name + "~connection-error",
                "service_type": "pg",
                "type": "connection-error",
                "label": "connection-error",
            }
        )
        edges.append(
            {
                "from": service_name,
                "to": "pg~" + service_name + "~connection-error",
                "label": "connection-error",
            }
        )

    if conn is not None:
        cur = conn.cursor()

        new_nodes, new_edges = explore_pg_database(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        new_nodes, new_edges = explore_pg_tablespaces(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        new_nodes, new_edges = explore_pg_tables(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        new_nodes, new_edges = explore_pg_users(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        new_nodes, new_edges = explore_pg_grants(cur, service_name)
        nodes = nodes + new_nodes
        edges = edges + new_edges

        cur.close()
        conn.close()
    return (
        service_conn_info["host"],
        service_conn_info["port"],
        nodes,
        edges,
        service_map,
    )


def explore_pg_database(cur, service_name):
    """Retrieves info about a PG database"""

    nodes = []
    edges = []

    cur.execute("SELECT datname FROM pg_database;")

    databases = cur.fetchall()
    for database in databases:
        # print(database)
        nodes.append(
            {
                "id": "pg~" + service_name + "~database~" + database[0],
                "service_type": "pg",
                "type": "database",
                "label": database[0],
            }
        )
        edges.append(
            {
                "from": service_name,
                "to": "pg~" + service_name + "~database~" + database[0],
                "label": "database",
            }
        )
    return nodes, edges


def explore_pg_tablespaces(cur, service_name):
    """Retrieves info about a PG tablespace"""

    nodes = []
    edges = []

    cur.execute(
        """
            select catalog_name, schema_name, schema_owner
            from information_schema.schemata;
            """
    )

    namespaces = cur.fetchall()
    for namespace in namespaces:
        nodes.append(
            {
                "id": "pg~" + service_name + "~schema~" + namespace[1],
                "service_type": "pg",
                "type": "schema",
                "label": namespace[1],
            }
        )
        edges.append(
            {
                "from": "pg~" + service_name + "~database~" + namespace[0],
                "to": "pg~" + service_name + "~schema~" + namespace[1],
                "label": "schema",
            }
        )
    return nodes, edges


def explore_pg_tables(cur, service_name):
    """Retrieves info about a PG tables"""

    nodes = []
    edges = []

    cur.execute(
        """
            SELECT schemaname, tablename, tableowner
            FROM pg_tables where tableowner <> 'postgres';
            """
    )

    tables = cur.fetchall()
    for table in tables:
        nodes.append(
            {
                "id": "pg~"
                + service_name
                + "~schema~"
                + table[0]
                + "~table~"
                + table[1],
                "service_type": "pg",
                "type": "table",
                "label": table[1],
            }
        )
        edges.append(
            {
                "from": "pg~" + service_name + "~schema~" + table[0],
                "to": "pg~"
                + service_name
                + "~schema~"
                + table[0]
                + "~table~"
                + table[1],
                "label": "table",
            }
        )
    return nodes, edges


def explore_pg_users(cur, service_name):
    """Retrieves info about a PG users"""

    nodes = []
    edges = []

    cur.execute("SELECT * FROM pg_user;")

    users = cur.fetchall()
    # print(users)
    for user in users:
        nodes.append(
            {
                "id": "pg~" + service_name + "~user~" + user[0],
                "service_type": "pg",
                "type": "user",
                "label": user[0],
            }
        )
        edges.append(
            {
                "from": "pg~" + service_name + "~user~" + user[0],
                "to": service_name,
                "label": "user",
            }
        )
    return nodes, edges


def explore_pg_grants(cur, service_name):
    """Retrieves info about a PG grants to users"""

    nodes = []
    edges = []
    cur.execute(
        """
            SELECT grantee, table_schema, table_name,
            privilege_type,is_grantable
            FROM information_schema.role_table_grants;
            """
    )

    role_table_grants = cur.fetchall()

    for role_table_grant in role_table_grants:
        edges.append(
            {
                "from": "pg~" + service_name + "~user~" + role_table_grant[0],
                "to": "pg~"
                + service_name
                + "~schema~"
                + role_table_grant[1]
                + "~table~"
                + role_table_grant[2],
                "label": "grant",
                "privilege_type": role_table_grant[3],
                "is_grantable": role_table_grant[4],
            }
        )
    return nodes, edges


def explore_pg_columns(cur, service_name):
    """Retrieves info about a PG columns"""

    nodes = []
    edges = []

    cur.execute(
        """
            select table_catalog, table_schema, table_name, column_name,
            data_type, is_nullable from information_schema.columns
            where table_schema not in ('information_schema', 'pg_catalog');
            """
    )

    columns = cur.fetchall()
    for column in columns:
        nodes.append(
            {
                "id": "pg~"
                + service_name
                + "~schema~"
                + column[1]
                + "~table~"
                + column[2]
                + "~column~"
                + column[3],
                "service_type": "pg",
                "type": "table column",
                "data_type": column[4],
                "is_nullable": column[5],
                "label": column[3],
            }
        )
        edges.append(
            {
                "from": "pg~"
                + service_name
                + "~schema~"
                + column[1]
                + "~table~"
                + column[2]
                + "~column~"
                + column[3],
                "to": "pg~"
                + service_name
                + "~schema~"
                + column[1]
                + "~table~"
                + column[2],
                "label": "column",
            }
        )
    return nodes, edges
