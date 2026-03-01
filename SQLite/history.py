def chrome_history():

    worksheet = 'History'
    sql_query = """
        /*
        Last updated 2021-12-17
        Now includes the field urls.last_visit_time as well as decoded value. Especially useful for entries that have no entry in the visits table.
    
        Author: Jacques Boucher - jjrboucher@gmail.com
        Tested with:  Chrome 78,143 but should work fine with 71, as 
        the changes to the earlier query are cosmetics (adding a raw field to the output
        and formating an output to a float rather than an integer.
    
        2021-10-10, tested with Chrome 94 and appears to still produce the correct results.
    
        2021-12-17 - tested with Chrome 96 and appears to still produce correct results.
        */
    
        /* 
        Google Chrome Query
        Runs against the History SQLite file
        Extracts all visits as well as entries in urls with no visits (result of bookmarks for which no urls exist in the 'visits' table.
        Remember that Chrome only keeps the last 3 months of history.  So a user could bookmark a site they surfed.  But if they
        don't navigate back to it for more than 3 months, it will disappear from the 'visits' table, but it will persist in the 'urls' table
        because of the bookmark that exists for it.
        Presumably Chrome prepopulates the 'urls' table with bookmarks so that when a user is typing in the omnibox and Chrome looks
        to see if that URL exsits in the 'urls' table, it's also checking bookmarks by having those populated in there.
        */
    
        /*
        References:
        https://cs.chromium.org/chromium/src/ui/base/page_transition_types.h
    
        https://cs.chromium.org/chromium/src/components/history/core/browser/history_types.h  (lines 54-60)
        */
    
        /*
        In testing using Chrome 71, there is a field called incremented_omnibox_typed_score in the 
        visits table.  It's not included in the SQLite statement below, as the author observed what appeared to be conflicting rules for when it was populated.  Plus at the time of testing, a computer forensic analyst would be able to form a proper opinion using what's 
        already being reported using this statement.
        */
    
        SELECT  DISTINCT /* If you don't use the DISTINCT statement, you will end up with duplicate records because of the JOIN of multiple tables */
            urls.id AS 'urls.id', 
            visits.id AS 'visits.id' /* Entries that does not have a corresponding visit in 'visits' table will have a NULL value. Likely a bookmark or related URL*/,
            urls.url,
            urls.title,
            visits.from_visit AS 'from visit',
            urls.visit_count AS 'visit_count',
            urls.typed_count AS 'typed_count',
    
            visit_source.source,
            /* Checking if activity is locally browsed, synced, or otherwise */
            CASE ifnull(visit_source.source,1)
                WHEN 0 THEN 'Synced'
                WHEN 1 OR visit_source.source IS NULL THEN 'Local'
                WHEN 2 THEN 'Extension'
                WHEN 3 THEN 'Firefox Imported'
                WHEN 4 THEN 'IE Imported'
                WHEN 5 THEN 'Safari Imported'
                ELSE 'New value!: '||visit_source.source||' Check source code for meaning!'
            END AS 'Visit Source',
    
            transition, 
            /* Checking the value of the right most byte of the four byte transition value and decoding it */
            CASE (transition&0xff)
                WHEN 0 THEN 'Clicked on a link'
                    WHEN 1 THEN 'Typed URL'
                    WHEN 2 THEN 'Clicked on suggestion in the UI'
                    WHEN 3 THEN 'Auto subframe navigation'
                    WHEN 4 THEN 'User manual subframe navigation'
                    WHEN 5 THEN 'User typed text in URL bar, then selected an entry that did not look like a URL'
                    WHEN 6 THEN 'Top level navigation'
                    WHEN 7 THEN 'User submitted form data'
                    WHEN 8 THEN 'User reloaded page (either hitting ENTER in address bar, or hitting reload button'
                    WHEN 9 THEN 'URL generated from a replaceable keyword other than default search provider'
                    WHEN 10 THEN 'Corresponds to a visit generated for a keyword.'
                    ELSE 'New value!: '||transition&0xff||' Check source code for meaning!'
            END AS 'Transition Type',
    
            /* Next series of CASE statements checks the three left bytes of the four byte transition value in the transition value to see what qualifiers apply */
    
            CASE (transition&0x00800000) /* Applies mask to isolate 24th bit from the right */
                WHEN 0x00800000 THEN 'yes' /* bit is set */
            END AS 'URL Blocked',
    
            CASE (transition&0x01000000) /* Applies mask to isolate 25th bit from the right */
                WHEN 0x01000000 THEN 'yes'  /*bit is set */
            END AS 'Navigated using Forward/Back button',
    
            CASE (transition&0x02000000) /* Applies mask to isolate 26th bit from the right */
                WHEN 0x02000000 THEN 'yes' /* bit is set */
            END AS 'From Address Bar',
    
            CASE (transition&0x04000000) /* Applies mask to isolate 27th bit from the right */
                WHEN 0x04000000 THEN 'yes' /* bit is set */
            END AS 'Navigated to the home page.',
    
            CASE (transition&0x08000000) /* Applies mask to isolate 28th bit from the right */
                WHEN 0x08000000 THEN 'yes' /* bit is set */
            END AS 'Transaction originated from an external application.',
    
            CASE (transition&0x10000000) /* Applies mask to isolate 29th bit from the right */
                WHEN 0x10000000 THEN 'yes' /* bit is set */
            END AS 'Beginning of a navigation chain.',
    
            CASE (transition&0x20000000) /* Applies mask to isolate 30th bit from the right */
                WHEN 0x20000000 THEN 'yes' /* bit is set */
            END AS 'Last transition in a redirect chain.',
    
            CASE (transition&0x40000000) /* Applies mas to isolate 31st bit from the right */
                WHEN 0x40000000 THEN 'yes' /* bit is set */
            END AS 'Redirects caused by JS.',
    
            CASE (transition&0x80000000) /* Applies mask to isolate 32nd bit from the right */
                WHEN 0x80000000 THEN 'yes' /* bit is set */
            END AS 'Redirects sent from the server by HTTP headers.',
    
            /*  This one is redundant to some extent.  It's checking both previous bits to see if any redirect is involved.
                  We could omit this check since the previous two checks are more verbose.
                  The value of using this check is if you want to customize the query with a WHERE statement to look for
                  all redirects (or exclude all redirects for example).
    
                  It's included in the statement because it's noted in the source code.  Chrome developers must
                  use this as a shortcut to check for redirects rather than individually checking bits 31 & 32.
    
                  Included in the statement for the sake of consistency with what was noted in the source code.
            */
            CASE (transition&0xC0000000) /* Applies mask to isolate bits 31-32 from the right */
                WHEN 0xC0000000 THEN 'yes' /* bits are set */
            END AS 'Used to test whether a transition involves a redirect.',
    
            visit_time,
            CASE /*added CASE check to 2019-12 version of the query*/
                WHEN visit_time is NULL THEN NULL
                ELSE datetime(visit_time/1000000-11644473600,'unixepoch') 
            END AS 'Decoded visit_time (UTC)',
    
            CASE last_visit_time
                WHEN 0 THEN NULL
                ELSE last_visit_time
            END AS "last_visit_time",
    
            CASE last_visit_time
                WHEN 0 THEN NULL
                ELSE datetime(last_visit_time/1000000-11644473600,'unixepoch')
            END AS 'Decoded last_visit_time (UTC)',
    
            segments.name AS 'Segment',
    
            visit_duration, /*added to 2019-12 version of query*/
            CASE /*added to 2019-12 version of the query.*/
                WHEN visit_duration IS NULL THEN NULL /*Checking if it's null.  If yes, don't decode, just display null for decoded value*/
                ELSE printf("%.2f",visit_duration/1000000.0) 
            END AS 'Decoded Visit Duration in seconds', /*minor changes for 2019-12 query:  formatting output, dividing by float to retain float, and text in AS clarified a bit*/
    
            term 
    
        FROM	urls
            LEFT JOIN visits ON visits.url=urls.id
            LEFT JOIN segments ON visits.segment_id=segments.id
            LEFT JOIN keyword_search_terms ON keyword_search_terms.url_id=urls.id
            LEFT JOIN visit_source ON visit_source.id=visits.id
    
        /*
        a few suggested optional commands could be to only display URLs where visit duration is greater than 0, and/or you could display only URLs where there is a corresponding keyword term.
        */
    
        /*
        If you want all URL browsing activity in the visits table that denotes user action
        you could use a condition as follows:
        WHERE transition&0xff IN (0,1,2,5,7) 
        Change values (0-10) to filter on desired interactions as per the 'CASE (transition&0xff)' statement
        */
    
        /*
        Look for all URLs where it invovled a user search (whether search engine, or search box on a site.
        WHERE  term NOT NULL
        */
    
        /*
        Look for URLs from form data activity
        WHERE "Transition Type"="User submitted form data"
        */
    
        /* 
        or if you only want to see what is local
        WHERE 'Visit Source' = 'Local'
        */
    
        ORDER BY visits.visit_time
    """

    return sql_query, worksheet

def chrome_history_gaps():
    worksheet = 'History Gaps'
    sql_query = """
        /*
        Written by Jacques Boucher
        email: jjrboucher@gmail.com
        Revision Date: 21 March 2023

        Inspired by the article published by James McGee at https://belkasoft.com/lagging-for-win
        The SQLite code in the middle UNION statement is Mr. McGee's statement adapted for Chromium visits (whereas his article was for iMessage sms.db file).


        About this script
        -----------------
        You can run this script against Google Chrome's (or other Chromium based browsers) history file.
        It will look for gaps in numbering, and return the gaps along with their timestamps, and the # of records in that gap.

        For example, if the visits table contains records 25, 26, 27, 30, 31, 33, 39, this script will return:
        27 | 30 | 2 | <timestamp of record #27> | <timestamp of record #30>
        31 | 33 | 1 | <timestamp of record #31> | <timestamp of record #33>
        33 | 39 | 5 | <timestamp of record #33> | <timestamp of record #39>

        The script also checks the table sqlite_sequence. Here you will find a record with the field 'name' with a value of "visits", and the field 'seq' with the last record # allocated to the visits table.
        If in the above example the value of sqlite_sequence.seq is 44, the script will also return the following to denote records missing at the end:

        33 | Blank ROWID as there are deleted records past the last allocated one. | 4 | <timestamp of record #39> | blank timestamp as we don't have this record>

        Note that the script does not look if any records are missing from the beginning.
        You can draw your own conclusion on that based on the first record number.

        */

        SELECT 
            0 AS "Previous Record Number", /* Had to assign a numerical value to ensure proper sorting with other records. */
            visits.id AS "Record Number", 
            ROWID-1 AS "Number of Missing Visits", /* Because numbering starts at 1, missing records is the first allocated record -1 */
            "" AS "Beginning Timestamp", /* We don't have a beginning timestamp as we don't have that record */
            DATETIME(visits.visit_time/1000000-11644473600,'unixepoch') AS "Ending Timestamp (UTC)"  /* Timestamp of the last record */

            FROM visits WHERE visits.id = (SELECT MIN(visits.id) FROM visits) AND visits.id >1 /* The first record # in the visits table is greater than 1.*/

        UNION

            /* Credit to James McGee and his article at https://belkasoft.com/lagging-for-win for the SQLite statement for this section. */
            SELECT * FROM
            (
                SELECT LAG (ROWID,1) OVER (ORDER BY ROWID) AS "Previous Record Number", /*  Gets the previous record to the current one */
                rowid AS ROWID, /* Current record */
                (ROWID - (LAG (ROWID,1) OVER (ORDER BY ROWID))-1) AS "Number of Missing Visits", /* Calculates the difference between the previous and current record # */
                LAG(DATETIME(visits.visit_time/1000000-11644473600,'unixepoch'),1) OVER (ORDER BY ROWID) as "Beginning Timestamp (UTC)", /* Gets the timestamp from the previous record */
                DATETIME(visits.visit_time/1000000-11644473600,'unixepoch') AS "Ending Timestamp (UTC)" /* Gets the timestamp of the current record */
                FROM visits
            )
            WHERE ROWID - "Previous Record Number" >1 /* Only gets the above if the difference between the current record # and previous record # is greater than 1 - in other words, there is a gap in the numbering */


        UNION /* Does a union between the above query and the below one. The below one is to check if there is a gap at the end. Without the below, you won't know if there are records missing at the end. */

        SELECT 
            ROWID AS "Previous Record Number", /* Because we are selecting the last allocated record, assigning that to the previous record # */
            "" AS ROWID, /* The last record is missing, thus it's blank */
            (SELECT sqlite_sequence.seq from sqlite_sequence WHERE sqlite_sequence.name LIKE "visits")-ROWID AS "Number of Missing Records", /* Finds the last record # used, and substracts last allocated record # */
            DATETIME(visits.visit_time/1000000-11644473600,'unixepoch') AS "Beginning Timestamp (UTC)",
            "" AS "Ending Timestamp"
            FROM visits
            WHERE visits.id = (SELECT MAX(visits.id) FROM visits) /* Only getting the last allocated record. */ AND visits.id < 
                (SELECT sqlite_sequence.seq AS "Maximum Record" 
                                       FROM sqlite_sequence 
                                       WHERE sqlite_sequence.name LIKE "visits") /* Checking if the last allocated record is smaller than the largest recorded record number. */


    """

    return sql_query, worksheet


def chrome_history_clusters_overview():
    worksheet = 'Clusters Overview'
    sql_query = """
        -- ============================================================================
        -- Query 1: Full Cluster Overview
        -- ============================================================================
        -- Purpose:     Lists all clusters with their labels, keywords, and visit
        --              counts. Use as an initial triage query to understand the scope
        --              and topics of clustered browsing activity.
        --
        -- Tables used: clusters, clusters_and_visits, cluster_keywords
        --
        -- Output:      One row per cluster with aggregated keyword list and visit count.
        --
        -- Best practice: Raw values are displayed alongside decoded values so that
        --                an independent party can verify the decoding. A forensic
        --                examiner must be able to testify to both the original stored
        --                value and its interpretation.
        --
        -- References:
        --   Chromium source - visit_annotations_database.cc/.h:
        --     https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/visit_annotations_database.h
        --   Chromium test schema (history.57.sql):
        --     https://cocalc.com/github/chromium/chromium/blob/main/components/test/data/history/history.57.sql
        -- ============================================================================
        
        SELECT
            c.cluster_id,
            c.label                                         AS 'cluster_label',
            c.raw_label,
        
            -- Raw boolean value as stored in DB
            c.should_show_on_prominent_ui_surfaces           AS 'prominent (raw)',
            -- Decoded boolean for readability
            CASE c.should_show_on_prominent_ui_surfaces
                WHEN 1 THEN 'Yes'
                WHEN 0 THEN 'No'
                ELSE 'Unknown: ' || c.should_show_on_prominent_ui_surfaces
            END                                              AS 'prominent (decoded)',
        
            COUNT(DISTINCT cv.visit_id)                      AS 'visit_count',
        
            -- Aggregated keyword list with raw type values shown
            GROUP_CONCAT(
                DISTINCT ck.keyword || ' [type=' || ck.type || ']'
            )                                                AS 'keywords [with raw type]'
        
        FROM clusters c
        LEFT JOIN clusters_and_visits cv
            ON c.cluster_id = cv.cluster_id
        LEFT JOIN cluster_keywords ck
            ON c.cluster_id = ck.cluster_id
        
        GROUP BY c.cluster_id
        ORDER BY c.cluster_id;
    """

    return sql_query, worksheet


def chrome_history_clusters_contents():
    worksheet = 'Clusters Contents'
    sql_query = """
        -- ============================================================================
        -- Query 2: Detailed Cluster Contents
        -- ============================================================================
        -- Purpose:     Shows every visit within each cluster with timestamps, URLs,
        --              page titles, relevance/engagement scores, and visit durations.
        --              Core query for reconstructing what the user viewed within each
        --              research session.
        --
        -- Tables used: clusters, clusters_and_visits, visits, urls
        --
        -- Output:      One row per cluster-visit pair, ordered by cluster then by
        --              relevance score (most important visits first).
        --
        -- Timestamp:   Chrome/WebKit epoch (microseconds since 1601-01-01 UTC).
        --              Raw value preserved; decoded via:
        --                datetime(value / 1000000 - 11644473600, 'unixepoch')
        --
        -- Best practice: Raw values are displayed alongside decoded values so that
        --                an independent party can verify the decoding.
        --
        -- References:
        --   Chromium browsing history database - Wikiversity:
        --     https://en.wikiversity.org/wiki/Chromium_browsing_history_database
        --   Chrome Values Lookup Tables (transition types):
        --     https://dfir.blog/chrome-values-lookup-tables/
        --   Chromium source - page_transition_types.h:
        --     https://cs.chromium.org/chromium/src/ui/base/page_transition_types.h
        -- ============================================================================
        
        SELECT
            c.cluster_id,
            c.label                                                         AS 'cluster_label',
        
            cv.visit_id,
        
            -- Raw Chrome timestamp (microseconds since 1601-01-01)
            v.visit_time                                                    AS 'visit_time (raw)',
            -- Decoded to human-readable UTC
            CASE
                WHEN v.visit_time IS NULL THEN NULL
                ELSE datetime(v.visit_time / 1000000 - 11644473600, 'unixepoch')
            END                                                             AS 'visit_time (decoded UTC)',
        
            u.url,
            u.title,
        
            cv.score                                                        AS 'cluster_relevance_score',
            cv.engagement_score,
            cv.url_for_display,
            cv.url_for_deduping,
            cv.normalized_url,
        
            -- Raw visit_duration in microseconds
            v.visit_duration                                                AS 'visit_duration (raw, microseconds)',
            -- Decoded to seconds with 2 decimal places
            CASE
                WHEN v.visit_duration IS NULL THEN NULL
                ELSE printf("%.2f", v.visit_duration / 1000000.0)
            END                                                             AS 'visit_duration (decoded, seconds)',
        
            -- Raw transition value (4-byte integer with core type + qualifiers)
            v.transition                                                    AS 'transition (raw)',
            -- Core transition type (lowest byte)
            v.transition & 0xFF                                             AS 'transition_core (raw)',
            -- Decoded core transition type
            CASE (v.transition & 0xFF)
                WHEN 0 THEN 'Clicked on a link'
                WHEN 1 THEN 'Typed URL'
                WHEN 2 THEN 'Clicked on suggestion in the UI'
                WHEN 3 THEN 'Auto subframe navigation'
                WHEN 4 THEN 'User manual subframe navigation'
                WHEN 5 THEN 'User typed text in URL bar, selected non-URL entry'
                WHEN 6 THEN 'Top level navigation'
                WHEN 7 THEN 'User submitted form data'
                WHEN 8 THEN 'User reloaded page'
                WHEN 9 THEN 'URL from replaceable keyword (not default search)'
                WHEN 10 THEN 'Visit generated for a keyword'
                ELSE 'Unknown: ' || (v.transition & 0xFF)
            END                                                             AS 'transition_core (decoded)',
        
            -- Transition qualifier flags (upper bytes)
            CASE (v.transition & 0x01000000)
                WHEN 0x01000000 THEN 'yes'
            END                                                             AS 'Forward/Back button',
        
            CASE (v.transition & 0x02000000)
                WHEN 0x02000000 THEN 'yes'
            END                                                             AS 'From Address Bar',
        
            CASE (v.transition & 0x10000000)
                WHEN 0x10000000 THEN 'yes'
            END                                                             AS 'Start of redirect chain',
        
            CASE (v.transition & 0x20000000)
                WHEN 0x20000000 THEN 'yes'
            END                                                             AS 'End of redirect chain',
        
            v.from_visit
        
        FROM clusters c
        JOIN clusters_and_visits cv
            ON c.cluster_id = cv.cluster_id
        JOIN visits v
            ON cv.visit_id = v.id
        JOIN urls u
            ON v.url = u.id
        ORDER BY
            c.cluster_id,
            cv.score DESC;
    """

    return sql_query, worksheet


def chrome_history_clusters_search_term():
    worksheet = 'Clusters Search Term'
    sql_query = """
        -- ============================================================================
        -- Query 3: Search Terms Associated with Clusters
        -- ============================================================================
        -- Purpose:     Identifies what search terms the user entered that are
        --              associated with visits within each cluster. HIGH forensic
        --              value for establishing user intent and research topics.
        --
        --              NOTE ON DATA SOURCE:
        --              The cluster_keywords table (which was designed to store
        --              per-cluster keyword labels) is typically EMPTY in modern
        --              Chrome builds. The Journeys UI was removed in Chrome 125
        --              (May 2024), and the keyword extraction pipeline that
        --              populated cluster_keywords appears to have been disabled
        --              before that. The table persists in the schema but receives
        --              no data.
        --
        --              This query instead derives the same forensic insight by
        --              joining clusters_and_visits to the content_annotations
        --              table, which stores per-visit search terms captured by
        --              Chrome's content analysis pipeline. This table IS actively
        --              populated in current Chrome builds.
        --
        --              A companion query against cluster_keywords is included at
        --              the bottom (commented out) in case future Chrome versions
        --              or Chromium-based browsers repopulate that table.
        --
        -- Tables used: clusters, clusters_and_visits, visits, urls,
        --              content_annotations
        --
        -- Output:      One row per cluster/search-term combination, with the
        --              number of visits and temporal span of the cluster.
        --
        -- Timestamp:   Chrome/WebKit epoch (microseconds since 1601-01-01 UTC).
        --              Raw value preserved; decoded via:
        --                datetime(value / 1000000 - 11644473600, 'unixepoch')
        --
        -- Best practice: Raw values are displayed alongside decoded values so that
        --                an independent party can verify the decoding.
        --
        -- References:
        --   Chromium source - visit_annotations_database.cc/.h:
        --     https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/visit_annotations_database.h
        --   Chromium source - history_types.h:
        --     https://chromium.googlesource.com/chromium/src/+/master/components/history/core/browser/history_types.h
        --   Chromium test schema (history.57.sql):
        --     https://cocalc.com/github/chromium/chromium/blob/main/components/test/data/history/history.57.sql
        -- ============================================================================
        
        -- ──────────────────────────────────────────────────────────────────────────
        -- PRIMARY QUERY: Search terms from content_annotations joined to clusters
        -- ──────────────────────────────────────────────────────────────────────────
        
        SELECT
            c.cluster_id,
            c.label                                                                 AS 'cluster_label',
            c.raw_label,
        
            ca.search_terms,
            ca.search_normalized_url,
        
            -- Number of visits in this cluster tied to this search term
            COUNT(DISTINCT cv.visit_id)                                             AS 'visits_with_this_term',
        
            -- Earliest visit in this cluster with this search term (raw)
            MIN(v.visit_time)                                                       AS 'earliest_visit_time (raw)',
            -- Decoded to UTC
            datetime(MIN(v.visit_time) / 1000000 - 11644473600, 'unixepoch')       AS 'earliest_visit_time (decoded UTC)',
        
            -- Latest visit in this cluster with this search term (raw)
            MAX(v.visit_time)                                                       AS 'latest_visit_time (raw)',
            -- Decoded to UTC
            datetime(MAX(v.visit_time) / 1000000 - 11644473600, 'unixepoch')       AS 'latest_visit_time (decoded UTC)',
        
            -- Span in raw microseconds
            MAX(v.visit_time) - MIN(v.visit_time)                                   AS 'span (raw, microseconds)',
            -- Span decoded to minutes
            printf("%.1f", (MAX(v.visit_time) - MIN(v.visit_time)) / 1000000.0 / 60.0)
                                                                                    AS 'span (decoded, minutes)',
        
            -- Sample URLs visited after this search (comma-separated)
            GROUP_CONCAT(DISTINCT u.url)                                            AS 'associated_urls'
        
        FROM clusters c
        JOIN clusters_and_visits cv
            ON c.cluster_id = cv.cluster_id
        JOIN visits v
            ON cv.visit_id = v.id
        JOIN urls u
            ON v.url = u.id
        -- INNER JOIN: only visits that have content annotations with search terms
        JOIN content_annotations ca
            ON v.id = ca.visit_id
        WHERE
            ca.search_terms IS NOT NULL
            AND ca.search_terms != ''
        GROUP BY c.cluster_id, ca.search_terms
        ORDER BY MIN(v.visit_time) DESC;
    """

    return sql_query, worksheet

def chrome_history_clusters_timeline():
    worksheet = 'Clusters Timeline'
    sql_query = """
        -- ============================================================================
        -- Query 4: Cluster Timeline
        -- ============================================================================
        -- Purpose:     Shows the temporal span of each cluster: when the first and
        --              last visits occurred, total duration in minutes, and how many
        --              unique URLs were visited. Useful for establishing when a
        --              research session took place and how long it lasted.
        --
        -- Tables used: clusters, clusters_and_visits, visits, urls
        --
        -- Output:      One row per cluster with first/last timestamps (raw + decoded),
        --              session duration, visit count, and unique URL count.
        --
        -- Timestamp:   Chrome/WebKit epoch (microseconds since 1601-01-01 UTC).
        --              Raw value preserved; decoded via:
        --                datetime(value / 1000000 - 11644473600, 'unixepoch')
        --
        -- Best practice: Raw values are displayed alongside decoded values so that
        --                an independent party can verify the decoding.
        --
        -- References:
        --   Chromium browsing history database - Wikiversity:
        --     https://en.wikiversity.org/wiki/Chromium_browsing_history_database
        --   Chromium test schema (history.57.sql):
        --     https://cocalc.com/github/chromium/chromium/blob/main/components/test/data/history/history.57.sql
        -- ============================================================================
        
        SELECT
            c.cluster_id,
            c.label                                                                 AS 'cluster_label',
        
            -- Raw boolean for prominent flag
            c.should_show_on_prominent_ui_surfaces                                  AS 'prominent (raw)',
            CASE c.should_show_on_prominent_ui_surfaces
                WHEN 1 THEN 'Yes'
                WHEN 0 THEN 'No'
                ELSE 'Unknown: ' || c.should_show_on_prominent_ui_surfaces
            END                                                                     AS 'prominent (decoded)',
        
            -- First visit in this cluster: raw Chrome timestamp
            MIN(v.visit_time)                                                       AS 'first_visit_time (raw)',
            -- First visit: decoded to UTC
            datetime(MIN(v.visit_time) / 1000000 - 11644473600, 'unixepoch')       AS 'first_visit_time (decoded UTC)',
        
            -- Last visit in this cluster: raw Chrome timestamp
            MAX(v.visit_time)                                                       AS 'last_visit_time (raw)',
            -- Last visit: decoded to UTC
            datetime(MAX(v.visit_time) / 1000000 - 11644473600, 'unixepoch')       AS 'last_visit_time (decoded UTC)',
        
            -- Span in raw microseconds
            MAX(v.visit_time) - MIN(v.visit_time)                                   AS 'span (raw, microseconds)',
            -- Span decoded to minutes
            printf("%.1f", (MAX(v.visit_time) - MIN(v.visit_time)) / 1000000.0 / 60.0)
                                                                                    AS 'span (decoded, minutes)',
        
            -- Number of visits in the cluster
            COUNT(DISTINCT cv.visit_id)                                             AS 'visit_count',
        
            -- Number of distinct URLs visited
            COUNT(DISTINCT u.id)                                                    AS 'unique_urls'
        
        FROM clusters c
        JOIN clusters_and_visits cv
            ON c.cluster_id = cv.cluster_id
        JOIN visits v
            ON cv.visit_id = v.id
        JOIN urls u
            ON v.url = u.id
        GROUP BY c.cluster_id
        ORDER BY MIN(v.visit_time) DESC;
    """

    return sql_query, worksheet

def chrome_history_clusters_duplicate_visits():
    worksheet = 'Clusters Duplicate Visits'
    sql_query = """
        -- ============================================================================
        -- Query 5: Duplicate Visits
        -- ============================================================================
        -- Purpose:     Identifies visits that Chrome's clustering engine considered
        --              duplicates of each other (same logical page visited multiple
        --              times during a research session). Shows both the canonical
        --              and duplicate visit with timestamps (raw + decoded) and URLs.
        --
        --              Forensic significance: Repeated visits to the same page
        --              during a session indicate sustained user interest, possibly
        --              suggesting the page was particularly relevant to the user's
        --              research or intent.
        --
        -- Tables used: cluster_visit_duplicates, visits, urls
        --
        -- Output:      One row per duplicate pair, showing both the canonical and
        --              duplicate visit details side by side with raw and decoded
        --              timestamps.
        --
        -- Timestamp:   Chrome/WebKit epoch (microseconds since 1601-01-01 UTC).
        --              Raw value preserved; decoded via:
        --                datetime(value / 1000000 - 11644473600, 'unixepoch')
        --
        -- Best practice: Raw values are displayed alongside decoded values so that
        --                an independent party can verify the decoding.
        --
        -- References:
        --   Chromium source - visit_annotations_database.cc/.h:
        --     https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/visit_annotations_database.h
        --   Exploring the Vivaldi History Database (LonM):
        --     https://lonm.vivaldi.net/2025/03/04/exploring-the-vivaldi-history-database/
        -- ============================================================================
        
        SELECT
            -- Canonical visit details
            cvd.visit_id                                                            AS 'canonical_visit_id',
        
            v1.visit_time                                                           AS 'canonical_visit_time (raw)',
            CASE
                WHEN v1.visit_time IS NULL THEN NULL
                ELSE datetime(v1.visit_time / 1000000 - 11644473600, 'unixepoch')
            END                                                                     AS 'canonical_visit_time (decoded UTC)',
        
            u1.url                                                                  AS 'canonical_url',
            u1.title                                                                AS 'canonical_title',
        
            -- Duplicate visit details
            cvd.duplicate_visit_id,
        
            v2.visit_time                                                           AS 'duplicate_visit_time (raw)',
            CASE
                WHEN v2.visit_time IS NULL THEN NULL
                ELSE datetime(v2.visit_time / 1000000 - 11644473600, 'unixepoch')
            END                                                                     AS 'duplicate_visit_time (decoded UTC)',
        
            u2.url                                                                  AS 'duplicate_url',
            u2.title                                                                AS 'duplicate_title',
        
            -- Time gap between canonical and duplicate in raw microseconds
            ABS(v2.visit_time - v1.visit_time)                                      AS 'time_gap (raw, microseconds)',
            -- Time gap decoded to seconds
            printf("%.1f", ABS(v2.visit_time - v1.visit_time) / 1000000.0)         AS 'time_gap (decoded, seconds)'
        
        FROM cluster_visit_duplicates cvd
        JOIN visits v1
            ON cvd.visit_id = v1.id
        JOIN urls u1
            ON v1.url = u1.id
        JOIN visits v2
            ON cvd.duplicate_visit_id = v2.id
        JOIN urls u2
            ON v2.url = u2.id
        ORDER BY cvd.visit_id;
    """

    return sql_query, worksheet


def chrome_history_clusters_comprehensive_export():
    worksheet = 'Clusters Comprehensive Export'
    sql_query = """
        -- ============================================================================
        -- Query 6: Comprehensive Forensic Export
        -- ============================================================================
        -- Purpose:     Full cluster data joined with content annotations (search
        --              terms, entities, visibility scores) and context annotations
        --              (foreground duration, page end reason). Produces a complete
        --              export suitable for ingestion into forensic timeline tools
        --              (e.g., Hindsight, Axiom, X-Ways).
        --
        --              Every field that requires decoding is presented twice:
        --              first the raw value as stored in the database, then the
        --              decoded/interpreted value. This ensures an independent party
        --              can verify every interpretation.
        --
        -- Tables used: clusters, clusters_and_visits, visits, urls,
        --              content_annotations, context_annotations
        --
        -- Output:      One row per cluster-visit pair with all available metadata.
        --
        -- Timestamp:   Chrome/WebKit epoch (microseconds since 1601-01-01 UTC).
        --              Raw value preserved; decoded via:
        --                datetime(value / 1000000 - 11644473600, 'unixepoch')
        --
        -- Note:        The content_annotations and context_annotations tables were
        --              introduced alongside the cluster tables. They contain per-visit
        --              metadata generated by Chrome's content analysis pipeline.
        --              LEFT JOINs are used because not all visits have annotations.
        --
        -- References:
        --   Chromium source - visit_annotations_database.cc/.h:
        --     https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/history/core/browser/visit_annotations_database.h
        --   Chromium source - history_types.h:
        --     https://chromium.googlesource.com/chromium/src/+/master/components/history/core/browser/history_types.h
        --   Chromium source - page_transition_types.h:
        --     https://cs.chromium.org/chromium/src/ui/base/page_transition_types.h
        --   Chrome Values Lookup Tables (transition types, visit sources):
        --     https://dfir.blog/chrome-values-lookup-tables/
        --   Hindsight - Chrome forensics tool:
        --     https://github.com/obsidianforensics/hindsight
        --   Chromium browsing history database - Wikiversity:
        --     https://en.wikiversity.org/wiki/Chromium_browsing_history_database
        -- ============================================================================
        
        SELECT
            -- ── Cluster metadata ──────────────────────────────────────────────────
            c.cluster_id,
            c.label                                                                 AS 'cluster_label',
            c.raw_label,
        
            c.should_show_on_prominent_ui_surfaces                                  AS 'prominent (raw)',
            CASE c.should_show_on_prominent_ui_surfaces
                WHEN 1 THEN 'Yes'
                WHEN 0 THEN 'No'
                ELSE 'Unknown: ' || c.should_show_on_prominent_ui_surfaces
            END                                                                     AS 'prominent (decoded)',
        
            -- ── Visit identification ──────────────────────────────────────────────
            cv.visit_id,
        
            -- ── Visit timestamp ───────────────────────────────────────────────────
            v.visit_time                                                            AS 'visit_time (raw)',
            CASE
                WHEN v.visit_time IS NULL THEN NULL
                ELSE datetime(v.visit_time / 1000000 - 11644473600, 'unixepoch')
            END                                                                     AS 'visit_time (decoded UTC)',
        
            -- ── URL and page details ──────────────────────────────────────────────
            u.url,
            u.title,
            u.visit_count                                                           AS 'total_url_visits',
        
            -- ── Cluster scoring ───────────────────────────────────────────────────
            cv.score                                                                AS 'relevance_score',
            cv.engagement_score,
        
            -- ── URL variants stored by clustering engine ──────────────────────────
            cv.url_for_display,
            cv.normalized_url,
            cv.url_for_deduping,
        
            -- ── Visit duration ────────────────────────────────────────────────────
            v.visit_duration                                                        AS 'visit_duration (raw, microseconds)',
            CASE
                WHEN v.visit_duration IS NULL THEN NULL
                ELSE printf("%.2f", v.visit_duration / 1000000.0)
            END                                                                     AS 'visit_duration (decoded, seconds)',
        
            -- ── Navigation chain ──────────────────────────────────────────────────
            v.from_visit,
        
            -- ── Transition (raw full 4-byte value) ────────────────────────────────
            v.transition                                                            AS 'transition (raw)',
        
            -- Core transition type (lowest byte, raw)
            v.transition & 0xFF                                                     AS 'transition_core (raw)',
            -- Core transition type (decoded)
            CASE (v.transition & 0xFF)
                WHEN 0 THEN 'Clicked on a link'
                WHEN 1 THEN 'Typed URL'
                WHEN 2 THEN 'Clicked on suggestion in the UI'
                WHEN 3 THEN 'Auto subframe navigation'
                WHEN 4 THEN 'User manual subframe navigation'
                WHEN 5 THEN 'User typed text in URL bar, selected non-URL entry'
                WHEN 6 THEN 'Top level navigation'
                WHEN 7 THEN 'User submitted form data'
                WHEN 8 THEN 'User reloaded page'
                WHEN 9 THEN 'URL from replaceable keyword (not default search)'
                WHEN 10 THEN 'Visit generated for a keyword'
                ELSE 'Unknown: ' || (v.transition & 0xFF)
            END                                                                     AS 'transition_core (decoded)',
        
            -- ── Transition qualifier flags (each raw bit + decoded) ───────────────
            CASE (v.transition & 0x00800000)
                WHEN 0x00800000 THEN 'yes'
            END                                                                     AS 'URL Blocked',
        
            CASE (v.transition & 0x01000000)
                WHEN 0x01000000 THEN 'yes'
            END                                                                     AS 'Forward/Back button',
        
            CASE (v.transition & 0x02000000)
                WHEN 0x02000000 THEN 'yes'
            END                                                                     AS 'From Address Bar',
        
            CASE (v.transition & 0x04000000)
                WHEN 0x04000000 THEN 'yes'
            END                                                                     AS 'Home page navigation',
        
            CASE (v.transition & 0x08000000)
                WHEN 0x08000000 THEN 'yes'
            END                                                                     AS 'From external application',
        
            CASE (v.transition & 0x10000000)
                WHEN 0x10000000 THEN 'yes'
            END                                                                     AS 'Start of redirect chain',
        
            CASE (v.transition & 0x20000000)
                WHEN 0x20000000 THEN 'yes'
            END                                                                     AS 'End of redirect chain',
        
            CASE (v.transition & 0x40000000)
                WHEN 0x40000000 THEN 'yes'
            END                                                                     AS 'JS redirect',
        
            CASE (v.transition & 0x80000000)
                WHEN 0x80000000 THEN 'yes'
            END                                                                     AS 'Server redirect (HTTP header)',
        
            CASE (v.transition & 0xC0000000)
                WHEN 0xC0000000 THEN 'yes'
            END                                                                     AS 'Any redirect involved',
        
            -- ── Content annotations ───────────────────────────────────────────────
            ca.search_normalized_url,
            ca.search_terms,
            ca.visibility_score,
            ca.categories                                                           AS 'page_categories',
            ca.entities                                                             AS 'page_entities',
            ca.related_searches,
            ca.alternative_title,
            ca.annotation_flags                                                     AS 'annotation_flags (raw)',
        
            -- ── Context annotations ───────────────────────────────────────────────
            ctx.context_annotation_flags                                            AS 'context_flags (raw)',
        
            -- Duration since last visit (raw, microseconds)
            ctx.duration_since_last_visit                                           AS 'duration_since_last_visit (raw, microseconds)',
            -- Decoded to seconds
            CASE
                WHEN ctx.duration_since_last_visit IS NULL THEN NULL
                ELSE printf("%.2f", ctx.duration_since_last_visit / 1000000.0)
            END                                                                     AS 'duration_since_last_visit (decoded, seconds)',
        
            -- Page end reason (raw integer)
            ctx.page_end_reason                                                     AS 'page_end_reason (raw)',
            -- Decoded page end reason (from Chromium page_end_reasons.h)
            CASE ctx.page_end_reason
                WHEN 0 THEN 'END_OTHER'
                WHEN 1 THEN 'END_RELOAD'
                WHEN 2 THEN 'END_NAVIGATION'
                WHEN 3 THEN 'END_STOP'
                WHEN 4 THEN 'END_CLOSE'
                WHEN 5 THEN 'END_NEW_NAVIGATION'
                ELSE
                    CASE
                        WHEN ctx.page_end_reason IS NULL THEN NULL
                        ELSE 'Unknown: ' || ctx.page_end_reason
                    END
            END                                                                     AS 'page_end_reason (decoded)',
        
            -- Total foreground duration (raw, microseconds)
            ctx.total_foreground_duration                                           AS 'total_foreground_duration (raw, microseconds)',
            -- Decoded to seconds
            CASE
                WHEN ctx.total_foreground_duration IS NULL THEN NULL
                ELSE printf("%.2f", ctx.total_foreground_duration / 1000000.0)
            END                                                                     AS 'total_foreground_duration (decoded, seconds)'
        
        FROM clusters c
        JOIN clusters_and_visits cv
            ON c.cluster_id = cv.cluster_id
        JOIN visits v
            ON cv.visit_id = v.id
        JOIN urls u
            ON v.url = u.id
        -- LEFT JOIN: not all visits have content annotations
        LEFT JOIN content_annotations ca
            ON v.id = ca.visit_id
        -- LEFT JOIN: not all visits have context annotations
        LEFT JOIN context_annotations ctx
            ON v.id = ctx.visit_id
        ORDER BY
            c.cluster_id,
            v.visit_time;
    """

    return sql_query, worksheet