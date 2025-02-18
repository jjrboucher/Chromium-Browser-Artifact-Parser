def chrome_topsites():
    worksheet = "Top Sites"
    sql_query = """
        /*
        Last modified: 2020-02-18
        Author: Jacques Boucher - jjrboucher@gmail.com
        */
        
        /*
        Chrome Browser
        Runs against "Top Sites" SQLite file located in the profile folder
        Extracts data from top_sites table.
        */    
    
        SELECT  url,
                url_rank,
                title
        FROM top_sites
    """


    return sql_query, worksheet
