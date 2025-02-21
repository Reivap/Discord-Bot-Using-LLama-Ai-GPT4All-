# Discord-Bot-Using-LLama-Ai-GPT4All-


**Steps**

**1) Install Dependancies**
--------------------------
- pip install discord.py
- pip install gpt4all
- pip install gpt4all[cuda]      # To fix library errors

**2) Run the bot**
--------------------------
- Replace token with your bot's token



**3) Usage**
--------------------------
 !chat < message >
- For single response message without previous context

 !chatc <context length(int)> < message > 
- Indicate the context length for the bot to load previous no of message into context.

 !clear
- To clear the bot

 !stop
-Stop the bot


**4) Examples**
--------------------------
  User: !chat What is the capital of France?
  Bot: The capital of France is Paris.
  
  User: !chatc 3 What is its population?
  Bot: The population of Paris is approximately 2.1 million people.
  
  User: !chatc 3 What is it known for?
  Bot: Paris is known for its art, fashion, culture, and iconic landmarks like the Eiffel Tower and the Louvre Museum.
  
  User: !chat Hello
  Bot: Hello! How can I assist you today?
  
  User: !chatc Hello
  Bot: Please provide a message. Usage: `!chatc <context_length> <message>`
  
  User: !clear
  Bot: Your chat context has been cleared.

  User: !stop
  Bot: Bot is stopping. Goodbye!
