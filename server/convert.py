import torch
from transformers import AutoModelForCausalLM

# Lade das Modell
model_name = "Qwen/Qwen2.5-1.5B"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)

# Wandle Gewichte in 4-Bit oder 8-Bit um
for name, param in model.named_parameters():
    param.data = param.data.half()  # Konvertiere in FP16

# Speichere das Modell im GGML-Format
torch.save(model.state_dict(), "qwen2.5-1.5b-ggml.bin")