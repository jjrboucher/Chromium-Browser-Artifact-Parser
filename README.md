When you run the script, it prompts you first for the browser profile folder you wish to process.

Next, it prompts you for the location and name of the MS Excel spreadsheet that is used for the output of the script.

It will work with Google Chrome profiles. It will also work with other Chromium browsers such as Edge. But some of the info in the Preferences file that the script parses may differ in other Chromium browsers. It's also possible that other Chromium browsers could have additional fields or tables not present in Chrome. Those will naturally be missed by the script. But in testing on Chrome and Edge, it seems to work well overall with both. Edge does have additional useful details in the Preferences file that I do not yet parse.

Older versions of Chrome used different tables and fields in some of the SQLite files, particularly as it relates to form data. This script is not designed to support those older versions.

If there is other data you know that can be parsed that is not being parsed, please reach out to me at the following gmail address: jjrboucher

There are package requirements which you can find in the requirements.txt file.

