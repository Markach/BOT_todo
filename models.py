from peewee import SqliteDatabase, Model, CharField, DateField, ForeignKeyField, BooleanField


db = SqliteDatabase('bot.sqlite3')  # создала БД


class User(Model):
    chat_id = CharField()   # создала первое поле

    class Meta:          # это управляющий класс, класс который управляет классом
        database = db


class Todo(Model):           
    task = CharField()                # первое поле задача
    is_done = BooleanField()         # закончена ли она
    date = DateField()               # на какой день делается
    user = ForeignKeyField(User)       # поле пользователь

    class Meta:
        database = db


if __name__ == '__main__':         # когда запускается файл, он выполняется в main потоке, есть переменная name, она в каждом
    db.create_tables([User, Todo])  # файле, содержит имя потока, и если мы запустили файл руками и имя этого потока main, тогда код выполнится, если я буду просто import этого файла
                                   # база данных не создастся
  