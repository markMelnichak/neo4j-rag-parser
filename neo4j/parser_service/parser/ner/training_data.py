from __future__ import annotations

TRAIN_DATA = [
    (
        "BERT is a Transformer model used for Text Classification and Question Answering. BERT uses Fine-tuning and is implemented in PyTorch.",
        {
            "entities": [
                (0, 4, "MODEL"),
                (10, 21, "CONCEPT"),
                (37, 56, "TASK"),
                (61, 79, "TASK"),
                (91, 102, "METHOD"),
                (125, 132, "FRAMEWORK"),
            ]
        },
    ),
    (
        "RoBERTa is a Transformer model used for Text Classification. RoBERTa uses Masked Language Modeling and Fine-tuning in PyTorch.",
        {
            "entities": [
                (0, 7, "MODEL"),
                (13, 24, "CONCEPT"),
                (40, 59, "TASK"),
                (74, 99, "METHOD"),
                (104, 115, "METHOD"),
                (119, 126, "FRAMEWORK"),
            ]
        },
    ),
    (
        "GPT is a Transformer model used for Machine Translation. GPT uses Adam Optimizer and Backpropagation in PyTorch.",
        {
            "entities": [
                (0, 3, "MODEL"),
                (9, 20, "CONCEPT"),
                (36, 55, "TASK"),
                (66, 80, "METHOD"),
                (85, 100, "METHOD"),
                (104, 111, "FRAMEWORK"),
            ]
        },
    ),
    (
        "ResNet is a Neural Network model used for Image Classification and implemented in TensorFlow.",
        {
            "entities": [
                (0, 6, "MODEL"),
                (12, 26, "CONCEPT"),
                (42, 62, "TASK"),
                (82, 92, "FRAMEWORK"),
            ]
        },
    ),
    (
        "T5 is a Transformer model used for Summarization, Machine Translation and Question Answering. T5 uses Fine-tuning in Hugging Face Transformers.",
        {
            "entities": [
                (0, 2, "MODEL"),
                (8, 19, "CONCEPT"),
                (35, 48, "TASK"),
                (50, 69, "TASK"),
                (74, 92, "TASK"),
                (102, 113, "METHOD"),
                (117, 144, "FRAMEWORK"),
            ]
        },
    ),
    (
        "LLaMA is a Transformer model. LLaMA uses LoRA and RLHF and is implemented in PyTorch.",
        {
            "entities": [
                (0, 5, "MODEL"),
                (11, 22, "CONCEPT"),
                (42, 46, "METHOD"),
                (51, 55, "METHOD"),
                (78, 85, "FRAMEWORK"),
            ]
        },
    ),
    (
        "Whisper is a Neural Network model used for Speech Recognition and Speech Translation. Whisper uses Fine-tuning in PyTorch.",
        {
            "entities": [
                (0, 7, "MODEL"),
                (13, 27, "CONCEPT"),
                (43, 61, "TASK"),
                (66, 84, "TASK"),
                (99, 110, "METHOD"),
                (114, 121, "FRAMEWORK"),
            ]
        },
    ),
    (
        "U-Net is a Neural Network model used for Image Segmentation and implemented in TensorFlow.",
        {
            "entities": [
                (0, 5, "MODEL"),
                (11, 25, "CONCEPT"),
                (41, 59, "TASK"),
                (79, 89, "FRAMEWORK"),
            ]
        },
    ),
    (
        "Diffusion Model is a Generative Model used for Image Generation. Diffusion Model uses Classifier-Free Guidance in PyTorch.",
        {
            "entities": [
                (0, 15, "MODEL"),
                (21, 37, "CONCEPT"),
                (53, 69, "TASK"),
                (92, 118, "METHOD"),
                (122, 129, "FRAMEWORK"),
            ]
        },
    ),
    (
        "Mistral is a Transformer model used for Text Generation and Summarization. Mistral uses Instruction Tuning in vLLM and PyTorch.",
        {
            "entities": [
                (0, 7, "MODEL"),
                (13, 24, "CONCEPT"),
                (40, 55, "TASK"),
                (60, 73, "TASK"),
                (88, 106, "METHOD"),
                (110, 114, "FRAMEWORK"),
                (119, 126, "FRAMEWORK"),
            ]
        },
    ),
    (
        "Mixtral is a Transformer model. Mixtral uses Mixture of Experts and is implemented in vLLM.",
        {
            "entities": [
                (0, 7, "MODEL"),
                (13, 24, "CONCEPT"),
                (45, 63, "METHOD"),
                (86, 90, "FRAMEWORK"),
            ]
        },
    ),
    (
        "Qwen is a Transformer model used for Retrieval-Augmented Generation and Question Answering. Qwen uses Quantization in ONNX Runtime.",
        {
            "entities": [
                (0, 4, "MODEL"),
                (10, 21, "CONCEPT"),
                (37, 68, "TASK"),
                (73, 91, "TASK"),
                (103, 115, "METHOD"),
                (119, 131, "FRAMEWORK"),
            ]
        },
    ),
    (
        "CLIP is a Neural Network model used for Image Retrieval and Zero-Shot Classification. CLIP uses Contrastive Learning in PyTorch.",
        {
            "entities": [
                (0, 4, "MODEL"),
                (10, 24, "CONCEPT"),
                (40, 55, "TASK"),
                (60, 84, "TASK"),
                (96, 116, "METHOD"),
                (120, 127, "FRAMEWORK"),
            ]
        },
    ),
    (
        "SAM is a Neural Network model used for Image Segmentation. SAM uses Prompt Encoding in PyTorch.",
        {
            "entities": [
                (0, 3, "MODEL"),
                (9, 23, "CONCEPT"),
                (39, 57, "TASK"),
                (69, 84, "METHOD"),
                (88, 95, "FRAMEWORK"),
            ]
        },
    ),
    (
        "Sparse Routing is related to Mixture of Experts. Joint Embedding Space is related to Contrastive Learning.",
        {
            "entities": [
                (0, 14, "CONCEPT"),
                (29, 47, "METHOD"),
                (49, 70, "CONCEPT"),
                (85, 105, "METHOD"),
            ]
        },
    ),
]
