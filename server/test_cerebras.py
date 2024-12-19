from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import warnings
warnings.filterwarnings("ignore")

# Modellname und Tokenizer laden
model_name = "cerebras/Cerebras-GPT-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Lade das Modell auf die GPU
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16
).to("cuda")  # Stelle sicher, dass das Modell auf der GPU ist

# Prompt für Inferenz
prompt = "Write some php code for an Article Class"

# Eingaben auf die GPU verschieben
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

# Antwort generieren (mit Temperatur)
outputs = model.generate(
    **inputs,
    max_length=200,  # Reduziere Länge für Speicheroptimierung
    pad_token_id=tokenizer.eos_token_id,
    temperature=0.7
)

# Ausgabe dekodieren
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Antwort:", response)
