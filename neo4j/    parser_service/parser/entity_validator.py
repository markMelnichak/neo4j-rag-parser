from __future__ import annotations

import re
from dataclasses import is_dataclass, replace
from typing import Any


ALLOWED_LABELS = {"Model", "Task", "Method", "Framework", "Concept"}

KNOWN_FRAMEWORKS = {
    "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "jax",
    "hugging face transformers", "transformers", "vllm", "langchain",
    "llamaindex", "milvus", "qdrant", "weaviate", "deepspeed",
    "megatron-lm", "openllm", "fastchat", "ollama", "onnx", "onnx runtime",
}

KNOWN_MODELS = {
    "bert", "roberta", "albert", "deberta", "electra", "xlm", "xlnet",
    "unilm", "gpt", "gpt-1", "gpt-2", "gpt-3", "gpt-4", "chatgpt",
    "instructgpt", "webgpt", "codex", "llama", "llama-2", "llama-2 chat",
    "mistral", "mistral-7b", "mixtral", "mixtral-8x7b", "qwen",
    "qwen-vl", "palm", "palm 2", "med-palm", "flan", "flan-palm",
    "lamda", "ernie", "ernie 3.0", "ernie 4.0", "t5", "bart",
    "bloom", "chinchilla", "gopher", "galactica", "codegen", "pythia",
    "orca", "starcoder", "gemini", "mamba", "rwkv", "hyena",
    "striped hyena", "claude", "grok", "deepseek-coder", "tinyllama",
    "alpaca", "vicuna", "guanaco", "koala", "zephyr", "docllm",
    "toolformer", "hugginggpt",
}

KNOWN_METHODS = {
    "fine-tuning", "fine tuning", "instruction tuning", "rlhf", "lora",
    "qlora", "peft", "masked language modeling", "mlm",
    "next sentence prediction", "next token prediction",
    "self-attention", "reinforcement learning",
    "direct preference optimization", "dpo", "kto",
    "chain-of-thought prompting", "chain of thought", "tree of thought",
    "self-consistency", "beam search", "greedy search",
    "top-k sampling", "top-p sampling", "nucleus sampling",
    "quantization", "knowledge distillation", "api distillation",
    "data parallelism", "pipeline parallelism", "sequence parallelism",
    "mixture of experts", "moe", "rope", "alibi",
    "bytepairencoding", "wordpieceencoding",
    "supervised method", "unsupervised method",
    "statistical language modeling", "markov chain models",
    "retrieval-augmented generation", "rag",
}

KNOWN_TASKS = {
    "text classification", "classification", "question answering", "qa",
    "machine translation", "summarization", "speech recognition",
    "named entity recognition", "information retrieval", "code generation",
    "reading comprehension", "sentiment analysis", "image segmentation",
    "image classification", "image generation", "speech translation",
    "masked language modeling", "autoregressive language modeling",
    "sequence-to-sequence prediction", "next token prediction",
}

KNOWN_CONCEPTS = {
    "transformer", "transformer architecture", "transformer network", "attention", "embedding", "tokenization",
    "neural network", "neural networks", "large language model",
    "large language models", "llm", "llms", "plm", "plms", "nlm", "nlms",
    "rnn", "rnns", "generative model", "overfitting", "hallucination",
    "retrieval augmented generation", "retrieval-augmented generation",
    "rag", "prompt engineering", "artificial general intelligence",
    "ai agents",  
    "state space models", "multi-modal llms",
}

BAD_EXACT = {
    "xnli crosslingual qa crosslingual tasks translation",
    "reading comprehension multi choice qa",
    "virtual acting physical acting",
    "stack of transformer encoders",
    "fully connected layer",
    "classifier layer",
    "web search",
    "recurrent neural networks",
    "gated recurrent unit",
    "unidirectional",
    "bidirectional",

    "ciirc", "c sur", "csur", "corr", "pmlr", "acm", "acm computing",
    "macmillan", "ducharme", "touvron", "solar-lezama", "fourrier",
    "stanford center", "gutman-solo", "w.-n. zhang",
    "data", "model", "models", "method", "methods", "algorithm",
    "information", "system", "task", "quality", "dataset", "datasets",
    "table", "figure", "section", "appendix", "references",
    "language models", "language model", "large language models",
    "large language model", "pretrained language model",
    "foundation model", "instruction model", "chat model",
    "transformer model", "transformer models",
    "данные", "модель", "метод", "алгоритм", "информация",
    "система", "задача", "качество", "таблица", "рисунок",
}

BAD_SUBSTRINGS = [
    "http://", "https://", "www.", "github.com", "doi.org", "arxiv",
    "isbn", "references", "bibliography", "copyright", "license",
    "this section provides", "et al", "proceedings", "conference",
    "journal", "fig.", "figure", "table", "appendix",
    " - - ", "✓", "стр.", "удк", "ббк",
    "ininternational conference",
    "datasets for emergent",
    "this section",
    "consist of",
    "contains",
    "above task categories",
    "connected with massive apis",
]

BAD_CHARS = {"✓", "ϵ", "∈", "{", "}", "№", "\\", "[", "]"}

BAD_ENDINGS = {
    "family", "families", "models", "model", "systems", "data",
    "layer", "network", "architecture",
}

BENCHMARKS_TO_DROP = {
    "math", "arc", "piqa", "siqa", "obqa", "openbookqa",
    "truthfulqa", "hotpotqa", "toolqa", "medqa", "squad",
    "hellaswag", "haleval", "halueval", "quac", "mbpp",
}


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _set_or_replace(obj: Any, **kwargs: Any) -> Any:
    if isinstance(obj, dict):
        copied = dict(obj)
        copied.update(kwargs)
        return copied

    if is_dataclass(obj):
        try:
            return replace(obj, **kwargs)
        except Exception:
            return obj

    for key, value in kwargs.items():
        try:
            setattr(obj, key, value)
        except Exception:
            pass

    return obj


def normalize_surface(value: str) -> str:
    value = str(value or "").strip()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" \n\t\r")
    value = value.strip(".,;:[]{}«»\"'")
    return value.strip()


def normalize_key(value: str) -> str:
    value = normalize_surface(value).lower()
    value = value.replace("-", "-").replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def canonicalize(value: str) -> str:
    raw = normalize_surface(value)
    key = normalize_key(raw)

    aliases = {
        "llama": "LLaMA",
        "llama 2": "LLaMA-2",
        "llama-2": "LLaMA-2",
        "gpt4": "GPT-4",
        "bert": "BERT",
        "roberta": "RoBERTa",
        "albert": "ALBERT",
        "electra": "ELECTRA",
        "xlnet": "XLNet",
        "unilm": "UNILM",
        "pytorch": "PyTorch",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "vllm": "vLLM",
        "lora": "LoRA",
        "qlora": "QLoRA",
        "rlhf": "RLHF",
        "rag": "RAG",
        "mlm": "Masked Language Modeling",
        "qa": "Question Answering",
        "self-attention": "Self-Attention",
        "fine tuning": "Fine-tuning",
        "fine-tuning": "Fine-tuning",
        "instruction tuning": "Instruction Tuning",
        "masked language modeling": "Masked Language Modeling",
        "question answering": "Question Answering",
        "machine translation": "Machine Translation",
        "text classification": "Text Classification",
        "speech recognition": "Speech Recognition",
        "summarization": "Summarization",
        "named entity recognition": "Named Entity Recognition",
        "retrieval augmented generation": "Retrieval-Augmented Generation",
        "retrieval-augmented generation": "Retrieval-Augmented Generation",
    }

    return aliases.get(key, raw)


def corrected_label(value: str, label: str) -> str:
    key = normalize_key(value)

    if key in KNOWN_FRAMEWORKS:
        return "Framework"
    if key in KNOWN_MODELS:
        return "Model"
    if key in KNOWN_METHODS:
        return "Method"
    if key in KNOWN_TASKS:
        return "Task"
    if key in KNOWN_CONCEPTS:
        return "Concept"

    # Heuristics
    if re.fullmatch(r"gpt-\d+(\.\d+)?", key):
        return "Model"

    if re.fullmatch(r".*-\d+b", key):
        return "Model"

    if key.endswith("gpt") or "gpt-" in key:
        return "Model"

    if key in {"milvus", "qdrant", "weaviate", "llamaindex", "langchain"}:
        return "Framework"

    return label


def looks_like_table_noise(value: str) -> bool:
    raw = value.strip()

    if re.search(r"\d+\s*-\s*-\s*-\s*\d+", raw):
        return True

    if raw.count("-") >= 4 and sum(ch.isdigit() for ch in raw) >= 2:
        return True

    if re.search(r"\b\d+(\.\d+)?\b.*\b\d+(\.\d+)?\b.*\b\d+(\.\d+)?\b", raw):
        return True

    if raw.count(" ") >= 5 and sum(ch.isdigit() for ch in raw) >= 3:
        return True

    return False


def looks_like_reference_noise(value: str) -> bool:
    raw = value.strip()
    low = raw.lower()

    if re.search(r"\[[0-9,\s\-]+\]", raw):
        return True

    if re.search(r"\b[A-Z][a-z]+,\s+[A-Z]\.", raw):
        return True

    if " et al" in low or "proceedings" in low or "conference" in low:
        return True

    if re.search(r"\bcite[a-z0-9_:-]+", low):
        return True

    return False


def is_allowed_by_known_lists(value: str) -> bool:
    key = normalize_key(value)
    return (
        key in KNOWN_FRAMEWORKS
        or key in KNOWN_MODELS
        or key in KNOWN_METHODS
        or key in KNOWN_TASKS
        or key in KNOWN_CONCEPTS
    )


def is_valid_entity_name(value: str, label: str) -> bool:
    raw = normalize_surface(value)
    low = normalize_key(raw)

    if not raw or label not in ALLOWED_LABELS:
        return False

    if low in BAD_EXACT:
        return False

    if low in BENCHMARKS_TO_DROP:
        return False

    if any(x in low for x in BAD_SUBSTRINGS):
        return False

    if any(ch in raw for ch in BAD_CHARS):
        return False

    if raw.startswith(("-", "–", "—", ".", ",", ";", ":", ")", "(")):
        return False

    if raw.endswith(("-", "–", "—", ".", ",", ";", ":", ")", "(")):
        return False

    if raw.count("(") != raw.count(")"):
        return False

    if len(raw) < 2:
        return False

    if len(raw) > 55 and not is_allowed_by_known_lists(raw):
        return False

    if raw.count(" ") > 5 and not is_allowed_by_known_lists(raw):
        return False

    if looks_like_table_noise(raw):
        return False

    if looks_like_reference_noise(raw):
        return False

    alpha_count = sum(ch.isalpha() for ch in raw)
    digit_count = sum(ch.isdigit() for ch in raw)

    if alpha_count < 2:
        return False

    if digit_count >= 6 and digit_count > alpha_count:
        return False

    # Отсекаем явно фразовые заголовки, которые NER принял за сущность.
    if re.search(
        r"\b(this|that|which|where|when|provides|consists|contains|shows|based on|overview|measuring|training compute|rethinking)\b",
        low,
    ):
        return False

    # Убираем слишком общие одиночные слова.
    if " " not in low and low in {
        "dynamic", "static", "prediction", "pipeline", "tensor",
        "dialog", "dialogue", "chains", "temperature", "reflection",
        "accuracy", "precision", "recall",
    }:
        return False

    # Не пускаем длинные generic phrases как Model.
    if label == "Model" and low.endswith(tuple(BAD_ENDINGS)) and not is_allowed_by_known_lists(raw):
        return False

    return True


def validate_entities(entities: list[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[tuple[str, str]] = set()
    removed = 0
    relabeled = 0

    for ent in entities:
        old_label = str(_get(ent, "label", "")).strip()
        text = str(_get(ent, "text", "")).strip()
        canonical = str(_get(ent, "canonical", "") or text).strip()

        surface = canonicalize(canonical or text)
        label = corrected_label(surface, old_label)

        if label != old_label:
            relabeled += 1

        if not is_valid_entity_name(surface, label):
            removed += 1
            continue

        key = (label, normalize_key(surface))

        if key in seen:
            continue

        seen.add(key)

        ent = _set_or_replace(
            ent,
            label=label,
            text=surface,
            canonical=surface,
            normalized_name=normalize_key(surface),
        )

        result.append(ent)

    print(f"  Entity validation: kept={len(result)} removed={removed} relabeled={relabeled}")
    return result


def _relation_field(rel: Any, names: list[str]) -> str:
    for name in names:
        value = _get(rel, name, "")
        if value:
            return str(value).strip()
    return ""


def validate_relations(relations: list[Any], entities: list[Any]) -> list[Any]:
    canonical_by_key: dict[str, str] = {}

    for ent in entities:
        name = str(_get(ent, "canonical", "") or _get(ent, "text", "")).strip()
        if not name:
            continue

        key = normalize_key(name)
        canonical_by_key[key] = name

        # Частые алиасы, чтобы связи не терялись после canonicalize()
        canonical_by_key[normalize_key(canonicalize(name))] = name

    result = []
    seen = set()
    removed = 0

    for rel in relations:
        from_name = _relation_field(rel, ["from_name", "source_name", "source", "head", "subject"])
        to_name = _relation_field(rel, ["to_name", "target_name", "target", "tail", "object"])
        rel_type = _relation_field(rel, ["type", "relation", "rel_type", "predicate"])

        from_name = canonicalize(from_name)
        to_name = canonicalize(to_name)

        from_key = normalize_key(from_name)
        to_key = normalize_key(to_name)

        if not from_key or not to_key or not rel_type:
            removed += 1
            continue

        if from_key == to_key:
            removed += 1
            continue

        if from_key not in canonical_by_key or to_key not in canonical_by_key:
            removed += 1
            continue

        key = (from_key, rel_type, to_key)

        if key in seen:
            continue

        seen.add(key)

        # Если relation — dict, поправим имена на canonical.
        if isinstance(rel, dict):
            rel = dict(rel)
            rel["from_name"] = canonical_by_key[from_key]
            rel["to_name"] = canonical_by_key[to_key]
            rel["type"] = rel_type

        result.append(rel)

    print(f"  Relation validation: kept={len(result)} removed={removed}")
    return result
