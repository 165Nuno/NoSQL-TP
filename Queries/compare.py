from prettytable import PrettyTable
import time # measure elapsed time
import os

from neo4j import *
from sql import *
from mongo import *
from Queries.neo4j_novas_queries import *

# Determine the script directory and create the output directory if it doesnt exist
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "out")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def write_to_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def compare_queries(query_name: str, neo4j_results, sql_results, mongo_results, neo4j_time, sql_time, mongo_time):
    # Convert lists of dictionaries to sets of tuples
    neo4j_set = {tuple(d.items()) for d in neo4j_results}
    sql_set = {tuple(d.items()) for d in sql_results}
    mongo_set = {tuple(d.items()) for d in mongo_results}

    # match is the boolean that represents if the results of the queries are equal or not
    match = neo4j_set == sql_set == mongo_set

    # Print the comparison result
    table = PrettyTable()
    table.title = "Comparison Result"
    table.field_names = [query_name]
    table.add_row(["Equal" if match else "Not Equal"])

    result_file_path = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}.txt")
    result_content = f"{query_name}\nResults: {'Equal' if match else 'Not Equal'}\n"

    if not match:
        # Find differences
        neo4j_only = neo4j_set - sql_set - mongo_set
        sql_only = sql_set - neo4j_set - mongo_set
        mongo_only = mongo_set - sql_set - neo4j_set

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

        if len(mongo_only) > 0:
            diff_table_mongo = PrettyTable()
            diff_table_mongo.title = "Different table Mongo"
            diff_table_mongo.field_names = ["Source"] + list(mongo_results[0].keys())
            mongo_columns = list(mongo_results[0].keys())
            for entry in mongo_only:
                entry_dict = dict(entry)
                row = ["MongoDB"] + [entry_dict[col] for col in mongo_columns]
                diff_table_mongo.add_row(row)
            result_content += f"\n{diff_table_mongo}\n"

    write_to_file(result_file_path, result_content)

    results_table_sql = PrettyTable()
    results_table_sql.title = "Results Sql"
    results_table_neo4j = PrettyTable()
    results_table_neo4j.title = "Results Neo4j"
    results_table_mongo = PrettyTable()
    results_table_mongo.title = "Results MongoDB"
    
    # Write the results and execution times to separate files
    neo4j_result_file = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}_neo4j.txt")
    sql_result_file = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}_sql.txt")
    mongo_result_file = os.path.join(output_dir, f"{query_name.lower().replace(' ', '_')}_mongodb.txt")
    
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
    
    if len(mongo_results) > 0:
        mongo_columns = list(mongo_results[0].keys())
        results_table_mongo.field_names = mongo_columns
        for entry in mongo_results:
            entry_dict = dict(entry)
            row = [entry_dict[col] for col in mongo_columns]
            results_table_mongo.add_row(row)

    sql_result_content = f"Execution Time: {sql_time:.5f} seconds\nResults:\n{results_table_sql if len(sql_results) > 0 else 'No Results'}"
    neo4j_result_content = f"Execution Time: {neo4j_time:.5f} seconds\nResults:\n{results_table_neo4j if len(neo4j_results) > 0 else 'No Results'}"
    mongo_result_content = f"Execution Time: {mongo_time:.5f} seconds\nResults:\n{results_table_mongo if len(mongo_results) > 0 else 'No Results'}"

    write_to_file(neo4j_result_file, neo4j_result_content)
    write_to_file(sql_result_file, sql_result_content)
    write_to_file(mongo_result_file, mongo_result_content)

"""
Measures the elapsed time of the query received as input.
Repeats the query num_trials times, and returns the average time
if skip_first, it doesn't count the first execution of the query

Returns the average time and the result of the query
"""
def measure_query_time(query_function, num_trials=1, skip_first=True):
    assert num_trials > 0
    result = None
    if skip_first:
        query_function()

    elapsed_times = []
    for i in range(num_trials):
        start_time = time.time()
        result = query_function()
        end_time = time.time()
        elapsed_times.append(end_time - start_time)

    avg_time = sum(elapsed_times) / len(elapsed_times)
    
    return avg_time, result


def run_and_compare_query(query_name, neo4j_function, sql_function, mongo_function):
    skip_first = True
    num_trials = 10

    # Run and time Neo4j query
    neo4j_time, neo4j_results = measure_query_time(neo4j_function, num_trials, skip_first)

    # Run and time SQL query
    sql_time, sql_results = measure_query_time(sql_function, num_trials, skip_first)

    # Run and time MongoDB query
    mongo_time, mongo_results = measure_query_time(mongo_function, num_trials, skip_first)

    # Compare the results
    compare_queries(query_name, neo4j_results, sql_results, mongo_results, neo4j_time, sql_time, mongo_time)

if __name__ == "__main__":
    #run_and_compare_query("Query 1", run_query1_neo4j, run_query1_sql, run_query1_mongo)
    #run_and_compare_query("Query 2", run_query2_neo4j, run_query2_sql, run_query2_mongo)
    #run_and_compare_query("Query 3", run_query3_neo4j, run_query3_sql, run_query3_mongo)
    #run_and_compare_query("Query 4", run_query4_neo4j, run_query4_sql, run_query4_mongo)
    #run_and_compare_query("Query 5", run_query5_neo4j, run_query5_sql, run_query5_mongo)
    #run_and_compare_query("Query 6", run_query6_neo4j, run_query6_sql, run_query6_mongo)
    #run_and_compare_query("Query 7", run_query7_neo4j, run_query7_sql, run_query7_mongo)
    #run_and_compare_query("Query 8", run_query8_neo4j, run_query8_sql, run_query8_mongo)
    #run_and_compare_query("Query 9", run_query9_neo4j, run_query9_sql, run_query9_mongo)
    #run_and_compare_query("Query 10", run_query10_neo4j, run_query10_sql, run_query10_mongo)
    #run_and_compare_query("Query 11", run_query11_neo4j, run_query11_sql, run_query11_mongo)
    #run_and_compare_query("Query 12", run_query12_neo4j, run_query12_sql, run_query12_mongo)
    #run_and_compare_query("Query 13", run_query13_neo4j, run_query13_sql, run_query13_mongo)
    run_and_compare_query("Query 1", run_query1_neo4j_nova, run_query1_sql, run_query1_mongo)
    run_and_compare_query("Query 2", run_query2_neo4j_nova, run_query2_sql, run_query2_mongo)
    run_and_compare_query("Query 3", run_query3_neo4j_nova, run_query3_sql, run_query3_mongo)
    run_and_compare_query("Query 4", run_query4_neo4j_nova, run_query4_sql, run_query4_mongo)
    run_and_compare_query("Query 5", run_query5_neo4j_nova, run_query5_sql, run_query5_mongo)
    run_and_compare_query("Query 6", run_query6_neo4j_nova, run_query6_sql, run_query6_mongo)
    run_and_compare_query("Query 7", run_query7_neo4j_nova, run_query7_sql, run_query7_mongo)
    run_and_compare_query("Query 8", run_query8_neo4j_nova, run_query8_sql, run_query8_mongo)
    run_and_compare_query("Query 9", run_query9_neo4j_nova, run_query9_sql, run_query9_mongo)
    run_and_compare_query("Query 10", run_query10_neo4j_nova, run_query10_sql, run_query10_mongo)
    run_and_compare_query("Query 11", run_query11_neo4j_nova, run_query11_sql, run_query11_mongo)
    run_and_compare_query("Query 12", run_query12_neo4j_nova, run_query12_sql, run_query12_mongo)
    run_and_compare_query("Query 13", run_query13_neo4j_nova, run_query13_sql, run_query13_mongo)