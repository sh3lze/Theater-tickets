import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton, QSpinBox, QLineEdit, \
    QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import re


class TicketBookingApp(QWidget):
    def __init__(self):
        super().__init__()

        # Подключаемся к базе данных
        self.conn = sqlite3.connect("theater.db")
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Театр AKA Макса")
        self.setGeometry(100, 100, 400, 500)

        self.layout = QVBoxLayout(self)

        # Переключатель темы
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["Темная", "Светлая"])
        self.layout.addWidget(QLabel("Выберите тему:"))
        self.layout.addWidget(self.theme_combo)
        self.theme_combo.currentTextChanged.connect(self.change_theme)

        # Установить темную тему по умолчанию
        self.set_theme("Темная")

        # Выбор даты (без автоматического выбора)
        self.date_combo = QComboBox(self)
        self.layout.addWidget(QLabel("Выберите дату:"))
        self.layout.addWidget(self.date_combo)

        # Выбор спектакля
        self.play_combo = QComboBox(self)
        self.layout.addWidget(QLabel("Выберите спектакль:"))
        self.layout.addWidget(self.play_combo)

        # Добавляем QLabel для отображения описания спектакля
        self.play_description_label = QLabel("Описание спектакля: Н/Д", self)
        self.layout.addWidget(self.play_description_label)

        # Выбор зоны
        self.zone_combo = QComboBox(self)
        self.layout.addWidget(QLabel("Выберите зону:"))
        self.layout.addWidget(self.zone_combo)

        # Доступные билеты
        self.available_tickets_label = QLabel("Доступно билетов: Н/Д", self)
        self.layout.addWidget(self.available_tickets_label)

        # Время начала
        self.start_time_label = QLabel("Время начала: Н/Д", self)
        self.layout.addWidget(self.start_time_label)

        # Длительность
        self.duration_label = QLabel("Длительность: Н/Д", self)
        self.layout.addWidget(self.duration_label)

        # Кол-во билетов
        self.ticket_count_label = QLabel("Количество билетов:", self)
        self.layout.addWidget(self.ticket_count_label)

        self.ticket_count_spinbox = QSpinBox(self)
        self.ticket_count_spinbox.setMinimum(1)
        self.layout.addWidget(self.ticket_count_spinbox)

        # Ввод почты
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Введите вашу почту")
        self.layout.addWidget(self.email_input)

        # Оформить заказ
        self.order_button = QPushButton("Оформить заказ", self)
        self.layout.addWidget(self.order_button)
        self.order_button.clicked.connect(self.handle_order)

        # История заказов
        self.history_button = QPushButton("История заказов", self)
        self.layout.addWidget(self.history_button)
        self.history_button.clicked.connect(self.show_order_history)

        # Отмена заказа
        self.cancel_button = QPushButton("Отменить последний заказ", self)
        self.layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_last_order)

        # Заполняем комбобокс с датами
        self.update_dates()

        # Обработчики изменений
        self.date_combo.currentTextChanged.connect(self.update_plays)
        self.play_combo.currentTextChanged.connect(self.update_zones)
        self.zone_combo.currentTextChanged.connect(self.update_available_tickets)
        self.play_combo.currentTextChanged.connect(self.update_play_description)
        self.play_combo.currentTextChanged.connect(self.update_play_time_and_duration)

    def cancel_last_order(self):
        """Отменить последний заказ"""
        email = self.email_input.text()

        if not self.is_valid_email(email):
            self.show_error("Пожалуйста, введите правильный адрес электронной почты!")
            return

        try:
            # Найдем последний заказ пользователя
            self.cursor.execute(
                "SELECT id, play_name, date, zone_name, ticket_count FROM orders WHERE email = ? ORDER BY id DESC LIMIT 1",
                (email,)
            )
            order = self.cursor.fetchone()

            if not order:
                self.show_error("У вас нет заказов для отмены.")
                return

            order_id, play_name, date, zone_name, ticket_count = order

            # Восстановим количество билетов в зоне
            self.cursor.execute(
                "UPDATE zones SET available_tickets = available_tickets + ? WHERE play_name = ? AND date = ? AND zone_name = ?",
                (ticket_count, play_name, date, zone_name)
            )
            self.conn.commit()

            # Удалим последний заказ
            self.cursor.execute(
                "DELETE FROM orders WHERE id = ?",
                (order_id,)
            )
            self.conn.commit()

            QMessageBox.information(self, "Отмена заказа", "Ваш последний заказ успешно отменен!")

        except Exception as e:
            self.show_error(f"Ошибка при отмене последнего заказа: {e}")

    def set_theme(self, theme):
        """Устанавливает тему приложения."""
        if theme == "Темная":
            self.setStyleSheet("""
                QWidget {
                    background-color: #2E2E2E;
                    color: #FFFFFF;
                }
                QLineEdit, QComboBox, QSpinBox, QPushButton {
                    background-color: #424242;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                }
                QPushButton:hover {
                    background-color: #616161;
                }
                QComboBox QAbstractItemView {
                    background-color: #424242;
                    color: #FFFFFF;
                }
            """)
        elif theme == "Светлая":
            self.setStyleSheet("""
                QWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                }
                QLineEdit, QComboBox, QSpinBox, QPushButton {
                    background-color: #F0F0F0;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
                QComboBox QAbstractItemView {
                    background-color: #F0F0F0;
                    color: #000000;
                }
            """)

    def change_theme(self, theme_name):
        """Изменяет тему в зависимости от выбора пользователя."""
        self.set_theme(theme_name)

    def update_dates(self):
        """Заполняет комбобокс с доступными датами спектаклей."""
        self.cursor.execute("SELECT DISTINCT date FROM showtimes ORDER BY date")
        dates = self.cursor.fetchall()

        self.date_combo.clear()
        self.date_combo.addItem("Выберите дату")  # Добавляем placeholder
        self.date_combo.addItems([date[0] for date in dates])

    def update_plays(self):
        """Обновляет список спектаклей в зависимости от выбранной даты."""
        date = self.date_combo.currentText()
        if date == "Выберите дату":  # Если дата не выбрана, не обновляем спектакли
            self.play_combo.clear()
            return

        self.cursor.execute("SELECT DISTINCT play_name FROM showtimes WHERE date = ? ORDER BY play_name", (date,))
        plays = self.cursor.fetchall()

        self.play_combo.clear()
        self.play_combo.addItem("Выберите спектакль")  # Добавляем placeholder
        self.play_combo.addItems([play[0] for play in plays])

    def update_zones(self):
        """Обновляет список доступных зон в зависимости от выбранного спектакля."""
        play_name = self.play_combo.currentText()
        date = self.date_combo.currentText()

        if play_name == "Выберите спектакль" or date == "Выберите дату":
            self.zone_combo.clear()
            return

        self.cursor.execute(
            "SELECT DISTINCT zone_name FROM zones WHERE play_name = ? AND date = ? ORDER BY zone_name",
            (play_name, date)
        )
        zones = self.cursor.fetchall()

        self.zone_combo.clear()
        self.zone_combo.addItem("Выберите зону")  # Добавляем placeholder
        self.zone_combo.addItems([zone[0] for zone in zones])

    def update_available_tickets(self):
        """Обновляет количество доступных билетов в зависимости от выбранной зоны, спектакля и даты."""
        play_name = self.play_combo.currentText()
        date = self.date_combo.currentText()
        zone_name = self.zone_combo.currentText()

        if play_name == "Выберите спектакль" or date == "Выберите дату" or zone_name == "Выберите зону":
            self.available_tickets_label.setText("Доступно билетов: Н/Д")
            return

        self.cursor.execute(
            "SELECT available_tickets FROM zones WHERE play_name = ? AND date = ? AND zone_name = ?",
            (play_name, date, zone_name)
        )
        available_tickets = self.cursor.fetchone()

        if available_tickets:
            self.available_tickets_label.setText(f"Доступно билетов: {available_tickets[0]}")
        else:
            self.available_tickets_label.setText("Доступно билетов: Н/Д")

    def update_play_description(self):
        """Обновляет описание выбранного спектакля."""
        play_name = self.play_combo.currentText()

        if play_name == "Выберите спектакль":
            self.play_description_label.setText("Описание спектакля: Н/Д")
            return

        self.cursor.execute("SELECT description FROM plays WHERE name = ?", (play_name,))
        description = self.cursor.fetchone()

        if description:
            self.play_description_label.setText(f"Описание спектакля: {description[0]}")
        else:
            self.play_description_label.setText("Описание спектакля: Н/Д")

    def update_play_time_and_duration(self):
        """Обновляет время начала и длительность спектакля."""
        play_name = self.play_combo.currentText()

        if play_name == "Выберите спектакль":
            self.start_time_label.setText("Время начала: Н/Д")
            self.duration_label.setText("Длительность: Н/Д")
            return

        try:
            self.cursor.execute("SELECT start_time, duration FROM showtimes WHERE play_name = ? LIMIT 1", (play_name,))
            result = self.cursor.fetchone()

            if result:
                start_time, duration = result
                self.start_time_label.setText(f"Время начала: {start_time}")
                if duration is not None:
                    self.duration_label.setText(f"Длительность: {duration} мин.")
                else:
                    self.duration_label.setText("Длительность: Н/Д")
            else:
                self.start_time_label.setText("Время начала: Н/Д")
                self.duration_label.setText("Длительность: Н/Д")
        except Exception as e:
            self.show_error(f"Ошибка при получении времени начала и длительности: {e}")

    def is_valid_email(self, email):
        """Проверка валидности email."""
        email_regex = r"(^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$)"
        return re.match(email_regex, email) is not None

    def show_error(self, message):
        """Показывает ошибку в виде всплывающего окна с изображением."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)  # Устанавливаем стандартную иконку ошибки
        msg.setText(message)
        msg.setWindowTitle("Ошибка")

        # Загружаем изображение
        pixmap = QPixmap("error_icon.jpg")  # Укажите путь к вашему изображению
        msg.setIconPixmap(pixmap)  # Устанавливаем изображение как иконку

        # Показываем сообщение
        msg.exec()

    def handle_order(self):
        """Оформление заказа"""
        email = self.email_input.text()
        play_name = self.play_combo.currentText()
        date = self.date_combo.currentText()
        zone_name = self.zone_combo.currentText()
        ticket_count = self.ticket_count_spinbox.value()

        if not self.is_valid_email(email):
            self.show_error("Пожалуйста, введите правильный адрес электронной почты!")
            return

        try:
            self.cursor.execute(
                "SELECT available_tickets FROM zones WHERE play_name = ? AND date = ? AND zone_name = ?",
                (play_name, date, zone_name)
            )
            available_tickets = self.cursor.fetchone()

            if not available_tickets or available_tickets[0] < ticket_count:
                self.show_error("Недостаточно доступных билетов!")
                return

            # Создаем заказ
            self.cursor.execute(
                "INSERT INTO orders (email, play_name, date, zone_name, ticket_count) VALUES (?, ?, ?, ?, ?)",
                (email, play_name, date, zone_name, ticket_count)
            )

            # Обновляем доступные билеты
            self.cursor.execute(
                "UPDATE zones SET available_tickets = available_tickets - ? WHERE play_name = ? AND date = ? AND zone_name = ?",
                (ticket_count, play_name, date, zone_name)
            )
            self.conn.commit()

            # Показываем окно с подтверждением и кнопкой сохранения билета
            self.show_success_window(email, play_name, date, zone_name, ticket_count)

        except Exception as e:
            self.show_error(f"Ошибка при оформлении заказа: {e}")

    def show_success_window(self, email, play_name, date, zone_name, ticket_count):
        """Показывает окно с подтверждением заказа и кнопкой сохранения билета"""
        success_msg = QMessageBox(self)
        success_msg.setIcon(QMessageBox.Icon.Information)
        success_msg.setText("Ваш заказ успешно оформлен!")
        success_msg.setWindowTitle("Заказ успешен")

        # Кнопка для сохранения билета
        save_button = success_msg.addButton("Сохранить билет", QMessageBox.ButtonRole.AcceptRole)
        save_button.clicked.connect(lambda: self.generate_ticket_pdf(email, play_name, date, zone_name, ticket_count))

        success_msg.exec()

    def generate_ticket_pdf(self, email, play_name, date, zone_name, ticket_count):
        """Генерирует PDF файл с билетом."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить билет", "", "PDF Files (*.pdf)")

        if not file_name:
            return  # Если пользователь не выбрал место для сохранения, выходим

        pdfmetrics.registerFont(TTFont('DejaVuSans', 'C:/Users/sh3lze/Desktop/project/pythonProject1/DejaVuSans.ttf'))  # Убедитесь, что путь правильный
        c = canvas.Canvas(file_name, pagesize=letter)
        c.setFont("DejaVuSans", 12)

        c.drawString(100, 750, f"Билет на спектакль: {play_name}")
        c.drawString(100, 730, f"Дата: {date}")
        c.drawString(100, 710, f"Зона: {zone_name}")
        c.drawString(100, 690, f"Количество билетов: {ticket_count}")
        c.drawString(100, 670, f"Email покупателя: {email}")
        c.drawString(100, 650, "Спасибо за покупку!")

        c.showPage()
        c.save()

        QMessageBox.information(self, "Билет сохранен", f"Ваш билет был сохранен как {file_name}.")

    def show_order_history(self):
        """Показывает историю заказов"""
        email = self.email_input.text()

        if not self.is_valid_email(email):
            self.show_error("Пожалуйста, введите правильный адрес электронной почты!")
            return

        try:
            self.cursor.execute(
                "SELECT play_name, date, zone_name, ticket_count FROM orders WHERE email = ? ORDER BY id DESC",
                (email,)
            )
            orders = self.cursor.fetchall()

            if not orders:
                self.show_error("У вас нет заказов.")
                return

            orders_text = "\n".join([f"{play} | {date} | {zone} | {tickets} билетов"
                                    for play, date, zone, tickets in orders])

            QMessageBox.information(self, "История заказов", orders_text)

        except Exception as e:
            self.show_error(f"Ошибка при получении истории заказов: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicketBookingApp()
    window.show()
    sys.exit(app.exec())
