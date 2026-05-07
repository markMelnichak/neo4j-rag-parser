/*
Q1. Найти сущность по точному имени, normalized_name или aliases
Параметр: $term
*/
MATCH (n)
WHERE n.name = $term
   OR n.normalized_name = toLower($term)
   OR $term IN coalesce(n.aliases, [])
RETURN labels(n) AS labels, n.name AS name, properties(n) AS props;

/*
Q2. Поиск сущностей по подстроке без учета регистра
Параметр: $q
*/
MATCH (n)
WHERE toLower(n.name) CONTAINS toLower($q)
   OR toLower(coalesce(n.normalized_name, '')) CONTAINS toLower($q)
RETURN labels(n) AS labels, n.name AS name
ORDER BY name
LIMIT 20;

/*
Q3. Получить определение/описание Concept
Параметр: $concept
*/
MATCH (c:Concept)
WHERE c.name = $concept
   OR c.normalized_name = toLower($concept)
   OR $concept IN coalesce(c.aliases, [])
RETURN c.name AS concept, c.description AS description;

/*
Q4. Соседи узла (контекст depth=1)
Параметр: $name
*/
MATCH (n)
WHERE n.name = $name
   OR n.normalized_name = toLower($name)
   OR $name IN coalesce(n.aliases, [])
MATCH (n)-[r]-(m)
RETURN n.name AS center, type(r) AS rel, labels(m) AS neighborType, m.name AS neighbor
LIMIT 50;

/*
Q5. Для чего используется модель (USED_FOR)
Параметр: $model
*/
MATCH (m:Model)
WHERE m.name = $model
   OR m.normalized_name = toLower($model)
   OR $model IN coalesce(m.aliases, [])
MATCH (m)-[:USED_FOR]->(t:Task)
RETURN m.name AS model, collect(DISTINCT t.name) AS tasks;

/*
Q6. Какие методы использует модель (USES)
Параметр: $model
*/
MATCH (m:Model)
WHERE m.name = $model
   OR m.normalized_name = toLower($model)
   OR $model IN coalesce(m.aliases, [])
MATCH (m)-[:USES]->(me:Method)
RETURN m.name AS model, collect(DISTINCT me.name) AS methods;

/*
Q7. В каком фреймворке реализована модель (IMPLEMENTED_IN)
Параметр: $model
*/
MATCH (m:Model)
WHERE m.name = $model
   OR m.normalized_name = toLower($model)
   OR $model IN coalesce(m.aliases, [])
MATCH (m)-[:IMPLEMENTED_IN]->(f:Framework)
RETURN m.name AS model, collect(DISTINCT f.name) AS frameworks;

/*
Q8. Сравнение двух моделей по задачам и методам
Параметры: $a, $b
*/
MATCH (a:Model {name:$a})
OPTIONAL MATCH (a)-[:USED_FOR]->(ta:Task)
OPTIONAL MATCH (a)-[:USES]->(ma:Method)
WITH a, collect(DISTINCT ta.name) AS tasksA, collect(DISTINCT ma.name) AS methodsA
MATCH (b:Model {name:$b})
OPTIONAL MATCH (b)-[:USED_FOR]->(tb:Task)
OPTIONAL MATCH (b)-[:USES]->(mb:Method)
RETURN
  a.name AS modelA, tasksA AS tasksA, methodsA AS methodsA,
  b.name AS modelB, collect(DISTINCT tb.name) AS tasksB, collect(DISTINCT mb.name) AS methodsB;

/*
Q9. Технический запрос: проверить, существует ли сущность по имени
Параметр: $name
*/
MATCH (n {name:$name})
RETURN count(n) AS exists_count;

/*
Q10. Технический запрос: найти все сущности с aliases
*/
MATCH (n)
WHERE size(coalesce(n.aliases, [])) > 0
RETURN labels(n) AS labels, n.name AS name, n.aliases AS aliases
ORDER BY name;

/*
Q11. Технический запрос: получить все связи, извлеченные из конкретного source
Параметр: $source
*/
MATCH (a)-[r]->(b)
WHERE r.source = $source
RETURN a.name AS from_name, type(r) AS rel, b.name AS to_name, r.evidence AS evidence, r.confidence AS confidence
ORDER BY from_name, rel, to_name;

/*
Q12. Технический запрос: удалить связи по source
Параметр: $source
*/
MATCH ()-[r]->()
WHERE r.source = $source
DELETE r;

/*
Q13. Технический запрос: удалить узлы, импортированные из source, если они изолированы
Параметр: $source
*/
MATCH (n)
WHERE n.source = $source
  AND NOT (n)--()
DELETE n;

MATCH (a)-[r]->(b)
WHERE r.source = 'ai_ner_semantic_test_en.pdf'
RETURN a.name AS from,
       type(r) AS relation,
       b.name AS to,
       r.confidence AS confidence,
       r.rule AS rule
ORDER BY from, relation, to;
