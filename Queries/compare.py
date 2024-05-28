from prettytable import PrettyTable

from neo4j import run_query1_neo4j
from sql import run_query1_sql

def compare_query1():
    neo4j_results = run_query1_neo4j()
    sql_results = run_query1_sql()
    
    # Convert lists of dictionaries to sets of tuples
    neo4j_set = {tuple(d.items()) for d in neo4j_results}
    sql_set = {tuple(d.items()) for d in sql_results}

    # match is the boolean that represents if the results of the queries are equal or not
    match = neo4j_set == sql_set

    # Print the comparison result
    table = PrettyTable()
    table.field_names = ["Comparison Result Query1"]
    table.add_row(["Equal" if match else "Not Equal"])
    print(table)

    if not match:
        # Find differences
        neo4j_only = neo4j_set - sql_set
        sql_only = sql_set - neo4j_set

        if len(neo4j_only) > 0:
            diff_table_neo4j = PrettyTable()
            neo4j_columns = list(neo4j_results[0].keys())
            diff_table_neo4j.field_names = ["Source"] + neo4j_columns
            for entry in neo4j_only:
                entry_dict = dict(entry)
                row = ["Neo4j"] + [entry_dict[col] for col in neo4j_columns]
                diff_table_neo4j.add_row(row)
            print("Different table neo4j:")
            print(diff_table_neo4j)

        if len(sql_only) > 0:
            diff_table_sql = PrettyTable()
            diff_table_sql.field_names = ["Source"] + list(sql_results[0].keys())
            sql_columns = list(sql_results[0].keys())
            for entry in sql_only:
                entry_dict = dict(entry)
                row = ["SQL"] + [entry_dict[col] for col in sql_columns]
                diff_table_sql.add_row(row)
            print("Different table sql:")
            print(diff_table_sql)

if __name__ == "__main__":
    compare_query1()