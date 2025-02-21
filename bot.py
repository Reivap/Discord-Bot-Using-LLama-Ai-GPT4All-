import discord
from discord.ext import commands
from gpt4all import GPT4All
import asyncio
import logging
from collections import defaultdict, deque

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GPT4All model (asynchronously to avoid blocking)
model = None
async def load_model():
    global model
    try:
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")  # Replace with your model path
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise  # Re-raise the exception to stop the bot if the model fails to load

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Rate limiting: Track user command usage
user_cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)  # 1 command per 60 seconds per user

# Contextual memory: Store chat context for each user/channel
user_context = defaultdict(lambda: deque(maxlen=5))  # Stores the last 5 messages per user

@bot.event
async def on_ready():
    logger.info(f'Bot is ready. Logged in as {bot.user.name}')
    await load_model()  # Load the model asynchronously

async def update_progress(message: discord.Message, progress: int):
    """
    Update the progress percentage in the original message.
    """
    try:
        await message.edit(content=f"Processing... {progress}%")
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

@bot.command(name='chat')
async def chat(ctx, *, message: str):
    """
    Generate a response without context.
    Usage: !chat <message>
    Example: !chat Hello
    """
    try:


        # Check if the model is loaded
        if not model:
            await ctx.send("The AI model is not ready. Please try again later.")
            return

        # Send a "Processing..." message
        progress_message = await ctx.send("Processing... 0%")

        # Generate a response without context
        with model.chat_session():
            response = ""
            progress_steps = [25, 50, 75, 100]
            for progress in progress_steps:
                await asyncio.sleep(1)  # Adjust the delay to control the speed of progress
                await update_progress(progress_message, progress)
            response = model.generate(message, max_tokens=2048)
        
        # Send the final response
        await progress_message.edit(content=response)
    except Exception as e:
        logger.error(f"Error in chat command: {e}")
        await ctx.send(f"An error occurred: {e}")

@bot.command(name='chatc')
async def chatc(ctx, context_length: int = 3, *, message: str = None):
    """
    Generate a response with context.
    Usage: !chatc <context_length> <message>
    Example: !chatc 5 Hello
    """
    try:
        # Check if the message is provided
        if message is None:
            await ctx.send("Please provide a message. Usage: `!chatc <context_length> <message>`")
            return

        # Rate limiting
        bucket = user_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"Please wait {retry_after:.1f} seconds before using this command again.")
            return

        # Check if the model is loaded
        if not model:
            await ctx.send("The AI model is not ready. Please try again later.")
            return

        # Send a "Processing..." message
        progress_message = await ctx.send("Processing... 0%")

        # Get the user's context
        user_id = ctx.author.id
        context = user_context[user_id]

        # Add the new message to the context
        context.append(f"You: {message}")

        # Prepare the context for the model
        context_str = "\n".join(list(context)[-context_length:])  # Use only the last N messages
        prompt = f"{context_str}\nAI:"

        # Generate a response using the GPT4All model
        with model.chat_session():
            response = ""
            progress_steps = [25, 50, 75, 100]
            for progress in progress_steps:
                await asyncio.sleep(1)  # Adjust the delay to control the speed of progress
                await update_progress(progress_message, progress)
                response = model.generate(prompt, max_tokens=2048)
        
        # Add the AI's response to the context
        context.append(f"AI: {response}")

        # Send the final response
        await progress_message.edit(content=response)
    except Exception as e:
        logger.error(f"Error in chatc command: {e}")
        await ctx.send(f"An error occurred: {e}")

@bot.command(name='clear')
async def clear(ctx):
    """Clear your chat context."""
    try:
        user_id = ctx.author.id
        if user_id in user_context:
            user_context[user_id].clear()
            await ctx.send("Your chat context has been cleared.")
        else:
            await ctx.send("You have no chat context to clear.")
    except Exception as e:
        logger.error(f"Error in clear command: {e}")
        await ctx.send(f"An error occurred: {e}")

@bot.command(name='stop')
async def stop(ctx):
    """Stop the bot gracefully."""
    try:
        logger.info("Bot is stopping...")
        await ctx.send("Bot is stopping. Goodbye!")
        await bot.close()
    except Exception as e:
        logger.error(f"Error in stop command: {e}")
        await ctx.send(f"An error occurred: {e}")

# Run the bot
if __name__ == "__main__":
    bot.run('Enter_BOT_TOKEN')  # Replace with your bot token