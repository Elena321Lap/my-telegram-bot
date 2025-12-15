# happy_bot.py - ТЕЛЕГРАМ БОТ ДЛЯ ХОРОШЕГО НАСТРОЕНИЯ
import asyncio
import logging
import random
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ========== НАСТРОЙКИ ==========
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8592759117:AAGu1MWM_RC9Gs1iK0JrNx61jjMxe1TIQyA"

if TELEGRAM_TOKEN == "ВАШ_TELEGRAM_ТОКЕН_ЗДЕСЬ":
    print("❌ ОШИБКА: Замените TELEGRAM_TOKEN на свой токен от @BotFather!")
    exit(1)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="🎭 Настроение?")],
        [KeyboardButton(text="😂 Шутка")],
        [KeyboardButton(text="🖼️ Картинка")],
        [KeyboardButton(text="💬 Мотивация")],
        [KeyboardButton(text="🎮 Для мужиков")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_mood_keyboard():
    buttons = [
        [KeyboardButton(text="Грустно"), KeyboardButton(text="Скучно")],
        [KeyboardButton(text="Устал"), KeyboardButton(text="Злюсь")],
        [KeyboardButton(text="Рад"), KeyboardButton(text="Нормально")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ========== БАЗА ДАННЫХ ШУТОК ==========
class FunnyDatabase:
    def __init__(self):
        self.jokes = [
            "😆 Мужик в аптеке: 'Дайте что-нибудь от головы'. Фармацевт: 'Таблетки'. Мужик: 'Нет, что-нибудь более радикальное. Молоток, например!'",
            "🤣 Встретились два друга. Один: 'У меня жена как кошка — днём спит, ночью гуляет'. Второй: 'А у меня как собака — целый день лает!'",
            "😂 Философ заказывал жене торт. Сказал: 'Напишите сверху: Ты не стареешь, снизу: Ты становишься лучше!' В итоге на торте: 'Ты не стареешь сверху, ты становишься лучше снизу!'"
        ]
        
        self.motivations = [
            "🚀 Ты круче, чем думаешь! Мозг просто забывает тебе это говорить.",
            "💪 Каждый день — новая страница. Напиши там что-то крутое!",
            "✨ Даже самая тёмная ночь заканчивается рассветом."
        ]
        
        # ИСПОЛЬЗУЕМ ТВОИ КАРТИНКИ
        self.local_images = [
            "images/actor.jpg.jpg",        # Актер
            "images/heppiness.jpg.jpg",    # Счастье (с опечаткой heppiness)
            "images/rat.jpg.jpg",          # Крыса
            "images/sea.jpg.jpg",          # Море
            "images/strong.jpg.jpg",       # Сила
            "images/together.jpg.jpg"      # Вместе
        ]
        
        self.available_images = []
        for img in self.local_images:
            if os.path.exists(img):
                self.available_images.append(img)
            else:
                print(f"⚠️ Файл не найден: {img}")
        
        if not self.available_images:
            print("⚠️ Используем онлайн картинки")
            self.available_images = [
                "https://cataas.com/cat",
                "https://placekitten.com/400/400"
            ]
        else:
            print(f"✅ Найдено {len(self.available_images)} картинок")
        
        # ДЛЯ УМНОГО ВЫБОРА КАРТИНОК
        self.image_index = 0
        self.shuffled_images = []
        self._shuffle_images()  # Первоначальное перемешивание
        
        self.guy_jokes = [
            "🍻 Мужик заходит в бар... и выходит через 3 часа, потому что вспомнил про жену.",
            "🛠️ Гараж: 1% для машины, 99% для 'вещей, которые пригодятся'."
        ]
        
        self.mood_responses = {
            "Грустно": ["Не грусти! А то писька не будет рости! ☁️"],
            "Скучно": ["Скучно? Завари скорее чай выпей с медом, не скучай! 📸"],
            "Устал": ["Устал? Отдохни, что может быть проще, ты же не робот! 🤖"],
            "Злюсь": ["Злишься? Злиться низя, приду покусаю! "],
            "Рад": ["Ура! Хороший маоьчик! 🍬"],
            "Нормально": ["Спорим ты не сможешь с открытым ртом сказать ТОРТ! 🎪"]
        }
    
    def _shuffle_images(self):
        """Перемешивает картинки и сбрасывает индекс"""
        if self.available_images:
            self.shuffled_images = self.available_images.copy()
            random.shuffle(self.shuffled_images)
            self.image_index = 0
    
    def get_joke(self): 
        return random.choice(self.jokes)
    
    def get_motivation(self): 
        return random.choice(self.motivations)
    
    def get_image_path(self):
        """Умный выбор картинки: показывает все по одному разу, затем перемешивает заново"""
        if not self.available_images:
            return None
        
        # Если мы показали все картинки из текущей перемешанной копии
        if self.image_index >= len(self.shuffled_images):
            self._shuffle_images()  # Перемешиваем заново
        
        # Берем следующую картинку
        image = self.shuffled_images[self.image_index]
        self.image_index += 1
        
        # Для отладки (можно удалить)
        print(f"📸 Отправляю картинку: {os.path.basename(image)} (№{self.image_index}/{len(self.shuffled_images)})")
        
        return image
    
    def get_guy_joke(self): 
        return random.choice(self.guy_jokes)
    
    def get_mood_response(self, mood): 
        return random.choice(self.mood_responses.get(mood, ["Улыбнись! 😊"]))

db = FunnyDatabase()

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = f"""🤖 Привет, {message.from_user.first_name}!
Я — бот против грусти! Выбирай что хочешь:"""
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Жми кнопки или пиши что чувствуешь!", reply_markup=get_main_keyboard())

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@dp.message(lambda m: m.text == "🎭 Настроение?")
async def ask_mood(message: Message):
    await message.answer("Какое у тебя настроение?", reply_markup=get_mood_keyboard())

@dp.message(lambda m: m.text in ["Грустно", "Скучно", "Устал", "Злюсь", "Рад", "Нормально"])
async def handle_mood(message: Message):
    response = db.get_mood_response(message.text)
    await message.answer(response, reply_markup=get_main_keyboard())

@dp.message(lambda m: m.text == "😂 Шутка")
async def send_joke(message: Message):
    await message.answer(db.get_joke(), reply_markup=get_main_keyboard())

@dp.message(lambda m: m.text == "💬 Мотивация")
async def send_motivation(message: Message):
    await message.answer(db.get_motivation(), reply_markup=get_main_keyboard())

@dp.message(lambda m: m.text == "🎮 Для мужиков")
async def send_guy_joke(message: Message):
    await message.answer(db.get_guy_joke(), reply_markup=get_main_keyboard())

@dp.message(lambda m: m.text == "🔙 Назад")
async def go_back(message: Message):
    await message.answer("Возвращаемся!", reply_markup=get_main_keyboard())

@dp.message(lambda m: m.text == "🖼️ Картинка")
async def send_meme(message: Message):
    await message.answer("🖼️ Ищу картинку...")
    
    try:
        image_source = db.get_image_path()
        
        if not image_source:
            await message.answer("Картинки нет! Но вот шутка:\n" + db.get_joke(), reply_markup=get_main_keyboard())
            return
        
        if image_source.startswith("http"):
            await message.answer_photo(image_source, caption="😄 Держи!")
        else:
            if os.path.exists(image_source):
                with open(image_source, 'rb') as f:
                    photo = BufferedInputFile(f.read(), filename=image_source)
                    await message.answer_photo(photo, caption="😄 Держи!")
            else:
                await message.answer("Файл не найден! Шутка:\n" + db.get_joke(), reply_markup=get_main_keyboard())
        
        await message.answer("Ещё что-нибудь?", reply_markup=get_main_keyboard())
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await message.answer("Ошибка! Но вот шутка:\n" + db.get_joke(), reply_markup=get_main_keyboard())

@dp.message()
async def handle_text(message: Message):
    text = message.text.lower()
    
    if len(text) < 3:
        await message.answer("Напиши что-нибудь ещё! 😊", reply_markup=get_main_keyboard())
        return
    
    if any(word in text for word in ["привет", "хай"]):
        await message.answer(f"Привет, {message.from_user.first_name}! Как настроение? 😊", reply_markup=get_main_keyboard())
    elif any(word in text for word in ["шутк", "анекдот"]):
        await message.answer(db.get_joke(), reply_markup=get_main_keyboard())
    elif any(word in text for word in ["картинк", "мем"]):
        await send_meme(message)
    elif any(word in text for word in ["груст", "плохо"]):
        await message.answer(db.get_mood_response("Грустно"), reply_markup=get_main_keyboard())
    elif any(word in text for word in ["скучн"]):
        await message.answer(db.get_mood_response("Скучно"), reply_markup=get_main_keyboard())
    elif any(word in text for word in ["уста"]):
        await message.answer(db.get_mood_response("Устал"), reply_markup=get_main_keyboard())
    else:
        await message.answer("Понял тебя! 😊", reply_markup=get_main_keyboard())

# ========== ЗАПУСК БОТА ==========
async def main():
    print("=" * 50)
    print("🤖 ЗАПУСК БОТА")
    print("=" * 50)
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("✅ Бот запущен!")
    print("⏳ Жду сообщений...")
    print("=" * 50)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")