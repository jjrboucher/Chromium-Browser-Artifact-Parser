from datetime import datetime, timedelta
import json

class Preferences:
    """
    This class accepts a "Preferences" file as input (with full path).
    Currently, parses Chrome artifacts. Edge has some slightly different artifacts, but so far working for Edge
    with exception that some preferences in the Preferences file are different in Edge, so missing those.
    """

    def __init__(self, pref_file):
        self.pref_file = pref_file
        #self.browser = browser
        with open(self.pref_file, 'r', encoding='utf-8') as p:
            self.prefs = json.load(p)

    def email(self):
        try:
            email_address =  self.prefs.get("account_info")[0].get("email")
        except (KeyError, IndexError, AttributeError, TypeError):
            email_address =  "not found"

        return 'None' if email_address is None else email_address

    def full_name(self):
        try:
            full_name =  self.prefs.get("account_info")[0].get("full_name")
        except (KeyError, IndexError, AttributeError, TypeError):
            full_name =  "not found"

        return 'None' if full_name is None else full_name

    def gaia(self):
        try:
            gaia_number =  self.prefs.get("account_info")[0].get("gaia")
        except (KeyError, IndexError, AttributeError, TypeError):
            gaia_number =  "not found"

        return 'None' if gaia_number is None else gaia_number

    def given_name(self):
        """
        Returns Google given name
        """
        try:
            given_name: object =  self.prefs.get("account_info")[0].get("given_name")
        except (KeyError, IndexError, AttributeError, TypeError):
            given_name = "not found"

        return given_name

    def profile_name(self):
        """
        Returns the profile name
        """
        try:
            profile_name: object =  self.prefs.get("profile").get("name")
        except (KeyError, IndexError, AttributeError, TypeError):
            profile_name = "not found"

        return profile_name

    def edge_first_name(self):

        try:
            fname = self.prefs.get("account_info")[0].get("edge_account_first_name")
        except (KeyError, IndexError, AttributeError, TypeError):
            fname = "not found"

        return fname

    def edge_last_name(self):

        try:
            lname = self.prefs.get("account_info")[0].get("edge_account_last_name")
        except (KeyError, IndexError, AttributeError, TypeError):
            lname = "not found"

        return lname


    def thumbnail_url(self):
        try:
            thumbnail_url =  self.prefs.get("account_info")[0].get("picture_url")
        except (KeyError, IndexError, AttributeError, TypeError):
            thumbnail_url =  "not found"

        return 'None' if thumbnail_url is None else thumbnail_url

    def language(self):
        try:
            lang =  self.prefs.get("account_info")[0].get("locale")
        except (KeyError, IndexError, AttributeError, TypeError):
            lang =  "not found"

        return lang

    def privacy_settings(self):
        try:
            privacy_settings =  self.prefs.get("browser").get("clear_data")
        except(KeyError, IndexError, AttributeError, TypeError):
            privacy_settings = "not found"

        return 'None' if privacy_settings is None else privacy_settings

    def country_id(self):
        try:
            c_id_int = self.prefs.get("countryid_at_install")  # Get the INT value
            binary_number = (c_id_int.bit_length() +7) // 8  # Determines the # of bytes in the decoded value
            binary_array =c_id_int.to_bytes(binary_number, "big")  # convert to an array - big endian
            country_id =  f'{c_id_int} = {binary_array.decode()}'  # return the raw and decoded values
        except (KeyError, IndexError, AttributeError, TypeError):
            country_id =  "not found"

        return country_id

    def profile_created_date(self):
        try:
            creation_time = self.prefs.get("profile").get("creation_time")
            # WebKit timestamp is in microseconds since January 1, 1601
            base_date = datetime(1601, 1, 1)
            # Convert WebKit time (microseconds) to seconds
            timestamp_in_seconds = int(creation_time) / 1_000_000
            # Add to base date
            human_readable_date = base_date + timedelta(seconds=timestamp_in_seconds)
            creation_time =  f'{creation_time} = {human_readable_date} UTC'
        except (KeyError, IndexError, AttributeError, TypeError):
            creation_time =  "not found"

        return creation_time

    def previousNavigationTime(self):
        try:
            prev_nav_time = self.prefs.get("NewTabPage").get("PrevNavigationTime")
            # WebKit timestamp is in microseconds since January 1, 1601
            base_date = datetime(1601, 1, 1)
            # Convert WebKit time (microseconds) to seconds
            timestamp_in_seconds = int(prev_nav_time) / 1_000_000
            # Add to base date
            human_readable_date = base_date + timedelta(seconds=timestamp_in_seconds)
            prev_nav_time =  f'{prev_nav_time} = {human_readable_date} UTC'
        except (KeyError, IndexError, AttributeError, TypeError):
            prev_nav_time =  "not found"

        return prev_nav_time


    def profile_created_version(self):
        try:
            profile_version =  self.prefs.get("profile").get("created_by_version")
        except (KeyError, IndexError, AttributeError, TypeError):
            profile_version = "not found"

        return profile_version

    def download_directory(self):
        try:
            dd =  self.prefs.get("download").get("default_directory")
        except (KeyError, IndexError, AttributeError, TypeError):
            dd =  "not found"

        return dd

    def save_file_directory(self):
        try:
            sfd =  self.prefs.get("savefile").get("default_directory")
        except (KeyError, IndexError, AttributeError, TypeError):
            sfd =  "not found"

        return sfd

    def prompt_for_download(self):
        try:
            prompt =  self.prefs.get("download").get("prompt_for_download")
        except (KeyError, IndexError, AttributeError, TypeError):
            prompt =  "not found"

        return prompt

    def new_tab(self):
        """
        links you see on a new tab
        """

        mv_parsed = ''
        try:
            mv = self.prefs.get("custom_links").get("list")
        except (KeyError, IndexError, AttributeError, TypeError):
            mv = "not found"

        if mv != "not found":  # meaning there are URLs to parse
            mv_parsed = f''
            for entry in mv:
                mv_parsed = mv_parsed + (f'     isMostVisited: {entry.get("isMostVisited")},  '
                                       f'title: {entry.get("title")},  '
                                       f'url: {entry.get("url")}\n')

        return f'     Nil' if mv_parsed == "" else mv_parsed

    def startup(self):
        """
        Returns the startup value and verbose description
        1 = Continue from where you left off.
        4 = Open specific URLs.
        5 = Open the New Tab page.

        Other values not defined at this time

        """

        startup_option={1:"Continue where you left off",
                        4:"Open specific URLs",
                        5:"Open the New Tab page"}

        try:
            startup_value = self.prefs.get("session").get("restore_on_startup")
        except (KeyError, IndexError, AttributeError, TypeError):
            startup_value = "not found"

        if startup_value != "not found":  # meaning there is a value
            return f'{startup_value}: {startup_option[startup_value]}' if startup_value in startup_option.keys() \
                else f'{startup_value}: New Value! Check source code.'

        return startup_value

    def startup_urls(self):
        """
        Returns the startup URLs.
        """
        url_list = f''
        try:
            urls = self.prefs.get("session").get("startup_urls")
        except (KeyError, IndexError, AttributeError, TypeError):
            urls = "not found"
            url_list = f'\n     Nil'

        if urls != "not found":  # meaning there are startup URLs.
            # returns a list of one or more URLs which must be broken down.
            for url in urls:
                url_list = url_list + f'\n     {url}'

        return url_list

    def homepage(self):
        """
        Returns the setting for the homepage button
        """
        try:
            home = self.prefs.get("homepage")
        except (KeyError, IndexError, AttributeError, TypeError):
            home = "not found"

        return "None" if home == "" else home

    def homepagenewtab(self):
        """
        Returns whether the home page button is a new tab.
        """

        try:
            homenewtab = self.prefs.get("homepage_is_newtabpage")
        except (KeyError, IndexError, AttributeError, TypeError):
            homenewtab = "not found"

        return homenewtab

    def exit_type(self):
        """
        Returns the exit type - Normal or Crashed
        """

        return self.prefs.get("profile").get("exit_type")

    def edgeArtifacts(self):
        """
        Returns Edge artifacts if present
        """
        try:
            edgeFirstName = f'Edge First name: {self.edge_first_name()}\n'
        except (KeyError, IndexError, AttributeError, TypeError):
            edgeFirstName = 'not found'

        try:
            edgeLastName = f'Edge Last name: {self.edge_last_name()}\n'
        except (KeyError, IndexError, AttributeError, TypeError):
            edgeLastName = 'not found'

        return (f'Edge First Name: {edgeFirstName}\n'
                f'Edge Last Name: {edgeLastName}\n')

    def chrome_sync(self):
        """
        To be parsed in the future
        self.prefs.get("sync").get("data_type_status_for_sync_to_signin")
        Use a tuple of values to parse
        """
        pass

    def edge_sync(self):
        """
        To be parsed in the future
        self.prefs.get("sync")
        use a tuple of values to parse
        """
        pass


    def __str__(self):

        preferences =  (f'\nEmail: {self.email()}\n'
                f'Full name: {self.full_name()}\n'
                f'Given name: {self.given_name()}\n'
                f'Profile name: {self.profile_name()}\n'
                f'Edge First Name (if applicable): {self.edge_first_name()}\n'
                f'Edge Last Name (if applicable): {self.edge_last_name()}\n'
                f'gaia: {self.gaia()}\n'
                f'Thumbnail URL: {self.thumbnail_url()}\n'
                f'Profile created: {self.profile_created_date()}\n'
                f'Profile created using browser version: {self.profile_created_version()}\n'
                f'Previous Navigation Time: {self.previousNavigationTime()}\n'
                f'Country ID at install: {self.country_id()}\n'
                f'Language: {self.language()}\n'
                f'Default Download Directory: {self.download_directory()}\n'
                f'Prompt for Download Directory: {self.prompt_for_download()}\n'
                f'Last "Save As" Directory: {self.save_file_directory()}\n'
                f'Exit Type: {self.exit_type()}\n'
                f'URL for Homepage button: {self.homepage()}\n'
                f'Is homepage a new tab? {self.homepagenewtab()}\n'
                f'Startup value: {self.startup()}\n'
                f'URL startup list: {self.startup_urls()}\n'
                f'\nThe following are shortcuts that appear on a new tab:\n'
                f'{self.new_tab()}')

        return preferences