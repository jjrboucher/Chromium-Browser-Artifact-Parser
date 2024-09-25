def chrome_autofill():
    worksheet = "Autofill"
    sql_query = """
        /*
        Last modified: 2023-03-14
        Author:  Jacques Boucher - jjrboucher@gmail.com
        Tested with:  MS Edge v.100.0.1185.44, 110.0.1587.63
                  Chrome v.83.0.4103.116-64, v.111.0.5563.64-64
        */

        /* 
        Chromium Browser query
        Runs against the Webdata SQLite file
        Extracts autofill from the autofill table
        */

        SELECT name AS "Name",
            value AS "User Input",
            count AS "# of times used",
            date_created,
            datetime(date_created,'unixepoch') AS 'Decoded date_created (UTC)',
            date_last_used,
            datetime(date_last_used,'unixepoch') AS 'Decoded date_last_used (UTC)',
            count AS "Count"

        FROM autofill
    """

    return sql_query, worksheet


def chrome_keywords():
    # This query extracts info from the keywords table in Web Data SQLite file.
    worksheet = "Keywords"
    sql_query = """
        /*
        Last modified: 2024-09-24
        Author: Jacques Boucher - jjrboucher@gmail.com
        Tested with: Chrome v. 129
        */
        
        /*
        Chrome Browser
        Runs against Web Data SQLite file
        Extracts data from keywords table.
        */
        
        SELECT 	id,
                short_name,
                keyword,
                url,
                date_created,
                datetime(date_created/1000000-11644473600,'unixepoch') AS 'Decoded date_created (UTC)',
                last_modified,
                datetime(last_modified/1000000-11644473600,'unixepoch') AS 'Decoded last_modified (UTC)',
                last_visited,
                datetime(last_visited/1000000-11644473600,'unixepoch') AS 'Decoded last_visited (UTC)',
                usage_count
        
        FROM keywords
    """

    return sql_query, worksheet


def chrome_masked_credit_cards():
    # This query extracts info from the masked_credit_cards table in Web Data SQLite file.
    worksheet = "Credit Cards"
    sql_query = """
        /*
        Last modified: 2024-09-24
        Author: Jacques Boucher - jjrboucher@gmail.com
        Tested with: Chrome v. 129
        */
        
        /*
        Chrome Browser
        Runs against Web Data SQLite file
        Extracts data from masked_credit_cards table.
        */

        SELECT 	product_description AS "Product Description",
                name_on_card AS "Name on card",
                network,
                last_four AS "Last Four",
                exp_month AS "Expiry Month",
                exp_year AS "Expiry Year",
                bank_name AS "Bank Name",
                nickname,
                card_art_url AS "Card Art URL"

        FROM masked_credit_cards    
    """

    return sql_query, worksheet


def chrome_masked_bank_accounts():
    # This query extracts info from the masked_bank_accounts table in Web Data SQLite file.
    worksheet = "Bank Accounts"
    sql_query = """
        /*
        Last modified: 2024-09-24
        Author: Jacques Boucher - jjrboucher@gmail.com
        Tested with: Chrome v. 129
        */

        /*
        Chrome Browser
        Runs against Web Data SQLite file
        Extracts data from masked_bank_accounts table.
        */

        SELECT 	bank_name AS "Bank Name",
                account_number_suffix AS "Account Number Suffix",
                account_type AS "Account Type",
                nickname

        FROM masked_bank_accounts    
    """

    return sql_query, worksheet


def autofill_profile():
    # This query does not work with later versions of the browser as the autofill_profile table has been removed.
    worksheet = "Autofill Profile"
    sql_query = """
        /*
        Last modified: 2019-01-17 (added comments, cleaned up formatting of query)
        Author:  Jacques Boucher - jjrboucher@gmail.com
        Tested with:  Chrome 71 and 78
        */
        
        /* 
        Google Chrome Query
        Runs against the Webdata SQLite file
        Extracts autofill information from several tables and aggregates the data based on guid values.
        */
        
        SELECT use_count,
            origin,
            date_modified,
            datetime(date_modified,'unixepoch') AS 'Decoded date_modified (UTC)',
            use_date,  datetime(use_date,'unixepoch') AS 'Decoded use_date (UTC)',
            autofill_profiles.guid,
            full_name,
            first_name,
            middle_name,
            last_name,
            street_address,
            city, state,
            zipcode,
            country_code,
            number, email
        
        FROM autofill_profile_names
            JOIN autofill_profiles ON autofill_profiles.guid == autofill_profile_names.guid 
            JOIN autofill_profile_phones ON autofill_profiles.guid == autofill_profile_phones.guid 
            JOIN autofill_profile_emails ON autofill_profiles.guid == autofill_profile_emails.guid
    """

    return sql_query, worksheet
