Новый контрольный PDF для проверки
гибридного извлечения сущностей
Этот PDF создан как новый тестовый документ для проверки гибридного
пайплайна извлечения знаний. В тексте намеренно использованы новые
сущности, которых не было в предыдущих документах, чтобы проверить,
сможет ли система расширять графовую базу знаний без полного ручного
обновления словаря. Документ посвящён современным моделям
искусственного интеллекта, задачам обработки текста, методам адаптации
и инфраструктуре развёртывания. Формулировки сделаны максимально
явными, чтобы парсеру было проще выделять сущности и строить отношения
между ними.
Новые языковые модели
Mistral является моделью Transformer и применяется для Text Generation,
Summarization и Question Answering. В инженерных обзорах Mistral часто
реализуется в vLLM и PyTorch. Mistral использует Instruction Tuning при
адаптации к прикладным сценариям. В ряде материалов Mistral также
связывают с Concept Context Window, потому что размер контекстного окна
влияет на качество работы языковой модели. Для системы извлечения
знаний важно, чтобы Mistral был распознан как новая Model, vLLM - как
Framework, Instruction Tuning - как Method, а Context Window - как Concept.
Mixtral является моделью Transformer и используется для Text Generation и
Summarization. Mixtral использует Mixture of Experts как ключевой Method. В
производственных сценариях Mixtral реализуется в PyTorch и vLLM. Кроме
того, Mixtral связан с Concept Sparse Routing, потому что в архитектуре
mixture-of-experts маршрутизация токенов играет важную роль. Если парсер
работает устойчиво, то он должен корректно извлечь новые сущности
Mixtral, Mixture of Experts, Sparse Routing и vLLM без ручного добавления
каждой из них в seed-граф.
Qwen является моделью Transformer и применяется для Question Answering и
Retrieval-Augmented Generation. Qwen использует Instruction Tuning и
Quantization. В ряде практических примеров Qwen реализуется в ONNX
Runtime и PyTorch. Qwen также связан с Concept Vector Index, потому что в
сценариях Retrieval-Augmented Generation важную роль играет
индексирование эмбеддингов. Для графовой базы знаний полезно, чтобы
Retrieval-Augmented Generation было распознано как Task, Quantization - как
Method, ONNX Runtime - как Framework, а Vector Index - как Concept.
Мультимодальные и визуальные модели
CLIP является моделью Neural Network и используется для Image Retrieval и
Zero-Shot Classification. CLIP использует Contrastive Learning и часто
реализуется в PyTorch. В статьях по мультимодальному обучению CLIP связан
с Concept Joint Embedding Space, поскольку изображения и тексты
проецируются в общее пространство представлений. Если система

корректно извлекает знания, она должна распознать CLIP как новую Model,
Contrastive Learning как Method, Image Retrieval и Zero-Shot Classification как
Task, а Joint Embedding Space как Concept.
SAM является моделью Neural Network и применяется для Image
Segmentation. SAM использует Prompt Encoding и может быть реализован в
PyTorch. Кроме того, SAM связан с Concept Mask Representation, потому что
сегментационные модели формируют представление объекта в виде маски.
Этот пример нужен для того, чтобы проверить, умеет ли парсер извлекать не
только языковые модели, но и современные модели компьютерного зрения с
новыми методами и концептами.
Связи между концептами
В документе также присутствуют отношения между концептами и методами.
Sparse Routing связано с Mixture of Experts, потому что маршрутизация
определяет, какие эксперты активируются на конкретном входе. Joint
Embedding Space связано с Contrastive Learning, так как контрастивное
обучение формирует согласованное пространство признаков. Vector Index
связано с Retrieval-Augmented Generation, поскольку retrieval-сценарий
опирается на поиск по векторам. Context Window связано с Instruction Tuning
только косвенно, поэтому такая связь не должна автоматически появляться
в графе без явного текстового маркера.
Цель контрольного теста
С практической точки зрения этот файл полезен как контрольный тест на
действительно новые сущности. В отличие от предыдущего русского PDF,
здесь специально собраны названия, которые могут отсутствовать в словаре
начальной версии системы. Если после прогона в Neo4j появятся узлы Mistral,
Mixtral, Qwen, CLIP, SAM, vLLM, ONNX Runtime, Mixture of Experts, Contrastive
Learning, Prompt Encoding, Vector Index и Joint Embedding Space, то это будет
означать, что система уже способна не только распознавать заранее
известные термины, но и частично расширять базу знаний за счёт
гибридного извлечения.
