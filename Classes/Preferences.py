from datetime import datetime, timedelta
import json

class Preferences:
    """
    This class accepts a "Preferences" file as input (with full path).
    Currently parses Chrome artifacts. Edge has some slightly different artifacts, but so far working for Edge
    with exception that some preferences in the Preferences file are different in Edge, so missing those.
    """

    def __init__(self, pref_file):
        self.pref_file = pref_file
        with open(self.pref_file, 'r', encoding='utf-8') as p:
            self.prefs = json.load(p)

    def previous_nav(self):
        return self.prefs.get("NewTabPage").get("PrevNavigationTime")

    def email(self):
        return self.prefs.get("account_info")[0].get("email")

    def full_name(self):
        return self.prefs.get("account_info")[0].get("full_name")

    def gaia(self):
        return self.prefs.get("account_info")[0].get("gaia")

    def given_name(self):
        return self.prefs.get("account_info")[0].get("given_name")

    def thumbnail_url(self):
        return self.prefs.get("account_info")[0].get("picture_url")

    def language(self):
        return self.prefs.get("account_info")[0].get("locale")

    def privacy_settings(self):
        return self.prefs.get("browser").get("clear_data")

    def country_id(self):
        c_id_int = self.prefs.get("countryid_at_install")  # Get the INT value
        binary_number = (c_id_int.bit_length() +7) // 8  # Determines the # of bytes in the decoded value
        binary_array =c_id_int.to_bytes(binary_number, "big")  # convert to an array - big endian
        return f'{c_id_int} = {binary_array.decode()}'  # return the raw and decoded values

    def profile_created_date(self):
        creation_time = self.prefs.get("profile").get("creation_time")
        # WebKit timestamp is in microseconds since January 1, 1601
        base_date = datetime(1601, 1, 1)
        # Convert WebKit time (microseconds) to seconds
        timestamp_in_seconds = int(creation_time) / 1_000_000
        # Add to base date
        human_readable_date = base_date + timedelta(seconds=timestamp_in_seconds)
        return f'{creation_time} = {human_readable_date} UTC'

    def profile_created_version(self):
        return self.prefs.get("profile").get("created_by_version")

    def download_directory(self):
        return self.prefs.get("savefile").get("default_directory)")

    def __str__(self):

        return (f'\nEmail: {self.email()}\n'
                f'Full name: {self.full_name()}\n'
                f'Given name: {self.given_name()}\n'
                f'gaia: {self.gaia()}\n'
                f'Thumbnail URL: {self.thumbnail_url()}\n'
                f'Profile created: {self.profile_created_date()}\n'
                f'Profile created using browser version {self.profile_created_version()}\n'
                f'Default Download Directory: {self.download_directory()}')