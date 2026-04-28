import streamlit as st
from converters.excel_to_ofx import convert_excel_to_ofx
from converters.pdf_to_ofx import convert_pdf_to_ofx

st.set_page_config(
    page_title="Conversor OFX - SparkWave",
    page_icon="💼",
    layout="centered"
)

st.title("Conversor OFX - SparkWave")
st.write("Envie um arquivo Excel ou PDF e converta automaticamente para OFX.")

uploaded_file = st.file_uploader(
    "Selecione o arquivo",
    type=["xlsx", "pdf"]
)

layout = st.selectbox(
    "Layout do arquivo",
    [
        "Automático",
        "SGPay / Excel padrão",
        "BG Bank PDF",
        "PagSeguro PDF"
    ]
)

bank_id = st.text_input("BANKID", value="000")
account_id = st.text_input("Conta / ACCTID", value="000000")
account_type = st.selectbox("Tipo de conta", ["CHECKING", "SAVINGS"], index=0)

if uploaded_file is not None:
    st.info(f"Arquivo carregado: {uploaded_file.name}")

    if st.button("Converter para OFX"):
        try:
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name.lower()

            if filename.endswith(".xlsx"):
                ofx_content, count = convert_excel_to_ofx(
                    file_bytes=file_bytes,
                    bank_id=bank_id,
                    account_id=account_id,
                    account_type=account_type
                )
            elif filename.endswith(".pdf"):
                ofx_content, count = convert_pdf_to_ofx(
                    file_bytes=file_bytes,
                    bank_id=bank_id,
                    account_id=account_id,
                    account_type=account_type,
                    layout=layout
                )
            else:
                st.error("Formato não suportado.")
                st.stop()

            if count == 0 or not ofx_content.strip():
                st.error("Nenhuma transação válida foi encontrada. O OFX não foi gerado.")
                st.stop()

            st.success(f"Arquivo convertido com sucesso! Transações encontradas: {count}")

            output_name = uploaded_file.name.rsplit(".", 1)[0] + ".ofx"

            st.download_button(
                label="Baixar OFX",
                data=ofx_content.encode("latin1", errors="ignore"),
                file_name=output_name,
                mime="application/x-ofx"
            )

        except Exception as e:
            st.error(f"Erro ao converter arquivo: {e}")
