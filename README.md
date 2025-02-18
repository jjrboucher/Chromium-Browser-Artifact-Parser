**NOTE:** The script was written for and tested against a Chrome profile on a Windows computer. It has been tested against Edge on Windows and works. But it won't work against a mobile Chrome user profile where the SQLite files have a different name (and possibly different structure requiring a different SQLite statement to work correctly?).<br>

**The application will look for the word "edge" (case insensitive) in the path.** If it's present, it will run the Edge specific SQLite statement to parse data in **WebAssistDatabase**. In a future update I hope to rely on the Preferences file to make that determination. The application could simply try to run the SQLite for Edge and skip over it when it can't find the file. But it will result in the summary worksheet showing that there are 0 items for that particular artifact. That could caues confusion given the artifact was not observed in Chrome, only Edge.<br>


When you run the script, it prompts you first for the browser profile folder you wish to process.

Next, it prompts you for the location and name of the MS Excel spreadsheet that is used for the output of the script.

It will work with Google Chrome profiles. It will also work with other Chromium browsers such as Edge. But some of the info in the Preferences file that the script parses may differ in other Chromium browsers. It's also possible that other Chromium browsers could have additional fields or tables not present in Chrome (e.g., Edge). Those will be missed by the script if I haven't coded for them. To date, The Edge database **WebAssistDatabase** is the only one I've identified that appears unique to Edge which I've added to the application. In testing on Chrome and Edge, it seems to work well overall with both. Edge does have additional useful details in the Preferences file that I do not yet parse.

Older versions of Chrome used different tables and fields in some of the SQLite files, particularly as it relates to form data. This script is not designed to support those older versions.

If there is other data you know that can be parsed that is not being parsed, please reach out to me at the following gmail address: jjrboucher

There are package requirements which you can find in the requirements.txt file.

