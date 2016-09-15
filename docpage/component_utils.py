''' Utilities for processing component specs '''


def preprocess_raw_table(src):
    ''' Parse table string into usable dict for html views '''
    table = {}
    # Split records by row seperator
    records = [s.strip() for s in src.split('---')]

    # Converts record string into list of fields, separated by "|"s
    strip_row = lambda row: [s.strip() for s in row.split('|')]

    # Handle header
    if records[0] != '':
        table['header'] = strip_row(records[0])

    # Handle records
    table['rows'] = [strip_row(record) for record in records[1:]]

    return table
