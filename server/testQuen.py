from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList, StoppingCriteria
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# GPT-Neo-125M Modell laden
model_name = "Qwen/Qwen-7B-Chat"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).eval()

# Eingabetext
input_text = "Erzähl mir etwas Interessantes über künstliche Intelligenz."

# Text in Tokens umwandeln
input_ids = tokenizer(input_text, return_tensors="pt").input_ids

# Benutzerdefinierte StoppingCriteria für Streaming
class StreamStoppingCriteria(StoppingCriteria):
    def __init__(self, max_length):
        self.max_length = max_length
        self.current_length = 0

    def __call__(self, input_ids, scores, **kwargs):
        self.current_length += 1
        # Stream den zuletzt generierten Token
        new_token = tokenizer.decode(input_ids[0, -1:], skip_special_tokens=True)
        print(new_token, end="", flush=True)  # Direktes Streamen
        return self.current_length >= self.max_length

# Generierung mit Token-Streaming
stopping_criteria = StoppingCriteriaList([StreamStoppingCriteria(max_length=200)])

print("\nAntwort:")
model.generate(
    input_ids,
    max_length=200,
    do_sample=True,
    temperature=0.7,
    pad_token_id=tokenizer.eos_token_id,
    stopping_criteria=stopping_criteria
)
