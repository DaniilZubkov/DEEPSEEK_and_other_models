from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from keyboards import main_keyboard

import asyncio
from openai import OpenAI
import re
from db import Database



bot = Bot('')
dp = Dispatcher(storage=MemoryStorage())
db = Database('database.db')



# DEEPSEEK SETTINGS (Deepseek-r1 qwen 32b) and other models
deepseek_client = OpenAI(api_key="", base_url="https://openrouter.ai/api/v1")



system_prompt = """🤖✨ You are an expert multilingual AI assistant and developer with extensive experience. Follow these advanced guidelines:

 🌐 1. Language Processing (Intelligent Multilingual Handling) 🧠
     - 🔍 Perform 3-step language analysis:
       1️⃣ 1. Detect primary language using linguistic patterns 🕵️♂️
       2️⃣ 2. Identify secondary languages if code-mixing exceeds 30% 🌍
       3️⃣ 3. Recognize technical terms that should remain untranslated ⚙️
     - 📢 Response language mirroring:
       * 🎯 Match the user's primary language with 98% accuracy
       * 🔒 Preserve original terminology for: proper nouns, technical terms, cultural concepts
       * 🌈 For mixed input (e.g., Hinglish, Spanglish), maintain the dominant language base

 📝 2. Advanced Response Formatting (Structured & Precise) 🎨
     - 🗂 Apply hierarchical organization:
       • 🚀 **<concise 15-word summary>**
       • 📌 Supporting arguments (bullet points)
       • 💻 Examples (indented code blocks if technical)
       • 🌍 Cultural/localization notes (italic when relevant)
     - ⏱ Strict length management:
       * 📏 Real-time character count including Markdown (max 4096)
       * ✂️ Auto-truncation algorithm:
         - 🔄 Preserve complete sentences
         - 🎯 Prioritize core information
         - ➕ Add "[...]" if truncated
     - 🎭 Important style work (other Markdown and emojis):
       * 😊 Use 3-5 relevant emojis per response section
       * 🔀 Use different fonts (MARKDOWN + EMOJI combinations)

 💼 3. Specialized Content Handling ⚙️
     - 👨💻 Technical material:
       > 🔧 Maintain original English terms with localized explanations
       > 💻 Use ```code blocks``` for all commands/APIs
     - 🌏 Cultural adaptation:
       * 📏 Adjust measurements (metric/imperial)
       * 💰 Localize examples (currency, idioms)
       * 🚨 Recognize region-specific sensitivities

 ✅ 4. Quality Assurance Protocols 🔍
     - 🔄 Run pre-response checks:
       1. 📚 Language consistency validation
       2. 📊 Information density audit
       3. 🌐 Cultural appropriateness scan
     - 🧐 Post-generation review:
       * ✔️ Verify factual accuracy
       * 🎚 Ensure tone alignment (professional → friendly spectrum)
       * 📖 Confirm readability score >80%

 📤 Output template:
 🚩 **<Language-detected response>**
   • 🎯 Key point 1
   • 🔑 Key point 2
   - 📍 Supporting detail
   - 💡 Example/excerpt
 🌍 <cultural/localization note if relevant>



"""


allowed_models = {
    # DEEPSEEK family
    'Deepseek-R1': {
        'code': 'deepseek-r1',
        'api-key': 'API KEY',
    },
    'Deepseek-V3': {
        'code': 'deepseek-v3',
        'api-key': 'API KEY',
   },


   # GPT family
   'GPT-4 Turbo': {
        'code': 'gpt4-turbo',
        'api-key': 'API KEY',
   },
   'GPT-4.1': {
        'code': 'gpt4.1',
        'api-key': 'API KEY',
   },
   'GPT-4o': {
       'code': 'gpt4-o',
       'api-key': 'API KEY',
   },

   # MINI GPT`s family
   'GPT-4.1 Mini': {
       'code': 'gpt4.1-mini',
       'api-key': 'API KEY',
   },
   'GPT-4o Mini': {
       'code': 'gpt4-o-mini',
       'api-key': 'API KEY',
   },

   # CLAUDE family
   'Claude 3.7 Sonnet': {
       'code': 'claude3.7-sonnet',
       'api-key': 'API KEY',
   },
   'Claude 3.7 Sonnet (thinking)': {
       'code': 'claude3.7-sonnet-thinking',
       'api-key': 'API KEY',
   },

   # Open AI family
   'OpenAI o3': {
       'code': 'open-ai-o3',
       'api-key': 'API KEY',
   },
   'Open AI o4 Mini': {
       'code': 'open-ai-o4-mini',
       'api-key': 'API KEY',
   },


   # Gemini family
   'Gemini 2.0 Flash Lite': {
       'code': 'open-ai-o4-mini',
       'api-key': 'API KEY',
   },
}





def format_answer(answer: str) -> str:
    # Пример форматирования: разделение по пунктам
    return "\n\n".join(answer.split('\n'))

def clean_output(text):
    return re.sub(r'\\boxed\{([^}]*)\}', r'\1', text)


def clean_markdown(text: str) -> str:
    patterns = [
        # (r'```.*?\n(.*?)\n```', r'\1', re.DOTALL), можно убрать код (если нужно)
        # (r'`(.*?)`', r'\1'),
        (r'\*\*(.*?)\*\*', r'*\1*'),  # Жирный → корректный Markdown
        (r'^#+\s*(.+)$', r'*\1*', re.MULTILINE),  # Заголовки → жирный
    ]

    for pattern in patterns:
        if len(pattern) == 3:
            p, r, f = pattern
            text = re.sub(p, r, text, flags=f)
        else:
            p, r = pattern
            text = re.sub(p, r, text)

    return text












@dp.message(Command('start'))
async def start(message: Message):
    try:
        db.create_tables()
        black_photo_path = 'fotos/black_img.jpg'

        if (not db.user_exists(message.from_user.id)):
            db.add_user(message.from_user.id)
            db.set_nickname(message.from_user.id, message.from_user.username)
            db.set_signup(message.from_user.id, 'done')

        await message.answer_photo(photo=FSInputFile(black_photo_path),
                                   caption=f'Привет, {message.from_user.first_name}. Я AI ассистент в Telegram. У меня есть модели:\n\n'
                                           f'***Ты можешь выбрать удобную для себя модель по кнопке.*** 👇',
                                   parse_mode="MARKDOWN", reply_markup=main_keyboard())
    except Exception:
        pass





@dp.message()
async def get_message(message: Message):
    try:
        await message.answer(f'🛠️ ***Пожалуйста подождите, {db.get_model(message.from_user.id)} обрабатывает ваш запрос...***', parse_mode="MARKDOWN")

        completion = deepseek_client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-r1-distill-qwen-32b",
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
            presence_penalty=0.2,  # Поощряет новые темы
        )

        deepseek_answer = completion.choices[0].message.content

        print(deepseek_answer)
        print(clean_markdown(deepseek_answer))
        print(len(clean_output(clean_markdown(deepseek_answer))))

        new_deepseek_answer = clean_output(clean_markdown(deepseek_answer))

        # if '`' in new_deepseek_answer[0:2] and '`' in new_deepseek_answer[-3:-1]:
        #     if len([char for char in new_deepseek_answer]) >= 4096:
        #         while new_deepseek_answer:
        #             await message.answer(new_deepseek_answer[:4096], parse_mode='MARKDOWN')
        #             # удаление отправленной части текста
        #             new_deepseek_answer = new_deepseek_answer[4096:]
        #     await message.answer(new_deepseek_answer[2:-3], parse_mode='MARKDOWN')

        if len([char for char in new_deepseek_answer]) >= 4096:
            while new_deepseek_answer:
                await message.answer(new_deepseek_answer[:4096], parse_mode='MARKDOWN')
                # удаление отправленной части текста
                new_deepseek_answer = new_deepseek_answer[4096:]

        await message.answer(new_deepseek_answer, parse_mode='MARKDOWN')


    except Exception:
        pass



@dp.callback_query(lambda F: True)
async def change_model(message: Message, callback_query: types.CallbackQuery):
    black_photo_path = 'fotos/black_img.jpg'

    try:
        if callback_query.data == 'change_model':
            await message.delete()
            await message.answer_photo(photo=FSInputFile(black_photo_path),
                                       caption=f'Привет, {message.from_user.first_name}. Я AI ассистент в Telegram. У меня есть модели:\n\n'
                                               f'***Ты можешь выбрать удобную для себя модель по кнопке.*** 👇',
                                       parse_mode="MARKDOWN", reply_markup=main_keyboard())

    except Exception:
        pass





# POLLING
async def main():
    await dp.start_polling(bot)

if '__main__' == __name__:
    asyncio.run(main())