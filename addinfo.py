import sqlite3


def create_database():
    """Создает базу данных и необходимые таблицы"""
    # Подключаемся к базе данных (если файл базы данных не существует, он будет создан)
    conn = sqlite3.connect("theater.db")
    cursor = conn.cursor()

    # Создаем таблицу спектаклей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

    # Создаем таблицу временных слотов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            play_name TEXT NOT NULL,
            date DATE NOT NULL,
            start_time TEXT NOT NULL,  -- Используем TEXT для времени (HH:MM)
            duration INTEGER,  -- длительность в минутах
            FOREIGN KEY (play_name) REFERENCES plays(name)
        )
    """)

    # Создаем таблицу зон (мест в театре)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            play_name TEXT NOT NULL,
            date DATE NOT NULL,
            zone_name TEXT NOT NULL,
            available_tickets INTEGER NOT NULL,  -- количество доступных билетов
            FOREIGN KEY (play_name) REFERENCES plays(name)
        )
    """)

    # Создаем таблицу заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            play_name TEXT NOT NULL,
            date DATE NOT NULL,
            zone_name TEXT NOT NULL,
            ticket_count INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (play_name) REFERENCES plays(name),
            FOREIGN KEY (zone_name) REFERENCES zones(zone_name)
        )
    """)

    # Вставляем тестовые данные для спектаклей
    cursor.execute("INSERT INTO plays (name, description) VALUES ('Гамлет', 'Трагедия Шекспира о датском принце')")
    cursor.execute(
        "INSERT INTO plays (name, description) VALUES ('Ромео и Джульетта', 'Романтическая трагедия о любви и трагедии двух влюбленных')")
    cursor.execute(
        "INSERT INTO plays (name, description) VALUES ('Три сестры', 'Драма Чехова о трех сестрах, мечтающих уехать в Москву')")
    cursor.execute(
        "INSERT INTO plays (name, description) VALUES ('Макбет', 'Трагедия Шекспира о амбициозном лорде Макбете')")
    cursor.execute(
        "INSERT INTO plays (name, description) VALUES ('Отелло', 'Трагедия Шекспира о ревности и манипуляциях')")
    cursor.execute(
        "INSERT INTO plays (name, description) VALUES ('Король Лир', 'Трагедия о старом короле, который делит свое королевство между дочерьми')")

    # Вставляем временные слоты для спектаклей (по несколько спектаклей на одну дату)
    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Гамлет', '2024-11-20', '19:00', 150)")
    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Ромео и Джульетта', '2024-11-20', '21:30', 120)")

    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Три сестры', '2024-11-21', '18:00', 130)")
    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Макбет', '2024-11-21', '20:30', 140)")

    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Отелло', '2024-11-22', '19:00', 135)")
    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Король Лир', '2024-11-22', '21:00', 160)")

    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Гамлет', '2024-11-23', '18:30', 150)")
    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Ромео и Джульетта', '2024-11-23', '20:45', 120)")

    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Макбет', '2024-11-24', '19:15', 140)")
    cursor.execute(
        "INSERT INTO showtimes (play_name, date, start_time, duration) VALUES ('Отелло', '2024-11-24', '21:00', 130)")

    # Вставляем зоны и количество доступных билетов (разные зоны для каждого спектакля)
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Гамлет', '2024-11-20', 'Партер', 50)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Гамлет', '2024-11-20', 'Балкон', 30)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Ромео и Джульетта', '2024-11-20', 'Партер', 40)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Ромео и Джульетта', '2024-11-20', 'Балкон', 25)")

    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Три сестры', '2024-11-21', 'Партер', 35)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Три сестры', '2024-11-21', 'Балкон', 20)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Макбет', '2024-11-21', 'Партер', 60)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Макбет', '2024-11-21', 'Балкон', 40)")

    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Отелло', '2024-11-22', 'Партер', 55)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Отелло', '2024-11-22', 'Балкон', 30)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Король Лир', '2024-11-22', 'Партер', 50)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Король Лир', '2024-11-22', 'Балкон', 25)")

    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Гамлет', '2024-11-23', 'Партер', 55)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Гамлет', '2024-11-23', 'Балкон', 35)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Ромео и Джульетта', '2024-11-23', 'Партер', 40)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Ромео и Джульетта', '2024-11-23', 'Балкон', 30)")

    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Макбет', '2024-11-24', 'Партер', 60)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Макбет', '2024-11-24', 'Балкон', 40)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Отелло', '2024-11-24', 'Партер', 50)")
    cursor.execute(
        "INSERT INTO zones (play_name, date, zone_name, available_tickets) VALUES ('Отелло', '2024-11-24', 'Балкон', 30)")

    # Вставляем несколько заказов
    cursor.execute(
        "INSERT INTO orders (email, play_name, date, zone_name, ticket_count) VALUES ('example@example.com', 'Гамлет', '2024-11-20', 'Партер', 2)")
    cursor.execute(
        "INSERT INTO orders (email, play_name, date, zone_name, ticket_count) VALUES ('user@domain.com', 'Ромео и Джульетта', '2024-11-20', 'Балкон', 3)")

    # Подтверждаем изменения и закрываем соединение
    conn.commit()
    conn.close()

    print("База данных создана и заполнена тестовыми данными.")


if __name__ == "__main__":
    create_database()
