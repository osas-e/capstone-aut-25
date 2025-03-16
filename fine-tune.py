import os
import ollama

# Run fine-tuning command via Ollama CLI
model_name = "gemma2"  # Change if using a different version

os.system(f"ollama create gemma-incose-expert -f ./modelfile")

print("Fine-tuning complete. Model saved as 'gemma-incose-expert' in Ollama.")

# ---------------------------
# 4️⃣ Use the Fine-Tuned Model in Ollama
# ---------------------------
def query_ollama(prompt):
    response = ollama.chat(model="gemma-incose-expert", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Example Test
test_input = "Evaluate this requirement against Rule 2: 'When stating quantities, all numbers should have appropriate and consistent units of measure.'\nRequirement: 'The system shall display the Events in a graph by time.'"
output = query_ollama(test_input)

print("Test Output from Fine-Tuned Model:")
print(output)