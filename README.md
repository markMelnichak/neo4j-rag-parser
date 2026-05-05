# RAG-справочная система на графовой базе знаний Neo4j

Проект представляет собой прототип **RAG-справочной системы на графовой базе знаний Neo4j**.

Основная идея проекта — автоматически извлекать знания из PDF-документов по теме искусственного интеллекта, машинного обучения и больших языковых моделей, формировать граф знаний и использовать его как структурированный источник контекста для последующей генерации ответов.

В отличие от обычного поиска по тексту, система работает не только с фрагментами документа, но и с явно выделенными сущностями и связями между ними.

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
# RAG-справочная система на графовой базе знаний Neo4j

Проект представляет собой прототип **RAG-справочной системы на графовой базе знаний Neo4j**.

Основная идея проекта — автоматически извлекать знания из PDF-документов по теме искусственного интеллекта, машинного обучения и больших языковых моделей, формировать граф знаний и использовать его как структурированный источник контекста для последующей генерации ответов.

В отличие от обычного поиска по тексту, система работает не только с фрагментами документа, но и с явно выделенными сущностями и связями между ними.

---

## 1. Назначение проекта

Система предназначена для обработки учебных, научных и справочных материалов по тематике AI/ML.

Проект решает следующие задачи:

- извлечение текста из PDF-документов;
- нормализация извлечённого текста;
- выделение сущностей предметной области;
- извлечение семантических связей между сущностями;
- формирование JSON-представления графа знаний;
- импорт узлов и связей в Neo4j;
- визуализация и проверка графа через Neo4j Browser;
- подготовка структурированного контекста для RAG-сценариев.

---

## 2. Общая архитектура

Пайплайн обработки документа:

```text
PDF-документ
    ↓
Извлечение текста
    ↓
Нормализация текста
    ↓
Извлечение сущностей
    ↓
Валидация сущностей
    ↓
Извлечение связей
    ↓
Валидация связей
    ↓
Формирование graph.json
    ↓
Импорт в Neo4j
    ↓
Графовая база знаний
```

Neo4j используется как графовая база данных, где сущности представлены в виде узлов, а отношения между ними — в виде рёбер графа.

---

## 3. Структура проекта

Актуальная структура репозитория может отличаться в зависимости от этапа разработки, но логически проект состоит из следующих частей:

```text
neo4j_project/
├── README.md
├── neo4j/
│   ├── cypher/
│   │   ├── constraints.cypher
│   │   ├── seed.cypher
│   │   └── queries.cypher
│   └── docker-compose.yml
├── parser_service/
│   ├── parser/
│   │   ├── main.py
│   │   ├── entity_extractor.py
│   │   ├── entity_validator.py
│   │   ├── relation_extractor.py
│   │   ├── relation_validator.py
│   │   ├── build_json.py
│   │   ├── import_to_neo4j.py
│   │   ├── ner/
│   │   ├── models/
│   │   ├── samples/
│   │   └── output/
│   └── requirements.txt
├── pict/
└── docs/
```

Если часть файлов находится внутри другой папки, команды нужно выполнять из соответствующей директории проекта.

---

## 4. Типы сущностей

В проекте используются следующие типы сущностей:

```text
Model      — модели искусственного интеллекта
Method     — методы, алгоритмы и подходы
Task       — задачи обработки данных
Concept    — общие понятия предметной области
Framework  — библиотеки, платформы и инструменты
```

Примеры сущностей:

```text
Model      | BERT
Model      | GPT
Model      | LLaMA
Model      | Mistral-7B
Method     | Fine-tuning
Method     | LoRA
Method     | Retrieval-Augmented Generation
Task       | Question Answering
Task       | Text Classification
Concept    | Transformer
Concept    | Embedding
Framework  | PyTorch
Framework  | LangChain
```

---

## 5. Типы связей

В графе знаний используются следующие отношения:

```text
IS_A            — принадлежность к классу, архитектуре или семейству
USES            — использование метода, механизма или концепции
USED_FOR        — применение для решения задачи
IMPLEMENTED_IN  — реализация с помощью библиотеки или платформы
RELATED_TO      — общая смысловая связь между сущностями
```

Примеры связей:

```text
BERT - USES -> Masked Language Modeling
BERT - USED_FOR -> Text Classification
GPT - USED_FOR -> Summarization
LLaMA - IS_A -> Transformer
LLaMA - USES -> LoRA
RAG - USES -> Vector Index
Whisper - USED_FOR -> Speech Recognition
```

---

## 6. Используемые технологии

В проекте используются:

```text
Python
spaCy
Neo4j
Docker
Docker Compose
Cypher
PDF text extraction
Dictionary-based entity extraction
LLM-assisted annotation
Rule-based relation extraction
```

Основной подход к извлечению знаний является гибридным: словарное извлечение, обученный NER, LLM-assisted разметка и rule-based извлечение связей.

---

## 7. Запуск Neo4j через Docker

Перейдите в корень проекта:

```bash
cd ~/Desktop/neo4j_project
```

Если используется `docker-compose.yml` внутри папки `neo4j`, запустите:

```bash
docker compose -f neo4j/docker-compose.yml up -d
```

Если Neo4j запускается вручную через `docker run`, используйте:

```bash
docker rm -f neo4j 2>/dev/null

docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -v neo4j_data:/data \
  -v "$PWD/neo4j/cypher:/cypher:ro" \
  neo4j:5
```

Проверить, что контейнер запущен:

```bash
docker ps
```

Neo4j Browser доступен по адресу:

```text
http://localhost:7474
```

Данные для входа:

```text
Login: neo4j
Password: password123
```

---

## 8. Загрузка базовой схемы и seed-данных

Применить ограничения:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 -f /cypher/constraints.cypher
```

Загрузить начальные данные:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 -f /cypher/seed.cypher
```

Файл `seed.cypher` должен использовать `MERGE`, чтобы повторный запуск не создавал дубликаты.

---

## 9. Подготовка Python-окружения и запуск парсера

Команды ниже выполняются из папки `parser_service`.

Проверьте, есть ли виртуальное окружение:

```bash
ls -la
```

Если в списке есть папка `.venv`, активируйте её:

```bash
source .venv/bin/activate
```

Если папки `.venv` нет, создайте виртуальное окружение и активируйте его:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установите зависимости из `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

Если зависимости не установлены, при запуске парсера возможна ошибка вида:

```text
ModuleNotFoundError: No module named 'spacy'
```

После подготовки окружения можно запускать парсер для PDF-документа:

```bash
python3 -m parser.main --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf --use-ner
```

После выполнения будет создан файл:

```text
parser/output/<имя_файла>.graph.json
```

Этот файл содержит узлы и связи, извлечённые из документа.

---

## 10. Проверка результата graph.json

Для просмотра краткой статистики по графу можно использовать команду:

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path("parser/output/ai_ner_semantic_test_en.graph.json")
data = json.loads(path.read_text(encoding="utf-8"))

print("SOURCE:", data["source"])
print("NODES:", len(data["nodes"]))
print("RELATIONS:", len(data["relations"]))

print("\nNODES:")
for n in data["nodes"]:
    print(n["label"], "|", n["name"])

print("\nRELATIONS:")
for r in data["relations"]:
    print(r["from_name"], "-", r["type"], "->", r["to_name"])
PY
```

---

## 11. Импорт графа в Neo4j

После формирования JSON-графа его можно импортировать в Neo4j:

```bash
python3 -m parser.import_to_neo4j --input parser/output/ai_ner_semantic_test_en.graph.json
```

После импорта данные можно проверить в Neo4j Browser.

---

## 12. Полезные Cypher-запросы

Показать все узлы:

```cypher
MATCH (n)
RETURN n
LIMIT 50;
```

Показать все связи:

```cypher
MATCH (a)-[r]->(b)
RETURN a, r, b
LIMIT 50;
```

Показать связи конкретной модели:

```cypher
MATCH (a {name: "BERT"})-[r]->(b)
RETURN a, r, b;
```

Показать все модели:

```cypher
MATCH (m:Model)
RETURN m.name;
```

Показать модели и задачи, для которых они используются:

```cypher
MATCH (m:Model)-[:USED_FOR]->(t:Task)
RETURN m.name, t.name;
```

Показать методы, которые используют модели:

```cypher
MATCH (m:Model)-[:USES]->(method:Method)
RETURN m.name, method.name;
```

---

## 13. Проверка качества

На контрольном англоязычном PDF были получены следующие результаты:

```text
NODES: 57
RELATIONS: 33
```

Примеры корректно извлечённых связей:

```text
BERT - USES -> Masked Language Modeling
BERT - USED_FOR -> Named Entity Recognition
BERT - USED_FOR -> Text Classification
BERT - USED_FOR -> Question Answering
GPT - USED_FOR -> Question Answering
GPT - USED_FOR -> Summarization
GPT-4 - IS_A -> GPT
Whisper - USED_FOR -> Speech Recognition
RAG - USES -> Vector Index
```

Экспертная оценка качества текущей версии:

```text
Точность извлечения сущностей: примерно 75–80%
Точность извлечения связей: примерно 75–80%
Общая точность графа: примерно 76%
```

Оценка является ориентировочной, так как выполнялась на контрольных документах и экспертном анализе результата, а не на большом размеченном эталонном корпусе.

---

## 14. Ограничения текущей версии

Система не является универсальным парсером любых PDF-документов.

Основные ограничения:

- качество зависит от корректности извлечения текста из PDF;
- таблицы и сложная вёрстка могут обрабатываться хуже;
- русскоязычные PDF могут содержать англоязычные канонические названия сущностей;
- часть связей извлекается rule-based методом, поэтому неявные отношения могут быть пропущены;
- при длинных предложениях с большим количеством сущностей возможны ошибочные связи;
- качество работы выше на тематических AI/ML-документах с явно выраженными связями.

---

## 15. Остановка и повторный запуск Docker

Остановить контейнер Neo4j без удаления данных:

```bash
docker stop neo4j
```

Запустить снова:

```bash
docker start neo4j
```

Остановить Docker Compose-инфраструктуру:

```bash
docker compose -f neo4j/docker-compose.yml down
```

Удалить контейнер вручную:

```bash
docker rm -f neo4j
```

Полностью удалить данные Neo4j из volume:

```bash
docker rm -f neo4j
docker volume rm neo4j_data
```

---

## 16. Что хранить в Git

В репозиторий следует добавлять:

```text
исходный код проекта
Dockerfile
docker-compose.yml
requirements.txt
README.md
.env.example
Cypher-скрипты
небольшие тестовые PDF
конфигурационные файлы без секретов
```

Не следует добавлять в Git:

```text
.env с паролями
.venv
__pycache__
neo4j/data
готовые Docker images
большие временные output-файлы
локальные кэши моделей
```

Готовый Docker image не хранится в Git-репозитории. В Git хранятся инструкции и файлы для сборки контейнера. При необходимости image публикуется отдельно в Docker Hub или GitHub Container Registry.

---

## 17. Научно-практическая значимость

Проект демонстрирует подход к построению предметной базы знаний на основе неструктурированных PDF-документов.

Графовая база знаний позволяет явно хранить связи между понятиями, моделями, методами, задачами и инструментами. Такой подход может использоваться как основа для RAG-системы, где ответ формируется не только по текстовым фрагментам, но и с учётом структуры предметной области.

---

## 18. Текущий статус проекта

Реализовано:

```text
извлечение текста из PDF;
нормализация текста;
LLM-assisted разметка сущностей;
обучение spaCy NER;
словарное извлечение сущностей;
валидация сущностей;
извлечение отношений;
валидация отношений;
формирование graph.json;
подготовка данных для импорта в Neo4j.
```

Планируемые улучшения:

```text
расширение словаря сущностей;
улучшение обработки русскоязычных документов;
добавление новых шаблонов отношений;
оценка качества на размеченном корпусе;
улучшение импорта в Neo4j;
упаковка parser-service в Docker-контейнер;
создание полноценного docker-compose запуска для Neo4j и parser-service.
```

---

## 19. Retrieval в RAG

Retrieval в данной версии проекта может выполняться через граф Neo4j:

```text
пользовательский вопрос
    ↓
поиск релевантных сущностей
    ↓
извлечение соседних узлов и связей
    ↓
формирование структурированного контекста
    ↓
передача контекста в LLM
    ↓
генерация ответа
```

Такой подход позволяет использовать не только текстовые совпадения, но и связи между сущностями предметной области.

---

## 20. Название проекта

Корректная формулировка названия:

```text
RAG-справочная система на графовой базе знаний Neo4j
```