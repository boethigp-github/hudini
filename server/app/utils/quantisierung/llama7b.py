import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Modellname und Speicherort
model_name = "tiiuae/falcon-7b-instruct"
save_directory = "./quantized_falcon_7b_instruct"

# Funktion zur Überprüfung und Initialisierung des Modells
def load_or_quantize_model():
    if os.path.exists(save_directory):
        print("Quantisiertes Modell gefunden. Lade Modell...")
        # Modell und Tokenizer laden
        model = AutoModelForCausalLM.from_pretrained(save_directory, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(save_directory, trust_remote_code=True)
    else:
        print("Quantisiertes Modell nicht gefunden. Lade und quantisiere Modell...")
        # BitsAndBytes-Konfiguration für 4-bit Quantisierung
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,                # 4-bit Quantisierung aktivieren
            bnb_4bit_compute_dtype="float16", # Rechenoperationen in FP16
            bnb_4bit_quant_type="nf4"         # Normalisierte 4-bit Quantisierung
        )

        # Modell mit Quantisierung laden
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",                # Automatische GPU-Zuweisung
            trust_remote_code=True            # Remote-Code-Ausführung erlauben
        )

        # Tokenizer laden
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        # Modell und Tokenizer speichern
        os.makedirs(save_directory, exist_ok=True)
        model.save_pretrained(save_directory)
        tokenizer.save_pretrained(save_directory)
        print(f"Quantisiertes Modell gespeichert in: {save_directory}")

    return model, tokenizer

# Lade oder quantisiere das Modell
model, tokenizer = load_or_quantize_model()

# Testanfrage
query = "Erkläre die Grundlagen des maschinellen Lernens."
inputs = tokenizer(query, return_tensors="pt").to("cuda")

# Text generieren
outputs = model.generate(inputs["input_ids"], max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
