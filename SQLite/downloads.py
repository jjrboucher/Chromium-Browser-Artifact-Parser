def chrome_downloads():
    worksheet = 'Downloads'
    sql_query = """
        /*
        Last updated: 2025-02-22
        Author:  Jacques Boucher - jjrboucher@gmail.com
        Tested with: Chrome 94
        Only changes from previous query that was tested with Chrome 71 and 78 is that a few
        extra download errors have been added. The previous statement will still work. If it
        sees a value it doesn't recognize, it alerts you of this fact and displays the value.
        */


        /* 
        Google Chrome Query
        Runs against the History SQLite file
        Extracts list of downloaded files.
        Downloads - Complex SQLite Statement
        */

        SELECT  downloads.id AS "downloads.id", 
                chains.chain_index AS "chain_index", 
                current_path, 
                target_path,
                received_bytes,
                total_bytes,
                start_time, 
                datetime(start_time/1000000-11644473600,'unixepoch') AS "Decoded start_time (UTC)", 
                
                end_time,
                CASE
                   WHEN end_time>0 THEN datetime(end_time/1000000-11644473600,'unixepoch')
                   ELSE 0
                END AS "Decoded end_time (UTC)",
                
                last_access_time,
                CASE 
                   WHEN last_access_time>0 THEN datetime(last_access_time/1000000-11644473600,'unixepoch')
                   ELSE 'Not opened via Chrome'
                END AS "Decoded last_access_time (UTC)",
                
                last_modified, 
                referrer,
                site_url, 
                tab_url, 
                tab_referrer_url,
                
                state,
                CASE state 
                   WHEN 1 THEN "Complete" 
                   WHEN 2 THEN "Interrupted"
                   ELSE "New value!: "||state||" Check source code for meaning!"
                END AS "Decoded state",
                
                danger_type,
                /* see https://source.chromium.org/chromium/chromium/src/+/main:components/download/public/common/download_danger_type.h?q=danger_type */
                CASE danger_type
                    WHEN 0 THEN "Not Dangerous"
                    WHEN 1 THEN "Dangerous File"
                    WHEN 2 THEN "Dangerous URL"
                    WHEN 3 THEN "Dangerous Content"
                    WHEN 4 THEN "Maybe Dangerous Content"
                    WHEN 5 THEN "Uncommon Content"
                    WHEN 6 THEN "User Validated"
                    WHEN 7 THEN "Dangerous Host"
                    WHEN 8 THEN "Potentially Unwanted"
                    WHEN 9 THEN "Allow Listed by Policy"
                    WHEN 10 THEN "ASYNC Scanning"
                    WHEN 11 THEN "Blocked Password Protected"
                    WHEN 12 THEN "Blocked too Large"
                    WHEN 13 THEN "Sensitive Content Warning"
                    WHEN 14 THEN "Sensitive Content Block"
                    WHEN 15 THEN "Deep Scanned Safe"
                    WHEN 16 THEN "Deep Scanned Opened Dangerous"
                    WHEN 17 THEN "Prompt for Scanning"
                    WHEN 18 THEN "Blocked Unsupported" /* Deprecated */
                    WHEN 19 THEN "Dangerous Account Compromise"
                    WHEN 20 THEN "Deep Scanned Failed"
                    WHEN 21 THEN "Prompt for Local Password Scanning"
                    WHEN 22 THEN "ASYNC Local Password Scanning"
                    WHEN 23 THEN "Blocked Scan Failed"
                ELSE "New value!: "||danger_type||" Check source code for meaning!"
                END AS "Decoded danger_type",
                
                interrupt_reason,
                /* 
                see https://source.chromium.org/chromium/chromium/src/+/main:components/download/public/common/download_interrupt_reason_values.h
                for interrupt reasons
                */
                CASE interrupt_reason
                   WHEN 0 THEN "Not Interrupted"
                   /* File errors */
                   WHEN 1 THEN "File Error"
                   WHEN 2 THEN "Access Denied"
                   WHEN 3 THEN "Disk Full"
                   WHEN 5 THEN "Path Too Long"
                   WHEN 6 THEN "File Too Large"
                   WHEN 7 THEN "Virus"
                   WHEN 10 THEN "Temporary Problem"
                   WHEN  11 THEN "Blocked"
                   WHEN 12 THEN "File Security Check Failed"
                   WHEN 13 THEN "On resume, file too short"
                   WHEN 14 THEN "Hash Mismatch"
                   WHEN 15 THEN "Source and target of download the same"
                   /* Network Errors */
                   WHEN 20 THEN "Network Error"
                   WHEN 21 THEN "Operation Timed Out"
                   WHEN 22 THEN "Connection Lost"
                   WHEN 23 THEN "Server Down"
                   WHEN 24 THEN "Network Invalid Request"
                   /* Server Responses */
                   WHEN 30 THEN "Server Failed"
                   WHEN 31 THEN "Server does not support range requests"
                   WHEN 32 THEN "Obsolete (shouldn't see this error)"
                   WHEN 33 THEN "Unable to get file"
                   WHEN 34 THEN "Server didn't authorize access"
                   WHEN 35 THEN "Server Certificate Problem"
                   When 36 THEN "Server access forbidden"
                   WHEN 37 THEN "Server Unreachable"
                   WHEN 38 THEN "Server content length mismatch"
                   WHEN 39 THEN "Server cross origin redirect"
                   /* User input */
                   WHEN 40 THEN "User canceled the download"
                   WHEN 41 THEN "User shut down the browser"
                   /* Crash */
                   WHEN 50 THEN "Browser crashed"
                   ELSE "New value!: "||interrupt_reason||" Check source code for meaning!"
                END AS "Decoded interrupt_reason",
                
                chains.url AS "Download Source"

        FROM downloads
        JOIN (SELECT id, chain_index, url FROM downloads_url_chains) AS chains

        WHERE chains.id=downloads.id

        ORDER by downloads.id, start_time
    """

    return sql_query, worksheet

def chrome_downloads_gaps():
    worksheet = 'Downloads Gaps'
    sql_query = """
        /*
        Written by Jacques Boucher
        email: jjrboucher@gmail.com
        Revision Date: 22 March 2023
        
        Inspired by the article published by James McGee at https://belkasoft.com/lagging-for-win
        The SQLite code in the middle UNION statement is Mr. McGee's statement adapted for Chromium visits (whereas his article was for iMessage sms.db file).
        
        
        About this script
        -----------------
        You can run this script against Google Chrome's (or other Chromium based browsers) history file.
        It will look for gaps in numbering for downloads, and return the gaps along with their timestamps (for start time of download), and the # of records in that gap.
        
        For example, if the visits table contains records 25, 26, 27, 30, 31, 33, 39, this script will return:
        27 | 30 | 2 | <timestamp of record #27> | <timestamp of record #30>
        31 | 33 | 1 | <timestamp of record #31> | <timestamp of record #33>
        33 | 39 | 5 | <timestamp of record #33> | <timestamp of record #39>
        
        The script can't check for gaps at the end, because the last used record number is not stored in sqlite_sequence.seq.
        
        Note that the script does not look if any records are missing from the beginning.
        You can draw your own conclusion on that based on the first record number.
        
        */
        
        SELECT 
            0 AS "Previous Record Number", /* Had to assign a numerical value to ensure proper sorting with other records. */
            downloads.id AS "Record Number", 
            ROWID-1 AS "Number of Missing Visits", /* Because numbering starts at 1, missing records is the first allocated record -1 */
            "" AS "Beginning Timestamp", /* We don't have a beginning timestamp as we don't have that record */
            DATETIME(downloads.start_time/1000000-11644473600,'unixepoch') AS "Ending Timestamp (UTC)"  /* Timestamp of the last record */
        
            FROM downloads WHERE downloads.id = (SELECT MIN(downloads.id) FROM downloads) AND downloads.id >1 /* The first record # in the visits table is greater than 1.*/
        
        UNION
            
            /* Credit to James McGee and his article at https://belkasoft.com/lagging-for-win for the SQLite statement for this section. */
            SELECT * FROM
            (
                SELECT LAG (ROWID,1) OVER (ORDER BY ROWID) AS "Previous Record Number", /*  Gets the previous record to the current one */
                rowid AS ROWID, /* Current record */
                (ROWID - (LAG (ROWID,1) OVER (ORDER BY ROWID))-1) AS "Number of Missing Visits", /* Calculates the difference between the previous and current record # */
                LAG(DATETIME(downloads.start_time/1000000-11644473600,'unixepoch'),1) OVER (ORDER BY ROWID) as "Beginning Timestamp (UTC)", /* Gets the timestamp from the previous record */
                DATETIME(downloads.start_time/1000000-11644473600,'unixepoch') AS "Ending Timestamp (UTC)" /* Gets the timestamp of the current record */
                FROM downloads
            )
        WHERE ROWID - "Previous Record Number" >1 /* Only gets the above if the difference between the current record # and previous record # is greater than 1 - in other words, there is a gap in the numbering */
    """

    return sql_query, worksheet
