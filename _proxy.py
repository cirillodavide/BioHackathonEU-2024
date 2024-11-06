#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
from bs4 import BeautifulSoup

class Proxy: 

    def set_new_proxy(vpn:str):
        """
        Set new proxy if the request to Google Scholar fails 
        because of too many queries to the website.
        --------------------------------------------------------------------
        """
        if vpn == 'desktop':

            while True:
                # Stop the run to change the proxy
                inp = input('You have been blocked, try changing your IP or using a VPN. '
                        'Press Enter to continue downloading, or type "exit" to stop and exit....')
                if inp.strip().lower() == "exit":
                    sys.exit()

                elif not inp.strip():
                    print("Wait 15 seconds...")
                    time.sleep(15)
                    return True

        if vpn == 'cmd':

            print('You have been blocked, try changing your IP or using a VPN. '
                'Reconnecting to a new proxy...')

            # Define the command you want to run with sudo
            command = "sudo protonvpn connect -r"

            # Use subprocess to run the command with sudo
            try:
                subprocess.check_call(["bash", "-c", command])
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")