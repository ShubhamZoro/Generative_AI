from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, TrainingArguments, Trainer
import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

peft_model_id = "ShubhamZoro/FLan-T5-Summarize"
config = PeftConfig.from_pretrained(peft_model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(config.base_model_name_or_path, return_dict=True, device_map='auto')
model = PeftModel.from_pretrained(model, peft_model_id)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path) 
import streamlit as st

st.title('Summarize')
txt=st.text_area('Text to analyze', '''''')

# Load saved model
def get_results(abs_text):
  dialogue = abs_text
  

  prompt = f"""
  Summarize the following conversation.

  {dialogue}

  Summary: """

  input_ids = tokenizer(prompt, return_tensors="pt").input_ids
  input_ids = input_ids.to(next(model.parameters()).device)

  peft_model_outputs = model.generate(input_ids=input_ids, generation_config=GenerationConfig(max_new_tokens=200, num_beams=1,do_sample=True, temperature=1.5))
  peft_model_text_output = tokenizer.decode(peft_model_outputs[0], skip_special_tokens=True)

  print(f'PEFT MODEL: {peft_model_text_output}')
  return peft_model_text_output
  


print("\nAI formatted abstract is given below:\n")
if st.button('summarize'):
  summary=get_results(txt)
  st.subheader("Generated Summary:")
  st.write(summary)
