def chrome_favicons():
    # parses the favicons in the Favicons SQLite file

    worksheet = 'FavIcons'
    sql_query = """
            /*
            Last updated 2024-09-25
            Author: Jacques Boucher - jjrboucher@gmail.com
            Tested with:  Chrome 129
            */
            
            /* 
            Google Chrome Query
            Runs against the Favicons SQLite file
            Extracts favicons information. 
            
            Decoded icon_type is commented out, as the author has not yet confirmed that it's indeed what is found in 
            the source code at: 
            https://cs.chromium.org/chromium/src/components/favicon_base/favicon_types.h?q=icon_type&g=0&l=86 
            lines 142-171
            
            If you run this from within DB Browser for SQLite, you can double click on a BLOB for the image_data and 
            select "Image" mode in the lower right pane to see the image of the favicon.
            */
            
            /*
            References:
            https://cs.chromium.org/chromium/src/ui/base/page_transition_types.h
            
            https://cs.chromium.org/chromium/src/components/history/core/browser/history_types.h  (lines 54-60)
            
            https://source.chromium.org/chromium/chromium/src/+/main:components/favicon/core/favicon_database.cc?q
            =icon_type%3D&ss=chromium 
            (lines 37-82) 
            */
            
            
            SELECT  favicons.id, 
                    icon_mapping.page_url AS 'page URL', 
                    favicons.url  AS 'favicon URL', 
                    favicon_bitmaps.image_data, 
                    (favicon_bitmaps.height || " X " || favicon_bitmaps.width) AS "icon dimensions", 
                    favicons.icon_type,
                    
                    /* REF: 
                    https://source.chromium.org/chromium/chromium/src/+/main:out/android-Debug/gen/components/favicon/
                    android/java/generated_java/input_srcjars/org/chromium/components/favicon/IconType.java?
                    q=touch_precomposed_icon&ss=chromium
                    */ 
                    CASE favicons.icon_type 
                        WHEN 0 THEN "INVALID" 
                        WHEN 1 THEN "FAVICON" 
                        WHEN 2 THEN "TOUCH_ICON" 
                        WHEN 3 THEN "TOUCH_PRECOMPOSED_ICON" 
                        WHEN 4 THEN "WEB_MANIFEST_ICON" 
                        ELSE "New value!: "||favicons.icon_type||" Check source code for meaning!" 
                    END AS "Icon Type (decoded)",
            
                    favicon_bitmaps.last_updated, 
                    CASE favicon_bitmaps.last_updated
                        WHEN 0 THEN 0
                        ELSE datetime(favicon_bitmaps.last_updated/1000000-11644473600,'unixepoch') 
                    END AS 'Decoded last_updated (UTC)',
                    
                    favicon_bitmaps.last_requested,
                    CASE favicon_bitmaps.last_requested
                        WHEN 0 THEN 0
                        ELSE datetime(favicon_bitmaps.last_requested/1000000-11644473600,'unixepoch')
                    END AS 'Decoded last_requested (UTC)'
            
            FROM 	favicons
                    LEFT JOIN favicon_bitmaps ON favicon_bitmaps.icon_id == favicons.id
                    LEFT JOIN icon_mapping ON icon_mapping.icon_id == favicons.id
        """

    return sql_query, worksheet
