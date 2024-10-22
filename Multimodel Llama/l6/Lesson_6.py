#!/usr/bin/env python
# coding: utf-8

# # Tool Calling Use Cases

# <p style="background-color:#fff6e4; padding:15px; border-width:3px; border-color:#f5ecda; border-style:solid; border-radius:6px"> ⏳ <b>Note <code>(Kernel Starting)</code>:</b> This notebook takes about 30 seconds to be ready to use. You may start and watch the video while you wait.</p>

# In[1]:


import warnings
warnings.filterwarnings('ignore')


# ## Get API keys

# In[45]:


from utils import get_tavily_api_key
TAVILY_API_KEY = get_tavily_api_key()


# ## Load helper functions

# In[3]:


from utils import llama31
from utils import cprint
import json


# <p style="background-color:#fff6ff; padding:15px; border-width:3px; border-color:#efe6ef; border-style:solid; border-radius:6px"> 💻 &nbsp; <b>Access <code>requirements.txt</code> and <code>utils.py</code> files:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Open"</em>. For more help, please see the <em>"Appendix - Tips and Help"</em> Lesson.</p>

# ## Define tool system prompt

# In[4]:


from datetime import datetime

current_date = datetime.now()
formatted_date = current_date.strftime("%d %B %Y")
print(formatted_date)


# In[5]:


tool_system_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Environment: ipython
Tools: brave_search, wolfram_alpha
Cutting Knowledge Date: December 2023
Today Date: {formatted_date}
"""


# ## The brave_search built-in tool

# In[6]:


prompt = tool_system_prompt + f"""<|eot_id|><|start_header_id|>user<|end_header_id|>

What is the current weather in Menlo Park, California?

<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""


# In[7]:


response = llama31(prompt)
print(response)


# In[8]:


no_tool_call_prompt = tool_system_prompt + f"""<|eot_id|><|start_header_id|>user<|end_header_id|>

What is the population of California?

<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""


# In[9]:


no_tool_call_response = llama31(no_tool_call_prompt)
print(no_tool_call_response)


# ### Calling the search API

# In[10]:


from tavily import TavilyClient
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

result = tavily_client.search("current weather in Menlo Park, California")
cprint(result)


# ### Reprompting Llama with search tool response

# In[11]:


search_result = result["results"][0]["content"]
print(search_result)


# In[12]:


prompt = tool_system_prompt + f"""<|eot_id|><|start_header_id|>user<|end_header_id|>
What is the current weather in Menlo Park, California?

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

<|python_tag|>{response}<|eom_id|>
<|start_header_id|>ipython<|end_header_id|>

{search_result}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
print(prompt)


# In[13]:


response = llama31(prompt)
print(response)


# ## Using the higher-level message

# In[14]:


system_prompt_content = f"""
Environment: ipython
Tools: brave_search, wolfram_alpha
Cutting Knowledge Date: December 2023
Today Date: {formatted_date}
"""


# In[15]:


messages = [
    {"role": "system", "content":  system_prompt_content},
    {"role": "user",   "content": "What is the current weather in Menlo Park, California?"}
  ]


# In[16]:


response = llama31(messages)
print(response)


# In[17]:


messages = [
    {"role": "system",     "content":  system_prompt_content},
    {"role": "user",       "content": "What is the current weather in Menlo Park, California?"},
    {"role": "assistant",  "content": response},
    {"role": "ipython",    "content": search_result}
  ]


# In[18]:


response = llama31(messages)
print(response)


# ## The Wolfram Alpha tool

# In[19]:


math_problem = "Can you help me solve this equation: x^3 - 2x^2 - x + 2 = 0?"


# In[20]:


messages = [
    {"role": "system",  "content": system_prompt_content},
    {"role": "user",    "content": math_problem}
]


# In[21]:


response = llama31(messages)
print(response)


# ### Calling the Wolfram Alpha tool

# In[22]:


from utils import wolfram_alpha
tool_result = wolfram_alpha("solve x^3 - 2x^2 - x + 2 = 0")
print(tool_result)


# ### Checking the result

# In[23]:


from sympy import symbols, Eq, solve

x = symbols('x')                           # Define the variable
equation = Eq(x**3 - 2*x**2 - 1*x + 2, 0) # Define the equation
solution = solve(equation, x)              # Solve the equation

print(solution)


# ### Reprompting Llama with Wolfram Alpha tool response

# In[24]:


messages = [
    {"role": "system", "content": system_prompt_content},
    {"role": "user",      "content": math_problem},
    {"role": "assistant", "content": response},
    {"role": "ipython",   "content": tool_result}
]


# In[25]:


response = llama31(messages)
print(response)


# ## The code interpreter built-in tool

# In[26]:


loan_question = (
    "How much is the monthly payment, total payment, "
    "and total interest paid for a 30 year mortgage of $1M "
    "at a fixed rate of 6% with a 20% down payment?"
)


# In[27]:


messages = [
    {"role": "system",     "content": system_prompt_content},
    {"role": "user",       "content": loan_question},
  ]


# In[28]:


response = llama31(messages)
print(response)


# # Calculate loan payments

# In[29]:


from utils import calculate_loan
monthly_payment, total_payment, total_interest_paid = calculate_loan(
    loan_amount = 1000000, 
    annual_interest_rate = 0.06, 
    loan_term = 30, 
    down_payment = 200000)

print(f"Monthly payment: ${(monthly_payment)}")
print(f"Total payment: ${(total_payment)}")
print(f"Total interest paid: ${(total_interest_paid)}")


# ## Generating the code in Java

# In[30]:


messages = [
    {"role":    "system",     
     "content": system_prompt_content + "\nGenerate the code in Java."},
    {"role":    "user",       "content": loan_question},
  ]


# In[31]:


response = llama31(messages)
print(response)


# ### Reprompting Llama with Code Interpreter tool response

# In[32]:


code_interpreter_tool_response="""
Monthly payment: $4796
Total payment: $1726705
Total interest paid: $926705
"""


# In[33]:


messages = [
    {"role": "system", "content":  system_prompt_content},
    {"role": "user",      "content": loan_question},
    {"role": "assistant", "content": response},
    {"role": "ipython",   "content": code_interpreter_tool_response}
  ]


# In[34]:


response = llama31(messages)
print(response)


# ## Llama 3.1 custom tool calling

# In[35]:


from utils import trending_songs, get_boiling_point

country = "US"
top_num = 5
top_songs = trending_songs(country, top_num)
print(f"Top {top_num} trending songs in {country}:")
print(top_songs)


# <p style="background-color:#fff6ff; padding:15px; border-width:3px; border-color:#efe6ef; border-style:solid; border-radius:6px"> 💻 &nbsp; <b>Access <code>trending_songs()</code> in <code>utils.py</code> files:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Open"</em>. For more help, please see the <em>"Appendix - Tips and Help"</em> Lesson.</p>

# ## Prompt Llama 3.1 for custom tool call

# In[36]:


user_prompt = """
Answer the user's question by using the following functions if needed.
If none of the functions can be used, please say so.
Functions (in JSON format):
{
    "type": "function", "function": {
        "name": "get_boiling_point",
        "description": "Get the boiling point of a liquid",
        "parameters": {
            "type": "object", "properties": [
                {"liquid_name": {"type": "object", "description": "name of the liquid"}},
                {"celsius": {"type": "object", "description": "whether to use celsius"}}
            ], "required": ["liquid_name"]
        }
    }
}
{
    "type": "function", "function": {
        "name": "trending_songs",
        "description": "Returns the trending songs on a Music site",
        "parameters": {
            "type": "object", "properties": [
                {"country": {"type": "object", "description": "country to return trending songs for"}},
                {"n": {"type": "object", "description": "The number of songs to return"}}
            ], "required": ["country"]
        }
    }
}

Question: Can you check the top 5 trending songs in US?
"""


# In[37]:


messages = [
    {
      "role": "system", "content":  f"""
Environment: ipython
Cutting Knowledge Date: December 2023
Today Date: {formatted_date}
"""},
    {"role": "user", "content": user_prompt}
  ]


# In[38]:


result = llama31(messages,405)
print(result)


# ### Calling the custom tool

# In[39]:


custom_tools = {"trending_songs": trending_songs,
                "get_boiling_point": get_boiling_point}


# In[40]:


res = json.loads(result)
function_name = res['name']
parameters = list(res['parameters'].values())
function_name, parameters


# In[41]:


tool_result = custom_tools[function_name](*parameters)
tool_result


# ### Reprompting Llama with custom tool call result

# In[42]:


messages = [
    {
      "role": "system", "content":  f"""
Environment: ipython
Cutting Knowledge Date: December 2023
Today Date: {formatted_date}
"""},
    {"role": "user", "content": user_prompt},
    {"role": "assistant", "content": result},
    {"role": "ipython", "content": ','.join(tool_result)}
  ]


# In[43]:


response = llama31(messages, 70)
print(response)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




