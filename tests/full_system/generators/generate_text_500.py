import os
import json
import random
import time
import evaluate
import numpy as np
from sklearn.metrics import confusion_matrix
import torch
from transformers import pipeline

def generate_500_text_samples():
    honduras_templates = [
        "Vos sos maje si pensás que {action}.",
        "Qué pijudo está {object}.",
        "Ese cipote siempre anda de {adjective}.",
        "Cheque maje, nos vemos en {place}.",
        "Pucha, qué {adjective} está el clima hoy.",
        "Ando hule hoy, prestame {amount} lempiras.",
        "Qué macizo le quedó el {object} a ese maitro.",
        "Ayer me eché unas potras en {place}.",
        "Este gobierno ya me tiene harto, puras pajas casacas.",
        "Esa chava está bien {adjective}.",
        "Man, no te vayas por ese lado que asaltan.",
        "Qué pijin nos metimos ayer en {place}.",
        "Las baleadas de {place} son las mejores, te lo juro maje."
    ]
    
    mexico_templates = [
        "Qué onda wey, ¿vamos a {action}?",
        "No mames, ese vato está re {adjective}.",
        "Está bien chido el {object} que compraste.",
        "Ahorita nos vemos en {place}, carnal.",
        "Me dio un chingo de {noun} ver eso.",
        "Pinche clima loco, ¿verdad?",
        "Ese güey siempre dice puras mamadas.",
        "Chale, ya la cagaste con el {noun}."
    ]
    
    ecuador_templates = [
        "Qué más ñaño, ¿todo bien?",
        "Esa manada de manes siempre haciendo {noun}.",
        "No sea gil, ponte pilas con el {object}.",
        "Chuta, qué frío hace en {place}.",
        "¡Qué bestia! No me la creo.",
        "De ley que voy mijo, espérame en {place}."
    ]
    
    neutral_templates = [
        "Hola, me gustaría {action} mañana.",
        "El {object} es muy {adjective}.",
        "Nos encontramos en {place} a las cinco.",
        "Tengo mucho {noun} por este proyecto.",
        "¿Podrías ayudarme a {action} por favor?",
        "El {object} cuesta {amount} dólares."
    ]
    
    english_templates = [
        "Hey man, let's go {action} today.",
        "That {object} looks really {adjective}.",
        "I'm feeling a lot of {noun} right now.",
        "Meet me at {place} tonight."
    ]
    
    gibberish = [
        "asdflkj hglkajsd fgjklsf 123",
        "qwerty uiop lkjhg fdsa zxcv bnm",
        "zxnczxc mncmxn sdkfjs sdfjsdf",
        "123 456 789 012 345 678",
        "kghjlk fsfs fsfsfs dfsdfsf"
    ]
    
    fillers = {
        "action": ["jugar partido", "salir temprano", "trabajar duro", "comer", "hacer eso"],
        "object": ["carro", "teléfono", "perro", "zapato", "libro", "juego"],
        "adjective": ["loco", "rápido", "fuerte", "bonito", "perezoso", "raro"],
        "place": ["la calle", "el parque", "el centro", "la tienda", "la capital"],
        "amount": ["cien", "doscientos", "cincuenta", "veinte", "diez", "mil"],
        "noun": ["sueño", "miedo", "hambre", "coraje", "alegría", "dolor"]
    }
    
    def fill(template):
        res = template
        for k, v in fillers.items():
            if f"{{{k}}}" in res:
                res = res.replace(f"{{{k}}}", random.choice(v))
        return res

    dataset = []
    
    # 250 Honduras
    for _ in range(250):
        dataset.append({
            "text": fill(random.choice(honduras_templates)),
            "dialect": "Honduras",
            "expected_label": 1
        })
        
    # 250 Negatives: 100 Mexico, 50 Ecuador, 50 Neutral, 25 English, 25 Gibberish
    for _ in range(100):
        dataset.append({ "text": fill(random.choice(mexico_templates)), "dialect": "Mexico", "expected_label": 0 })
    for _ in range(50):
        dataset.append({ "text": fill(random.choice(ecuador_templates)), "dialect": "Ecuador", "expected_label": 0 })
    for _ in range(50):
        dataset.append({ "text": fill(random.choice(neutral_templates)), "dialect": "Neutral", "expected_label": 0 })
    for _ in range(25):
        dataset.append({ "text": fill(random.choice(english_templates)), "dialect": "English", "expected_label": 0 })
    for _ in range(25):
        dataset.append({ "text": random.choice(gibberish), "dialect": "Gibberish", "expected_label": 0 })
        
    random.shuffle(dataset)
    return dataset

def run_evaluation(dataset, output_json, output_report):
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    model_path = os.path.join(base_dir, "models", "honduras_dialect_binary_classifier")
    
    print(f"Loading Dict-Classifier from {model_path} ...")
    device = 0 if torch.backends.mps.is_available() else -1
    classifier = pipeline("text-classification", model=model_path, tokenizer=model_path, device=device)
    
    y_true = []
    y_pred = []
    results = []
    
    start_time = time.time()
    for item in dataset:
        text = item['text']
        expected = item['expected_label']
        y_true.append(expected)
        
        res = classifier(text)[0]
        pred = 1 if res['label'] == "Honduras" else 0
        conf = res['score']
        
        y_pred.append(pred)
        item['predicted_label'] = pred
        item['confidence'] = conf
        results.append(item)
        
    calc_time = time.time() - start_time
    
    # Metrics
    acc_metric = evaluate.load("accuracy")
    pre_metric = evaluate.load("precision")
    rec_metric = evaluate.load("recall")
    f1_metric = evaluate.load("f1")
    
    acc = acc_metric.compute(predictions=y_pred, references=y_true)['accuracy']
    prec = pre_metric.compute(predictions=y_pred, references=y_true, zero_division=0)['precision']
    rec = rec_metric.compute(predictions=y_pred, references=y_true, zero_division=0)['recall']
    f1 = f1_metric.compute(predictions=y_pred, references=y_true, average='weighted')['f1']
    cm = confusion_matrix(y_true, y_pred, labels=[1, 0])
    
    # Save JSON 
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    # Markdown Report
    report = [
        f"## Text Dialect Testing Report (N=500)",
        f"- **Processing Time**: {calc_time:.2f}s",
        f"- **Accuracy**: {acc:.4f}",
        f"- **Precision**: {prec:.4f}",
        f"- **Recall**: {rec:.4f}",
        f"- **F1 Score**: {f1:.4f}",
        f"",
        f"### Confusion Matrix",
        f"| | Predicted Honduras | Predicted Other |",
        f"|---|---|---|",
        f"| **Actual Honduras** | True Positives: **{cm[0][0]}** | False Negatives: **{cm[0][1]}** |",
        f"| **Actual Other** | False Positives: **{cm[1][0]}** | True Negatives: **{cm[1][1]}** |",
    ]
    
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"✅ Extrapolated {len(dataset)} Text permutations successfully.")
    print("\n".join(report))

if __name__ == "__main__":
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    out_json = os.path.join(base_dir, "tests", "full_system", "results", "text_evaluation.json")
    out_rep = os.path.join(base_dir, "tests", "full_system", "results", "text_metrics.md")
    
    data = generate_500_text_samples()
    run_evaluation(data, out_json, out_rep)
