import json

class Preferences:
    """
    This class accepts a "Preferences" file as input (with full path)
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

    def __str__(self):

        return (f'Email: {self.email()}\n'
                f'Full name: {self.full_name()}\n'
                f'Given name: {self.given_name()}\n'
                f'gaia: {self.gaia()}\n'
                f'Thumbnail URL: {self.thumbnail_url()}')