**IMPORTANT CAVEATS - NOT A FORENSIC TOOL - THIS IS A TRIAGE TOOL**

**The guides included with the script were created with Claude.ai. Thus, there may be some inaccuracies in the instructions. But they should suffice to allow you to successfully use the application and review the output.**

**programer's manual** technical manual about the application

**user's guide** Guide for those who will run the application

**investigator's guide** Guide to give to your investigator who will be reviewing the extracted report in Excel

The script currently opens the DB in Read Only mode. Journaling file not processed. Meaning there could be pending transactions in the journaling file that you will not see in the output of this script.

The script also does not look for deleted pages within an SQLite file.

**NOTE:** The script was written for and tested against a Chrome profile on a Windows computer. It has been tested against Edge on Windows and works. But it won't work against a mobile Chrome user profile where the SQLite files have a different name (and possibly different structure requiring a different SQLite statement to work correctly?).<br>

**The application will look for the word "edge" (case insensitive) in the path.** If it's present, it will run the Edge specific SQLite statement to parse data in **WebAssistDatabase**. In a future update I hope to rely on the Preferences file to make that determination. The application could simply try to run the SQLite for Edge and skip over it when it can't find the file. But it will result in the summary worksheet showing that there are 0 items for that particular artifact. That could cause confusion given the artifact was not observed in Chrome, only Edge.<br>


When you run the script, it prompts you first for the browser profile folder you wish to process.

Next, it prompts you for the location and name of the MS Excel spreadsheet that is used for the output of the script.

It will work with Google Chrome profiles. It will also work with other Chromium browsers such as Edge. But some of the info in the Preferences file that the script parses may differ in other Chromium browsers. It's also possible that other Chromium browsers could have additional fields or tables not present in Chrome (e.g., Edge). Those will be missed by the script if I haven't coded for them. To date, The Edge database **WebAssistDatabase** is the only one I've identified that appears unique to Edge which I've added to the application. In testing on Chrome and Edge, it seems to work well overall with both. Edge does have additional useful details in the Preferences file that I do not yet parse.

Older versions of Chrome used different tables and fields in some of the SQLite files, particularly as it relates to form data. This script is not designed to support those older versions.

**New in version 2026-Mar-1:**
- **History Clusters** artifact: Parses the cluster tables introduced in modern Chrome builds (`clusters`, `clusters_and_visits`, `content_annotations`, `context_annotations`, `cluster_visit_duplicates`). Produces six dedicated worksheets — Clusters Overview, Clusters Contents, Clusters Search Term, Clusters Timeline, Clusters Duplicate Visits, and Clusters Comprehensive Export. Note: the `cluster_keywords` table is empty in current Chrome builds (the Journeys UI was removed in Chrome 125); search terms are instead derived from the `content_annotations` table.
- **Extensions** artifact: Reads each extension's `manifest.json` from the `Extensions/` subfolder of the profile and extracts the extension ID, name, version, description, author, and homepage URL.
- Tested with Chrome 129, 145, Edge 129, Opera 113.

If there is other data you know that can be parsed that is not being parsed, please reach out to me at the following gmail address: jjrboucher

There are package requirements which you can find in the requirements.txt file.
