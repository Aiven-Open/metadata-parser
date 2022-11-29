Aiven Metadata Parser
========================

Want to get all the juicy metadata out of your Aiven services? Check out the Aiven Metadata Parser! 

Based on the `aiven-client` python library, the Aiven Metadata Parser exports the metadata from your services in order to build a connected graph showing all interconnections.

![Graph in action](img/graph.gif)

Currently the Aiven Metadata Parser is a work in progress and extracts only a limited amount of information and connections.

Create a set of test services
=============================

You can use the `create_services.sh` and `delete_services.sh` to create and destroy a pre-set of services.
The `create_services.sh` uses:

* [jq](https://stedolan.github.io/jq/) to parse JSON output
* [kcat](https://github.com/edenhill/kcat) for Apache Kafka®
* [psql](https://www.postgresql.org/docs/current/app-psql.html) for PostgreSQL®
* [The Aiven CLI](https://github.com/aiven/aiven-client) to connect and create services
* The Python packages in the `requirements.txt` file to push data to Grafana

Before starting it, please install the required dependences, login with the [Aiven CLI](https://github.com/aiven/aiven-client) and execute:

```bash
./scripts/create_services.sh <PROJECT_NAME>
```

Where `<PROJECT_NAME>` is the name of your Aiven project.

To delete the services you can call:

```bash
./scripts/delete_services.sh <PROJECT_NAME>
```

If `<PROJECT_NAME>` is not passed, the default project will be used.

Start with the Aiven Metadata Parser
=======================================

You need to be on Python 3.7, install the required libraries with:

```bash
pip install -r requirements.txt
```

Copy the `conf.env.sample` file to `conf.env` in the `conf` folder and edit the token parameter and the project name from which you want to extract parameters.
If you don't have a project with services already running you can create a sample set of services with the `create_services.sh` file, which requires the `aiven-client` to be installed and the user to be logged in.

Once `conf.env` is set, you can start the metadata extraction with: 

```bash
python main.py
```

This will generate:
* A file `graph_data.dot` containing the information in [DOT format](https://graphviz.org/doc/info/lang.html)
* A file `graph_data.gml` containing the information in [GML format](https://en.wikipedia.org/wiki/Geography_Markup_Language)
* A file `nx.html` containing the complete interactive graph
![Graph in action](img/graph.gif)
* (Disabled for the moment) A file `filtered.html` containing the complete interactive graph filtered on the node with id `pg~demo-pg~schema~public~table~pasta` (this might error out if you don't have such node)

Furthermore if, after executing the `main.py` you also execute the following:

```bash
python app.py
```

The `app.py` reads the `graph_data.gml` file generated at step 1 and creates a Reactive Web Applications with [Plotly](https://plot.ly/python/) and [Dash](https://plot.ly/dash/) (code taken from [here](https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7)).

Lastly the following allows you to push the content to a PG database passing the PG URI:

```
python write_pg.py PG_URI
```

**Warning** 
The code is a bare minimum product, doesn't cover all services and options and is quite chaotic! It demonstrates the idea and how we could start implementing it.

Possible issues and solutions
============

- If you run `python app.py` and see an error saying `No such file or directory: 'neato'`, you will have to install `graphviz` on your machine (the package version from pip doesn't seem to work) - fi.d out how to install it [here](https://graphviz.org/download/).

Contributing
============

Wanna contribute? Check the [CONTRIBUTING file](CONTRIBUTING.md)

License
============
Aiven Metadata Extractor is licensed under the Apache license, version 2.0. Full license text is available in the [LICENSE](LICENSE) file.

Please note that the project explicitly does not require a CLA (Contributor License Agreement) from its contributors.

Contact
============
Bug reports and patches are very welcome, please post them as GitHub issues and pull requests at https://github.com/aiven/metadata-parser . 
To report any possible vulnerabilities or other serious issues please see our [security](SECURITY.md) policy.

All images under the `src` folder and shown in `nx.html` file are taken from https://www.flaticon.com/
All images under the `src/services` folder are a property of Aiven


Apache, Apache Kafka, Kafka, Apache Flink, Flink, Apache Cassandra, and Cassandra are either registered trademarks or trademarks of the Apache Software Foundation in the United States and/or other countries. ClickHouse is a registered trademark of ClickHouse, Inc. https://clickhouse.com. M3, M3 Aggregator, M3 Coordinator, OpenSearch, PostgreSQL, MySQL, InfluxDB, Grafana, Terraform, and Kubernetes are trademarks and property of their respective owners. *Redis is a trademark of Redis Ltd. and the Redis box logo is a mark of Redis Ltd. Any rights therein are reserved to Redis Ltd. Any use by Aiven is for referential purposes only and does not indicate any sponsorship, endorsement or affiliation between Redis and Aiven.  All product and service names used in this website are for identification purposes only and do not imply endorsement.
