"""
gerador_produtos.py
SEMANA 27 - Banco de Dados (Prof. Pedro Yokada)
Aluno: Bruno De Lima - Turma: 3° B

Script para popular o MongoDB com 10.000 documentos e testar consultas/indices.
"""

from pymongo import MongoClient
import random
from datetime import datetime, timedelta

def popular_banco():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Teste de conexao simples
        client.server_info()
    except Exception as e:
        print("[AVISO] Servidor MongoDB local nao ativo no momento:", e)
        print("[INFO] O script pode ser executado em ambiente com MongoDB ativo.")
        return

    db = client["store"]
    collection = db["products"]
    collection.drop()

    categorias = ["eletrônicos", "moda", "livros", "casa", "esportes", "games"]
    documentos = []
    data_base = datetime(2026, 1, 1)

    print("Gerando 10.000 documentos...")
    for i in range(1, 10001):
        cat = random.choice(categorias)
        preco = round(random.uniform(20.0, 1500.0), 2)
        estoque = random.randint(0, 100)
        data_criacao = data_base + timedelta(days=random.randint(0, 300), minutes=random.randint(0, 1440))
        
        qtd_reviews = random.randint(1, 4)
        reviews = []
        for r in range(qtd_reviews):
            reviews.append({
                "user_id": f"usr_{random.randint(100, 999)}",
                "rating": random.randint(1, 5),
                "comment": f"Comentario do review {r+1} no produto {i}"
            })

        documentos.append({
            "product_name": f"Produto {cat.capitalize()} Ref_{i}",
            "category": cat,
            "price": preco,
            "stock": estoque,
            "created_at": data_criacao,
            "reviews": reviews
        })

    collection.insert_many(documentos)
    print(f"Sucesso! {collection.count_documents({})} documentos inseridos.")

if __name__ == "__main__":
    popular_banco()
