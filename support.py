import pandas as pd
import logging
import re

PATH = 'data/Transactions2013.json'
logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

def group_transactions(df):
    filtered_df = df[['To', 'From', 'Amount']]
    to_give = filtered_df.groupby(['From']).sum()
    to_get = filtered_df.groupby(['To']).sum()

    all_df = (to_give.join(to_get,how='outer',
                          lsuffix='_to_give', rsuffix='_to_get')
              .filter(like='Amount'))

    return all_df

def search_account(df, account):
    return df.loc[(df['From'] == account) | (df['To'] == account)]

def validate_df(path):
    df = pd.read_csv(path) if path.endswith('.csv') else pd.read_json(path)

    for col in df.columns:
        if 'From' in col:
            df.rename(columns={col: 'From'}, inplace=True)
        if 'To' in col:
            df.rename(columns={col: 'To'}, inplace=True)
        if 'Amount' in col:
            df.rename(columns={col: 'Amount'}, inplace=True)

    if df['Amount'].dtype not in ['int64', 'float64']:
        print('Amount column is not of numeric type. All such rows will be ignored!')
        logging.debug('Amount column is not of numeric type')

        df = df[df['Amount'].str.match(r"^-?\d+\.\d+$", na=False)]

        df['Amount'] = df['Amount'].apply(float)

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
