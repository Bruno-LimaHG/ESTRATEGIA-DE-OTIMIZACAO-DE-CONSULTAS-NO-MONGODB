# SEMANA 27 — Banco de Dados (NoSQL / MongoDB)

**Docente:** Prof. Pedro Yokada  
**Estudante:** Bruno De Lima  
**Turma:** 3° B  
**Componente:** Banco de Dados  

---

## 📋 Atividade da Semana
- **Documento Oficial:** `[SIS]ANO2C4B4S27A2AP.docx`
- **Tema:** *Explorando e aplicando estratégias de otimização de consultas no MongoDB*
- **Arquivo de Resolução:** [`[SIS]ANO2C4B4S27A2AP_Relatorio_Otimizacao_Consultas_MongoDB.md`](file:///C:/Users/BrunoDeLima/Desktop/IA/BD/SEMANA%2027/%5BSIS%5DANO2C4B4S27A2AP_Relatorio_Otimizacao_Consultas_MongoDB.md)
- **Script Gerador de Dados:** [`gerador_produtos.py`](file:///C:/Users/BrunoDeLima/Desktop/IA/BD/SEMANA%2027/gerador_produtos.py)

---

## 📌 Conteúdos Principais Desenvolvidos
1. **Auditoria e Profiling:** Utilização do Profiler (`db.setProfilingLevel(2)`) e do método `explain("executionStats")` para identificar planos ineficientes com `COLLSCAN`.
2. **Engenharia de Índices:** Implementação de índices simples (`category_1`) e índices compostos ordenados (`price_1_created_at_-1`), convertendo varreduras em `IXSCAN` com ganhos superiores a 98% em tempo de execução.
3. **Pipelines de Agregação:** Desconstrução e análise técnica das etapas `$unwind` e `$group` para cálculo analítico de métricas por categoria.
4. **Relatório Executivo:** Formatação em padrão de e-mail corporativo para a gestão com diagnóstico, soluções, matriz comparativa e boas práticas.
