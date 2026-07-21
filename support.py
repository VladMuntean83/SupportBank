import pandas as pd
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

def group_transactions(df):

    from_col = filter(lambda s: 'From' in s, df.columns).__next__()
    to_col = filter(lambda s: 'To' in s, df.columns).__next__()

    to_give = df[[from_col, 'Amount']].groupby([from_col]).sum()
    to_get = df[[to_col, 'Amount']].groupby([to_col]).sum()

    all_df = (to_give.join(to_get,how='outer',
                          lsuffix='_to_give', rsuffix='_to_get')
              .filter(like='Amount')).fillna(0)

    all_df['Balance'] = all_df['Amount_to_get'] - all_df['Amount_to_give']

    return all_df[['Balance']]

def search_account(df, account):
    from_col = filter(lambda s: 'From' in s, df.columns).__next__()
    to_col = filter(lambda s: 'To' in s, df.columns).__next__()

    return df.loc[(df[from_col] == account) | (df[to_col] == account)]

def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    to_df = []

    for row in root.findall('SupportTransaction'):
        transaction = {
            'Date': pd.to_datetime(int(row.get('Date')), unit='D', origin='1899-12-30').strftime('%d/%m/%Y'),
            'Description': row.find('Description').text,
            'Amount': float(row.find('Value').text or 0),
            'From': row.find('Parties/From').text or '',
            'To': row.find('Parties/To').text or ''
        }

        to_df.append(transaction)

    return pd.DataFrame(to_df)

def validate_df(path):
    if path.endswith('.xml'):
        df = parse_xml(path)
    else:
        df = pd.read_csv(path) if path.endswith('.csv') else pd.read_json(path)

    if df['Date'].dtype != 'datetime64[ns]':
        print('Date column is not of datetime type. All such rows will be ignored!')
        formated_date = pd.to_datetime(df['Date'],format='%d/%m/%Y',  errors='coerce')

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
                print('Program stopped by user.')
                break
            else:
                print('Invalid command')
        except (EOFError, KeyboardInterrupt) as e:
            print('Program stopped by user.')
            break
        except Exception as e:
            logging.exception(f"Exception occured: {e}")
            print(f'Exception occurred: {e}')