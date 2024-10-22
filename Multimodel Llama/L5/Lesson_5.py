#!/usr/bin/env python
# coding: utf-8

# # L5: Tokenization

# <p style="background-color:#fff6e4; padding:15px; border-width:3px; border-color:#f5ecda; border-style:solid; border-radius:6px"> ⏳ <b>Note <code>(Kernel Starting)</code>:</b> This notebook takes about 30 seconds to be ready to use. You may start and watch the video while you wait.</p>

# In[ ]:


import warnings
warnings.filterwarnings('ignore')


# ## Initialize tiktoken tokenizer

# In[ ]:


from pathlib import Path
import tiktoken
from tiktoken.load import load_tiktoken_bpe
import torch
import json
import matplotlib.pyplot as plt

tokenizer_path = "./content/tokenizer.model"
num_reserved_special_tokens = 256

mergeable_ranks = load_tiktoken_bpe(tokenizer_path)

num_base_tokens = len(mergeable_ranks)
special_tokens = [
    "<|begin_of_text|>",
    "<|end_of_text|>",
    "<|reserved_special_token_0|>",
    "<|reserved_special_token_1|>",
    "<|finetune_right_pad_id|>",
    "<|step_id|>",
    "<|start_header_id|>",
    "<|end_header_id|>",
    "<|eom_id|>",
    "<|eot_id|>",
    "<|python_tag|>",
]
reserved_tokens = [
    f"<|reserved_special_token_{2 + i}|>"
    for i in range(num_reserved_special_tokens - len(special_tokens))
]
special_tokens = special_tokens + reserved_tokens

# source: https://github.com/meta-llama/llama-models/blob/main/models/llama3/api/tokenizer.py#L53
tokenizer = tiktoken.Encoding(
    name=Path(tokenizer_path).name,
    pat_str=r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+",
    mergeable_ranks=mergeable_ranks,
    special_tokens={token: len(mergeable_ranks) + i for i, token in enumerate(special_tokens)},
)


# In[ ]:


tokenizer.encode("hello")


# In[ ]:


tokenizer.decode([15339])


# In[ ]:


tokenizer.encode("hello Andrew")


# In[ ]:


tokenizer.encode("hello andrew")


# ### Tokens.ipynb
# If you would like to view a UTF-8 view of the Tokens.model file, uncomment the following line and run it.

# In[ ]:


#!cat Tokens.ipynb


# You can also go to file->open to find Tokens.ipynb file. Please note that the file is large and opening it might take some time.

# ## Getting the length of tokens of an input text

# In[ ]:


input_text = "hello world"
len(tokenizer.encode(input_text))


# In[ ]:


question = "Who wrote the book Charlotte's Web?"
prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
len(encoded_tokens)


# In[ ]:


decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
for e, d in zip(encoded_tokens, decoded_tokens):
    print(e, d)


# In[ ]:


from IPython.display import display, HTML
from utils import html_tokens, llama31


# <p style="background-color:#fff6ff; padding:15px; border-width:3px; border-color:#efe6ef; border-style:solid; border-radius:6px"> 💻 &nbsp; <b>Access <code>requirements.txt</code> and <code>utils.py</code> files:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Open"</em>. For more help, please see the <em>"Appendix - Tips and Help"</em> Lesson.</p>

# In[ ]:


display(HTML(html_tokens(decoded_tokens)))


# In[ ]:


#Try one of you own:
prompt = "Supercalifragilisticexpialidocious"
encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
display(HTML(html_tokens(decoded_tokens)))


# # LLM reasoning vs tokenization

# In[ ]:


question = "How many r's in the word strawberry?"
prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
response = llama31(prompt)
print(response)


# In[ ]:


encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
display(HTML(html_tokens(decoded_tokens)))


# In[ ]:


question = "How many r's in the word s t r a w b e r r y? "
prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
response = llama31(prompt)
print(response)


# In[ ]:


encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
display(HTML(html_tokens(decoded_tokens)))


# # Extra examples

# ## Llama 3.1 tokenization model file demystification
# 
# The Llama 3.1 tokenization model, named as tokenizer.model, can be downloaded along with the Llama 3.1 model weights or from the Llama models repo.

# In[ ]:


# download the Llama 3.1 tokenizer model
#!wget https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3/api/tokenizer.model


# If you take a quick look at the model file, you'll see it has 128,000 lines and each line has two values separated by a space: a mysterious string and a number that starts with 0 and ends with 127,999.

# In[ ]:


get_ipython().system('head -10 ./content/tokenizer.model')


# In[ ]:


get_ipython().system('tail -10 ./content/tokenizer.model')


# In[ ]:


get_ipython().system('wc -l ./content/tokenizer.model')


# Each line indeed describes one token out of 128K total tokens and its associated integer ID, and the string on each line is base64 encoded. Use the code snippet below to decode those 128K encoded strings, and then convert the decoded bytes to more readable UTF-8 tokens.

# In[ ]:


import base64

encoded_tokens = []
decoded_byte_tokens = []
decoded_utf8_tokens = []

with open("./content/tokenizer.model", 'r') as file:
  for i, line in enumerate(file):
    k, v = line.strip().split(' ')
    encoded_tokens.append({k: v})
    decoded_byte_tokens.append({base64.b64decode(k): v})
    decoded_utf8_tokens.append({base64.b64decode(k).decode('utf-8', errors="replace") : v})


# Let's check the first ten encoded tokens (what's stored in the tokenizer.model), and their decoded byte and UTF-8 tokens.

# In[ ]:


list(encoded_tokens)[:10]


# In[ ]:


list(decoded_byte_tokens)[:10]


# In[ ]:


list(decoded_utf8_tokens)[:10]


# Let's confirm the tokenizer.model file stores the base64 encoded strings for tokens, e.g. the token "hello".

# In[ ]:


base64.b64encode('h'.encode('utf-8'))


# In[ ]:


base64.b64encode('hello'.encode('utf-8'))


# In[ ]:


get_ipython().system('grep "aGVsbG8=" ./content/tokenizer.model')


# # More LLM reasoning vs tokenization
# 
# Let's try out Llama 3.1 on some recent tokenization related LLM problems, and see if we can improve its reasoning by some prompt engineering.

# ## Simple math problem

# In[ ]:


question = "Which number is bigger, 9.11 or 9.9? "
prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
response = llama31(prompt)
print(response)


# In[ ]:


response = llama31(prompt, 70)
print(response)


# In[ ]:


response = llama31(prompt, 405)
print(response)


# Somehow the largest Llama 3.1 405b model returns the incorrect result. From the visualization of the tokens in the prompt, you can see the number 9.11 is split into 3 tokens: "9", ".", and ".11", while 9.9 into 2 tokens: "9", ".", "9". If the two numbers are encoded as the two numbers themselves, correct model response will be more likely.

# In[ ]:


encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
[x for x in zip(encoded_tokens, decoded_tokens)]


# In[ ]:


display(HTML(html_tokens(decoded_tokens)))


# ## String reversing
# 
# First, for a common word "amazing", all 3 Llama 3.1 chat models reverse the string correctly.

# In[ ]:


input = "Reverse the string 'amazing'"
prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
response = llama31(prompt)
print(response)


# In[ ]:


response = llama31(prompt, 70)
print(response)


# In[ ]:


response = llama31(prompt, 405)
print(response)


# In[ ]:


encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
display(HTML(html_tokens(decoded_tokens)))


# For a less common word "language", Llama 3.1 8B doesn't return the correct result, but 70B and 405B do.

# In[ ]:


input = "Reverse the string 'language'"
prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
response = llama31(prompt)
print(response)


# In[ ]:


response = llama31(prompt, 70)
print(response)


# In[ ]:


response = llama31(prompt, 405)
print(response)


# In[ ]:


encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
display(HTML(html_tokens(decoded_tokens)))


# For the string "XMLElement", none of the 3 models is correct.

# In[ ]:


input = "Reverse the string 'XMLElement'"
prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
response = llama31(prompt)
print(response)


# In[ ]:


response = llama31(prompt, 70)
print(response)


# In[ ]:


response = llama31(prompt, 405)
print(response)


# In[ ]:


encoded_tokens = tokenizer.encode(prompt, allowed_special="all")
decoded_tokens = [tokenizer.decode([token]) for token in encoded_tokens]
display(HTML(html_tokens(decoded_tokens)))


# In[ ]:




