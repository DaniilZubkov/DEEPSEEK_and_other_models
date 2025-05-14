from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode

import asyncio
from openai import OpenAI
import re



bot = Bot('')
dp = Dispatcher(storage=MemoryStorage())

# DEEPSEEK SETTINGS (Deepseek-r1-zero:free)
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




def format_answer(answer: str) -> str:
    # Пример форматирования: разделение по пунктам
    return "\n\n".join(answer.split('\n'))

def clean_output(text):
    return re.sub(r'\\boxed\{([^}]*)\}', r'\1', text)


def clean_markdown(text: str) -> str:
    patterns = [
        # (r'```.*?\n(.*?)\n```', r'\1', re.DOTALL),
        (r'`(.*?)`', r'\1'),
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


# def adaptive_context_window(task_type):
#     config = {
#         'code': {'max_length': 4096, 'rope_theta': 1e6},
#         'text': {'max_length': 2048, 'rope_theta': 1e4},
#         'math': {'max_length': 1024, 'rope_theta': 1e5}
#     }
#     return config[task_type]










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
        presence_penalty=0.2,    # Поощряет новые темы
    )

    deepseek_answer = completion.choices[0].message.content

    print(deepseek_answer)
    print(clean_markdown(deepseek_answer))
    print(len(clean_output(clean_markdown(deepseek_answer))))

    new_deepseek_answer = clean_output(clean_markdown(deepseek_answer))


    if '`' in new_deepseek_answer[0:2] and '`' in new_deepseek_answer[-3:-1]:
        if len([char for char in new_deepseek_answer]) >= 4096:
            while new_deepseek_answer:
                await message.answer(new_deepseek_answer[:4096], parse_mode='MARKDOWN')
                # удаление отправленной части текста
                new_deepseek_answer = new_deepseek_answer[4096:]
        await message.answer(new_deepseek_answer[2:-3], parse_mode='MARKDOWN')

    if len([char for char in new_deepseek_answer]) >= 4096:
        while new_deepseek_answer:
            await message.answer(new_deepseek_answer[:4096], parse_mode='MARKDOWN')
            # удаление отправленной части текста
            new_deepseek_answer = new_deepseek_answer[4096:]

    await message.answer(new_deepseek_answer, parse_mode='MARKDOWN')







# POLLING
async def main():
    await dp.start_polling(bot)

if '__main__' == __name__:
    asyncio.run(main())