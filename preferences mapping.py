import json

with open ('C:/Users/Forensics/AppData/Local/Google/Chrome/User Data/Default/Preferences', 'r', encoding='utf8') as profile:
    p = json.load(profile)

# account info
for i in ['email', 'full_name', 'gaia', 'given_name', 'picture_url']:
    print(f'{i}: {p["account_info"][0][i]}')

# privacy settings

for privacy in p['browser']['clear_data'].keys():
    print(f'{privacy}: {p['browser']['clear_data'][privacy]}')

# shortcuts that appears on new tab
#Is it set?
p['custom_links']['initialized']
# what are they?
for items in p['custom_links']['list']:
    print(f'title: {items['title']}, url: {items['url']}')

# country at install
# it's a decimal #. You need to convert to binary, extract the left and right bytes, then convert those to ASCII.
p['countryid_at_install']  # returns an integer
left_byte = bin(p['countryid_at_install'])[2:-8]
right_byte = bin(p['countryid_at_install'])[-8:]
country=chr(int(left_byte, 2))+chr(int(right_byte, 2))

# downloads
p['savefile']['default_directory']
p['download']['last_complete_time']  # needs to be converted from webkit time
p['download']['prompt_for_download']

# sync info
# lots under p['sync']
# what is configured to sync:
for k in p['sync']['data_type_status_for_sync_to_signin'].keys():
    print(f'{k}: {p['sync']['data_type_status_for_sync_to_signin'][k]}')
