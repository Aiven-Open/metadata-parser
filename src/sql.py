"""Parsing SQL"""

from sqllineage.runner import LineageRunner
from sqllineage.core.models import SubQuery


def explore_sql(sql_statement, service_name, schema, target, service_type):
    """Parsing SQL"""
    nodes = []
    edges = []

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

    for line in runner.get_column_lineage(exclude_subquery=False):
        prev_col_id = None

        for col in reversed(line):
            is_subquery = False
            if isinstance(col.parent, SubQuery):
                table_name = col.parent.alias
                is_subquery = True
            else:
                table_name = col.parent.raw_name
            column_name = col.raw_name

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
            if is_subquery:
                nodes.append(
                    {
                        "id": new_col_id,
                        "service_type": service_type,
                        "type": "reference",
                        "label": column_name,
                    }
                )
                nodes.append(
                    {
                        "id": new_col_id.split("~column~")[0],
                        "service_type": service_type,
                        "type": "sql_reference",
                        "label": new_col_id.split("~column~")[0].split(
                            "~table_view~"
                        )[1],
                    }
                )
                edges.append(
                    {
                        "from": new_col_id,
                        "to": new_col_id.split("~column~")[0],
                        "type": "sql_reference",
                    }
                )
                edges.append(
                    {
                        "from": service_type
                        + "~"
                        + service_name
                        + "~schema~"
                        + schema
                        + "~table_view~"
                        + target,
                        "to": new_col_id.split("~column~")[0],
                        "type": "sql_reference",
                        "label": target,
                    }
                )

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
