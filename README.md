# RAG-справочная система на графовой базе знаний Neo4j

Этот репозиторий содержит **графовую базу знаний (Neo4j)** для RAG-справочной системы по теме ИИ.  
Контекст извлекается **Cypher-запросами** (узлы + связи), затем передаётся в LLM для генерации ответа.

---

## 1) Требования

- Docker Desktop установлен и **запущен**
- Свободны порты:
  - **7474** — Neo4j Browser (HTTP)
  - **7687** — Bolt (подключение из кода)

Проверка Docker:
```bash
docker --version
docker info
```

---

## 2) Структура проекта

```text
neo4j/
  cypher/
    constraints.cypher   # ограничения (unique по name)
    seed.cypher          # наполнение (20–30 узлов + связи, без мусора и дублей)
    queries.cypher       # 5–8 "контрактных" запросов (для API)
```

---

## 3) Запуск Neo4j в Docker

Запускать из **корня проекта** (там где папка `neo4j/`):

```bash
docker rm -f neo4j 2>/dev/null

docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -v neo4j_data:/data \
  -v "$PWD/neo4j/cypher:/cypher:ro" \
  neo4j:5
```

Проверка, что контейнер запущен:
```bash
docker ps
```

---

## 4) Загрузка схемы и данных (constraints + seed)

Применить ограничения:
```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 -f /cypher/constraints.cypher
```

Загрузить seed:
```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 -f /cypher/seed.cypher
```

> `seed.cypher` использует `MERGE`, поэтому повторный прогон не создаёт дубликаты.

---

## 5) Быстрая проверка базы

Кол-во узлов:
```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "MATCH (n) RETURN count(n) AS nodes;"
```

Проверка мусора (узлы без name или без label):
```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "MATCH (n) WHERE n.name IS NULL OR size(labels(n))=0 RETURN count(n) AS garbage;"
```

Ожидаемо:
- `nodes` ≈ **20–30**
- `garbage` = **0**

---

## 6) Neo4j Browser

- URL: **http://localhost:7474**
- Login: **neo4j**
- Password: **password123**

Показать весь граф:
```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m;
```

---

## 7) Контрактные Cypher-запросы

Файл: `neo4j/cypher/queries.cypher` — набор типовых запросов (“контракт”) для интеграции с Python API.

---

## 8) Остановка / продолжение работы

Остановить контейнер (данные сохраняются в volume):
```bash
docker stop neo4j
```

Запустить снова:
```bash
docker start neo4j
```

Удалить контейнер (данные в volume останутся):
```bash
docker rm -f neo4j
```

Полностью удалить данные (ОСТОРОЖНО):
```bash
docker rm -f neo4j
docker volume rm neo4j_data
```

---

## 9) Примечание по Retrieval в RAG

Retrieval в этой реализации выполняется **не через embeddings**, а через **запросы к графу Neo4j**:
- извлекаются релевантные сущности и их связи (подграф/соседи)
- полученный структурированный контекст передаётся в LLM для генерации ответа