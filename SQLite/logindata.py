def chrome_login_data():
    worksheet = "Login Data"
    sql_query = """
        /*
        Last updated 2025-04-29
        Author: Jacques Boucher - jjrboucher@gmail.com
        Tested on Chrome v.108 and Edge v.101
        */
        
        /* 
        Google Chrome Query
        Runs against the Login Data SQLite file
        */
        
        SELECT id,
            signon_realm,
            origin_url,
            action_url,
            username_value,
            display_name,
            username_element,
            password_element,
            date_created,
            datetime(date_created/1000000-11644473600,'unixepoch') AS 'Decoded date_created (UTC)',
            date_last_used,
            CASE date_last_used
                WHEN 0 THEN 'Synced. Not used on this device.'
                ELSE datetime(date_last_used/1000000-11644473600,'unixepoch') 
            END AS 'Decoded date_last_used (UTC)',
                date_password_modified,
            CASE date_password_modified
                WHEN 0 THEN 'Never'
                ELSE datetime(date_password_modified/1000000-11644473600,'unixepoch') 
            END AS 'Decoded date_password_modified (UTC)',
            times_used AS "# of times used",
        
            blacklisted_by_user,
            CASE blacklisted_by_user
                WHEN 1 THEN 'TRUE'
                WHEN 0 THEN 'FALSE'
                ELSE 'unknown value'
            END AS 'Decoded blacklisted_by_user (TRUE means do not save the password for this site)',
        
            password_type,
            
            /* 
            password_type reference:
            https://source.chromium.org/chromium/chromium/src/+/main:components/password_manager/core/browser/password_manager_metrics_util.h;l=345?q=PRIMARY_ACCOUNT_PASSWORD&ss=chromium%2Fchromium%2Fsrc 
            " // Passwords saved by password manager.
              SAVED_PASSWORD = 0,
              // Passwords used for Chrome sign-in and is closest ("blessed") to be set to
              // sync when signed into multiple profiles if user wants to set up sync.
              // The primary account is equivalent to the "sync account" if this profile has
              // enabled sync.
              PRIMARY_ACCOUNT_PASSWORD = 1,
              // Other Gaia passwords used in Chrome other than the sync password.
              OTHER_GAIA_PASSWORD = 2,
              // Passwords captured from enterprise login page.
              ENTERPRISE_PASSWORD = 3,
              // Unknown password type. Used by downstream code to indicate there was not a
              // password reuse.
              PASSWORD_TYPE_UNKNOWN = 4"
            */
            CASE password_type
                WHEN 0 THEN 'Saved by password manager.'
                WHEN 1 THEN 'Will sync if sync is enabled.'
                WHEN 2 THEN 'Passwords other than Synced ones.'
                WHEN 3 THEN 'Captured from enterprise login page.'
                WHEN 4 THEN 'Unknown type.'
                ELSE 'Unknown value. Check Chromium source code!'
            END AS 'Decoded password_type',
            
        /* You can optionally exclude the scheme if not relevant.  If doing so, remove the comma after the above as that become the last field in the query. */
            scheme,
            CASE scheme
                WHEN 0 THEN 'HTML (Default)'
                WHEN 1 THEN 'BASIC'
                WHEN 2 THEN 'DIGEST'
                WHEN 3 THEN 'OTHER'
                WHEN 4 THEN 'USERNAME ONLY'
                ELSE 'unknown value'
            END AS 'Decoded type of input form'
        
        FROM logins
        
        ORDER by date_created
    """

    return sql_query, worksheet

def chrome_login_data_gaps():
    worksheet = "Login Data Gaps"
    sql_query = """
        /*
        Written by Jacques Boucher
        email: jjrboucher@gmail.com
        Revision Date: 21 March 2023
        
        Inspired by the article published by James McGee at https://belkasoft.com/lagging-for-win
        The SQLite code in the middle UNION statement is Mr. McGee's statement adapted for Chromium visits (whereas his article was for iMessage sms.db file).
        
        
        About this script
        -----------------
        You can run this script against Google Chrome's (or other Chromium based browsers) Login Data file.
        It will look for gaps in numbering, and return the gaps along with their timestamps, and the # of records in that gap.
        
        For example, if the visits table contains records 25, 26, 27, 30, 31, 33, 39, this script will return:
        27 | 30 | 2 | <timestamp of record #27> | <timestamp of record #30>
        31 | 33 | 1 | <timestamp of record #31> | <timestamp of record #33>
        33 | 39 | 5 | <timestamp of record #33> | <timestamp of record #39>
        
        The script also checks the table sqlite_sequence.seq to see if there are records missing at the end.
        
        */
        
        SELECT 
            0 AS "Previous Record Number", /* Had to assign a numerical value to ensure proper sorting with other records. */
            logins.id AS "Record Number", 
            ROWID-1 AS "Number of Missing Visits", /* Because numbering starts at 1, missing records is the first allocated record -1 */
            "" AS "Beginning Date Created Timestamp", /* We don't have a beginning timestamp as we don't have that record */
            DATETIME(logins.date_created/1000000-11644473600,'unixepoch') AS "Ending Date Created Timestamp (UTC)"  /* Timestamp of the last record */
        
            FROM logins WHERE logins.id = (SELECT MIN(logins.id) FROM logins) AND logins.id >1 /* The first record # in the visits table is greater than 1.*/
        
        UNION
            
            /* Credit to James McGee and his article at https://belkasoft.com/lagging-for-win for the SQLite statement for this section. */
            SELECT * FROM
            (
                SELECT LAG (ROWID,1) OVER (ORDER BY ROWID) AS "Previous Record Number", /*  Gets the previous record to the current one */
                rowid AS ROWID, /* Current record */
                (ROWID - (LAG (ROWID,1) OVER (ORDER BY ROWID))-1) AS "Number of Missing Visits", /* Calculates the difference between the previous and current record # */
                LAG(DATETIME(logins.date_created/1000000-11644473600,'unixepoch'),1) OVER (ORDER BY ROWID) as "Beginning Date Created Timestamp (UTC)", /* Gets the timestamp from the previous record */
                DATETIME(logins.date_created/1000000-11644473600,'unixepoch') AS "Ending Date Created Timestamp (UTC)" /* Gets the timestamp of the current record */
                FROM logins
            )
            WHERE ROWID - "Previous Record Number" >1 /* Only gets the above if the difference between the current record # and previous record # is greater than 1 - in other words, there is a gap in the numbering */
            
            
        UNION /* Does a union between the above query and the below one. The below one is to check if there is a gap at the end. Without the below, you won't know if there are records missing at the end. */
        
        SELECT 
            ROWID AS "Previous Record Number", /* Because we are selecting the last allocated record, assigning that to the previous record # */
            "" AS ROWID, /* The last record is missing, thus it's blank */
            (SELECT sqlite_sequence.seq from sqlite_sequence WHERE sqlite_sequence.name LIKE "logins")-ROWID AS "Number of Missing Records", /* Finds the last record # used, and substracts last allocated record # */
            DATETIME(logins.date_created/1000000-11644473600,'unixepoch') AS "Beginning Date Created Timestamp (UTC)",
            "" AS "Ending Date Created Timestamp"
            FROM logins
            WHERE logins.id = (SELECT MAX(logins.id) FROM logins) /* Only getting the last allocated record. */ AND logins.id < 
                (SELECT sqlite_sequence.seq AS "Maximum Record" 
                                       FROM sqlite_sequence 
                                       WHERE sqlite_sequence.name LIKE "logins") /* Checking if the last allocated record is smaller than the largest recorded record number. */
    """

    return sql_query, worksheet