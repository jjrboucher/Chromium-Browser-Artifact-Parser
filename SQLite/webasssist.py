def edge_webassist():
    worksheet = "WebAssist"
    sql_query = """
        /*
        Created by Jacques Boucher
        Date: 18 February 2025
        Browser: Edge
        SQLite file: WebAssistDatabase
        
        */
        
        SELECT 	url,
                id,
                title,
                metadata,
                urldata,
                last_visited_time,
                DATETIME(last_visited_time, 'unixepoch') AS "decoded last_visited_time (UTC)",
                num_visits
        
        FROM navigation_history
        
        ORDER BY last_visited_time       
    """

    return sql_query, worksheet