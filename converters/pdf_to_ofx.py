from io import BytesIO
import re
from datetime import datetime
from pypdf import PdfReader
from converters.ofx_builder import build_ofx


def parse_brazilian_money(value_text):
    value_text = str(value_text).replace("R$", "").replace(" ", "").strip()
    negative = "-" in value_text
    value_text = value_text.replace("-", "")
    value_text = value_text.replace(".", "").replace(",", ".")

    try:
        amount = float(value_text)
        return -amount if negative else amount
    except Exception:
        return None


def extract_text_from_pdf(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))
    text_parts = []

    for page in reader.pages:
        text_parts.append(page.extract_text() or "")

    return "\n".join(text_parts)


def parse_bg_bank_pdf(text):
    transactions = []

    dates = re.findall(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}", text)
    values = re.findall(r"-?R\$\s?[\d\.]+,\d{2}", text)

    if dates and values:
        total = min(len(dates), len(values))

        for index in range(total):
            date_part = dates[index].split()[0]
            amount = parse_brazilian_money(values[index])

            if amount is None:
                continue

            transactions.append({
                "date": datetime.strptime(date_part, "%d/%m/%Y"),
                "memo": "Pix",
                "amount": amount
            })

        return transactions

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)
        value_matches = re.findall(r"-?\s?R?\$?\s?\d{1,3}(?:\.\d{3})*,\d{2}", line)

        if date_match and value_matches:
            date_str = date_match.group()
            amount_str = value_matches[0]
            amount = parse_brazilian_money(amount_str)

            if amount is None:
                continue

            memo = "Pix" if "Pix" in line or "PIX" in line else "Movimentação"

            try:
                transactions.append({
                    "date": datetime.strptime(date_str, "%d/%m/%Y"),
                    "memo": memo,
                    "amount": amount
                })
            except Exception:
                continue

    return transactions


def parse_pagseguro_pdf(text):
    transactions = []

    pattern = re.compile(
        r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?R\$\s?[\d\.]+,\d{2})"
    )

    for match in pattern.finditer(text):
        memo = match.group(2).strip()

        if memo.lower().startswith("saldo do dia"):
            continue

        amount = parse_brazilian_money(match.group(3))

        if amount is None:
            continue

        transactions.append({
            "date": datetime.strptime(match.group(1), "%d/%m/%Y"),
            "memo": memo,
            "amount": amount
        })

    return transactions


def parse_transactions_by_layout(text, layout):
    if layout == "BG Bank PDF":
        return parse_bg_bank_pdf(text)

    if layout == "PagSeguro PDF":
        return parse_pagseguro_pdf(text)

    transactions = parse_bg_bank_pdf(text)

    if not transactions:
        transactions = parse_pagseguro_pdf(text)

    return transactions


def convert_pdf_to_ofx(file_bytes, bank_id="000", account_id="000000", account_type="CHECKING", layout="Automático"):
    text = extract_text_from_pdf(file_bytes)

    transactions = parse_transactions_by_layout(text, layout)

    if not transactions:
        raise ValueError(
            "Nenhuma transação encontrada. Este PDF pode ser imagem. "
            "Na versão web, use Excel ou PDF com texto selecionável. "
            "PDF imagem deve ser convertido na versão local com OCR."
        )

    ofx = build_ofx(
        transactions=transactions,
        bank_id=bank_id,
        account_id=account_id,
        account_type=account_type
    )

    return ofx, len(transactions)