import os
import string
import csv
import math

from datetime import datetime, timedelta

from data import Transaction

# EXCPECT_HEADERS = [
#     'Date started (UTC)', 'Time started (UTC)', 'Date completed (UTC)',
#     'Time completed (UTC)', 'State', 'Type', 'Description', 'Reference',
#     'Payer', 'Card name', 'Card number', 'Orig currency', 'Orig amount',
#     'Payment currency', 'Amount', 'Fee', 'Balance', 'Account',
#     'Beneficiary account number', 'Beneficiary sort code or routing number',
#     'Beneficiary IBAN', 'Beneficiary BIC'
# ]
EXCPECT_HEADERS = ['SN', 'Transaction Date', 'Ref No', 'Transaction Details', 'Value Date', 'Withdrawals', 'Lodgements', 'Balance', 'IBAN' ]


NAME_REMOVE_PREFIXES = [
    'Payment from ',
    'To '
]

# DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT = '%m-%d-%Y'
TIME_FORMAT = '%H:%M:%S'
# DATETIME_FORMAT = DATE_FORMAT + TIME_FORMAT
DATETIME_FORMAT = DATE_FORMAT

FEE_NAME = '#####'
FEE_IBAN = ''
FEE_DESCRIPTION_FORMAT = 'Bank transaction fee {}'
FEE_DATETIME_DELTA = timedelta(seconds=1)


class CsvReader:

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise ValueError('File does not exist: {}'.format(filename))

        self.filename = filename

        self.file = open(self.filename, 'r')
        self.reader = csv.reader(self.file)

        self._validate()

        print(self.filename)


    def __del__(self):
        if not self.file.closed:
            self.file.close()


    def _validate(self):
        def _santize_header(header):
            header = ''.join([c for c in header
                              if c in string.printable])
            header = header.strip()
            return header

        headers = [_santize_header(h) for h in next(self.reader)]
        if headers != EXCPECT_HEADERS:
            raise ValueError('Headers do not match expected Deloitte CSV format.')


    def get_all_transactions(self):
        transactions = []
        for row in self.reader:
            transactions = self._parse_transaction(row) + transactions

        return transactions[::-1]


    def _parse_transaction(self, row):

        def _santize_name(name_):
            for remove_prefix in NAME_REMOVE_PREFIXES:
                if name_.startswith(remove_prefix):
                    name_ = name_[len(remove_prefix):]

            return name_

        # def _parse_datetime(date_str, time_str):
        #     return datetime.strptime(date_str + time_str, DATETIME_FORMAT)
        


        def _parse_datetime(date_str):
            print(','.join(date_str.split('-')))
            return datetime.strptime(date_str , DATETIME_FORMAT).date()




        
        # _0, _1, completed_date_str, completed_time_str, _4, _5, name, description, _8, _9, _10, \
        # _11, _12, _13, amount_str, fee_str, balance_str, _17, _18, _19, iban, _21 \
        #     = row
        
        _0, transaction_date_str, ref_no, description, value_date_str, withdrawal_str, lodgement_str, balance_str, iban = row

        completed_datetime = _parse_datetime( value_date_str)
        withdrawal, deposit,   balance = \
            float(withdrawal_str.replace(',','')), float(lodgement_str.replace(',','')), float(balance_str.replace(',',''))




        transaction_without_fee = Transaction(
            amount=withdrawal,
            name=_santize_name(''),
            iban=iban,
            description=description,
            datetime=completed_datetime,
            before_balance=balance,
            after_balance=balance + withdrawal,
            reference_no=ref_no)

        batch = [transaction_without_fee]

        # if not math.isclose(fee, 0.00):
        #     fee_transaction = self._make_fee_transaction(
        #         completed_datetime,
        #         balance,
        #         fee)

        #     batch.append(fee_transaction)

        return batch


    # def _make_fee_transaction(self, completed_datetime, balance, fee):
    #     return Transaction(
    #         amount=fee,
    #         name=FEE_NAME,
    #         iban=FEE_IBAN,
    #         # include timestamp of transaction to make sure that BlackLine
    #         # does not detect similar transactions as the same one
    #         description=FEE_DESCRIPTION_FORMAT.format(int(completed_datetime.timestamp())),
    #         datetime=completed_datetime + FEE_DATETIME_DELTA,
    #         before_balance=balance - fee,
    #         after_balance=balance)

