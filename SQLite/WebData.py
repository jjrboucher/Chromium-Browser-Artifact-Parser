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
        This queries the keywords table in the the Web Data SQLite.
        It provides you with a summary of the different keywords in the keywords table, including when they 
        were created, and when they were last used.
        
        If a user navigates to a site with a search feature on it and does a search, that may result in a new record
        added to this table with the date_created field being when they first did a query on that site.
        
        Thus, this query can provide you with some interesting insight about different sites a user accessed and 
        conducted searches via a search bar on the site.
        
        One caveat is that at least for Google search engine, the dates don't seem to update to match when a Google
        search was last done. It's not clear what triggers that to be updated. But in a test of a site never 
        previously navigated that has a search function, upon navigating to that site and conducting a search, it was
        correctly added to this table and the timestamps correctly reflected when that took place.
        
        Last modified: 2024-10-19
        Author:  Jacques Boucher - jjrboucher@gmail.com
        Tested with:  Chrome 129
        */
        
        SELECT	id,
                short_name,
                keyword,
                url,
                date_created,
                CASE date_created
                    WHEN 0 THEN ""
                    ELSE datetime(date_created/1000000-11644473600,'unixepoch')
                END	AS "Decoded date_created (UTC)",
                keywords.last_modified,
                CASE last_modified
                    WHEN 0 THEN ""
                    ELSE datetime(last_modified/1000000-11644473600,'unixepoch')
                END AS "Decoded last_modified (UTC)",
                keywords.last_visited,
                CASE last_visited
                    WHEN 0 THEN ""
                    ELSE datetime(last_visited/1000000-11644473600,'unixepoch')
                END AS "Decoded last_visited (UTC)"
            
        FROM keywords
    """

    return sql_query, worksheet


def chrome_masked_credit_cards():
    # This query extracts info from the masked_credit_cards table in Web Data SQLite file.
    worksheet = "Credit Cards"
    sql_query = """
                /*
                Written by Jacques Boucher
                Date: 29 Jan 2025
                
                Queries two tables to pull out credit card information.
                The use_date does not correspond to the last time it was used.
                There is protobuf data in autofill_sync_metadata for the masked_credit_cards.id
                with an encoded date that appears to more closely align with when it was last used.
                But parsing that info is more involved, thus not parsed at this time.
                */
                SELECT 	mcc.id, 
                        mcc.name_on_card,
                        mcc.network,
                        mcc.last_four,
                        mcc.exp_month,
                        mcc.exp_year,
                        scm.use_count,
                        scm.use_date,
                        DATETIME(scm.use_date/1000000-11644473600,'unixepoch') AS "Decoded use_date (UTC)",
                        scm.billing_address_id AS "Billing Address ID",
                        mcc.bank_name,
                        mcc.nickname,
                        mcc.card_issuer,
                        mcc.card_issuer_id,
                        mcc.virtual_card_enrollment_state,
                        mcc.card_art_url,
                        mcc.product_description
                
                FROM masked_credit_cards AS mcc
                LEFT JOIN server_card_metadata AS scm on mcc.id == scm.id   
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


def chrome_addresses():
    # This query extracts info from the masked_credit_cards table in Web Data SQLite file.
    worksheet = "Addresses"
    sql_query = """
                /*
                Written by Jacques Boucher
                Date: 30 Jan 2025

                Queries two tables to pull out main artifacts from stored address information.
                
                */
                SELECT 	addresses.guid, 
                        atk_first_name.value AS "First Name", 
                        atk_last_name.value AS "Last Name",
                        atk_full_name.value AS "Last Name",
                        atk_email.value AS "Email",
                        atk_phone.value AS "Phone",
                        atk_office.value AS "Office",
                        atk_street.value AS "Street",
                        atk_city.value AS "City",
                        atk_state.value AS "State/Province",
                        atk_zip.value AS "Zip/Postal Code",
                        atk_country.value AS "Country",
                        addresses.use_count, 
                        addresses.use_date,
                        DATETIME(use_date,'unixepoch') AS "Decoded use_date (UTC)",
                        addresses.date_modified,
                        DATETIME(date_modified,'unixepoch') AS "Decoded date_modified (UTC)"
                FROM addresses
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 3 ) AS atk_first_name ON addresses.guid == atk_first_name.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 5 ) AS atk_last_name ON addresses.guid == atk_last_name.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 7 ) AS atk_full_name ON addresses.guid == atk_full_name.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 9 ) AS atk_email ON addresses.guid == atk_email.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 14 ) AS atk_phone ON addresses.guid == atk_phone.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 77 ) AS atk_street ON addresses.guid == atk_street.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 33 ) AS atk_city ON addresses.guid == atk_city.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 34 ) AS atk_state ON addresses.guid == atk_state.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 35 ) AS atk_zip ON addresses.guid == atk_zip.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 36 ) AS atk_country ON addresses.guid == atk_country.guid
                LEFT JOIN (SELECT * FROM address_type_tokens WHERE type == 60 ) AS atk_office ON addresses.guid == atk_office.guid

    """

    return sql_query, worksheet
