import pandas as pd

PATH = 'data/Transactions2014.csv'

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


if __name__ == '__main__':
    print('Starting up...')

    df = pd.read_csv(PATH)

    print('Type a command:')
    while True:
        try:
            cmd = input()
            elif cmd == 'List All':
                print(group_transactions(df))
            elif cmd.startswith('List '):
                print(search_account(df, cmd[5:]))
            elif cmd == 'exit':
                raise Exception('Program stopped by user')
            else:
                print('Invalid command')
        except Exception as e:
            print('Stopping program...')
            break
