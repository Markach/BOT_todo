from datetime import datetime
from threading import Thread
import telebot
import schedule
import time 
from models import User, Todo

bot = telebot.TeleBot('   api token   ')

# /start 
@bot.message_handler(commands=['start'])
def start_handler(message):        # проверка что пользователя нет в БД
    if not User.select().where(User.chat_id == message.chat.id):
        User.create(chat_id=message.chat.id)   # id пользователя буду сохранять в базе данных
    bot.send_message(
        message.chat.id,
        f"Hello {message.chat.first_name} {message.chat.last_name or ''}!"
    )

# функция генерации сообщения с незавершенными задачами 
def create_all_todo_message(chat_id):
    user = User.get(User.chat_id == chat_id)
    todos = Todo.select().where(Todo.user == user,
                                Todo.date == datetime.today())
    message_text = []

    for todo in todos:
        if todo.is_done:  # сообщения отредактированы таким образом, чтобы мы видели какие todo уже закончены
            message_text.append(f"<b><s>{todo.id}. {todo.task}</s></b>\n")
        else:
            message_text.append(f"<b>{todo.id}. {todo.task}</b>\n")
    return "".join(message_text)

# вывод всех todo на текущий день
@bot.message_handler(commands=['today', 't'])
def get_todo_list(message):

    bot.send_message(
        message.chat.id,
        create_all_todo_message(message.chat.id),
        parse_mode='HTML'
    )

# хендлер помечает что задача сделана
@bot.message_handler(regexp="\d+ done")
def make_done(message):
    todo_id = message.text.split(' ')[0]  # проверяю какой id  у todo
    todo = Todo.get(Todo.id == todo_id)   # достаю это id и сохраняю
    todo.is_done = True
    todo.save()

    bot.send_message(
        message.chat.id,
        f"{todo.task} is done now"
    )

# когда пишу текст отрабатывает этот хендлер
@bot.message_handler(content_types=['text'])
def create_todo_handler(message):
    user = User.get(User.chat_id == message.chat.id)  # беру id пользователя .get()
    Todo.create(              # создаю todo на текущий день
        task=message.text,
        is_done=False,
        user=user,
        date=datetime.today()
    )
    bot.send_message(
        message.chat.id,
        "Your todo was saved!"    # говорю пользователю что todo сохранен
    )

# функция берет всех пользователей и проверяет есть ли у них незавершенные дела
def check_notify():
    for user in User.select():
        todos = Todo.select().where(Todo.user == user,
                                    Todo.date == datetime.today(),
                                    Todo.is_done == False) # ищем для текущего пользователя только незавершенные, если нет - не отправляем сообщение
        if todos:  # если есть todo, отправляю пользователю сообщение
            bot.send_message(
                user.chat_id,
                create_all_todo_message(user.chat_id),
                parse_mode='HTML'
            )


def run_scheduler():
    schedule.every(1).hours.do(check_notify)  # напоминание каждый час
    while True:              # для работы schedule используется цикл while True, а у нас уже есть бесконечный цикл polling()
        schedule.run_pending()  # можно использовать Thread для разграничения потоков
        time.sleep(1)

  
if __name__ == "__main__":
    Thread(target=run_scheduler).start()
    bot.infinity_polling()