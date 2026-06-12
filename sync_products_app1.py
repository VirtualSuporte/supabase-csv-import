import os
from decimal import Decimal
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

client = create_client(SUPABASE_URL, SUPABASE_KEY)


def safe_decimal(value, default="0"):
    if value is None or value == "":
        return default
    return str(value)


# 1. Buscar produtos da master
master = client.table("products_master").select("*").execute()
products_master = master.data

print(f"Produtos na master: {len(products_master)}")


# 2. Criar categorias que não existem
categories_names = {
    p.get("categoria")
    for p in products_master
    if p.get("categoria")
}

existing_categories = client.table("categories").select("id,name").execute()
category_map = {
    c["name"]: c["id"]
    for c in existing_categories.data
}

new_categories = [
    {"name": name}
    for name in categories_names
    if name not in category_map
]

if new_categories:
    client.table("categories").insert(new_categories).execute()
    print(f"Categorias criadas: {len(new_categories)}")

    existing_categories = client.table("categories").select("id,name").execute()
    category_map = {
        c["name"]: c["id"]
        for c in existing_categories.data
    }


# 3. Preparar produtos para tabela products
records = []

for p in products_master:
    categoria_nome = p.get("categoria")
    category_id = category_map.get(categoria_nome)

    cost_price = safe_decimal(p.get("pr_custo"))
    sale_price = safe_decimal(p.get("pr_venda"))

    try:
        if Decimal(cost_price) > 0:
            profit_margin = str(
                ((Decimal(sale_price) - Decimal(cost_price)) / Decimal(cost_price)) * 100
            )
        else:
            profit_margin = "0"
    except Exception:
        profit_margin = "0"

    records.append({
        "codigo_externo": p.get("codigo"),
        "name": p.get("produto") or "SEM NOME",
        "barcode": p.get("cod_barra"),
        "category_id": category_id,
        "cost_price": cost_price,
        "sale_price": sale_price,
        "profit_margin": profit_margin,
        "unit": "unidade",
        "stock_quantity": safe_decimal(p.get("estoque")),
        "min_stock": "0",
        "active": True
    })


# 4. Upsert na tabela products
batch_size = 100

for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]

    client.table("products").upsert(
        batch,
        on_conflict="codigo_externo"
    ).execute()

    print(f"Batch products {i // batch_size + 1} enviado")

print("Sincronização do App 1 concluída com sucesso!")
