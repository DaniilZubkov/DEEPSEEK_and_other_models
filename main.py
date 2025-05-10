
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, FSInputFile

import asyncio
from openai import OpenAI



bot = Bot('YOUR BOT TOKEN')
dp = Dispatcher(storage=MemoryStorage())

# DEEPSEEK SETTINGS
deepseek_client = OpenAI(api_key="YOUR DEEPSEEK TOKEN", base_url="https://openrouter.ai/api/v1")
system_prompt = """You are a multilingual assistant. Follow these rules:
1. Language detection:
   - Automatically detect the user's language from their message
   - Respond in the same language as the user's message
   - If language is unclear, default to English
   - First analyze the user's message and identify its language
   - Then formulate your response strictly in that language
   - Maintain all formatting rules regardless of language
   - If user mixes languages, respond in the predominant language
   - Preserve important terms in their original language when necessary

2. Response format:
   - Use clear, concise language
   - Format lists with bullet points (•) or numbers
   - Separate key points with newlines
   - For long answers, add a short summary at the end

3. Special cases:
   - For code/technical terms, keep original English terms if needed
   - Maintain polite and professional tone in all languages
   - Adapt cultural references when appropriate
"""



def format_answer(answer: str) -> str:
    # Пример форматирования: разделение по пунктам
    return "\n\n".join(answer.split('\n'))






@dp.message(Command('start'))
async def start(message: Message):
    black_photo_path = 'fotos/black_img.jpg'

    await message.answer_photo(photo=FSInputFile(black_photo_path), caption=f'Привет, {message.from_user.first_name}. Я модель Deepseek в Телеграм.\n\n'
                               f'')



@dp.message()
async def get_message(message: Message):
    completion = deepseek_client.chat.completions.create(
        extra_body={},
        model="deepseek/deepseek-r1-zero:free",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": message.text
            }
        ],
        temperature=0.7,  # Контроль "креативности" (0–1)
        top_p=0.9,  # Влияет на разнообразие ответов
        frequency_penalty=0.2,  # Уменьшает повторения
        presence_penalty=0.2    # Поощряет новые темы
    )

    deepseek_answer = completion.choices[0].message.content
    print(deepseek_answer)

    await message.answer(f'{deepseek_answer}', parse_mode='MARKDOWN')







# POLLING
async def main():
    await dp.start_polling(bot)

if '__main__' == __name__:
    asyncio.run(main())