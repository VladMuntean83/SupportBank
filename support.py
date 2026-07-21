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

    return all_df[['Balance']]

def search_account(df, account):
    return df.loc[(df['From'] == account) | (df['To'] == account)]

def validate_df(path):
    df = pd.read_csv(path)

    if df['Amount'].dtype not in ['int64', 'float64']:
        numeric_amount = pd.to_numeric(df['Amount'], errors='coerce')
        print('Amount column is not of numeric type. All such rows will be ignored!')
        print(df[numeric_amount.isna()])
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
                print('Program stopped by user.')
                break
            else:
                print('Invalid command')
        except (EOFError, KeyboardInterrupt):
            print('Program stopped by user.')
            break
        except Exception as e:
            logging.exception(f"Exception occured: {e}")
            print(f'Exception occurred: {e}')
