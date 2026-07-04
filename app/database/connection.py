import sqlite3


def get_sales_analytics(
        partner: str = None,
        service: str = None,
        start_date: str = None,
        end_date: str = None,
        intent: str = "sum",
        limit: int = None
) -> list:
    where_clause = "WHERE 1=1"
    params = []

    if partner:
        where_clause += " AND LOWER_CYR(Partner) LIKE ?"
        params.append(f"%{partner.lower()}%")
    if service:
        where_clause += " AND Service = ?"
        params.append(service)
    if start_date and end_date:
        where_clause += " AND Date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date:
        where_clause += " AND Date >= ?"
        params.append(start_date)

    if intent == "count":
        query = f"SELECT COUNT(*) as TotalOrders FROM sales {where_clause}"

    elif intent == "avg":
        query = f"SELECT AVG(Tickets) as AverageTickets FROM sales {where_clause}"

    elif intent == "top":
        group_field = "Partner"

        limit_clause = "LIMIT ?" if limit else "LIMIT 5"
        query = f"SELECT {group_field}, SUM(Tickets) as TotalTickets FROM sales {where_clause} GROUP BY {group_field} ORDER BY TotalTickets DESC {limit_clause}"
        if limit: params.append(int(limit))

    elif intent == "daily":
        query = f"SELECT Date, SUM(Tickets) as TotalTickets FROM sales {where_clause} GROUP BY Date ORDER BY Date"
    else:
        if partner and not service:
            query = f"SELECT Partner, SUM(Tickets) as TotalTickets FROM sales {where_clause} GROUP BY Partner"
        elif service and not partner:
            query = f"SELECT Service, SUM(Tickets) as TotalTickets FROM sales {where_clause} GROUP BY Service"
        else:
            query = f"SELECT Service, SUM(Tickets) as TotalTickets FROM sales {where_clause} GROUP BY Service"

    connection = sqlite3.connect("file:sales.db?mode=ro", uri=True)
    connection.create_function("LOWER_CYR", 1, lambda x: str(x).lower() if x else None)

    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except sqlite3.Error as error:
        return [{"error": f"Database error: {str(error)}"}]
    finally:
        connection.close()