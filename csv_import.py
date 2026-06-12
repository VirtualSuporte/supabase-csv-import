import os
import pandas as pd
from supabase import create_client

# Credenciais do Supabase (configuradas no GitHub Secrets)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Criar cliente Supabase
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ler CSV
df = pd.read_csv("products.csv")

# Verificar quais id's já existem para evitar duplicação
existing = client.table("products").select("id").execute()
existing_ids = set([item["id"] for item in existing.data])

# Só inserir linhas com id novo
new_rows = df[df["id"].notin(existing_ids)]

print(f"Tabela tem {len(existing_ids)} linhas, CSV tem {len(df)} linhas")
print(f"Inserindo {len(new_rows)} novas linhas...")

# Inserir em batches (melhor para 3500 linhas)
batch_size = 100
for i in range(0, len(new_rows), batch_size):
    batch = new_rows[i:i+batch_size].to_dict("records")
    client.table("products").insert(batch).execute()
    print(f"Batch {i//batch_size + 1} inserido!")

print("✅ CSV importado com sucesso!")
