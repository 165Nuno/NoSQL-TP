from py2neo import Graph, Node, Relationship

uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

neo4j = Graph(uri, auth=(user, password))

print("Conexão Neo4j realizada com sucesso!")


# Create procedure
def neo_update_bill_status(p_bill_id, p_paid_value):
    try:
        query = """
        MATCH (b:Bill {id_bill: $p_bill_id})
        RETURN b.total AS total
        """
        v_total = neo4j.run(query, p_bill_id=p_bill_id).evaluate("total")
        if v_total is None:
            raise ValueError(f"No bill found with id {p_bill_id}")
        
        # Check if the paid value is less than the total value of the bill
        if p_paid_value < v_total:
            # If paid value is less than total, update status to FAILURE
            update_query = """
            MATCH (b:Bill {id_bill: $p_bill_id})
            SET b.payment_status = 'FAILURE'
            """
            neo4j.run(update_query, p_bill_id=p_bill_id)

            # Raise an error
            raise ValueError("Paid value is inferior to the total value of the bill.")
        else:
            # If paid value is equal to total, update status to PROCESSED
            update_query = """
            MATCH (b:Bill {id_bill: $p_bill_id})
            SET b.payment_status = 'PROCESSED'
            """
            neo4j.run(update_query, p_bill_id=p_bill_id)

        print("Bill status updated successfully.")
    
    except Exception as e:
        print("Error executing Cypher query:", e)


if __name__ == "__main__":
    # run procedure
    neo_update_bill_status(16, 2000) # Caso de PROCESSED (total = 1980)
    neo_update_bill_status(19, 200) # CASO DE FAILURE (total = 260)