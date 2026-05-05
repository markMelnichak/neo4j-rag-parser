// =========================
// Concepts
// =========================
MERGE (c1:Concept {name:'Transformer'})
SET c1.description='Архитектура на механизме внимания',
    c1.normalized_name='transformer',
    c1.aliases=['transformer architecture'],
    c1.source='manual_seed';

MERGE (c2:Concept {name:'Neural Network'})
SET c2.description='Модель машинного обучения на основе слоёв нейронов',
    c2.normalized_name='neural network',
    c2.aliases=['neural networks'],
    c2.source='manual_seed';

MERGE (c3:Concept {name:'Attention'})
SET c3.description='Механизм выделения важных частей входа',
    c3.normalized_name='attention',
    c3.aliases=[],
    c3.source='manual_seed';

MERGE (c4:Concept {name:'Overfitting'})
SET c4.description='Переобучение: плохая обобщающая способность',
    c4.normalized_name='overfitting',
    c4.aliases=['overfit'],
    c4.source='manual_seed';

MERGE (c5:Concept {name:'Regularization'})
SET c5.description='Методы уменьшения переобучения',
    c5.normalized_name='regularization',
    c5.aliases=['regularisation'],
    c5.source='manual_seed';

MERGE (c6:Concept {name:'Embedding'})
SET c6.description='Векторное представление объекта',
    c6.normalized_name='embedding',
    c6.aliases=['embeddings'],
    c6.source='manual_seed';

MERGE (c7:Concept {name:'Tokenization'})
SET c7.description='Разбиение текста на токены',
    c7.normalized_name='tokenization',
    c7.aliases=['tokenisation', 'tokenizing'],
    c7.source='manual_seed';

// =========================
// Models
// =========================
MERGE (m1:Model {name:'BERT'})
SET m1.type='NLP model',
    m1.normalized_name='bert',
    m1.aliases=[],
    m1.source='manual_seed';

MERGE (m2:Model {name:'RoBERTa'})
SET m2.type='NLP model',
    m2.normalized_name='roberta',
    m2.aliases=['robustly optimized bert approach'],
    m2.source='manual_seed';

MERGE (m3:Model {name:'GPT'})
SET m3.type='LLM',
    m3.normalized_name='gpt',
    m3.aliases=['generative pre-trained transformer'],
    m3.source='manual_seed';

MERGE (m4:Model {name:'ResNet'})
SET m4.type='CV model',
    m4.normalized_name='resnet',
    m4.aliases=['residual network'],
    m4.source='manual_seed';

// =========================
// Tasks
// =========================
MERGE (t1:Task {name:'Text Classification'})
SET t1.normalized_name='text classification',
    t1.aliases=[],
    t1.source='manual_seed';

MERGE (t2:Task {name:'Question Answering'})
SET t2.normalized_name='question answering',
    t2.aliases=['qa'],
    t2.source='manual_seed';

MERGE (t3:Task {name:'Named Entity Recognition'})
SET t3.normalized_name='named entity recognition',
    t3.aliases=['ner'],
    t3.source='manual_seed';

MERGE (t4:Task {name:'Machine Translation'})
SET t4.normalized_name='machine translation',
    t4.aliases=['mt'],
    t4.source='manual_seed';

MERGE (t5:Task {name:'Image Classification'})
SET t5.normalized_name='image classification',
    t5.aliases=[],
    t5.source='manual_seed';

// =========================
// Methods
// =========================
MERGE (me1:Method {name:'Self-Attention'})
SET me1.normalized_name='self-attention',
    me1.aliases=['self attention'],
    me1.source='manual_seed';

MERGE (me2:Method {name:'Fine-tuning'})
SET me2.normalized_name='fine-tuning',
    me2.aliases=['fine tuning'],
    me2.source='manual_seed';

MERGE (me3:Method {name:'Dropout'})
SET me3.normalized_name='dropout',
    me3.aliases=[],
    me3.source='manual_seed';

MERGE (me4:Method {name:'Weight Decay'})
SET me4.normalized_name='weight decay',
    me4.aliases=[],
    me4.source='manual_seed';

MERGE (me5:Method {name:'Adam Optimizer'})
SET me5.normalized_name='adam optimizer',
    me5.aliases=['adam'],
    me5.source='manual_seed';

MERGE (me6:Method {name:'Backpropagation'})
SET me6.normalized_name='backpropagation',
    me6.aliases=['back propagation', 'backprop'],
    me6.source='manual_seed';

MERGE (me7:Method {name:'Masked Language Modeling'})
SET me7.normalized_name='masked language modeling',
    me7.aliases=['mlm'],
    me7.source='manual_seed';

// =========================
// Frameworks
// =========================
MERGE (f1:Framework {name:'PyTorch'})
SET f1.normalized_name='pytorch',
    f1.aliases=[],
    f1.source='manual_seed';

MERGE (f2:Framework {name:'TensorFlow'})
SET f2.normalized_name='tensorflow',
    f2.aliases=['tf'],
    f2.source='manual_seed';

// =========================
// Relations
// =========================
MATCH (m:Model {name:'BERT'}), (c:Concept {name:'Transformer'})
MERGE (m)-[r:IS_A]->(c)
SET r.source='manual_seed', r.evidence='BERT is a transformer model', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'RoBERTa'}), (c:Concept {name:'Transformer'})
MERGE (m)-[r:IS_A]->(c)
SET r.source='manual_seed', r.evidence='RoBERTa is a transformer model', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'GPT'}), (c:Concept {name:'Transformer'})
MERGE (m)-[r:IS_A]->(c)
SET r.source='manual_seed', r.evidence='GPT is a transformer model', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'ResNet'}), (c:Concept {name:'Neural Network'})
MERGE (m)-[r:IS_A]->(c)
SET r.source='manual_seed', r.evidence='ResNet is a neural network model', r.confidence=1.0, r.rule='seed_manual';

MATCH (c:Concept {name:'Transformer'}), (a:Concept {name:'Attention'})
MERGE (c)-[r:USES]->(a)
SET r.source='manual_seed', r.evidence='Transformer uses attention', r.confidence=1.0, r.rule='seed_manual';

MATCH (c:Concept {name:'Attention'}), (sa:Method {name:'Self-Attention'})
MERGE (c)-[r:RELATED_TO]->(sa)
SET r.source='manual_seed', r.evidence='Attention is related to self-attention', r.confidence=1.0, r.rule='seed_manual';

MATCH (c:Concept {name:'Overfitting'}), (r2:Concept {name:'Regularization'})
MERGE (c)-[r:RELATED_TO]->(r2)
SET r.source='manual_seed', r.evidence='Overfitting is related to regularization', r.confidence=1.0, r.rule='seed_manual';

MATCH (r2:Concept {name:'Regularization'}), (d:Method {name:'Dropout'})
MERGE (r2)-[r:USES]->(d)
SET r.source='manual_seed', r.evidence='Regularization uses dropout', r.confidence=1.0, r.rule='seed_manual';

MATCH (r2:Concept {name:'Regularization'}), (w:Method {name:'Weight Decay'})
MERGE (r2)-[r:USES]->(w)
SET r.source='manual_seed', r.evidence='Regularization uses weight decay', r.confidence=1.0, r.rule='seed_manual';

MATCH (c:Concept {name:'Embedding'}), (tok:Concept {name:'Tokenization'})
MERGE (c)-[r:RELATED_TO]->(tok)
SET r.source='manual_seed', r.evidence='Embedding is related to tokenization', r.confidence=1.0, r.rule='seed_manual';

// USED_FOR
MATCH (m:Model {name:'BERT'}), (t:Task {name:'Text Classification'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='BERT is used for text classification', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'BERT'}), (t:Task {name:'Question Answering'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='BERT is used for question answering', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'BERT'}), (t:Task {name:'Named Entity Recognition'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='BERT is used for named entity recognition', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'RoBERTa'}), (t:Task {name:'Text Classification'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='RoBERTa is used for text classification', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'RoBERTa'}), (t:Task {name:'Question Answering'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='RoBERTa is used for question answering', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'GPT'}), (t:Task {name:'Machine Translation'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='GPT is used for machine translation', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'ResNet'}), (t:Task {name:'Image Classification'})
MERGE (m)-[r:USED_FOR]->(t)
SET r.source='manual_seed', r.evidence='ResNet is used for image classification', r.confidence=1.0, r.rule='seed_manual';

// USES methods
MATCH (m:Model {name:'BERT'}), (me:Method {name:'Fine-tuning'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='BERT uses fine-tuning', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'BERT'}), (me:Method {name:'Masked Language Modeling'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='BERT uses masked language modeling', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'RoBERTa'}), (me:Method {name:'Fine-tuning'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='RoBERTa uses fine-tuning', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'RoBERTa'}), (me:Method {name:'Masked Language Modeling'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='RoBERTa uses masked language modeling', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'GPT'}), (me:Method {name:'Backpropagation'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='GPT uses backpropagation', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'GPT'}), (me:Method {name:'Adam Optimizer'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='GPT uses Adam optimizer', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'ResNet'}), (me:Method {name:'Backpropagation'})
MERGE (m)-[r:USES]->(me)
SET r.source='manual_seed', r.evidence='ResNet uses backpropagation', r.confidence=1.0, r.rule='seed_manual';

// IMPLEMENTED_IN
MATCH (m:Model {name:'BERT'}), (f:Framework {name:'PyTorch'})
MERGE (m)-[r:IMPLEMENTED_IN]->(f)
SET r.source='manual_seed', r.evidence='BERT implemented in PyTorch', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'RoBERTa'}), (f:Framework {name:'PyTorch'})
MERGE (m)-[r:IMPLEMENTED_IN]->(f)
SET r.source='manual_seed', r.evidence='RoBERTa implemented in PyTorch', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'GPT'}), (f:Framework {name:'PyTorch'})
MERGE (m)-[r:IMPLEMENTED_IN]->(f)
SET r.source='manual_seed', r.evidence='GPT implemented in PyTorch', r.confidence=1.0, r.rule='seed_manual';

MATCH (m:Model {name:'ResNet'}), (f:Framework {name:'TensorFlow'})
MERGE (m)-[r:IMPLEMENTED_IN]->(f)
SET r.source='manual_seed', r.evidence='ResNet implemented in TensorFlow', r.confidence=1.0, r.rule='seed_manual';
