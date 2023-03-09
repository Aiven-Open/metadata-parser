"""Parsing Apache Flink® services"""


def explore_flink(self, service, service_name, project, service_map):
    """Explores an Apache Flink service"""
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = 443

    # Parsing Applications
    new_nodes, new_edges = explore_flink_applications(
        self, service_name, project
    )
    nodes = nodes + new_nodes
    edges = edges + new_edges

    return host, port, nodes, edges, service_map


def explore_flink_applications(self, service_name, project):
    """Explores Flink applications"""
    nodes = []
    edges = []

    applications = self.flink_list_applications(
        service=service_name, project=project
    )
    for application in applications["applications"]:
        # Creating a node beween table and service
        nodes.append(
            {
                "id": "flink~"
                + service_name
                + "~application~"
                + application["name"],
                "service_type": "flink",
                "type": "flink application",
                "application_id": application["id"],
                "label": application["name"],
            }
        )

        edges.append(
            {
                "from": "flink~"
                + service_name
                + "~application~"
                + application["name"],
                "to": service_name,
                "label": "flink application",
            }
        )

        application_details = self.flink_get_application(
            service=service_name,
            project=project,
            application_id=application["id"],
        )

        for application_version in application_details["application_versions"]:
            nodes.append(
                {
                    "id": "flink~"
                    + service_name
                    + "~application~"
                    + application["name"]
                    + "~version~"
                    + str(application_version["version"]),
                    "service_type": "flink",
                    "type": "flink application version",
                    "application_version_id": application_version["id"],
                    "label": str(application_version["version"]),
                }
            )

            edges.append(
                {
                    "from": "flink~"
                    + service_name
                    + "~application~"
                    + application["name"],
                    "to": "flink~"
                    + service_name
                    + "~application~"
                    + application["name"]
                    + "~version~"
                    + str(application_version["version"]),
                    "label": "flink application version",
                }
            )

            for source in application_version["sources"]:
                print(source)
                # TODO - explore application versions

    return nodes, edges


def explore_flink_tables(self, service_name, project):
    """Explores Flink tables - old, not to be used"""

    nodes = []
    edges = []

    tables = self.list_flink_tables(service=service_name, project=project)
    tables_map = {}

    # Checking each table definition in Flink
    for table in tables:
        # Creating a node beween table and service
        nodes.append(
            {
                "id": "flink~"
                + service_name
                + "~table~"
                + table["table_name"],
                "service_type": "flink",
                "type": "flink table",
                "table_id": table["table_id"],
                "label": table["table_name"],
            }
        )
        # For each column in the table
        new_nodes, new_edges = explore_flink_columns(
            service_name,
            table["table_name"],
            table["table_id"],
            table["columns"],
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

        # List the integrations
        integrations = self.get_service_integrations(
            service=service_name, project=project
        )
        src_name = ""
        i = 0
        # Look for an integration that has the same id as the table
        # Probably we want to do once per flink service
        # rather than doing it for every table
        while src_name == "":
            if (
                integrations[i]["service_integration_id"]
                == table["integration_id"]
            ):
                # print(integrations[i])
                src_name = integrations[i]["source_service"]
            i = i + 1
        # Creatind edge between table and service
        edges.append(
            {
                "from": "flink~"
                + service_name
                + "~table~"
                + table["table_name"],
                "to": service_name,
                "label": "topic",
            }
        )

        service = self.get_service(project=project, service=src_name)
        # table_details = self.get_flink_table(
        #    service=service_name, project=project, table_id=table["table_id"]
        # )
        # print(table_details)
        # tobedone parse more details of the table (each column?)
        tables_map[table["table_id"]] = table["table_name"]

        # Creating the edge between table and target topic/table/index
        if service["service_type"] == "pg":
            edges.append(
                {
                    "from": "flink~"
                    + service_name
                    + "~table~"
                    + table["table_name"],
                    "to": src_name,
                    "label": "flink pg src",
                }
            )
            # TO_DO once flink returns the src table or topic name,
            # link that one
        elif service["service_type"] == "opensearch":
            edges.append(
                {
                    "from": "flink~"
                    + service_name
                    + "~table~"
                    + table["table_name"],
                    "to": src_name,
                    "label": "flink opensearch src",
                }
            )
        else:
            edges.append(
                {
                    "from": "flink~"
                    + service_name
                    + "~table~"
                    + table["table_name"],
                    "to": src_name,
                    "label": "flink kafka src",
                }
            )
            # TO_DO once flink returns the src table or topic name,
            # link that one
    return nodes, edges


def explore_flink_jobs(self, service_name, project):
    """Explores Flink jobs"""

    nodes = []
    edges = []
    jobs = self.list_flink_jobs(service=service_name, project=project)
    for job in jobs:
        job_det = self.get_flink_job(
            service=service_name, project=project, job_id=job["id"]
        )
        # Adding Job node
        nodes.append(
            {
                "id": "flink~" + service_name + "~job~" + job_det["name"],
                "service_type": "flink",
                "type": "flink job",
                "job_id": job_det["jid"],
                "label": job_det["name"],
            }
        )
        # Adding edges between Job node and service
        edges.append(
            {
                "from": "flink~" + service_name + "~job~" + job_det["name"],
                "to": service_name,
                "label": "flink job",
            }
        )
    # tobedone: once the api returns the Flink tables used for the job,
    # create edges between tables and jobs
    return nodes, edges


def explore_flink_columns(service_name, table_name, table_id, columns):
    """Explores Flink tables columns"""

    nodes = []
    edges = []
    for column in columns:
        # Create node for the column
        nodes.append(
            {
                "id": "flink~"
                + service_name
                + "~table~"
                + table_name
                + "~column~"
                + column["name"],
                "service_type": "flink",
                "type": "flink table column",
                "table_id": table_id,
                "datatype": column["data_type"],
                "nullable": column["nullable"],
                "label": column["name"],
            }
        )
        # Create edge between table and column
        edges.append(
            {
                "from": "flink~"
                + service_name
                + "~table~"
                + table_name
                + "~column~"
                + column["name"],
                "to": "flink~" + service_name + "~table~" + table_name,
                "label": "table_column",
            }
        )
    # tobedone: once the api returns the Flink tables used for the job,
    # create edges between tables and jobs
    return nodes, edges
