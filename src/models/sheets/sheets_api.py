from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import src.models.sheets.errors as SheetErrors

__author__ = "nblhn"


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_range_values(spreadsheetId, rangeName):

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
    except Exception as e:
        raise SheetErrors.NamedRangeError(e._get_reason())

    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        row_count = 0
        dict_head = {}
        range_value_list = []

        for row in values:
            # Creates dict for storing Column Names, which is on row 0.
            if row_count == 0:
                for i in range(0,len(row)):
                    dict_head[i] = row[i]
                    i+=1
                row_count+=1
            else:
                # Stores each row under appropriate Column name as a dict.
                row_value_dict = {}
                for i in range(0,len(row)):
                    col_name = dict_head[i]
                    row_val = row[i]

                    if col_name in ["Customers","Non-Customers"]:
                        row_val = int(row_val)

                    row_value_dict[col_name] = row_val

                    i+=1
                range_value_list.append(row_value_dict)

        return range_value_list

