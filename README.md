# Conversor OFX - SparkWave

Sistema web simples em Streamlit para converter extratos Excel/PDF para OFX.

## Como rodar

1. Crie um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

No Windows:

```bash
venv\Scripts\activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Rode o sistema:

```bash
streamlit run app.py
```

## Funcionalidades

- Upload de Excel `.xlsx`
- Upload de PDF `.pdf`
- Conversão para OFX
- Validação contra arquivo vazio
- Download do OFX
- Identificação de layouts:
  - SGPay/planilhas similares
  - BG Bank PDF
  - PagSeguro PDF
