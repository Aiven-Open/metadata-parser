"""Parsing SQL"""

from sqllineage.runner import LineageRunner


def explore_sql(sql_statement, service_name, schema, target, service_type):
    """Parsing SQL"""
    nodes = []
    edges = []
    print(sql_statement)
    if not sql_statement.upper().startswith("INSERT"):
        sql_statement = "INSERT INTO " + target + " AS " + sql_statement
    runner = LineageRunner(
        sql_statement,
        verbose=False,
        draw_options={
            "host": "abc",
            "port": 123,
            "f": "sql.sql",
        },
    )

    for line in runner.get_column_lineage():
        prev_col_id = None
        print(str(line))
        for col in reversed(line):
            print(str(col))
            table_name = col.parent.raw_name
            column_name = col.raw_name
            print(column_name)
            if table_name is None:
                # This is the case where is a reference to the end column
                new_col_id = (
                    service_type
                    + "~"
                    + service_name
                    + "~schema~"
                    + schema
                    + "~table_view~"
                    + target
                    + "~"
                    + "column"
                    + "~"
                    + column_name
                )
                # nodes.append(
                #     {
                #         "id": new_col_id,
                #         "service_type": service_type,
                #         "type": "sql_column_reference",
                #         "label": column_name,
                #     }
                # )
            else:
                new_col_id = (
                    service_type
                    + "~"
                    + service_name
                    + "~schema~"
                    + schema
                    + "~table_view~"
                    + table_name
                    + "~column~"
                    + column_name
                )
                # nodes.append(
                #     {
                #         "id": new_col_id,
                #         "service_type": service_type,
                #         "type": "sql_column_reference",
                #         "label": column_name,
                #     }
                # )
            if prev_col_id is not None:
                edges.append(
                    {
                        "from": new_col_id,
                        "to": prev_col_id,
                        "type": "sql_reference",
                    }
                )
            prev_col_id = new_col_id
    return nodes, edges
