

# Neo4j RAG Parser

Проект представляет собой прототип RAG-справочной системы на графовой базе знаний Neo4j.

Основная идея проекта: хранить знания не только в виде текстовых фрагментов, но и в виде графа сущностей и отношений. В графе сущностями выступают модели, методы, задачи, фреймворки и концепции из области искусственного интеллекта. Связи между ними показывают, как эти сущности связаны между собой: что является чем, что используется для какой задачи, какая модель использует какой метод и так далее.

Проект состоит из двух связанных частей:

1. Ручная графовая база знаний Neo4j, созданная с помощью Cypher-скриптов.
2. Python-парсер PDF-документов, который автоматически извлекает сущности и связи из PDF и может импортировать их в Neo4j.

---

## 1. Назначение проекта

Проект нужен для построения и расширения графовой базы знаний по теме искусственного интеллекта.

Система позволяет:

- создать начальную базу знаний вручную через Cypher;
- извлекать текст из PDF-документов;
- нормализовать извлечённый текст;
- выделять сущности с помощью словарного подхода и обученной spaCy NER-модели;
- извлекать отношения между сущностями;
- формировать промежуточный JSON-представитель графа;
- импортировать найденные узлы и связи в Neo4j;
- проверять содержимое графа через Cypher-запросы.

Общий pipeline выглядит так:

```text
PDF
  ↓
извлечение текста
  ↓
нормализация текста
  ↓
извлечение сущностей
  ↓
валидация сущностей
  ↓
извлечение отношений
  ↓
валидация отношений
  ↓
graph.json
  ↓
импорт в Neo4j
```

---

## 2. Общая архитектура

```text
neo4j_project/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── neo4j/
    ├── cypher/
    │   ├── constraints.cypher
    │   ├── seed.cypher
    │   └── queries.cypher
    └── parser_service/
        ├── requirements.txt
        ├── main.py
        └── parser/
            ├── main.py
            ├── extract_text.py
            ├── normalize.py
            ├── entity_extractor.py
            ├── entity_validator.py
            ├── relation_extractor.py
            ├── build_json.py
            ├── import_to_neo4j.py
            ├── config/
            │   └── entity_dict.json
            ├── models/
            │   └── ner_model/
            ├── ner/
            ├── samples/
            │   └── corpus_pdfs/
            └── output/
```

Neo4j используется как графовая база данных. Сущности сохраняются как узлы графа, а отношения между ними — как направленные рёбра.

Python-парсер отвечает за обработку PDF-документов и автоматическое расширение базы знаний.

---

## 3. Ручная часть графовой базы знаний

До реализации автоматического парсера в проекте была создана ручная графовая база знаний на Neo4j. Она задаёт стартовую структуру графа и демонстрирует основной паттерн хранения знаний.

Ручная часть находится в папке:

```text
neo4j/cypher
```

В ней используются три основных файла:

```text
constraints.cypher — ограничения и индексы для графовой базы данных;
seed.cypher        — начальное ручное наполнение базы знаний;
queries.cypher     — готовые запросы для проверки и анализа графа.
```

### 3.1. `constraints.cypher`

Файл `constraints.cypher` отвечает за создание ограничений уникальности для основных типов узлов.

В проекте используются следующие типы узлов:

```text
Model
Method
Task
Framework
Concept
```

Ограничения нужны для того, чтобы при повторном запуске seed-скриптов или при автоматическом импорте из PDF не создавались дублирующиеся узлы с одинаковыми именами.

Пример логики ограничения:

```cypher
CREATE CONSTRAINT model_name IF NOT EXISTS
FOR (m:Model) REQUIRE m.name IS UNIQUE;
```

Это означает, что в графе не должно быть двух узлов `Model` с одинаковым свойством `name`.

### 3.2. `seed.cypher`

Файл `seed.cypher` содержит ручное начальное наполнение базы знаний.

В нём создаются базовые сущности, например:

```text
BERT
GPT
Transformer
Attention
Fine-tuning
PyTorch
Question Answering
Text Classification
```

Также в нём вручную задаются отношения между сущностями.

Основные типы отношений:

```text
IS_A           — отношение принадлежности к классу или архитектуре;
USES           — отношение использования метода, концепции или инструмента;
USED_FOR       — отношение применения для задачи;
IMPLEMENTED_IN — отношение реализации во фреймворке;
RELATED_TO     — общая смысловая связь между сущностями.
```

Примеры отношений:

```text
BERT - IS_A -> Transformer
BERT - USES -> Masked Language Modeling
BERT - USED_FOR -> Text Classification
BERT - IMPLEMENTED_IN -> PyTorch
Attention - RELATED_TO -> Self-Attention
```

Ручная база знаний выступает как проверенный каркас. Она нужна для того, чтобы заранее задать структуру графа, основные типы узлов и примеры корректных связей.

### 3.3. `queries.cypher`

Файл `queries.cypher` содержит готовые Cypher-запросы для проверки базы знаний.

В нём находятся запросы для:

- поиска сущности по имени;
- поиска сущностей по подстроке;
- получения описания концепции;
- просмотра соседей узла;
- поиска задач, для которых используется модель;
- поиска методов, которые использует модель;
- сравнения двух моделей;
- проверки связей, импортированных из конкретного PDF;
- удаления связей по `source`;
- удаления изолированных узлов, импортированных из конкретного источника.

Например, запрос для просмотра связей, импортированных из PDF:

```cypher
MATCH (a)-[r]->(b)
WHERE r.source = 'ai_ner_semantic_test_en.pdf'
RETURN a.name AS from,
       type(r) AS relation,
       b.name AS to,
       r.confidence AS confidence,
       r.rule AS rule
ORDER BY from, relation, to;
```

Для визуальной проверки связи в Neo4j Browser можно использовать:

```cypher
MATCH (a {name:'RAG'})-[r:USES]->(b {name:'Vector Index'})
RETURN a, r, b;
```

---

## 4. Автоматический парсер PDF

Автоматический парсер находится в папке:

```text
neo4j/parser_service
```

Основной файл запуска:

```text
neo4j/parser_service/parser/main.py
```

Парсер выполняет полный pipeline обработки PDF:

1. Извлекает текст из PDF.
2. Сохраняет промежуточные `.txt` и `.md` файлы.
3. Нормализует текст.
4. Извлекает сущности словарным способом.
5. Дополнительно извлекает сущности через spaCy NER-модель при флаге `--use-ner`.
6. Объединяет найденные сущности.
7. Валидирует сущности.
8. Извлекает отношения между сущностями.
9. Валидирует отношения.
10. Формирует `graph.json`.
11. При флаге `--import-neo4j` импортирует результат в Neo4j.

---

## 5. Сущности и отношения

### 5.1. Типы сущностей

В проекте используются пять основных типов сущностей:

```text
Model     — модели искусственного интеллекта;
Method    — методы, техники и подходы;
Task      — задачи, для которых применяются модели или методы;
Framework — библиотеки, инструменты и платформы;
Concept   — общие понятия и концепции.
```

Примеры:

```text
Model     | BERT
Model     | GPT
Model     | LLaMA
Method    | LoRA
Method    | Fine-tuning
Task      | Question Answering
Task      | Text Classification
Framework | PyTorch
Framework | Qdrant
Concept   | Vector Index
Concept   | Embedding
```

### 5.2. Типы отношений

В проекте используются следующие типы отношений:

```text
IS_A
USES
USED_FOR
IMPLEMENTED_IN
RELATED_TO
```

Примеры:

```text
BERT - IS_A -> Transformer
BERT - USES -> Masked Language Modeling
BERT - USED_FOR -> Named Entity Recognition
RAG - USES -> Vector Index
LLaMA - USES -> LoRA
Mixtral-8x7B - USES -> Mixture of Experts
CLIP - USES -> Contrastive Learning
```

### 5.3. Метаданные связей

Автоматически извлечённые связи имеют дополнительные свойства:

```text
source      — источник связи, например имя PDF-файла;
evidence    — текстовый фрагмент, на основании которого была найдена связь;
confidence  — условная оценка уверенности в корректности связи;
rule        — правило, по которому связь была извлечена.
```

Пример связи в Neo4j:

```text
RAG - USES -> Vector Index
source = ai_ner_semantic_test_en.pdf
confidence = 0.82
rule = strict_uses
```

`confidence` в текущей реализации является эвристической оценкой, а не точной статистической вероятностью. Для ручной базы знаний обычно используется `confidence = 1.0`, так как эти связи добавлены вручную.

---

## 6. Установка и локальный запуск без Docker

Перейти в папку парсера:

```bash
cd ~/Desktop/neo4j_project/neo4j/parser_service
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установить зависимости:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Проверить, что `spaCy` установлен:

```bash
python3 - <<'PY'
import spacy
print('spaCy OK:', spacy.__version__)
PY
```

---

## 7. Запуск Neo4j

Neo4j запускается через Docker Compose из корня проекта:

```bash
cd ~/Desktop/neo4j_project

docker compose up -d neo4j
```

Проверить, что контейнер запущен:

```bash
docker ps | grep neo4j
```

Neo4j Browser доступен по адресу:

```text
http://localhost:7474
```

Данные для входа:

```text
login: neo4j
password: password123
```

---

## 8. Применение ручной базы знаний

После запуска Neo4j нужно применить ограничения:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 -f /cypher/constraints.cypher
```

Затем загрузить ручную базу знаний:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 -f /cypher/seed.cypher
```

После этого в Neo4j появятся ручные узлы и связи с `source = manual_seed`.

Проверить количество узлов:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "
MATCH (n)
RETURN labels(n)[0] AS label, count(n) AS count
ORDER BY count DESC;
"
```

Проверить количество связей:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "
MATCH ()-[r]->()
RETURN type(r) AS relation, count(r) AS count
ORDER BY count DESC;
"
```

---

## 9. Парсинг PDF без импорта в Neo4j

Если нужно только распарсить PDF и получить `graph.json`, используется команда без флага `--import-neo4j`:

```bash
cd ~/Desktop/neo4j_project/neo4j/parser_service

source .venv/bin/activate

python3 -m parser.main \
  --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf \
  --use-ner
```

После выполнения появится файл:

```text
parser/output/ai_ner_semantic_test_en.graph.json
```

Также создаются промежуточные файлы:

```text
parser/output/ai_ner_semantic_test_en.txt
parser/output/ai_ner_semantic_test_en.md
parser/output/ai_ner_semantic_test_en.normalized.txt
```

Проверить содержимое `graph.json` можно так:

```bash
python3 - <<'PY'
import json
from pathlib import Path

path = Path('parser/output/ai_ner_semantic_test_en.graph.json')

if not path.exists():
    raise SystemExit(f'Файл не найден: {path}')

data = json.loads(path.read_text(encoding='utf-8'))

print('SOURCE:', data['source'])
print('NODES:', len(data['nodes']))
print('RELATIONS:', len(data['relations']))

print('\nNODES:')
for n in data['nodes']:
    print(n['label'], '|', n['name'])

print('\nRELATIONS:')
for r in data['relations']:
    print(r['from_name'], '-', r['type'], '->', r['to_name'])
PY
```

---

## 10. Парсинг PDF с автоматическим импортом в Neo4j

Для полного цикла используется флаг:

```text
--import-neo4j
```

Команда:

```bash
cd ~/Desktop/neo4j_project/neo4j/parser_service

source .venv/bin/activate

export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password123"
export NEO4J_DATABASE="neo4j"

python3 -m parser.main \
  --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf \
  --use-ner \
  --import-neo4j
```

В этом режиме происходит полный pipeline:

```text
PDF → text/markdown → normalized text → entities → relations → graph.json → Neo4j
```

После успешного выполнения в терминале должны быть строки вида:

```text
[6/6] Building JSON payload...
JSON: .../parser/output/ai_ner_semantic_test_en.graph.json
[Neo4j] Importing payload into database...
[Neo4j] Import finished.
Done.
```

Это означает, что PDF не только распарсился, но и найденные узлы и связи были добавлены в Neo4j.

---

## 11. Проверка импортированных данных в Neo4j

Проверить конкретную связь:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "
MATCH (a {name:'RAG'})-[r:USES]->(b {name:'Vector Index'})
RETURN a.name AS from,
       type(r) AS relation,
       b.name AS to,
       r.source AS source,
       r.confidence AS confidence,
       r.rule AS rule;
"
```

Ожидаемый результат:

```text
RAG | USES | Vector Index | ai_ner_semantic_test_en.pdf | 0.82 | strict_uses
```

Проверить все связи, импортированные из конкретного PDF:

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "
MATCH (a)-[r]->(b)
WHERE r.source = 'ai_ner_semantic_test_en.pdf'
RETURN a.name AS from,
       type(r) AS relation,
       b.name AS to,
       r.confidence AS confidence,
       r.rule AS rule
ORDER BY from, relation, to
LIMIT 50;
"
```

Через Neo4j Browser можно визуально посмотреть граф:

```cypher
MATCH (a {name:'RAG'})-[r:USES]->(b {name:'Vector Index'})
RETURN a, r, b;
```

---

## 12. Режимы работы парсера

У парсера есть два основных режима.

### 12.1. Только парсинг

```bash
python3 -m parser.main \
  --input <path_to_pdf> \
  --use-ner
```

Результат:

```text
создаётся graph.json, но Neo4j не изменяется
```

Этот режим удобен, если нужно сначала проверить качество извлечённых сущностей и отношений.

### 12.2. Парсинг и импорт в Neo4j

```bash
python3 -m parser.main \
  --input <path_to_pdf> \
  --use-ner \
  --import-neo4j
```

Результат:

```text
создаётся graph.json, затем найденные узлы и связи импортируются в Neo4j
```

Этот режим нужен для автоматического пополнения графовой базы знаний.

---

## 13. Как работает импорт в Neo4j

Импорт реализован в файле:

```text
neo4j/parser_service/parser/import_to_neo4j.py
```

Этот модуль берёт `graph.json` или готовый `payload` из парсера и добавляет данные в Neo4j.

Для узлов используется логика `MERGE`, чтобы не создавать дубликаты:

```cypher
MERGE (n:Label {name: $name})
```

Для связей также используется `MERGE`:

```cypher
MERGE (a)-[r:RELATION_TYPE]->(b)
```

После этого для связи задаются свойства:

```text
source
evidence
confidence
rule
```

Поэтому один и тот же PDF можно обработать повторно: Neo4j не должен создавать дублирующиеся узлы и связи, а будет обновлять существующие элементы.

---

## 14. Инструкция для backend-интеграции

На текущем этапе `parser_service` работает как самостоятельный CLI-модуль. Он принимает путь к PDF-файлу, выполняет парсинг и при необходимости сам импортирует результат в Neo4j.

Если в проекте есть endpoint или другой механизм загрузки файлов, его нужно связать с `parser_service`.

Логика backend-интеграции должна быть такой:

1. Пользователь загружает PDF через интерфейс.
2. Backend сохраняет файл на сервере.
3. Backend получает локальный путь к сохранённому PDF.
4. Backend вызывает `parser_service` в режиме полного цикла.
5. Парсер создаёт `graph.json`.
6. Парсер автоматически импортирует найденные сущности и связи в Neo4j.
7. Backend возвращает пользователю статус обработки.

Важно: backend не должен самостоятельно разбирать `graph.json` и вручную формировать Cypher-запросы. Эта логика уже реализована внутри `parser_service`.

Со стороны backend нужно только корректно вызвать парсер после загрузки файла и передать путь к PDF.

Полный режим должен включать импорт в Neo4j:

```text
--import-neo4j
```

Если запускать парсер без этого режима, файл будет обработан, `graph.json` будет создан, но новые знания в Neo4j не попадут.

### 14.1. Что backend должен передать парсеру

Backend должен передать:

```text
путь к PDF-файлу;
флаг использования NER;
флаг импорта в Neo4j;
доступные env-переменные подключения к Neo4j.
```

Минимальная логика:

```text
после загрузки PDF вызвать parser.main с параметрами:
--input <path_to_uploaded_pdf>
--use-ner
--import-neo4j
```

### 14.2. Переменные окружения для Neo4j

Парсер берёт настройки подключения к Neo4j из env:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
NEO4J_DATABASE=neo4j
```

В production-режиме пароль и адрес Neo4j должны задаваться через переменные окружения, а не быть жёстко прописаны в коде.

### 14.3. Что возвращать пользователю

Backend может возвращать пользователю статус:

```text
файл загружен;
парсинг выполнен;
graph.json создан;
данные импортированы в Neo4j;
количество найденных узлов;
количество найденных связей.
```

Для этого можно ориентироваться на вывод парсера:

```text
[Neo4j] Import finished.
Done.
```

В дальнейшем можно доработать parser_service так, чтобы он возвращал структурированный результат в JSON-формате для backend.

---

## 15. Проверка работы полного pipeline

Полная проверка состоит из трёх шагов.

### 15.1. Запустить Neo4j

```bash
cd ~/Desktop/neo4j_project

docker compose up -d neo4j
```

### 15.2. Запустить парсер с импортом

```bash
cd ~/Desktop/neo4j_project/neo4j/parser_service

source .venv/bin/activate

export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password123"
export NEO4J_DATABASE="neo4j"

python3 -m parser.main \
  --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf \
  --use-ner \
  --import-neo4j
```

### 15.3. Проверить данные в Neo4j

```bash
docker exec -it neo4j cypher-shell -u neo4j -p password123 "
MATCH (a)-[r]->(b)
WHERE r.source = 'ai_ner_semantic_test_en.pdf'
RETURN a.name AS from,
       type(r) AS relation,
       b.name AS to,
       r.confidence AS confidence,
       r.rule AS rule
ORDER BY from, relation, to
LIMIT 50;
"
```

Если запрос возвращает связи, значит база знаний расширилась данными из PDF.

---

## 16. Docker Compose

В проекте используется `docker-compose.yml` для запуска Neo4j и parser-service.

Neo4j запускается как контейнер:

```yaml
neo4j:
  image: neo4j:5
  container_name: neo4j
  ports:
    - "7474:7474"
    - "7687:7687"
```

При первом запуске Docker Compose скачивает образ `neo4j:5`, если он ещё не загружен локально, создаёт контейнер и запускает Neo4j. Neo4j не устанавливается напрямую в операционную систему, а работает внутри Docker-контейнера.

Запуск Neo4j:

```bash
docker compose up -d neo4j
```

Остановка контейнеров:

```bash
docker compose down
```

Если нужно полностью удалить данные Neo4j volume, это делается отдельно:

```bash
docker volume rm neo4j_project_neo4j_data
```

Эту команду нужно использовать осторожно, так как она удаляет данные базы.

---

## 17. Типовые проблемы

### 17.1. `ModuleNotFoundError: No module named 'spacy'`

Причина: зависимости не установлены в активное виртуальное окружение.

Решение:

```bash
cd ~/Desktop/neo4j_project/neo4j/parser_service
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### 17.2. `zsh: permission denied: /path/to/parser_service`

Причина: в терминале был введён путь к папке как команда.

Неправильно:

```bash
~/Desktop/neo4j_project/neo4j/parser_service
```

Правильно:

```bash
cd ~/Desktop/neo4j_project/neo4j/parser_service
```

### 17.3. Neo4j не запущен

Проверить:

```bash
docker ps | grep neo4j
```

Запустить:

```bash
cd ~/Desktop/neo4j_project
docker compose up -d neo4j
```

### 17.4. Импорт не попал в Neo4j

Проверить, что команда запускалась с флагом:

```text
--import-neo4j
```

Если флага не было, был создан только `graph.json`, но база знаний не изменилась.

### 17.5. Дубликаты parser_service

Папка должна называться строго:

```text
neo4j/parser_service
```

Нельзя использовать путь с пробелами перед именем папки:

```text
neo4j/    parser_service
```

Если такая папка появилась, её нужно удалить и проверить Git:

```bash
cd ~/Desktop/neo4j_project
ls -lb neo4j
git ls-files | grep "    parser_service"
```

---

## 18. Текущий статус проекта

На текущем этапе реализовано:

- ручная база знаний Neo4j через Cypher;
- ограничения уникальности для основных типов узлов;
- начальное наполнение графа через `seed.cypher`;
- набор проверочных запросов в `queries.cypher`;
- извлечение текста из PDF;
- нормализация текста;
- словарное извлечение сущностей;
- извлечение сущностей через spaCy NER;
- объединение и валидация сущностей;
- извлечение отношений;
- валидация отношений;
- формирование `graph.json`;
- отдельный импорт `graph.json` в Neo4j;
- автоматический импорт в Neo4j через флаг `--import-neo4j`.

Главная рабочая команда полного цикла:

```bash
python3 -m parser.main \
  --input parser/samples/corpus_pdfs/ai_ner_semantic_test_en.pdf \
  --use-ner \
  --import-neo4j
```

Результат:

```text
PDF распарсен;
graph.json создан;
узлы и связи добавлены в Neo4j;
база знаний расширена данными из документа.
```

---

## 19. Возможные дальнейшие улучшения

Проект уже выполняет полный цикл пополнения графовой базы знаний, но его можно развивать дальше.

Возможные улучшения:

- улучшить валидацию сущностей, чтобы отсекать мусорные узлы;
- добавить LLM-проверку извлечённых отношений;
- добавить Entity Linking пользовательских запросов к узлам Neo4j;
- добавить LLM-классификацию пользовательских запросов;
- добавить backend endpoint для загрузки PDF;
- добавить очередь задач для долгой обработки документов;
- добавить статус обработки документа;
- добавить хранение текстовых chunks как отдельного слоя RAG;
- связать узлы и отношения с evidence/chunks;
- сделать интерфейс для просмотра импортированных документов и связей.

---

## 20. Краткое описание для защиты

Проект реализует RAG-справочную систему на графовой базе знаний Neo4j. Сначала была создана ручная база знаний с помощью Cypher-скриптов: заданы основные типы узлов, отношения и стартовые данные. Затем был реализован Python-парсер PDF-документов, который извлекает текст, находит сущности и отношения, формирует JSON-представление графа и при флаге `--import-neo4j` автоматически импортирует найденные знания в Neo4j.

Таким образом, система позволяет не только вручную задавать знания в графе, но и автоматически расширять базу знаний на основе новых PDF-документов.