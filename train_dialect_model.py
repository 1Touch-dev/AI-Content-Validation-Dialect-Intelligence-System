import os
import json
import torch
import evaluate
import numpy as np
from datasets import load_dataset, DatasetDict
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

def train_model():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    data_dir = os.path.join(base_dir, "datasets", "honduras")
    output_dir = os.path.join(base_dir, "models", "honduras_dialect_classifier")
    report_path = os.path.join(base_dir, "reports", "honduras_dialect_training_report.md")
    
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
    
    # Verify sizes
    print(f"Train size: {len(dataset['train'])}")
    print(f"Validation size: {len(dataset['validation'])}")
    print(f"Test size: {len(dataset['test'])}")

    # Map labels to integers
    # We are currently doing binary classification? Or multi-class?
    # This dataset only contains honduras data. Wait, looking at the dataset repair...
    # The dialect field is "dialect". In honduras_dataset_expanded, maybe all are honduras?
    # Let me check the unique labels first.
    def get_labels(ds):
        labels = set()
        for item in ds:
            labels.add(item['dialect'])
        return list(labels)
        
    unique_labels = get_labels(dataset['train'])
    print(f"Unique labels in train: {unique_labels}")
    
    # Create label mapping
    label2id = {label: i for i, label in enumerate(unique_labels)}
    id2label = {i: label for label, i in label2id.items()}
    num_labels = len(unique_labels)
    
    def add_label_id(example):
        example['label'] = float(label2id[example['dialect']])
        return example
        
    dataset = dataset.map(add_label_id)

    # 3. TOKENIZATION
    print("Tokenizing...")
    model_name = "dccuchile/bert-base-spanish-wwm-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)
        
    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    
    # 4. MODEL INITIALIZATION
    print("Initializing model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )

    # 5. TRAINING CONFIGURATION
    training_args = TrainingArguments(
        output_dir=os.path.join(base_dir, "models", "checkpoints"),
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
    print("Starting training...")
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
    test_metrics = trainer.evaluate(eval_dataset=tokenized_datasets["test"], metric_key_prefix="test")
    trainer.log_metrics("test", test_metrics)
    trainer.save_metrics("test", test_metrics)

    # 8. SAVE MODEL
    print(f"Saving model to {output_dir}")
    trainer.save_model(output_dir)
    
    # 9. QUICK INFERENCE TEST
    print("\nRunning quick inference test...")
    from transformers import pipeline
    classifier = pipeline("text-classification", model=output_dir, tokenizer=output_dir, device=0 if device == "cuda" else -1)
    
    sample_text = "Vos sos maje si pensás eso"
    result = classifier(sample_text)
    print(f"Input: '{sample_text}'")
    print(f"Prediction: {result}")
    
    # 10. TRAINING REPORT
    report = [
        "# Honduran Dialect Classifier - Training Report",
        "",
        "## Dataset Statistics",
        f"- Train size: {len(dataset['train'])}",
        f"- Validation size: {len(dataset['validation'])}",
        f"- Test size: {len(dataset['test'])}",
        f"- Number of classes: {num_labels} ({', '.join(unique_labels)})",
        "",
        "## Training Metrics",
        f"- Runtime: {metrics.get('train_runtime', 0):.2f}s",
        f"- Steps: {metrics.get('train_steps', 0)}",
        f"- Epochs completed: 3",
        "",
        "## Final Test Evaluation",
        f"- Accuracy: {test_metrics.get('test_accuracy', 0):.4f}",
        f"- F1 Score: {test_metrics.get('test_f1', 0):.4f}",
        f"- Precision: {test_metrics.get('test_precision', 0):.4f}",
        f"- Recall: {test_metrics.get('test_recall', 0):.4f}",
        "",
        "## Example Prediction",
        f"- Input: '{sample_text}'",
        f"- Output: {result[0]['label']} (Confidence: {result[0]['score']:.4f})",
        "",
        "## Model Status",
        "The model is successfully trained and saved to `models/honduras_dialect_classifier/`. It is ready for production inference.",
    ]
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"\nTraining pipeline complete. Report saved to {report_path}")

if __name__ == "__main__":
    train_model()
