import pandas as pd

PATH = 'data/Transactions2014.csv'

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


if __name__ == '__main__':
    print('Starting up...')

    df = pd.read_csv(PATH)

    print('Type a command:')
    while True:
        try:
            cmd = input()
            if cmd == 'List All':
                print(group_transactions(df))
            elif cmd.startswith('List '):
                print(search_account(df, cmd[5:]))
            elif cmd == 'exit':
                print('Program stopped by user.')
                break
            else:
                print('Invalid command')
        except (EOFError, KeyboardInterrupt):
            print('Program stopped by user.')
            break
        except Exception as e:
            print(f'Exception occurred: {e}')
