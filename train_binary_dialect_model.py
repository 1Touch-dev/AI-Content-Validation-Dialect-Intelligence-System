import os
import json
import torch
import evaluate
import numpy as np
from datasets import load_dataset
from sklearn.metrics import confusion_matrix
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer
)

def compute_metrics(eval_pred):
    metric_acc = evaluate.load("accuracy")
    metric_f1 = evaluate.load("f1")
    metric_p = evaluate.load("precision")
    metric_r = evaluate.load("recall")
    
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    acc = metric_acc.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = metric_f1.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    precision = metric_p.compute(predictions=predictions, references=labels, average="weighted")["precision"]
    recall = metric_r.compute(predictions=predictions, references=labels, average="weighted")["recall"]
    
    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

def train_binary_model():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    data_dir = os.path.join(base_dir, "datasets", "honduras")
    output_dir = os.path.join(base_dir, "models", "honduras_dialect_binary_classifier")
    report_path = os.path.join(base_dir, "reports", "honduras_dialect_binary_training_report.md")
    
    # 1. HARDWARE DETECTION
    device = "cpu"
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    print(f"Using device: {device}")

    # 2. LOAD DATASETS
    print("Loading datasets...")
    data_files = {
        "train": os.path.join(data_dir, "train.jsonl"),
        "validation": os.path.join(data_dir, "validation.jsonl"),
        "test": os.path.join(data_dir, "test.jsonl")
    }
    dataset = load_dataset("json", data_files=data_files)
    
    print(f"Train size: {len(dataset['train'])}")
    print(f"Validation size: {len(dataset['validation'])}")
    print(f"Test size: {len(dataset['test'])}")

    # We enforce labels explicitly so we can safely output 1/0
    # Other -> 0, Honduras -> 1
    unique_labels = ['Other', 'Honduras']
    label2id = {'Other': 0, 'Honduras': 1}
    id2label = {0: 'Other', 1: 'Honduras'}
    num_labels = 2
    
    def add_label_id(example):
        return {'label': int(label2id[example['binary_dialect']])}
        
    dataset = dataset.map(add_label_id)
    
    # Cast explicitly to ClassLabel so HF doesn't treat as regression/multi-label due to floats
    from datasets import ClassLabel
    dataset = dataset.cast_column("label", ClassLabel(names=unique_labels))

    # 3. TOKENIZATION
    print("Tokenizing...")
    model_name = "dccuchile/bert-base-spanish-wwm-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)
        
    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    
    # 4. MODEL INITIALIZATION
    print("Initializing binary model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
        problem_type="single_label_classification",
        ignore_mismatched_sizes=True
    )

    # 5. TRAINING CONFIGURATION
    training_args = TrainingArguments(
        output_dir=os.path.join(base_dir, "models", "checkpoints_binary"),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy"
    )

    # 6. TRAIN MODEL
    print("Starting binary training...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        compute_metrics=compute_metrics,
        processing_class=tokenizer
    )
    
    train_result = trainer.train()
    metrics = train_result.metrics
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)

    # 7. MODEL EVALUATION
    print("Evaluating on test set...")
    test_results = trainer.predict(tokenized_datasets["test"])
    test_metrics = test_results.metrics
    
    pred_labels = np.argmax(test_results.predictions, axis=-1)
    true_labels = test_results.label_ids
    cm = confusion_matrix(true_labels, pred_labels)
    
    # 8. SAVE MODEL
    print(f"Saving binary model to {output_dir}")
    trainer.save_model(output_dir)
    
    # 9. INFERENCE TESTS
    print("\nRunning required inference tests...")
    import transformers
    transformers.logging.set_verbosity_error()
    from transformers import pipeline
    classifier = pipeline("text-classification", model=output_dir, tokenizer=output_dir, device=0 if device in ["cuda"] else -1)
    
    test_1 = "Vos sos maje si pensás eso"
    test_1_res = classifier(test_1)
    print(f"Input: '{test_1}' -> {test_1_res}")
    
    test_2 = "Qué onda wey"
    test_2_res = classifier(test_2)
    print(f"Input: '{test_2}' -> {test_2_res}")

    # 10. TRAINING REPORT
    report = [
        "# Binary Dialect Classifier (Honduras vs Other) - Training Report",
        "",
        "## Dataset Statistics",
        f"- Target representation: Downsampled to 50/50 balance (Total {len(dataset['train'])+len(dataset['validation'])+len(dataset['test'])} records)",
        f"- Train size: {len(dataset['train'])}",
        f"- Validation size: {len(dataset['validation'])}",
        f"- Test size: {len(dataset['test'])}",
        "",
        "## Training Metrics",
        f"- Runtime: {metrics.get('train_runtime', 0):.2f}s",
        f"- Epochs completed: 3",
        "",
        "## Test Evaluation",
        f"- Accuracy: {test_metrics.get('test_accuracy', 0):.4f}",
        f"- F1 Score: {test_metrics.get('test_f1', 0):.4f}",
        f"- Precision: {test_metrics.get('test_precision', 0):.4f}",
        f"- Recall: {test_metrics.get('test_recall', 0):.4f}",
        "",
        "## Confusion Matrix (Test Set)",
        "| True \\ Predicted | Other (0) | Honduras (1) |",
        "|---|---|---|",
        f"| **Other (0)** | {cm[0][0]} | {cm[0][1]} |",
        f"| **Honduras (1)** | {cm[1][0]} | {cm[1][1]} |",
        "",
        "## Required Inference Tests",
        f"1. **Input**: '{test_1}'",
        f"   - **Prediction**: {test_1_res[0]['label']} (Confidence: {test_1_res[0]['score']:.4f})",
        f"2. **Input**: '{test_2}'",
        f"   - **Prediction**: {test_2_res[0]['label']} (Confidence: {test_2_res[0]['score']:.4f})",
        "",
        "## Model Status",
        f"The binary dialect classifier is built and safely exported to `models/honduras_dialect_binary_classifier/`."
    ]
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"\nTraining pipeline complete. Report saved to {report_path}")

if __name__ == "__main__":
    train_binary_model()
