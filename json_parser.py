#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import typing 
from pathlib import Path

class JsonParser:

    # CORE_DATA
    PMCID = 'PMCID'
    FIRST_AUTHOR = 'FIRST_AUTHOR'
    # NOTE: CHANGE
    FIRST_AUTHOR_NAME = 'FIRST_AUTHOR_NAME'
    # NOTE: CHANGE
    LAST_AUTHOR = 'LAST_AUTHOR'
    # NOTE: CHANGE
    LAST_AUTHOR_NAME = 'LAST_AUTHOR_NAME'
    # NOTE: CHANGE
    ASSOCIATED_AUTHORS = 'ASSOCIATED_AUTHORS'

    # FIRST_AUTHOR_NATION
    ## name
    # FIRST_AUTHOR_NATION_NAME = 'FIRST_AUTHOR_NATION_NAME'
    # FIRST_AUTHOR_NATION_PROBABILITY_NAME = 'FIRST_AUTHOR_COUNTRY_PROBABILITY_NAME'
    # FIRST_AUTHOR_NATION_STATUS_NAME = 'FIRST_AUTHOR_NATION_STATUS_NAME'
    ## surname 
    # FIRST_AUTHOR_NATION_SURNAME = 'FIRST_AUTHOR_NATION_SURNAME'
    # FIRST_AUTHOR_NATION_PROBABILITY_SURNAME = 'FIRST_AUTHOR_COUNTRY_PROBABILITY_SURNAME'
    # FIRST_AUTHOR_NATION_STATUS_SURNAME = 'FIRST_AUTHOR_NATION_STATUS_SURNAME'
    # FIRST_AUTHOR_GENDER
    FIRST_AUTHOR_GENDER = 'FIRST_AUTHOR_GENDER'
    FIRST_AUTHOR_GENDER_PROBABILITY = 'FIRST_AUTHOR_GENDER_PROBABILITY'
    FIRST_NAME_GENDER_STATUS = 'FIRST_NAME_GENDER_STATUS'
    # FIRST_AUTHOR_SELECTED_NATION_CATEGORY = 'FIRST_AUTHOR_SELECTED_NATION_CATEGORY'

    # LAST_AUTHOR_NATION
    ## name
    # LAST_AUTHOR_NATION_NAME = 'LAST_AUTHOR_NATION_NAME'
    # LAST_AUTHOR_NATION_PROBABILITY_NAME = 'LAST_AUTHOR_COUNTRY_PROBABILITY_NAME'
    # LAST_AUTHOR_NATION_STATUS_NAME = 'LAST_AUTHOR_NATION_STATUS_NAME'
    # ## surname
    # LAST_AUTHOR_NATION_SURNAME = 'LAST_AUTHOR_NATION_SURNAME'
    # LAST_AUTHOR_NATION_PROBABILITY_SURNAME = 'LAST_AUTHOR_COUNTRY_PROBABILITY_SURNAME'
    # LAST_AUTHOR_NATION_STATUS_SURNAME = 'LAST_AUTHOR_NATION_STATUS_SURNAME'
    # LAST_AUTHOR_GENDER
    LAST_AUTHOR_GENDER = 'LAST_AUTHOR_GENDER'
    LAST_AUTHOR_PROBABILITY = 'LAST_AUTHOR_PROBABILITY'
    LAST_AUTHOR_GENDER_STATUS = 'LAST_AUTHOR_GENDER_STATUS'
    LAST_AUTHOR_GENDER_PROBABILITY = 'LAST_AUTHOR_GENDER_PROBABILITY'
    # LAST_AUTHOR_SELECTED_NATION_CATEGORY = 'LAST_AUTHOR_SELECTED_NATION_CATEGORY'


    def read(json_path: dict) -> dict :
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)


    def get_authors(json_entries: dict) -> dict:
        """
        Get first and last authors for each project (pmcid)
        ------------------------------------
            :param json_entries: Json project data
        """
        authors_dict = {}
        for entry in json_entries:

            # Transform string to list
            authors_list = json.loads(entry.get('authors', '[]'))
            
            # NOTE: CHANGE
            # Check if authors_list is not empty
            if authors_list:
                authors_dict[entry.get('pmcid')] = {
                    'first_author' : authors_list[0].strip(), 
                    'first_author_firstname' : authors_list[1].strip(), 
                    'first_author_lastname' : authors_list[2].strip(),
                    'last_author' : authors_list[-3].strip(),
                    'last_author_firstname': authors_list[-2].strip(),
                    'last_author_lastname': authors_list[-1].strip(),
                    'status': "PASS"
                }
            else:
                authors_dict[entry.get('pmcid')] = {
                    'first_author':"",
                    'first_author_firstname' :"",
                    'first_author_lastname' :"",
                    'last_author':"",
                    'last_author_firstname': "",
                    'last_author_lastname': "",
                    'status': "MISSING"
                    }
            # NOTE: CHANGE

        return authors_dict


    def is_pmcid_in_csv( csvpath:str, pmcid:str ) -> bool:
        """
        Check if an entry already exists in a CSV file.
        ------------------------------------
            :param csvpath: Path to the CSV file.
            :param entry: The entry (as a dictionary) to check for.
            :return: True if the entry exists in the CSV, False otherwise.
        """
        try:
            with open(csvpath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('PMCID') == pmcid:
                        return True
                return False
        except FileNotFoundError:
            return False

    # NOTE: CHANGE
    def is_authorname_in_csv( csvpath:str, author_name:str ) -> bool:
        """
        Check if an entry already exists in a CSV file.
        ------------------------------------
            :param csvpath: Path to the CSV file.
            :param entry: The entry (as a dictionary) to check for.
            :return: True if the entry exists in the CSV, False otherwise.
        """
        try:
            with open(csvpath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('FIRST_AUTHOR_NAME') == author_name:
                        author_gender = row.get('FIRST_AUTHOR_GENDER')
                        author_gender_prob = row.get('FIRST_AUTHOR_GENDER_PROBABILITY')
                        author_gender_stat = row.get('FIRST_NAME_GENDER_STATUS')
                        return (author_gender, author_gender_prob, author_gender_stat)
                    if row.get('LAST_AUTHOR_NAME') == author_name:
                        author_gender = row.get('LAST_AUTHOR_GENDER')
                        author_gender_prob = row.get('LAST_AUTHOR_GENDER_PROBABILITY')
                        author_gender_stat = row.get('LAST_AUTHOR_GENDER_STATUS')
                        return (author_gender, author_gender_prob, author_gender_stat)
                return False
        except FileNotFoundError:
            return False
    # NOTE: CHANGE


    def json2csv( entry:dict,  outfile:str ) -> None:
        """
        Write CSV with data.
        ------------------------------------
            :param entry:    Dict with data
            :param outdir:   Folder where store CSV with results
        """

        # # Final csv file
        # outfile = Path(outdir) / ( 'gender_analysis' + '.csv')

        # # Check information in csv
        # if not JsonParser.is_json_entry_in_csv(outfile, entry):

            # Create and save information in csv
        # NOTE: CHANGE
        with open(str(outfile), 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                JsonParser.PMCID,
                JsonParser.FIRST_AUTHOR,
                JsonParser.FIRST_AUTHOR_NAME,
                JsonParser.LAST_AUTHOR,
                JsonParser.LAST_AUTHOR_NAME,
                JsonParser.ASSOCIATED_AUTHORS,
                # JsonParser.FIRST_AUTHOR_NATION_NAME,
                # JsonParser.FIRST_AUTHOR_NATION_PROBABILITY_NAME,
                # JsonParser.FIRST_AUTHOR_NATION_STATUS_NAME,
                # JsonParser.FIRST_AUTHOR_NATION_SURNAME,
                # JsonParser.FIRST_AUTHOR_NATION_PROBABILITY_SURNAME,
                # JsonParser.FIRST_AUTHOR_NATION_STATUS_SURNAME,
                JsonParser.FIRST_AUTHOR_GENDER,
                JsonParser.FIRST_AUTHOR_GENDER_PROBABILITY,
                JsonParser.FIRST_NAME_GENDER_STATUS,
                # JsonParser.FIRST_AUTHOR_SELECTED_NATION_CATEGORY,
                # JsonParser.LAST_AUTHOR_NATION_NAME,
                # JsonParser.LAST_AUTHOR_NATION_PROBABILITY_NAME,
                # JsonParser.LAST_AUTHOR_NATION_STATUS_NAME,
                # JsonParser.LAST_AUTHOR_NATION_SURNAME,
                # JsonParser.LAST_AUTHOR_NATION_PROBABILITY_SURNAME,
                # JsonParser.LAST_AUTHOR_NATION_STATUS_SURNAME,
                JsonParser.LAST_AUTHOR_GENDER,
                JsonParser.LAST_AUTHOR_GENDER_PROBABILITY,
                JsonParser.LAST_AUTHOR_GENDER_STATUS
                # JsonParser.LAST_AUTHOR_SELECTED_NATION_CATEGORY
            ]
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, delimiter=',')
            if  outfile.stat().st_size == 0 :
                writer.writeheader()
            writer.writerow(entry)
            # NOTE: CHANGE


