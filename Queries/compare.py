from prettytable import PrettyTable
import time # measure elapsed time
import os

from neo4j import *
from sql import *

# Determine the script directory and create the output directory if it doesnt exist
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "out")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def write_to_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def compare_queries(query_name: str, neo4j_results, sql_results, neo4j_time, sql_time):
    # Convert lists of dictionaries to sets of tuples
    neo4j_set = {tuple(d.items()) for d in neo4j_results}
    sql_set = {tuple(d.items()) for d in sql_results}

    # match is the boolean that represents if the results of the queries are equal or not
    match = neo4j_set == sql_set

    # Print the comparison result
    table = PrettyTable()
    table.title = "Comparison Result"
    table.field_names = [query_name]
    table.add_row(["Equal" if match else "Not Equal"])

    result_file_path = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}.txt")
    result_content = f"{query_name}\nResults: {'Equal' if match else 'Not Equal'}\n"

    if not match:
        # Find differences
        neo4j_only = neo4j_set - sql_set
        sql_only = sql_set - neo4j_set

        if len(neo4j_only) > 0:
            diff_table_neo4j = PrettyTable()
            diff_table_neo4j.title = "Different table Neo4j"
            neo4j_columns = list(neo4j_results[0].keys())
            diff_table_neo4j.field_names = ["Source"] + neo4j_columns
            for entry in neo4j_only:
                entry_dict = dict(entry)
                row = ["Neo4j"] + [entry_dict[col] for col in neo4j_columns]
                diff_table_neo4j.add_row(row)
            result_content += f"\n{diff_table_neo4j}\n"

        if len(sql_only) > 0:
            diff_table_sql = PrettyTable()
            diff_table_sql.title = "Different table Sql"
            diff_table_sql.field_names = ["Source"] + list(sql_results[0].keys())
            sql_columns = list(sql_results[0].keys())
            for entry in sql_only:
                entry_dict = dict(entry)
                row = ["SQL"] + [entry_dict[col] for col in sql_columns]
                diff_table_sql.add_row(row)
            result_content += f"\n{diff_table_sql}\n"

    write_to_file(result_file_path, result_content)

    results_table_sql = PrettyTable()
    results_table_sql.title = "Results Sql"
    results_table_neo4j = PrettyTable()
    results_table_neo4j.title = "Results Neo4j"
    
    # Write the results and execution times to separate files
    neo4j_result_file = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}_neo4j.txt")
    sql_result_file = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}_sql.txt")
    
    if len(sql_results) > 0:
        sql_columns = list(sql_results[0].keys())
        results_table_sql.field_names = sql_columns
        for entry in sql_results:
            entry_dict = dict(entry)
            row = [entry_dict[col] for col in sql_columns]
            results_table_sql.add_row(row)
    
    if len(neo4j_results) > 0:
        neo4j_columns = list(neo4j_results[0].keys())
        results_table_neo4j.field_names = neo4j_columns
        for entry in neo4j_results:
            entry_dict = dict(entry)
            row = [entry_dict[col] for col in neo4j_columns]
            results_table_neo4j.add_row(row)
    print(results_table_sql)
    print(results_table_neo4j)

    sql_result_content = f"Execution Time: {sql_time:.5f} seconds\nResults:\n{results_table_sql}"
    neo4j_result_content = f"Execution Time: {neo4j_time:.5f} seconds\nResults:\n{results_table_neo4j}"

    write_to_file(neo4j_result_file, neo4j_result_content)
    write_to_file(sql_result_file, sql_result_content)

def run_and_compare_query(query_name, neo4j_function, sql_function):
    # Run and time Neo4j query
    start_time = time.time()
    neo4j_results = neo4j_function()
    neo4j_time = time.time() - start_time

    # Run and time SQL query
    start_time = time.time()
    sql_results = sql_function()
    sql_time = time.time() - start_time

    # Compare the results
    compare_queries(query_name, neo4j_results, sql_results, neo4j_time, sql_time)

if __name__ == "__main__":
    run_and_compare_query("Query 1", run_query1_neo4j, run_query1_sql)
    run_and_compare_query("Query 2", run_query2_neo4j, run_query2_sql)
    run_and_compare_query("Query 3", run_query3_neo4j, run_query3_sql)
    run_and_compare_query("Query 4", run_query4_neo4j, run_query4_sql)
    run_and_compare_query("Query 5", run_query5_neo4j, run_query5_sql)
    run_and_compare_query("Query 6", run_query6_neo4j, run_query6_sql)
    run_and_compare_query("Query 7", run_query7_neo4j, run_query7_sql)
    run_and_compare_query("Query 8", run_query8_neo4j, run_query8_sql)
    run_and_compare_query("Query 9", run_query9_neo4j, run_query9_sql)
    run_and_compare_query("Query 10", run_query10_neo4j, run_query10_sql)
    run_and_compare_query("Query 11", run_query11_neo4j, run_query11_sql)
    run_and_compare_query("Query 12", run_query12_neo4j, run_query12_sql)
    run_and_compare_query("Query 13", run_query13_neo4j, run_query13_sql)