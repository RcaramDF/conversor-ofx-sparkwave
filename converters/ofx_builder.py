from datetime import datetime
from html import escape


def build_ofx(transactions, bank_id="000", account_id="000000", account_type="CHECKING"):
    if not transactions:
        raise ValueError("Nenhuma transação válida encontrada.")

    header = f'''OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<TRNUID>1
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<STMTRS>
<CURDEF>BRL
<BANKACCTFROM>
<BANKID>{escape(str(bank_id))}
<ACCTID>{escape(str(account_id))}
<ACCTTYPE>{escape(str(account_type))}
</BANKACCTFROM>
<BANKTRANLIST>
'''

    footer = '''
</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>
'''

    body = ""

    for index, transaction in enumerate(transactions, start=1):
        date = transaction["date"]
        memo = escape(str(transaction.get("memo", "")))
        amount = float(transaction["amount"])

        if isinstance(date, datetime):
            dt = date.strftime("%Y%m%d")
        else:
            dt = datetime.strptime(str(date), "%d/%m/%Y").strftime("%Y%m%d")

        trntype = "DEBIT" if amount < 0 else "CREDIT"
        fitid = f"{dt}{index:05d}{abs(int(round(amount * 100)))}"

        body += f'''
<STMTTRN>
<TRNTYPE>{trntype}
<DTPOSTED>{dt}
<TRNAMT>{amount:.2f}
<FITID>{fitid}
<MEMO>{memo}
</STMTTRN>
'''

    return header + body + footer
