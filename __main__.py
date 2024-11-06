#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import typing 
from pathlib import Path
# from .proxy import Proxy
from .json_parser import JsonParser
from collections import OrderedDict
from .demografix import GenderPredictor
import time

def run ( json_path: str, outfile: str, verbose: bool) -> None:

    # read json 
    json_data = JsonParser.read(json_path)

    # authors: { pmcid: {first_author_firstname, first_author_lastname last_author_firstname, last_author_lastname, status} }
    data_authors = JsonParser.get_authors(json_data)

    # done_authors = {}

    # perdict gender fullnames
    for pmcid, authors in data_authors.items():

        # NOTE: CHANGE
        fauthor_fullname = authors.get('first_author')
        fauthor_fname = authors.get('first_author_firstname')
        fauthor_lname = authors.get('first_author_lastname')
        lauthor_fullname = authors.get('last_author')
        lauthor_fname = authors.get('last_author_firstname')
        lauthor_lname = authors.get('last_author_lastname')
        # NOTE: CHANGE

        # check if entry is already saved
        # if JsonParser.is_pmcid_in_csv( outfile, pmcid ):
        #     continue

        if (verbose):
            index = 1
            print(f"Gender inference for: {pmcid}\n", end='', flush=True)

        if authors.get('status') == "PASS":
            # try: 
            ## FIRST AUTHOR
    
            # fist_author: infering  name nation 
            # fauthor_nation, fselected_category = GenderPredictor.get_nation(authors.get('first_author'))
            
            # NOTE: CHANGE
            # fist_author: infering gender name
            # fauthor_gender = GenderPredictor.get_gender(authors.get('first_author'), fauthor_nation, fselected_category)
            if JsonParser.is_authorname_in_csv( outfile, fauthor_fname ):
                if verbose:
                    print(f"Repeated name: {fauthor_fname} - copying metrics already calculated.")
                fauthor_gender_gender, fauthor_gender_prob, fauthor_gender_stat = JsonParser.is_authorname_in_csv( outfile, fauthor_fname )
            else:
                if verbose:
                    print(f"Attempting gender prediction on first author: {fauthor_fullname}")
                fauthor_gender = GenderPredictor.get_gender(fauthor_fullname, fauthor_fname, fauthor_lname)

                fauthor_gender_gender = fauthor_gender.get(authors.get('first_author')).get('name').get('gender')
                fauthor_gender_prob = fauthor_gender.get(authors.get('first_author')).get('name').get('gender_score')
                fauthor_gender_stat = fauthor_gender.get(authors.get('first_author')).get('name').get('gender_status')
                # done_authors[fauthor_fname] = fauthor_gender
            # NOTE: CHANGE
                
            # LAST AUTHOR

            # last_author: infering name nation 
            # lauthor_nation, lselected_category = GenderPredictor.get_nation(authors.get('last_author'))

            # NOTE: CHANGE
            # last_author: infering gender name
            # lauthor_gender = GenderPredictor.get_gender(authors.get('last_author'), lauthor_nation, lselected_category)
            if JsonParser.is_authorname_in_csv( outfile, lauthor_fname ):
                if verbose:
                    print(f"Repeated name: {lauthor_fname} - copying metrics already calculated.")
                lauthor_gender_gender, lauthor_gender_prob, lauthor_gender_stat = JsonParser.is_authorname_in_csv( outfile, lauthor_fname )
            else:
                if verbose:
                    print(f"Attempting gender prediction on last author: {lauthor_fullname}")
                lauthor_gender = GenderPredictor.get_gender(lauthor_fullname, lauthor_fname, lauthor_lname)

                lauthor_gender_gender = lauthor_gender.get(authors.get('last_author')).get('name').get('gender')
                lauthor_gender_prob = lauthor_gender.get(authors.get('last_author')).get('name').get('gender_score')
                lauthor_gender_stat = lauthor_gender.get(authors.get('last_author')).get('name').get('gender_status')
                # done_authors[lauthor_fname] = lauthor_gender
            # NOTE: CHANGE

            # define entry
            entry = {
                # CORE_DATA
                JsonParser.PMCID:pmcid,
                JsonParser.FIRST_AUTHOR: authors.get('first_author'),
                JsonParser.FIRST_AUTHOR_NAME: authors.get('first_author_firstname'),
                JsonParser.LAST_AUTHOR: authors.get('last_author'),
                JsonParser.LAST_AUTHOR_NAME: authors.get('last_author_firstname'),
                JsonParser.ASSOCIATED_AUTHORS: authors.get('status'),

                # FIRST_AUTHOR_NATION
                ## name
                # JsonParser.FIRST_AUTHOR_NATION_NAME: fauthor_nation.get(authors.get('first_author')).get(fselected_category).get('country_id'),
                # JsonParser.FIRST_AUTHOR_NATION_PROBABILITY_NAME: fauthor_nation.get(authors.get('first_author')).get(fselected_category).get('country_score'),
                # JsonParser.FIRST_AUTHOR_NATION_STATUS_NAME:fauthor_nation.get(authors.get('first_author')).get(fselected_category).get('country_status'),
                ## surname
                # JsonParser.FIRST_AUTHOR_NATION_SURNAME: fauthor_nation.get(authors.get('first_author')).get(fselected_category).get('country_id'),
                # JsonParser.FIRST_AUTHOR_NATION_PROBABILITY_SURNAME: fauthor_nation.get(authors.get('first_author')).get(fselected_category).get('country_score'),
                # JsonParser.FIRST_AUTHOR_NATION_STATUS_SURNAME:fauthor_nation.get(authors.get('first_author')).get(fselected_category).get('country_status'),
                # FIRST_AUTHOR_GENDER
                JsonParser.FIRST_AUTHOR_GENDER: fauthor_gender_gender,
                JsonParser.FIRST_AUTHOR_GENDER_PROBABILITY: fauthor_gender_prob,
                JsonParser.FIRST_NAME_GENDER_STATUS: fauthor_gender_stat,
                # JsonParser.FIRST_AUTHOR_SELECTED_NATION_CATEGORY: fselected_category,
                
                # LAST_AUTHOR_NATION
                ## name
                # JsonParser.LAST_AUTHOR_NATION_NAME: lauthor_nation.get(authors.get('last_author')).get(lselected_category).get('country_id'),
                # JsonParser.LAST_AUTHOR_NATION_PROBABILITY_NAME: lauthor_nation.get(authors.get('last_author')).get(lselected_category).get('country_score'),
                # JsonParser.LAST_AUTHOR_NATION_STATUS_NAME: lauthor_nation.get(authors.get('last_author')).get(lselected_category).get('country_status'),
                # ## surname
                # JsonParser.LAST_AUTHOR_NATION_SURNAME: lauthor_nation.get(authors.get('last_author')).get(lselected_category).get('country_id'),
                # JsonParser.LAST_AUTHOR_NATION_PROBABILITY_SURNAME: lauthor_nation.get(authors.get('last_author')).get(lselected_category).get('country_score'),
                # JsonParser.LAST_AUTHOR_NATION_STATUS_SURNAME: lauthor_nation.get(authors.get('last_author')).get(lselected_category).get('country_status'),
                # LAST_AUTHOR_GENDER
                JsonParser.LAST_AUTHOR_GENDER: lauthor_gender_gender,
                JsonParser.LAST_AUTHOR_GENDER_PROBABILITY: lauthor_gender_prob,
                JsonParser.LAST_AUTHOR_GENDER_STATUS: lauthor_gender_stat,
                # JsonParser.LAST_AUTHOR_SELECTED_NATION_CATEGORY: lselected_category
            }

            if (verbose):
                index += 1
                print(f"\rGender inference for: {pmcid} [OK]")


        else:
            entry = {
                # CORE_DATA
                JsonParser.PMCID:pmcid,
                JsonParser.FIRST_AUTHOR: authors.get('first_author'),
                JsonParser.FIRST_AUTHOR_NAME: authors.get('first_author_firstname'),
                JsonParser.LAST_AUTHOR: authors.get('last_author'),
                JsonParser.LAST_AUTHOR_NAME: authors.get('last_author_firstname'),
                JsonParser.ASSOCIATED_AUTHORS: authors.get('status'),

                # FIRST_AUTHOR_NATION
                ## name
                # JsonParser.FIRST_AUTHOR_NATION_NAME: "",
                # JsonParser.FIRST_AUTHOR_NATION_PROBABILITY_NAME: 0.0,
                # JsonParser.FIRST_AUTHOR_NATION_STATUS_NAME: "MISSING",
                ## surname 
                # JsonParser.FIRST_AUTHOR_NATION_SURNAME: "",
                # JsonParser.FIRST_AUTHOR_NATION_PROBABILITY_SURNAME: 0.0,
                # JsonParser.FIRST_AUTHOR_NATION_STATUS_SURNAME: "MISSING",
                # FIRST_AUTHOR_GENDER
                JsonParser.FIRST_AUTHOR_GENDER: "",
                JsonParser.FIRST_AUTHOR_GENDER_PROBABILITY: 0.0,
                JsonParser.FIRST_NAME_GENDER_STATUS: "MISSING",
                # JsonParser.FIRST_AUTHOR_SELECTED_NATION_CATEGORY: "",

                # LAST_AUTHOR_NATION
                ## name
                # JsonParser.LAST_AUTHOR_NATION_NAME: "",
                # JsonParser.LAST_AUTHOR_NATION_PROBABILITY_NAME: 0.0,
                # JsonParser.LAST_AUTHOR_NATION_STATUS_NAME: "MISSING",
                ## surname
                # JsonParser.LAST_AUTHOR_NATION_SURNAME: "",
                # JsonParser.LAST_AUTHOR_NATION_PROBABILITY_SURNAME: 0.0,
                # JsonParser.LAST_AUTHOR_NATION_STATUS_SURNAME: "MISSING",
                # LAST_AUTHOR_GENDER
                JsonParser.LAST_AUTHOR_GENDER: "",
                JsonParser.LAST_AUTHOR_GENDER_PROBABILITY: 0.0,
                JsonParser.LAST_AUTHOR_GENDER_STATUS: "MISSING",
                # JsonParser.LAST_AUTHOR_SELECTED_NATION_CATEGORY: ""
            }

            if (verbose):
                index += 1
                print(f"\rGender inference for: {pmcid} [EMPTY]")


        if (verbose):    
            if index % 100 == 0:
                print(f"Checked {index} projects in this run.")

        
        # Write .csv
        JsonParser.json2csv(entry, outfile)

        # if (verbose):
        #     print(f"Sleeping 2s until next item...")
        # time.sleep(2)
        

def main():

    # CMD Arguments
    parser = argparse.ArgumentParser(
        description='genderTracker is python tool to infer to gender from a fullname')

    parser.add_argument('-j', '--json', type=str, default=None,
                        help='Set jason file with authors entries')

    parser.add_argument('-od', '--outdir', type=str, default=".",
                        help='Set a custom path for the directory where the search .CSV files should be stored.')

    parser.add_argument('-v', '--verbose', type=bool, default=True,
                        help='Verbose mode.')

    
    args = parser.parse_args()


    if args.json is None:
        print("[ Input Error ] Provide at least one of the following arguments: --json or -j")
        sys.exit()

    if args.outdir is None:
        print("[ Input Error ] Provide at least one of the following arguments: --outdir or -od")
        sys.exit()
    else:
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True,exist_ok=True)
        # Final csv file
        outfile = Path(outdir) / ( 'gender_analysis' + '.csv')

    if args.verbose:
        print("genderTraker")
        print(f"analyzing json: {args.json}")
        print(f"Output path: {outfile}")


    # Execution
    run ( args.json, outfile, args.verbose )


if __name__ == "__main__":
    main()