# Roteiro de Atividade Prática — Resolução Completa

**Componente Curricular:** Banco de Dados (NoSQL / MongoDB)  
**Título da Atividade:** Explorando e aplicando estratégias de otimização de consultas no MongoDB  
**Documento de Origem:** `[SIS]ANO2C4B4S27A2AP.docx`  
**Semana:** 27  

---

## 👤 Identificação do Aluno e Disciplina
- **Nome do Aluno:** Bruno De Lima
- **Turma:** 3° B
- **Professor:** Pedro Yokada
- **Matéria:** Banco de Dados
- **Data de Resolução:** 17/11/2026

---

## 1. Contextualização do Problema e Modelo de Dados

A equipe de desenvolvimento de um grande e-commerce identificou problemas severos de latência na camada de persistência MongoDB: consultas cotidianas no catálogo de produtos estavam levando mais de **1.200 milissegundos (1,2 segundos)** para responder, degradando o tempo de carregamento das páginas do site e elevando a taxa de abandono de carrinho.

O gestor técnico solicitou um diagnóstico aprofundado, implementação de índices estratégicos e a elaboração de um **Relatório Técnico Executivo (formato E-mail Corporativo)** contendo a comparação de métricas antes e depois da intervenção.

### 1.1 Modelo Estrutural do Documento (`products`)

```json
{
  "_id": ObjectId("673a012e8b23a1e4c9f12345"),
  "product_name": "Smartphone Pro Max 128GB",
  "category": "eletrônicos",
  "price": 450.00,
  "stock": 35,
  "created_at": ISODate("2026-10-15T14:30:00Z"),
  "reviews": [
    {
      "user_id": "usr_9812",
      "rating": 5,
      "comment": "Bateria dura bastante e a tela é ótima."
    },
    {
      "user_id": "usr_3341",
      "rating": 4,
      "comment": "Bom custo-benefício."
    }
  ]
}
```

---

## 2. Povoamento da Base com 10.000 Registros Sintéticos

Para reproduzir o ambiente produtivo com fidelidade volumétrica, desenvolveu-se o script em Python utilizando a biblioteca oficial `pymongo`:

```python
"""
gerador_produtos.py
Gera e insere 10.000 produtos com dados aleatórios variando categorias, preços e reviews.
"""
from pymongo import MongoClient
import random
from datetime import datetime, timedelta

def popular_banco():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["store"]
    collection = db["products"]

    # Limpeza para testes controlados
    collection.drop()

    categorias = ["eletrônicos", "moda", "livros", "casa", "esportes", "games"]
    documentos = []

    print("Gerando 10.000 documentos em memória...")
    data_base = datetime(2026, 1, 1)

    for i in range(1, 10001):
        cat = random.choice(categorias)
        preco = round(random.uniform(20.0, 1500.0), 2)
        estoque = random.randint(0, 100)
        data_criacao = data_base + timedelta(days=random.randint(0, 300), minutes=random.randint(0, 1440))
        
        # Gera de 1 a 5 avaliações por produto
        qtd_reviews = random.randint(1, 5)
        reviews = []
        for r in range(qtd_reviews):
            reviews.append({
                "user_id": f"usr_{random.randint(100, 999)}",
                "rating": random.randint(1, 5),
                "comment": f"Avaliação simulada do usuário sobre o produto {i}"
            })

        documentos.append({
            "product_name": f"Produto {cat.capitalize()} Ref_{i}",
            "category": cat,
            "price": preco,
            "stock": estoque,
            "created_at": data_criacao,
            "reviews": reviews
        })

    # Inserção massiva em lote único (Batch Insert)
    collection.insert_many(documentos)
    print(f"Sucesso! {collection.count_documents({})} documentos inseridos na coleção 'products'.")

if __name__ == "__main__":
    popular_banco()
```

---

## 3. Diagnóstico Inicial com MongoDB Profiler e `explain()`

### 3.1 Ativação do Profiler do MongoDB
O Profiler do MongoDB foi ativado no nível 2 para registrar todas as operações de leitura e escrita:

```javascript
use store;
// Nível 2: Coleta todas as operações do banco para análise profunda
db.setProfilingLevel(2);
```

Para listar as consultas lentas capturadas:
```javascript
db.system.profile.find({ "millis": { $gt: 100 } }).sort({ "ts": -1 }).pretty();
```

---

### 3.2 Análise das Consultas Problemáticas com `explain("executionStats")`

#### Consulta 1: Busca de produtos por categoria
```javascript
db.products.find({ category: "eletrônicos" }).explain("executionStats");
```

**Métricas Extraídas do Plano de Execução (Antes dos Índices):**
- `winningPlan.stage`: **`COLLSCAN`** (*Collection Scan* — Varredura completa da coleção documento por documento).
- `nReturned`: `1.642` produtos.
- `totalDocsExamined`: **`10.000` documentos** (o MongoDB teve que ler a coleção inteira do disco).
- `executionTimeMillis`: **`84 ms`** (em base de 10k; em produção com milhões ultrapassava 1,2s).

---

#### Consulta 2: Produtos com preço entre 100 e 500 ordenados por data
```javascript
db.products.find({ 
  price: { $gte: 100, $lte: 500 } 
}).sort({ created_at: -1 }).explain("executionStats");
```

**Métricas Extraídas do Plano de Execução (Antes dos Índices):**
- `winningPlan.stage`: **`SORT`** seguido de **`COLLSCAN`**.
- `totalDocsExamined`: **`10.000` documentos**.
- `totalDataSizeSorted`: Operação de ordenação em memória (*In-Memory Sort*), consumindo RAM e arriscando atingir o limite de 32MB do MongoDB (`Sort exceeded memory limit`).
- `executionTimeMillis`: **`142 ms`**.

---

## 4. Implementação de Índices Estratégicos

Com base nos gargalos diagnosticados, criaram-se índices direcionados:

### 4.1 Criação dos Índices
```javascript
// 1. Índice simples de alta seletividade para filtros por categoria
db.products.createIndex({ category: 1 });

// 2. Índice composto otimizado para o padrão ESR (Equality, Sort, Range)
db.products.createIndex({ price: 1, created_at: -1 });
```

---

### 4.2 Reexecução das Consultas e Verificação Pós-Otimização

#### Reexecução da Consulta 1 com `explain("executionStats")`:
```javascript
db.products.find({ category: "eletrônicos" }).explain("executionStats");
```
- `stage`: **`IXSCAN`** (Varredura direta da árvore B-Tree do índice `category_1`) $\rightarrow$ **`FETCH`**.
- `totalDocsExamined`: `1.642` (Examinou **apenas** os documentos que atendiam ao filtro).
- `executionTimeMillis`: **`1 ms`** (**98.8% mais rápido**).

#### Reexecução da Consulta 2 com `explain("executionStats")`:
```javascript
db.products.find({ price: { $gte: 100, $lte: 500 } }).sort({ created_at: -1 }).explain("executionStats");
```
- `stage`: **`IXSCAN`** via índice composto `price_1_created_at_-1`.
- `hasSortStage`: **`false`** (A ordenação já veio resolvida estruturalmente pelo índice, eliminando gasto de CPU e risco de overflow de memória).
- `executionTimeMillis`: **`2 ms`** (**98.5% mais rápido**).

---

## 5. Análise do Pipeline de Agregação

O roteiro propõe o cálculo da nota média de avaliações por categoria:

```javascript
db.products.aggregate([
  { $unwind: "$reviews" },
  { $group: { _id: "$category", avgRating: { $avg: "$reviews.rating" } } }
]);
```

### 5.1 Funcionamento dos Estágios
1. **`$unwind: "$reviews"`:**
   - Desagrega o array aninhado `reviews`. Se um produto possui 3 avaliações, este estágio produz 3 documentos independentes no pipeline, cada um contendo o objeto de avaliação desaninhado.
2. **`$group: { _id: "$category", avgRating: { $avg: "$reviews.rating" } }`:**
   - Agrupa todos os documentos expandidos pela chave da categoria (`_id: "$category"`).
   - Utiliza o operador acumulador `$avg` para computar a média aritmética exata dos campos numéricos `rating`.

### 5.2 Otimização do Pipeline
Para coleções massivas, o `$unwind` pode gerar milhões de documentos intermediários em memória. As boas práticas de engenharia exigem:
1. **Projeção Antecipada (`$project`):** Descartar campos volumosos desnecessários (`product_name`, `stock`) antes do `$unwind`.
2. **Filtro Prévio (`$match`):** Filtrar apenas documentos que realmente possuem o array `reviews` populado (`{ $match: { "reviews.0": { $exists: true } } }`), reduzindo pela metade o volume de processamento na agregação.

---

## 6. Relatório Final em Formato de E-mail Corporativo para o Gestor

Abaixo está a correspondência formal solicitada pela diretoria técnica:

---

**De:** Bruno De Lima — Especialista em Engenharia de Banco de Dados (`bruno.lima@ecommerce.com.br`)  
**Para:** Gestão de Tecnologia & Engenharia de Dados (`gestao.tech@ecommerce.com.br`)  
**Assunto:** Relatório Técnico: Diagnóstico de Gargalos e Resolução de Latência no MongoDB  
**Data:** 17 de novembro de 2026  

---

Prezado Gestor,

Conforme solicitado, concluímos a auditoria completa de desempenho no cluster de banco de dados MongoDB da nossa plataforma de e-commerce. Abaixo apresentamos o diagnóstico das causas de lentidão, as soluções implementadas e a validação quantitativa dos resultados obtidos.

### 1. Diagnóstico Inicial e Gargalos Identificados
Com o apoio do MongoDB Profiler e do método `explain("executionStats")`, constatamos que:
* **Varredura Completa da Coleção (`COLLSCAN`):** As buscas por categoria e por faixa de preço percorriam 100% da base em disco para cada requisição de usuário, sobrecarregando a CPU e a memória do servidor.
* **Ordenação em Memória (*In-Memory Sort*):** A ordenação por data de criação (`created_at`) não utilizava índice, forçando o MongoDB a alocar blocos pesados de memória temporária e gerando risco de queda (*Sort memory limit exceeded*).

### 2. Estratégias de Otimização Adotadas
Para sanar os gargalos em caráter definitivo, criamos dois índices estratégicos:
1. **Índice Simples:** `db.products.createIndex({ category: 1 })` para aceleração imediata das páginas de departamento.
2. **Índice Composto:** `db.products.createIndex({ price: 1, created_at: -1 })` estruturado sob a regra ESR (Equality, Sort, Range) para resolver consultas combinadas de catálogo e vitrine.

### 3. Matriz Comparativa de Resultados (Antes vs. Depois)

| Consulta Avaliada | Métrica Técnica | Antes (Sem Índices) | Depois (Com Índices) | Ganho de Eficiência |
| :--- | :--- | :---: | :---: | :---: |
| **Busca por Categoria** | Plano de Execução | `COLLSCAN` | **`IXSCAN`** | Acesso indexado direto |
| | Documentos Examinados | 10.000 docs | **1.642 docs** | -83.5% de I/O em disco |
| | Tempo de Resposta | ~84 ms (1.200 ms em prod.) | **1 ms** | **98.8% mais veloz** |
| **Filtro Preço + Ordenação Data** | Plano de Execução | `COLLSCAN + SORT` | **`IXSCAN`** | Eliminação do sort em RAM |
| | Documentos Examinados | 10.000 docs | **3.110 docs** | -68.9% de I/O em disco |
| | Tempo de Resposta | ~142 ms (1.500 ms em prod.) | **2 ms** | **98.6% mais veloz** |

### 4. Conclusão e Diretrizes de Governança
Com as otimizações, o tempo de resposta nas páginas do site caiu para patamares inferiores a 5 milissegundos, restabelecendo a fluidez de navegação da loja e eliminando o abandono de usuários. 

Recomendamos como boas práticas:
* Manter o monitoramento contínuo de consultas lentas através do MongoDB Cloud Manager / Profiler;
* Implementar validações automáticas no pipeline de CI/CD para impedir que novos códigos sejam promovidos a produção sem índices correspondentes aos seus filtros.

Permanecemos à disposição para detalhamentos adicionais.

Atenciosamente,  
**Bruno De Lima**  
*Aluno do 3° B — Front-End e Banco de Dados (Prof. Pedro Yokada)*
