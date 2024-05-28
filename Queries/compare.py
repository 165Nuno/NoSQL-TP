from prettytable import PrettyTable

from neo4j import *
from sql import *

def compare_queries(query_name: str, neo4j_results, sql_results, print_results=False):
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
    print(table)

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
            print(diff_table_neo4j)

        if len(sql_only) > 0:
            diff_table_sql = PrettyTable()
            diff_table_sql.title = "Different table Sql"
            diff_table_sql.field_names = ["Source"] + list(sql_results[0].keys())
            sql_columns = list(sql_results[0].keys())
            for entry in sql_only:
                entry_dict = dict(entry)
                row = ["SQL"] + [entry_dict[col] for col in sql_columns]
                diff_table_sql.add_row(row)
            print(diff_table_sql)

    if print_results:
        results_table_sql = PrettyTable()
        results_table_sql.title = "Results Sql"
        results_table_neo4j = PrettyTable()
        results_table_neo4j.title = "Results Neo4j"
        
        if len(neo4j_results) > 0:
            neo4j_columns = list(neo4j_results[0].keys())
            results_table_neo4j.field_names = neo4j_columns
            for entry in neo4j_results:
                entry_dict = dict(entry)
                row = [entry_dict[col] for col in neo4j_columns]
                results_table_neo4j.add_row(row)
        
        if len(sql_results) > 0:
            sql_columns = list(sql_results[0].keys())
            results_table_sql.field_names = sql_columns
            for entry in sql_results:
                entry_dict = dict(entry)
                row = [entry_dict[col] for col in sql_columns]
                results_table_sql.add_row(row)

        print(results_table_sql)
        print(results_table_neo4j)


def compare_query1(print_results=False):
    neo4j_results = run_query1_neo4j()
    sql_results = run_query1_sql()
    compare_queries("Query 1", neo4j_results, sql_results, print_results)

def compare_query2(print_results=False):
    neo4j_results = run_query2_neo4j()
    sql_results = run_query2_sql()
    compare_queries("Query 2", neo4j_results, sql_results, print_results)

def compare_query3(print_results=False):
    neo4j_results = run_query3_neo4j()
    sql_results = run_query3_sql()
    compare_queries("Query 3", neo4j_results, sql_results, print_results)

def compare_query4(print_results=False):
    neo4j_results = run_query4_neo4j()
    sql_results = run_query4_sql()
    compare_queries("Query 4", neo4j_results, sql_results, print_results)

def compare_query5(print_results=False):
    neo4j_results = run_query5_neo4j()
    sql_results = run_query5_sql()
    compare_queries("Query 5", neo4j_results, sql_results, print_results)

def compare_query6(print_results=False):
    neo4j_results = run_query6_neo4j()
    sql_results = run_query6_sql()
    compare_queries("Query 6", neo4j_results, sql_results, print_results)

def compare_query7(print_results=False):
    neo4j_results = run_query7_neo4j()
    sql_results = run_query7_sql()
    compare_queries("Query 7", neo4j_results, sql_results, print_results)

def compare_query8(print_results=False):
    neo4j_results = run_query8_neo4j()
    sql_results = run_query8_sql()
    compare_queries("Query 8", neo4j_results, sql_results, print_results)

def compare_query9(print_results=False):
    neo4j_results = run_query9_neo4j()
    sql_results = run_query9_sql()
    compare_queries("Query 9", neo4j_results, sql_results, print_results)

def compare_query10(print_results=False):
    neo4j_results = run_query10_neo4j()
    sql_results = run_query10_sql()
    compare_queries("Query 10", neo4j_results, sql_results, print_results)

def compare_query11(print_results=False):
    neo4j_results = run_query11_neo4j()
    sql_results = run_query11_sql()
    compare_queries("Query 11", neo4j_results, sql_results, print_results)

# Compares Query to Get Patients with the Most Appointments
def compare_query12(print_results=False):
    neo4j_results = run_query12_neo4j()
    sql_results = run_query12_sql()
    compare_queries("Query 12", neo4j_results, sql_results, print_results)

def compare_query13(print_results=False):
    neo4j_results = run_query13_neo4j()
    sql_results = run_query13_sql()
    compare_queries("Query 13", neo4j_results, sql_results, print_results)

def compare_query14(print_results=False):
    neo4j_results = run_query14_neo4j()
    sql_results = run_query14_sql()
    compare_queries("Query 14", neo4j_results, sql_results, print_results)

if __name__ == "__main__":
    compare_query1()
    compare_query2()
    compare_query3()
    compare_query4()
    compare_query5()
    compare_query6()
    compare_query7()
    compare_query8()
    compare_query9()
    compare_query10()
    compare_query11()
    compare_query12()
    compare_query13()
    compare_query14()