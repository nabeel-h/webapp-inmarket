import pandas as pd
import re

from src.models.sheets.sheets_api import get_range_values
from src.models.sheets.constants import AGE_RANGE_NAME, STORES_RANGE_NAME
import src.models.sheets.errors as SheetErrors

__author__ = "nblhn"

'''
stores_visited_data_list = get_range_values(spreadsheetId,stores_rangeName)
age_range_data_list = get_range_values(spreadsheetId,age_rangeName)

stores_df = pd.DataFrame(stores_visited_data_list)
ages_df = pd.DataFrame(age_range_data_list)
'''

def get_spreadsheetID(url):
    p = re.compile("/spreadsheets/d/([a-zA-Z0-9-_]+)")
    sheet_id = p.findall(url)

    if sheet_id:
        return sheet_id[0]
    return None

def create_customer_buy_pct(df):
    """
    Creates Customer_Buy_% column
    :param df:
    :return: returns pandas df with update in place
    """
    df['Customer_Buy_%'] = round(df['Customers'] / (df['Non-Customers'] + df['Customers']),4)
    return None

def create_total_customers(df):
    df['Total Customers'] = (df['Non-Customers'] + df['Customers'])
    return None

def create_total_pct_of_pop(df):
    df['% of Total Population'] = round((df['Non-Customers'] + df['Customers']) / df['Total Customers'].sum(),4)
    return None

def create_pct_total_sales(df):
    df['% of Total Sales'] = round(df['Customers'] / df['Customers'].sum(),4)
    return None

def add_basic_cols(df):
    create_customer_buy_pct(df)
    create_total_customers(df)
    create_total_pct_of_pop(df)
    create_pct_total_sales(df)
    return None

def store_chain_summary_df(df):
    alt_stores = pd.DataFrame(df)
    alt_stores.rename(columns={'Chain': 'Store', 'Customers': 'Customer Sales'}, inplace=True)

    by_type = alt_stores.groupby(['Chain Category'])
    agg_type = by_type.agg(
        {"Customer Sales": 'sum', "Customer_Buy_%": 'mean', "Store": "count", '% of Total Sales': 'sum'})

    agg_type['Average # of Sales per Store'] = (agg_type['Customer Sales']) / (agg_type['Store'])
    agg_type.rename(columns={'Store': 'Total # of Stores', 'Customer Sales': 'Total Customer Sales'}, inplace=True)

    agg_type['Customer_Buy_%'] = round(agg_type['Customer_Buy_%'],4)
    agg_type['Average # of Sales per Store'] = round(agg_type['Average # of Sales per Store'],0)


    return agg_type


def return_prepped_dfs(spreadsheetId):
    """

    :param spreadsheetId: string for specific Google Spreadsheet
    :return: returns the age table as a df for now
    """
    try:
        age_range_data_list = get_range_values(spreadsheetId, AGE_RANGE_NAME)
        stores_range_data_list = get_range_values(spreadsheetId, STORES_RANGE_NAME)
    except SheetErrors.SheetErrors as e:
        raise e

    ages_df = pd.DataFrame(age_range_data_list)
    stores_df = pd.DataFrame(stores_range_data_list)

    add_basic_cols(ages_df)
    add_basic_cols(stores_df)

    chain_df = store_chain_summary_df(stores_df)
    ages_df.set_index('Age range', inplace=True)
    stores_df.set_index('Chain', inplace=True)


    return [ages_df, chain_df, stores_df]


