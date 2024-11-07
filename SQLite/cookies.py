# See code at https://www.cyberark.com/resources/threat-research-blog/the-current-state-of-browser-cookies
# to implement decryption of cookie.
# Another example: https://gist.github.com/DakuTree/428e5b737306937628f2944fbfdc4ffc
# Other resource: https://www.bleepingcomputer.com/news/security/new-tool-bypasses-google-chromes-new-cookie-encryption-system/

def chrome_cookies():
    worksheet = "Cookies"
    sql_query = """
        /*
        Last modified: 2024-09-24
        Author: Jacques Boucher - jjrboucher@gmail.com
        Tested with: Chrome v. 129
        */
        
        /*
        Chrome Browser
        Runs against cookies SQLite file located in the Networks folder
        Extracts data from cookies table.
        */
        
         SELECT	name,
                host_key,
                creation_utc,
                datetime(creation_utc/1000000-11644473600,'unixepoch') AS 'Decoded creation_utc (UTC)',
                last_access_utc,
                datetime(last_access_utc/1000000-11644473600,'unixepoch') AS 'Decoded last_access_utc (UTC)',
                last_update_utc,
                datetime(last_update_utc/1000000-11644473600,'unixepoch') AS 'Decoded last_update_utc(UTC)',
                expires_utc,
                CASE expires_utc
                    WHEN 0 then ""
                    ELSE datetime(expires_utc/1000000-11644473600,'unixepoch')
                END  AS 'Decoded expires_utc(UTC)'
                
        FROM cookies   
    """

    return sql_query, worksheet
