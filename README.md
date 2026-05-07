

# RAG-справочная система на графовой базе знаний Neo4j

Проект представляет собой прототип **RAG-справочной системы на графовой базе знаний Neo4j**.

Система предназначена для автоматического извлечения знаний из PDF-документов по теме искусственного интеллекта, машинного обучения и больших языковых моделей. Из документов извлекаются сущности, связи между ними, после чего формируется граф знаний, который может использоваться как структурированный источник контекста для RAG-сценариев.

В отличие от обычного поиска по тексту, проект работает не только с фрагментами документа, но и с явно выделенными сущностями и отношениями между ними.

---

## 1. Назначение проекта

Проект решает следующие задачи:

- извлечение текста из PDF-документов;
- нормализация извлечённого текста;
- выделение сущностей предметной области;
- использование словарного извлечения и NER-модели;
- валидация найденных сущностей;
- извлечение семантических связей между сущностями;
- валидация связей;
- формирование JSON-представления графа знаний;
- импорт узлов и связей в Neo4j;
- визуализация графа через Neo4j Browser;
- подготовка структурированного контекста для RAG-системы.

---

## 2. Общая архитектура

Общий пайплайн обработки документа:

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

Neo4j используется как графовая база данных. Сущности сохраняются как узлы графа, а отношения между ними — как рёбра.

---

## 3. Структура проекта

```text
neo4j_project/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── neo4j/
│   ├── cypher/
│   │   ├── constraints.cypher
│   │   ├── seed.cypher
│   │   └── queries.cypher
│   └── parser_service/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── main.py
│       └── parser/
│           ├── main.py
│           ├── extract_text.py
│           ├── normalize.py
│           ├── entity_extractor.py
│           ├── entity_validator.py
│           ├── relation_extractor.py
│           ├── build_json.py
│           ├── import_to_neo4j.py
│           ├── config/
│           ├── ner/
│           ├── models/
│           ├── samples/
│           └── output/
└── pict/
```

---

## 4. Основные компоненты

### `parser_service`

Основной Python-сервис, который выполняет обработку PDF-документов.

Он отвечает за:

- чтение PDF;
- преобразование PDF в текст;
- нормализацию текста;
- извлечение сущностей;
- запуск NER;
- извлечение связей;
- формирование JSON-графа;
- импорт результата в Neo4j.

### `neo4j/cypher`

Папка с Cypher-скриптами для Neo4j.

```text
constraints.cypher — ограничения и индексы;
seed.cypher        — начальное наполнение графа;
queries.cypher     — типовые запросы к графу.
```

### `parser/output`

Папка, куда сохраняются результаты обработки PDF.

Основной результат работы парсера:

```text
<имя_файла>.graph.json
```

---

## 5. Типы сущностей

В проекте используются следующие типы сущностей:

```text
Model      — модели искусственного интеллекта;
Method     — методы, алгоритмы и подходы;
Task       — задачи обработки данных;
Concept    — общие понятия предметной области;
Framework  — библиотеки, платформы и инструменты.
```

Примеры:

```text
Model      | BERT
Model      | GPT
Model      | LLaMA
Model      | Mistral
Method     | Fine-tuning
Method     | LoRA
Method     | Retrieval-Augmented Generation
Task       | Question Answering
Task       | Text Classification
Concept    | Transformer
Concept    | Embedding
Framework  | PyTorch
Framework  | vLLM
```

---

## 6. Типы связей

В графе знаний используются следующие типы отношений:

```text
IS_A            — принадлежность к классу, архитектуре или семейству;
USES            — использование метода, механизма или концепции;
USED_FOR        — применение для решения задачи;
IMPLEMENTED_IN  — реализация с помощью библиотеки, платформы или инструмента;
RELATED_TO      — общая смысловая связь между сущностями.
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

## 7. Используемые технологии

В проекте используются:

```text
Python
spaCy
Neo4j
Docker
Docker Compose
Cypher
pypdf
python-dotenv
PyYAML
Rule-based relation extraction
Dictionary-based entity extraction
NER
```

Подход к извлечению знаний является гибридным:

```text
словарное извлечение
+ обученная NER-модель
+ валидация сущностей
+ rule-based извлечение связей
+ валидация связей
```

---

## 8. Переменные окружения

Пример файла `.env.example`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
NEO4J_DATABASE=neo4j
```

Файл `.env.example` можно хранить в репозитории как пример.

Файл `.env` с реальными параметрами подключения лучше не добавлять в Git.

---

## 9. Запуск через Docker Compose

Из корня проекта:

```bash
docker compose up -d
```

Эта команда запускает:

```text
Neo4j
parser-service
```

Проверить запущенные контейнеры:

```bash
docker ps
```

Neo4j Browser будет доступен по адресу:

```text
http://localhost:7474
```

Данные для входа:

```text
Login: neo4j
Password: password123
```

---

## 10. Что делает docker-compose.yml

Файл `docker-compose.yml` поднимает два сервиса.

### Neo4j

```text
neo4j
```

Используется как графовая база знаний.

Открытые порты:

```text
7474 — Neo4j Browser
7687 — Bolt-подключение для Python
```

Данные Neo4j сохраняются в Docker volume:

```text
neo4j_data
```

### parser-service

```text
parser-service
```

Сервис собирается из папки:

```text
./neo4j/parser_service
```

Он предназначен для запуска Python-парсера внутри Docker-контейнера.

По умолчанию контейнер запускает справку:

```bash
python -m parser.main --help
```

Для обработки конкретного PDF используется отдельная команда.

---

## 11. Запуск парсера локально без Docker

Перейти в папку сервиса:

```bash
cd neo4j/parser_service
```

Создать виртуальное окружение:

```bash
python3 -m venv .venv
```

Активировать окружение:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
python3 -m pip install -r requirements.txt
```

Запустить обработку тестового PDF:

```bash
python3 -m parser.main --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf --use-ner
```

После выполнения будет создан файл:

```text
parser/output/ai_ner_semantic_test_en.graph.json
```

---

## 12. Запуск парсера через Docker

Из корня проекта:

```bash
docker compose run --rm parser-service \
  python -m parser.main \
  --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf \
  --use-ner
```

Результат будет сохранён в:

```text
neo4j/parser_service/parser/output/
```

---

## 13. Проверка результата graph.json

Из папки `neo4j/parser_service` можно выполнить:

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

## 14. Импорт графа в Neo4j

Перед импортом Neo4j должен быть запущен.

Из папки `neo4j/parser_service`:

```bash
python3 -m parser.import_to_neo4j --input parser/output/ai_ner_semantic_test_en.graph.json
```

Если используется Docker Compose, параметры подключения к Neo4j берутся из переменных окружения.

---

## 15. Загрузка constraints и seed-данных

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

## 16. Полезные Cypher-запросы

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

Показать все модели:

```cypher
MATCH (m:Model)
RETURN m.name;
```

Показать связи конкретной модели:

```cypher
MATCH (a {name: "BERT"})-[r]->(b)
RETURN a, r, b;
```

Показать модели и задачи:

```cypher
MATCH (m:Model)-[:USED_FOR]->(t:Task)
RETURN m.name, t.name;
```

Показать методы, используемые моделями:

```cypher
MATCH (m:Model)-[:USES]->(method:Method)
RETURN m.name, method.name;
```

---

## 17. Проверка качества

На контрольных PDF-документах система показала ориентировочно следующий уровень качества:

```text
Точность извлечения сущностей: примерно 75–80%
Точность извлечения связей: примерно 75–80%
Общая экспертная оценка графа: примерно 76%
```

Оценка является ориентировочной, так как выполнялась на тестовых документах и экспертном анализе результата, а не на большом размеченном эталонном корпусе.

---

## 18. Ограничения текущей версии

Система не является универсальным парсером любых PDF-документов.

Основные ограничения:

- качество зависит от корректности извлечения текста из PDF;
- таблицы и сложная вёрстка могут обрабатываться хуже;
- русскоязычные PDF могут содержать англоязычные канонические названия сущностей;
- часть связей извлекается rule-based методом;
- неявные отношения между сущностями могут быть пропущены;
- при длинных предложениях с большим количеством сущностей возможны ошибочные связи;
- качество выше на тематических AI/ML-документах с явно выраженными связями.

---


## 19. Остановка Docker

Остановить контейнеры:

```bash
docker compose down
```

Остановить только Neo4j-контейнер:

```bash
docker stop neo4j
```

Запустить Neo4j снова:

```bash
docker start neo4j
```

Полностью удалить контейнер Neo4j:

```bash
docker rm -f neo4j
```

Удалить данные Neo4j из volume:

```bash
docker volume rm neo4j_project_neo4j_data
```

Название volume может отличаться. Проверить список volume можно командой:

```bash
docker volume ls
```

---

## 20. Научно-практическая значимость

Проект демонстрирует подход к построению предметной базы знаний на основе неструктурированных PDF-документов.

Графовая база знаний позволяет явно хранить связи между понятиями, моделями, методами, задачами и инструментами. Такой подход может использоваться как основа для RAG-системы, где ответ формируется не только по текстовым фрагментам, но и с учётом структуры предметной области.

---

## 21. Текущий статус проекта

Реализовано:

```text
извлечение текста из PDF;
нормализация текста;
словарное извлечение сущностей;
обучение и подключение spaCy NER;
валидация сущностей;
извлечение отношений;
валидация отношений;
формирование graph.json;
подготовка импорта в Neo4j;
Docker Compose для запуска инфраструктуры.
```

Планируемые улучшения:

```text
расширение словаря сущностей;
улучшение обработки русскоязычных документов;
добавление новых шаблонов отношений;
оценка качества на размеченном корпусе;
улучшение импорта в Neo4j;
добавление API-слоя для запросов к графу;
интеграция графового retrieval с LLM.
```

---

## 22. Retrieval в RAG

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

Такой подход позволяет использовать не только текстовое совпадение, но и связи между сущностями предметной области.

---

## 23. Корректное название проекта

```text
RAG-справочная система на графовой базе знаний Neo4j
```