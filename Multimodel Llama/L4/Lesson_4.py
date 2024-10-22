#!/usr/bin/env python
# coding: utf-8

# # Prompt Format

# <p style="background-color:#fff6e4; padding:15px; border-width:3px; border-color:#f5ecda; border-style:solid; border-radius:6px"> ⏳ <b>Note <code>(Kernel Starting)</code>:</b> This notebook takes about 30 seconds to be ready to use. You may start and watch the video while you wait.</p>

# In[1]:


import warnings
warnings.filterwarnings('ignore')


# If you would like to view the utils.py file, uncomment the following line and run it. Alternately to view it in an editor, click `file->open` and look for utils.py

# In[ ]:


#!cat utils.py


# <p style="background-color:#fff6ff; padding:15px; border-width:3px; border-color:#efe6ef; border-style:solid; border-radius:6px"> 💻 &nbsp; <b>Access <code>requirements.txt</code> and <code>utils.py</code> files:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Open"</em>. For more help, please see the <em>"Appendix - Tips and Help"</em> Lesson.</p>

# ## Using the "user" and "assistant" roles

# In[2]:


question = "Who wrote the book Charlotte's Web?"

prompt = (
    "<|begin_of_text|>"                              # start of prompt
    "<|start_header_id|>user<|end_header_id|>"       # user header
    f"{question}"                                    # user input
    "<|eot_id|>"                                     #end of turn
    "<|start_header_id|>assistant<|end_header_id|>"  #assistant header
)

print(prompt)


# In[3]:


from  utils import llama31
response = llama31(prompt,8)
print(response)


# In[4]:


from utils import cprint
response = llama31(prompt,8, raw=True)

cprint(response)


# # Multi-turn chat

# In[5]:


follow_up_question = "Three best quotes in it"
follow_up_prompt = (
    "<|begin_of_text|>"                              # start of prompt
    "<|start_header_id|>user<|end_header_id|>"        # past  
    f"{question}"                                     # past
    "<|eot_id|>"                                      # past
    "<|start_header_id|>assistant<|end_header_id|>"   # past
    f"{response}"                                     # past
    "<|eot_id|>"                                      # past
    "<|start_header_id|>user<|end_header_id|>"       # new
    f"{follow_up_question}"                          # new
    "<|eot_id|>"                                     # new
    "<|start_header_id|>assistant<|end_header_id|>"  # new
)


# In[6]:


follow_up_response = llama31(follow_up_prompt)
print(follow_up_response)


# In[7]:


from IPython.display import Markdown, display
display(Markdown(follow_up_response))


# #### Without message history
# This is not in the video, but you can try the same prompt *Without* including history and see the models responds with three quotes - but not from the book.

# In[8]:


question = "Three Best quotes"
prompt = (
    "<|begin_of_text|>"  
    "<|start_header_id|>user<|end_header_id|>"
    f"{question}"
    "<|eot_id|>"
    "<|start_header_id|>assistant<|end_header_id|>"
)
response = llama31(prompt,8)
display(Markdown(response))


# ## Using "system" role

# In[9]:


question = "Three Great quotes"
system_message = (
    "You are an expert in quotes about sports " 
    "You provide just the quotes and no commentary. "
    "Reply in markdown"
)

prompt = (
    "<|begin_of_text|>"
    "<|start_header_id|>system<|end_header_id|>"
    f"{system_message}"
    "<|eot_id|>"    
    "<|start_header_id|>user<|end_header_id|>"
    f"{question}"
    "<|eot_id|>"
    "<|start_header_id|>assistant<|end_header_id|>"
)
response = llama31(prompt,70)
display(Markdown(response))


# In[10]:


follow_up_question = "three more"
follow_up_prompt = (
    "<|begin_of_text|>"
    "<|start_header_id|>system<|end_header_id|>"      # system
    f"{system_message}"                               # system
    "<|eot_id|>"                                      # system
    "<|start_header_id|>user<|end_header_id|>"        # past
    f"{question}"                                     # past
    "<|eot_id|>"                                      # past
    "<|start_header_id|>assistant<|end_header_id|>"   # past
    f"{response}"                                     # past
    "<|eot_id|>"                                      # past
    "<|start_header_id|>user<|end_header_id|>"         # new
    f"{follow_up_question}"                            # new     
    "<|eot_id|>"                                       # new
    "<|start_header_id|>assistant<|end_header_id|>"    # new
)
response = llama31(follow_up_prompt)
display(Markdown(response))


# # Chat with Llama using higher-level message

# In[11]:


prompt = (
    "<|begin_of_text|>"                              # start of prompt
    "<|start_header_id|>user<|end_header_id|>"       # user header
    "Who wrote the book Charlotte's Web?"                                    # user input
    "<|eot_id|>"                                     #end of turn
    "<|start_header_id|>assistant<|end_header_id|>"  #assistant header
)
response = llama31(prompt,8)
print(response)


# In[12]:


messages = [
    {
      "role": "user",
      "content": "Who wrote the book Charlotte's Web?"
    }
  ]
response = llama31(messages,8)
print(response)


# In[13]:


follow_up_question = "Three Best quotes"

messages = [
    {
      "role": "system",
      "content": "You are an terse expert in children's literature"
    },
    {
      "role": "user",
      "content": "Who wrote the book Charlotte's Web?"
    },
    {
      "role": "assistant",
      "content": response
    },
    {
      "role": "user",
      "content": follow_up_question
    }
  ]

response = llama31(messages,8)
print(response)


# In[14]:


class Conversation:
    def __init__(self, system=""):
        self.messages = []
        if system:
            self.messages.append({"role": "system", "content": system})
    def generate(self, user_question, model=8, temp=0):
        self.messages.append({"role": "user", "content":user_question})
        response = llama31(self.messages, model, temperature=temp)
        self.messages.append({"role":"assistant", "content":response})
        return response
        


# In[15]:


system_message = "You are a terse expert in Childrens literature." 
conv = Conversation(system_message)
conv.generate("Who wrote the book Charlotte's Web?")


# In[16]:


response = conv.generate("What are three quotes")
display(Markdown(response))


# In[17]:


conv.messages


# ## Multi-lingual Llama

# In[18]:


system_message = (
    "Answer in 8 languages: English, German, French, Italian," 
    "Portuguese, Hindi, Spanish, and Thai"
)
ml_conv = Conversation(system_message)
response = ml_conv.generate("3 basic phrases")
display(Markdown(response))


# ## Chatbot App

# In[19]:


code_query = """
I need a Python script for a Gradio chatbot app that should be run
within a Jupyter notebook.
1) When calling the LLM, use this class, which is already defined,
    dont redefine it:
class Conversation:
    def __init__(self, system=""):
        self.messages = []
        if system:
            self.messages.append({"role": "system", "content": system})

    def generate(self, user_question, model=8, temp=0):
        self.messages.append({"role": "user", "content": user_question})
        response = llama31(self.messages, model, temperature=temp)  
        self.messages.append({"role": "assistant", "content": response})
        return response
2) initialize the class with a system message of:
    "You are an expert in liturature. You provide brief replies"
3) the llama() function is defined like this:
    def llama(prompt_or_messages, model_size=8, 
              temperature=0, raw=False, debug=False):
    and returns a reponse in a string. Don't redefine this.
    valid model sizes are 8, 70 and 405.
"""
coder_system_message = (
    "You are an expert writing python Gradio chatbots" 
)
coder_conv = Conversation(coder_system_message)
response = coder_conv.generate(code_query, 405)
print(response)


# In[20]:


# This is the code generated by Llama in the video
# Your response to the above prompt may differ - try running your response as well!
# note, the final line was hand edited to add "server_name="0.0.0.0" to run in the course environment

import gradio as gr

# Initialize the conversation with a system message
conversation = Conversation("You are an expert in literature. You provide brief replies.")

# Define a function to generate a response to the user's input
def generate_response(user_input, model_size, temperature):
    try:
        model_size = int(model_size)
        if model_size not in [8, 70, 405]:
            return "Invalid model size. Please choose from 8, 70, or 405."
        temperature = float(temperature)
        if temperature < 0 or temperature > 1:
            return "Invalid temperature. Please choose a value between 0 and 1."
        response = conversation.generate(user_input, model=model_size, temp=temperature)
        return response
    except Exception as e:
        return str(e)

# Create a Gradio interface for the chatbot
demo = gr.Interface(
    fn=generate_response,
    inputs=[
        gr.Textbox(label="User Input"),
        gr.Radio(label="Model Size", choices=["8", "70", "405"]),
        gr.Slider(label="Temperature", minimum=0, maximum=1, step=0.1, value=0)
    ],
    outputs=gr.Textbox(label="Response"),
    title="Literature Expert Chatbot",
    description="Ask a question about literature and get a brief response from an expert."
)

# Launch the Gradio app
demo.launch(server_name="0.0.0.0")


# # A few more examples

# ## Compare with different sized Llama chat models
# 
# By default, the llama31 call uses the Llama 3.1 8B Instruct model. To see how the 70B or 405B model responds, simply pass 70 or 405 after prompt. For example, let compare how the 3 different sized Llama 3.1 chat models respond to the question about a quote in Hemingway's classic The Old Man and the Sea.

# In[21]:


question = "The quote that starts with 'Everything about him is old' in The Old Man and the Sea"

prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

response = llama31(prompt)
print(response)


# If you like Hemingway, you know Llama 3.1 8B is hallucinating a bit, and "old before they were young"? Now try to see if 70B does better.

# In[22]:


response = llama31(prompt, 70)
print(response)


# The response makes more sense, but definitely not Hemingway would've written. In fact, it'd hurt the eyes of his fans. Let's hope 405 will cure the pain.

# In[23]:


response = llama31(prompt, 405)
print(response)


# In[ ]:




