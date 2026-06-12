import os
import pandas as pd
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

df = pd.read_csv(
    "products.csv",
    sep=";",
    dtype=str,
    encoding="utf-8-sig"
)

df.columns = df.columns.str.strip()
print("Colunas do CSV:", df.columns.tolist())

df = df.rename(columns={
    "Codigo": "codigo",
    "Produto": "produto",
    "CodBarra": "cod_barra",
    "Emb": "emb",
    "Pack": "pack",
    "Estoque": "estoque",
    "Pr_Custo": "pr_custo",
    "Pr_Venda": "pr_venda",
    "CodCategoria": "codcategoria",
    "Categoria": "categoria",
    "Pr_Promoc": "pr_promoc",
    "Inic_Promo": "inic_promo",
    "Valid_Promo": "valid_promo",
    "UltAlt_PVenda": "ultalt_pvenda"
})

# Limpar código de barras vindo como ="9002490214166"
df["cod_barra"] = (
    df["cod_barra"]
    .str.replace('="', '', regex=False)
    .str.replace('"', '', regex=False)
    .str.strip()
)

# Converter valores numéricos brasileiros
for col in ["pack", "estoque", "pr_custo", "pr_venda", "pr_promoc"]:
    df[col] = (
        df[col]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

# Converter datas dd/mm/yyyy
for col in ["inic_promo", "valid_promo", "ultalt_pvenda"]:
    df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m-%d")

# Trocar NaN por None
df = df.where(pd.notnull(df), None)

records = df.to_dict("records")

batch_size = 100

for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]

    client.table("products_master").upsert(
        batch,
        on_conflict="codigo"
    ).execute()

    print(f"Batch {i // batch_size + 1} enviado")

print("Produtos atualizados com sucesso!")
