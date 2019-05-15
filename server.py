from flask import Flask, render_template, request, redirect, url_for
from wtforms import Form, StringField, TextAreaField, validators
import db
import random

my_flask_app = Flask(__name__)


# Сохраняем карточку в базу (по дефолту score = 0 и active = true)
def create_card(en_meaning, ru_meaning, example, extra_info):
    card = db.Card(en_meaning, ru_meaning, example, extra_info, 0, 'true')
    db.db_session.add(card)
    db.db_session.commit()


# Обновляем карточку
def update_card(card, en_meaning, ru_meaning, example, extra_info):
    card.en_meaning = en_meaning
    card.ru_meaning = ru_meaning
    card.example = example
    card.extra_info = extra_info
    db.db_session.commit()


# Обновляем score карточки в зависимости от нажатой на странице тренировки кнопки
def update_score(card):
    training_score = {'know': 1, 'not-sure': 0, 'dont-know': -1}[request.form['score-button']]   
    card.score = card.score + int(training_score)
    db.db_session.commit()
    return card.score


# Удаляем карточку из базы
def delete_card(card):
    db.db_session.delete(card)
    db.db_session.commit()


# Выбираем случайный id карточки из всех имеющихся
def random_card():
    #query = db.db_session.query(db.Card)
    card_all_ids = db.db_session.query(db.Card).count()
    rand_card_id = random.randint(1, card_all_ids)
    rand_card = db.db_session.query(db.Card).get(rand_card_id)
    return rand_card


# Выбираем карточку с наименьшим score с возможность указать, какие карточки не показывать следом
def choose_low_score_card(exclude=None):
    query = db.db_session.query(db.Card)
    if exclude:
        query = query.filter(db.Card.id.notin_(exclude))
    return query.order_by(db.Card.score).first()


class CreateCardForm(Form):
    en_meaning = StringField(
        'Английское слово:', [validators.InputRequired(message='Не может быть пустым'), validators.Length(max=500, message='Не может быть длиннее 500 символов')]
        )
    ru_meaning = StringField(
        'Русский перевод:', [validators.Length(max=500, message='Не может быть длиннее 500 символов')]
        )
    example = TextAreaField(
        'Пример:', [validators.Length(max=500, message='Не может быть длиннее 500 символов')]
        )
    extra_info = TextAreaField(
        'Дополнительная информация:', [validators.Length(max=500, message='Не может быть длиннее 500 символов')]
        )


# Главная страница
@my_flask_app.route('/')
def index():
    return render_template(
        'index.html', title="Карточки для изучения иностранного языка"
        )


# Страница создания новой карточки
@my_flask_app.route('/new/', methods=['GET', 'POST'])
def new_card():
    form = CreateCardForm(request.form)

    if request.method == 'POST' and form.validate():
        # Получаем данные из полей формы
        en_meaning = str(request.form.get('en_meaning')).strip()
        ru_meaning = str(request.form.get('ru_meaning'))
        example = str(request.form.get('example'))
        extra_info = str(request.form.get('extra_info'))

        # Проверяем на наличие в базе карточки с таким же en_meaning
        if db.Card.query.filter(db.Card.en_meaning == en_meaning).first():
            return 'Такая карточка уже есть'

        # Добавление в базу новой карточки    
        create_card(en_meaning, ru_meaning, example, extra_info)

        # После отправки формы показываем листинг всех карточек
        return redirect(url_for('all_cards'))

    return render_template(
        'new_card.html', 
        form=form, 
        title="Создание новой карточки", 
        nav_link_1=url_for('all_cards'), 
        nav_link_2="/training/", 
        nav_link_1_name="Все карточки", 
        nav_link_2_name="Тренировка"
        )


# Страница просмотра карточки
@my_flask_app.route('/card/<int:card_id>', methods=['GET', 'POST'])
def view_card(card_id):
    card = db.db_session.query(db.Card).get(card_id)
    form = CreateCardForm(request.form, card)
    return render_template(
        'view_card.html', 
        form=form, 
        title="Просмотр карточки", 
        nav_link_1="/new/", 
        nav_link_2="/cards/", 
        nav_link_3="/training/", 
        nav_link_1_name="Создание новой карточки", 
        nav_link_2_name="Все карточки", 
        nav_link_3_name="Тренировка",
        # выводим конкретную карточку по id
        card=card
        )


# Страница редактирования карточки
@my_flask_app.route('/card/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    card = db.db_session.query(db.Card).get(card_id)
    form = CreateCardForm(request.form, card)

    if request.method == 'POST' and form.validate():
        # Получаем данные из полей формы
        en_meaning = str(request.form.get('en_meaning')).strip()
        ru_meaning = str(request.form.get('ru_meaning'))
        example = str(request.form.get('example'))
        extra_info = str(request.form.get('extra_info'))

        # Проверяем на наличие в базе карточки с таким же en_meaning
        if db.Card.query.filter(
                db.Card.en_meaning == en_meaning,
                db.Card.id != card.id,
                                ).first():
            return 'Такая карточка уже есть'
        # Добавление в базу новой карточки   
        update_card(card, en_meaning, ru_meaning, example, extra_info)
        # После отправки формы показываем листинг всех карточек
        return redirect(url_for('all_cards'))

    return render_template(
        'edit_card.html', 
        form=form, 
        title="Редактирование карточки", 
        nav_link_1="/new/", 
        nav_link_2="/cards/", 
        nav_link_3="/training/", 
        nav_link_1_name="Создание новой карточки", 
        nav_link_2_name="Все карточки", 
        nav_link_3_name="Тренировка",
        # выводим конкретную карточку по id
        card=card
        ) 


# Листинг всех карточек
@my_flask_app.route('/cards/', methods=['GET'])
def all_cards():
    print(db.db_session.query(db.Card))
    return render_template(
        'all_cards.html', 
        title="Все карточки", 
        nav_link_1="/new/", 
        nav_link_2="/training/", 
        nav_link_1_name="Создание новой карточки", 
        nav_link_2_name="Тренировка",
        cards=db.db_session.query(db.Card).all()
        )


# Страница удаления карточки
@my_flask_app.route('/card/<int:card_id>/delete/', methods=['POST'])
def del_card(card_id):
    card = db.db_session.query(db.Card).get(card_id)
    delete_card(card) 
    return redirect(url_for('all_cards'))   


# Страница тренировки
@my_flask_app.route('/training/', methods=['GET', 'POST'])
def training():
    # Если пользователь пришел сюда нажав одну из кнопок
    if request.method == 'POST':
        # то из скрытого поля нам приходит 'card-id' той карточки
        # на которую он сейчас отвечает, и мы ее можем исключить
        # из выдачи
        # и в зависимости от того, какую он кнопку нажал нам приходет
        # сответствующий 'score-button'
        current_card = db.db_session.query(db.Card).get(int(request.form['card-id']))
        update_score(current_card)

        card = choose_low_score_card(exclude=[current_card.id])

    else:
        # Иначе пользователь просто нажал на кнопку тренировки
        # и мы ему выдаем самую сложную карту
        card = choose_low_score_card()
    return render_template(
        'training.html', 
        title="Тренировка", 
        nav_link_1="/new/", 
        nav_link_2="/cards/", 
        nav_link_1_name="Создание новой карточки", 
        nav_link_2_name="Все карточки",
        card=card
        )
      

if __name__ == "__main__":
    my_flask_app.run(debug=True)   
