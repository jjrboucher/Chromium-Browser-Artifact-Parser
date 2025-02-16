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
        try:
            previous_nav = self.prefs.get("NewTabPage").get("PrevNavigationTime")
        except (KeyError, IndexError):
            previous_nav = "not found"

        return 'None' if previous_nav is None else previous_nav

    def email(self):
        try:
            email_address =  self.prefs.get("account_info")[0].get("email")
        except (KeyError, IndexError):
            email_address =  "not found"

        return 'None' if email_address is None else email_address

    def full_name(self):
        try:
            full_name =  self.prefs.get("account_info")[0].get("full_name")
        except (KeyError, IndexError):
            full_name =  "not found"

        return 'None' if full_name is None else full_name

    def gaia(self):
        try:
            gaia_number =  self.prefs.get("account_info")[0].get("gaia")
        except (KeyError, IndexError):
            gaia_number =  "not found"

        return 'None' if gaia_number is None else gaia_number

    def given_name(self):
        try:
            given_name: object =  self.prefs.get("account_info")[0].get("given_name")
        except (KeyError, IndexError):
            given_name = "not found"

        return 'None' if given_name is None else given_name

    def thumbnail_url(self):
        try:
            thumbnail_url =  self.prefs.get("account_info")[0].get("picture_url")
        except (KeyError, IndexError):
            thumbnail_url =  "not found"

        return 'None' if thumbnail_url is None else thumbnail_url

    def language(self):
        try:
            lang =  self.prefs.get("account_info")[0].get("locale")
        except (KeyError, IndexError):
            lang =  "not found"

        return 'None' if lang is None else lang

    def privacy_settings(self):
        try:
            privacy_settings =  self.prefs.get("browser").get("clear_data")
        except(KeyError, IndexError):
            privacy_settings = "not found"

        return 'None' if privacy_settings is None else privacy_settings

    def country_id(self):
        try:
            c_id_int = self.prefs.get("countryid_at_install")  # Get the INT value
            binary_number = (c_id_int.bit_length() +7) // 8  # Determines the # of bytes in the decoded value
            binary_array =c_id_int.to_bytes(binary_number, "big")  # convert to an array - big endian
            country_id =  f'{c_id_int} = {binary_array.decode()}'  # return the raw and decoded values
        except (KeyError, IndexError):
            country_id =  "not found"

        return 'None' if country_id is None else country_id

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
        except (KeyError, IndexError):
            creation_time =  "not found"

        return 'None' if creation_time is None else creation_time

    def profile_created_version(self):
        try:
            profile_version =  self.prefs.get("profile").get("created_by_version")
        except (KeyError, IndexError):
            profile_version = "not found"

        return 'None' if profile_version is None else profile_version

    def download_directory(self):
        try:
            dd =  self.prefs.get("download").get("default_directory")
        except (KeyError, IndexError):
            try:
                dd =  self.prefs.get("savefile").get("default_directory")
            except (KeyError, IndexError):
                dd =  "not found"

        return 'None' if dd is None else dd

    def prompt_for_download(self):
        try:
            prompt =  self.prefs.get("download").get("prompt_for_download")
        except (KeyError, IndexError):
            prompt =  "not found"

        return 'None' if prompt is None else prompt

    def most_visited(self):
        """
        links you see on a new tab
        """
        try:
            mv = self.prefs.get("custom_links").get("list")
        except (KeyError, IndexError):
            mv = "not found"

        if mv != "not found":  # meaning there are URLs to parse
            mv_parsed = f''

            for entry in mv:
                mv_parsed = mv_parsed + (f'     isMostVisited: {entry.get("isMostVisited")},  '
                                       f'title: {entry.get("title")},  '
                                       f'url: {entry.get("url")}\n')

        return mv_parsed

    def __str__(self):

        return (f'\nEmail: {self.email()}\n'
                f'Full name: {self.full_name()}\n'
                f'Given name: {self.given_name()}\n'
                f'gaia: {self.gaia()}\n'
                f'Thumbnail URL: {self.thumbnail_url()}\n'
                f'Profile created: {self.profile_created_date()}\n'
                f'Profile created using browser version: {self.profile_created_version()}\n'
                f'Default Download Directory: {self.download_directory()}\n'
                f'Prompt for Download Directory: {self.prompt_for_download()}'
                f'\n\nThe following are shortcuts that appear on a new tab:\n'
                f'{self.most_visited()}')