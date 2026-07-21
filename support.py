import pandas as pd
import logging

logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

def group_transactions(df):
    filtered_df = df[['To', 'From', 'Amount']]

    to_give = filtered_df[['From', 'Amount']].groupby(['From']).sum()
    to_get = filtered_df[['To', 'Amount']].groupby(['To']).sum()

    all_df = (to_give.join(to_get,how='outer',
                          lsuffix='_to_give', rsuffix='_to_get')
              .filter(like='Amount')).fillna(0)

    all_df['Balance'] = all_df['Amount_to_get'] - all_df['Amount_to_give']

def search_account(df, account):
    return df.loc[(df['From'] == account) | (df['To'] == account)]

def validate_df(path):
    df = pd.read_csv(path) if path.endswith('.csv') else pd.read_json(path)

    if df['Date'].dtype != 'datetime64[ns]':
        print('Date column is not of datetime type. All such rows will be ignored!')
        formated_date = pd.to_datetime(df['Date'],format='%d/%m/%Y',  errors='coerce')
        print(formated_date)

        for i, r in df[pd.isnull(formated_date)].iterrows():
            logging.debug(f"Problematic date {i}: {r}")

        df = df[~pd.isnull(formated_date)]
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    if df['Amount'].dtype not in ['int64', 'float64']:
        numeric_amount = pd.to_numeric(df['Amount'], errors='coerce')
        print('Amount column is not of numeric type. All such rows will be ignored!')

        for i, r in df[numeric_amount.isna()].iterrows():
            logging.debug(f"Problematic amount {i}: {r}")

        logging.debug('Amount column is not of numeric type.')

        df = df[df['Amount'].str.match(r"^-?\d+\.?\d*$", na=False)]

        df['Amount'] = pd.to_numeric(df['Amount'])

    return df

if __name__ == '__main__':
    print('Starting up...')
    logging.debug('Starting up...')


    df = pd.DataFrame()

    print('Type a command:')
    while True:
        try:
            cmd = input()
            if cmd.startswith('Import '):
                df = validate_df('data/' + cmd[7:])
            elif cmd == 'List All':
                print(group_transactions(df) if not df.empty else 'Select a file!')
            elif cmd.startswith('List '):
                print(search_account(df, cmd[5:]) if not df.empty else 'Select a file!')
            elif cmd == 'exit':
                raise Exception('Program stopped by user')
            else:
                print('Invalid command')
        except Exception as e:
            print('Stopping program...')
            logging.exception(f'Exception occurred: {e}')
            break
