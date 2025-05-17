from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['My_english']
word_trainer = db['word_trainer']
lessons_collection = word_trainer['lessons']
words_collection = word_trainer['words']

def get_lessons():
    try:
        lessons = list(lessons_collection.find())
        lessons.sort(key=lambda x: (0 if x['name'] == 'Головний' else 1, x.get('created_at', datetime.now())))
        return lessons
    except Exception as e:
        print(f"Помилка при отриманні уроків: {e}")
        return []

def load_words(lesson_name=None, show_learned=False):
    try:
        words = {}
        
        if lesson_name is None or lesson_name == "Всі уроки":
            # Завантажуємо всі слова
            query = {"learned": True if show_learned else False}
        else:
            # Завантажуємо слова тільки з вказаного уроку
            query = {
                "lesson": lesson_name,
                "learned": True if show_learned else False
            }
            
        cursor = words_collection.find(query)
        
        for word in cursor:
            words[word['english']] = {
                "translation": word['ukrainian'],
                "learned": word.get('learned', False),
                "lesson": word.get('lesson', 'Головний')
            }
                
        return words
    except Exception as e:
        print(f"Помилка при завантаженні слів: {e}")
        return {}

def save_word(english, ukrainian, lesson_name):
    try:
        print(f"Спроба зберегти слово: {english} - {ukrainian} в урок {lesson_name}")
        existing_word = words_collection.find_one({
            'english': english,
            'lesson': lesson_name
        })
        if existing_word:
            print(f"Слово {english} вже існує в уроці {lesson_name}")
            return False
        result = words_collection.insert_one({
            'english': english,
            'ukrainian': ukrainian,
            'learned': False,
            'lesson': lesson_name
        })
        print(f"Результат збереження слова: {result.acknowledged}")
        return result.acknowledged
    except Exception as e:
        print(f"Помилка при збереженні слова: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_lesson(lesson_name, description=""):
    try:
        print(f"Спроба створити урок: {lesson_name}")
        if not lessons_collection.find_one({"name": lesson_name}):
            result = lessons_collection.insert_one({
                "name": lesson_name,
                "description": description,
                "created_at": datetime.now()
            })
            print(f"Результат створення уроку: {result.acknowledged}")
            return result.acknowledged
        else:
            print(f"Урок з назвою {lesson_name} вже існує")
        return False
    except Exception as e:
        print(f"Помилка при створенні уроку: {e}")
        import traceback
        traceback.print_exc()
        return False

def rename_lesson(old_name, new_name):
    try:
        if old_name == new_name:
            return True
        if not lessons_collection.find_one({"name": new_name}):
            lessons_collection.update_one(
                {"name": old_name},
                {"$set": {"name": new_name}}
            )
            words_collection.update_many(
                {"lesson": old_name},
                {"$set": {"lesson": new_name}}
            )
            return True
        return False
    except Exception as e:
        print(f"Помилка при перейменуванні уроку: {e}")
        return False

def toggle_word_learned(english):
    """Змінює статус вивчення слова."""
    try:
        # Знаходимо слово
        word = words_collection.find_one({'english': english})
        if word:
            # Отримуємо поточний статус
            current_status = word.get('learned', False)
            # Змінюємо статус на протилежний
            result = words_collection.update_one(
                {'english': english},
                {'$set': {'learned': not current_status}}
            )
            # Перевіряємо, чи оновлення було успішним
            return result.modified_count > 0
        return False
    except Exception as e:
        print(f"Помилка при зміні статусу слова: {e}")
        return False

def save_words(words_dict):
    """Зберігає словник слів у базу даних."""
    try:
        # Очищаємо колекцію слів
        words_collection.delete_many({})
        
        # Додаємо нові слова
        for en_word, details in words_dict.items():
            words_collection.insert_one({
                'english': en_word,
                'ukrainian': details['translation'],
                'learned': details.get('learned', False),
                'lesson': details.get('lesson', 'Головний')
            })
        return True
    except Exception as e:
        print(f"Помилка при збереженні слів: {e}")
        return False 

def update_word(old_english, new_english, new_ukrainian, lesson_name):
    """Оновлює існуюче слово в базі даних."""
    try:
        # Знаходимо слово
        word = words_collection.find_one({'english': old_english})
        if word:
            # Зберігаємо поточний статус вивчення
            current_learned_status = word.get('learned', False)
            
            # Якщо змінилося англійське слово, перевіряємо, чи нове слово вже існує
            if old_english != new_english:
                existing_word = words_collection.find_one({
                    'english': new_english,
                    'lesson': lesson_name
                })
                if existing_word:
                    return False  # Слово з такою назвою вже існує
            
            # Оновлюємо слово
            result = words_collection.update_one(
                {'english': old_english},
                {'$set': {
                    'english': new_english,
                    'ukrainian': new_ukrainian,
                    'lesson': lesson_name,
                    'learned': current_learned_status
                }}
            )
            
            # Перевіряємо, чи оновлення було успішним
            return result.modified_count > 0
        return False
    except Exception as e:
        print(f"Помилка при оновленні слова: {e}")
        return False