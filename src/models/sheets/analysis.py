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


def return_prepped_dfs_from_gsheets(spreadsheetId):
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


def return_prepped_dfs_from_excel(wb):

    try:
        age_range = wb.defined_names[AGE_RANGE_NAME]

        stores_range = wb.defined_names[STORES_RANGE_NAME]

    except Exception as e:
        raise e

    age_cells = named_range_to_list(age_range.destinations, wb)

    stores_cells = named_range_to_list(stores_range.destinations, wb)

    stores_df = excel_cells_to_df(stores_cells)
    ages_df = excel_cells_to_df(age_cells)

    add_basic_cols(ages_df)
    add_basic_cols(stores_df)


    chain_df = store_chain_summary_df(stores_df)
    ages_df.set_index('Age range', inplace=True)
    stores_df.set_index('Chain', inplace=True)

    return [ages_df, chain_df, stores_df]


def named_range_to_list(excel_dest, wb):

    excel_cells = []
    value_cells = []

    if excel_dest is not None:

        for title, coord in excel_dest:
            ws = wb[title]
            excel_cells.append(ws[coord])


        for lines in excel_cells:
            for row in lines:
                row_list = []
                for cell in row:
                    row_list.append(cell.value)
                value_cells.append(row_list)
        return value_cells

    return None

def excel_cells_to_df(list_cell_lists):
    return pd.DataFrame(list_cell_lists[1:],columns=list_cell_lists[0])


def potential_sales_df(stores_df, chain_df):
    """
    Look at each Category and collect Categories that have at least more than 10 stores.
        'Chain Category', 10% of Total # of Stores

    Look at Stores sorted by each Chain Category and look at the top 10% of them (rounded).
    Iterate through each of those and check their Customer_Buy_% with their categories average.
    If their Buy_% is lower then find the difference and multiply their 'Total Customers' by that % difference.


    :param stores_df:
    :param chain_df:
    :return:
    """

    store_rows = []

    # Retrieve Categories that have at least above a count of 10 stores.
    Cats_Stores_Above_10 = []
    for index, row in chain_df[chain_df['Total # of Stores'] > 9].iterrows():
        Cats_Stores_Above_10.append([index, int(round(row['Total # of Stores'] / 10))])

    # Loop through each category to get underperforms in terms of the Customer Buy % mean within their category
    # who are also top 10 % in sales.
    for category in Cats_Stores_Above_10:
        chain_category = category[0]
        num_stores = category[1]
        top_sellers_in_Cat = stores_df[stores_df['Chain Category'] == chain_category].sort_values('% of Total Sales',
                                                                                                  ascending=False).head(
            num_stores).reset_index()

        # Loop through stores with top 10% in sales and check their Customer Buy % with their Category Mean

        for index, row in top_sellers_in_Cat.iterrows():
            row_dict = {}
            category_buy_average = chain_df.loc[row['Chain Category']]['Customer_Buy_%']
            store_buy_average = row['Customer_Buy_%']
            if store_buy_average < category_buy_average:
                value_below_average = round(category_buy_average - store_buy_average, 3)
                potential_additional_sales = round(value_below_average * row['Total Customers'])

                row_dict['Chain'] = row['Chain']
                row_dict['Inter-Category Rank'] = index + 1
                row_dict['% Below Category Buy Average'] = value_below_average
                row_dict['Potential Additional Customers'] = potential_additional_sales
                row_dict['Chain Category'] = chain_category

            # If store had a below average buy % then append
            if len(row_dict) > 0:
                store_rows.append(row_dict)

    # If there is at least one store in the top 10% of sales that also is under the categories mean buy % then add
    if len(store_rows) > 0:
        pot_df = pd.DataFrame(store_rows).set_index('Chain')

    return pot_df