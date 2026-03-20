import os
import json
import random

def generate_text_cases(output_path):
    positive_honduras_templates = [
        "Vos sos maje si pensás que {action}.",
        "Qué pijudo está {object}.",
        "Ese cipote siempre anda de {adjective}.",
        "Cheque maje, nos vemos en {place}.",
        "Pucha, qué {adjective} está el clima hoy.",
        "Ando hule hoy, prestame {amount} lempiras.",
        "Qué macizo le quedó el {object} a ese maitro.",
        "Vos siempre de paja, nunca dejas de {action}.",
        "Esa chava está bien {adjective}.",
        "Ayer me eché unas potras en {place}."
    ]
    
    negative_mexico_templates = [
        "Qué onda wey, ¿vamos a {action}?",
        "No mames, ese vato está re {adjective}.",
        "Está bien chido el {object} que compraste.",
        "Ahorita nos vemos en {place}, carnal.",
        "Me dio un chingo de {noun} ver eso.",
        "Pinche clima loco, ¿verdad?",
        "Ese güey siempre dice puras mamadas.",
        "Qué pedo con el {object} de allá.",
        "Chale, ya la cagaste con el {noun}.",
        "No manches, está cañón {action}."
    ]
    
    neutral_spanish_templates = [
        "Hola, me gustaría {action} mañana.",
        "El {object} es muy {adjective}.",
        "Nos encontramos en {place} a las cinco.",
        "Tengo mucho {noun} por este proyecto.",
        "El clima está bastante agradable hoy.",
        "¿Podrías ayudarme a {action} por favor?",
        "Ese señor fue muy amable con nosotros.",
        "El {object} cuesta {amount} dólares.",
        "Es importante mantener la calma.",
        "Gracias por tu tiempo y atención."
    ]
    
    gibberish_sentences = [
        "Jsfkj ksjflsj fljsfl kd.",
        "Aasd fghj kl qwer tyu.",
        "Zxcv bnm asdfg hjkl.",
        "Qeqw eqe qeqwe qweq weq.",
        "1234 567 890 abc def."
    ]
    
    fillers = {
        "action": ["jugar partido", "salir temprano", "trabajar duro", "comer baleadas", "hacer eso"],
        "object": ["carro", "teléfono", "perro", "zapato", "libro"],
        "adjective": ["loco", "rápido", "fuerte", "bonito", "perezoso"],
        "place": ["la calle", "el parque", "el centro", "la tienda", "Tegucigalpa"],
        "amount": ["cien", "doscientos", "cincuenta", "veinte", "diez"],
        "noun": ["sueño", "miedo", "hambre", "coraje", "alegría"]
    }
    
    def fill_template(template):
        for key, values in fillers.items():
            if f"{{{key}}}" in template:
                template = template.replace(f"{{{key}}}", random.choice(values))
        return template

    dataset = []
    
    # Generate 50 Honduras (Positive)
    for _ in range(50):
        text = fill_template(random.choice(positive_honduras_templates))
        dataset.append({
            "text": text,
            "type": "Honduras",
            "expected_dialect_pass": True,
            "expected_model_prediction": "Honduras"
        })
        
    # Generate 50 Mexico (Negative)
    for _ in range(50):
        text = fill_template(random.choice(negative_mexico_templates))
        dataset.append({
            "text": text,
            "type": "Mexico",
            "expected_dialect_pass": False,
            "expected_model_prediction": "Other"
        })

    # Generate 50 Neutral (Negative)
    for _ in range(50):
        text = fill_template(random.choice(neutral_spanish_templates))
        dataset.append({
            "text": text,
            "type": "Neutral",
            "expected_dialect_pass": False,
            "expected_model_prediction": "Other"
        })
        
    # Generate 10 Gibberish (Negative)
    for _ in range(10):
        dataset.append({
            "text": random.choice(gibberish_sentences),
            "type": "Gibberish",
            "expected_dialect_pass": False,
            "expected_model_prediction": "Other"
        })
        
    random.shuffle(dataset)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)
        
    print(f"Generated {len(dataset)} synthetic text cases at {output_path}")

if __name__ == "__main__":
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    output = os.path.join(base_dir, "tests", "expected_outputs", "text_cases.json")
    generate_text_cases(output)
