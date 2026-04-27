import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "trainings.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("900x600")

        # Данные
        self.trainings = []
        self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()

        # Обновление таблицы
        self.refresh_table()

    def create_input_frame(self):
        """Форма для добавления тренировки"""
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=5)
        self.training_type_var = tk.StringVar()
        training_types = ["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Растяжка", "Кардио", "Другое"]
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.training_type_var, values=training_types, width=15)
        self.type_combo.grid(row=0, column=3, padx=5)
        self.type_combo.set("Бег")

        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=5)
        self.duration_entry = ttk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_btn.grid(row=0, column=6, padx=10)

    def create_table_frame(self):
        """Таблица с тренировками"""
        table_frame = ttk.LabelFrame(self.root, text="Список тренировок", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы
        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")

        self.tree.column("id", width=50)
        self.tree.column("date", width=100)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=100)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_filter_frame(self):
        """Фильтрация"""
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу тренировки
        ttk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=0, padx=5)
        self.filter_type_var = tk.StringVar()
        training_types = ["Все"] + ["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Растяжка", "Кардио", "Другое"]
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                                                values=training_types, width=15)
        self.filter_type_combo.grid(row=0, column=1, padx=5)
        self.filter_type_combo.set("Все")

        # Фильтр по дате (начало)
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=15)
        self.filter_date_from.grid(row=0, column=3, padx=5)

        # Фильтр по дате (конец)
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=5)
        self.filter_date_to = ttk.Entry(filter_frame, width=15)
        self.filter_date_to.grid(row=0, column=5, padx=5)

        # Кнопка применения фильтра
        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        filter_btn.grid(row=0, column=6, padx=10)

        # Кнопка сброса фильтра
        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_btn.grid(row=0, column=7, padx=5)

        # Дополнительная статистика
        stats_btn = ttk.Button(filter_frame, text="Показать статистику", command=self.show_statistics)
        stats_btn.grid(row=1, column=0, columnspan=8, pady=5)

    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        """Проверка длительности"""
        try:
            duration = float(duration_str)
            if duration <= 0:
                return False, "Длительность должна быть положительным числом"
            if duration > 1440:  # Максимум 24 часа
                return False, "Длительность не может превышать 1440 минут (24 часа)"
            return True, duration
        except ValueError:
            return False, "Длительность должна быть числом"

    def add_training(self):
        """Добавление тренировки"""
        date_str = self.date_entry.get().strip()
        training_type = self.training_type_var.get()
        duration_str = self.duration_entry.get().strip()

        # Валидация даты
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД\nПример: 2024-12-25")
            return

        # Валидация длительности
        is_valid_duration, duration_or_error = self.validate_duration(duration_str)
        if not is_valid_duration:
            messagebox.showerror("Ошибка", duration_or_error)
            return

        # Добавление
        training = {
            "id": len(self.trainings) + 1,
            "date": date_str,
            "type": training_type,
            "duration": duration_or_error
        }
        self.trainings.append(training)
        self.save_data()

        # Очистка полей
        self.duration_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.refresh_table()
        messagebox.showinfo("Успех", f"Тренировка добавлена!\nТип: {training_type}\nДлительность: {duration_or_error} мин")

    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение фильтров
        type_filter = self.filter_type_var.get()
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        # Фильтрация
        filtered_trainings = self.trainings

        if type_filter != "Все":
            filtered_trainings = [t for t in filtered_trainings if t["type"] == type_filter]

        if date_from:
            filtered_trainings = [t for t in filtered_trainings if t["date"] >= date_from]

        if date_to:
            filtered_trainings = [t for t in filtered_trainings if t["date"] <= date_to]

        # Отображение
        for training in filtered_trainings:
            self.tree.insert("", "end", values=(
                training["id"],
                training["date"],
                training["type"],
                f"{training['duration']:.1f}"
            ))

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_type_combo.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("Фильтр сброшен", "Все фильтры были сброшены")

    def show_statistics(self):
        """Показать статистику тренировок"""
        if not self.trainings:
            messagebox.showinfo("Статистика", "Нет данных для статистики")
            return

        # Статистика по типам тренировок
        type_stats = {}
        total_duration = 0
        total_trainings = len(self.trainings)

        for training in self.trainings:
            training_type = training["type"]
            duration = training["duration"]

            if training_type not in type_stats:
                type_stats[training_type] = {"count": 0, "total_duration": 0}

            type_stats[training_type]["count"] += 1
            type_stats[training_type]["total_duration"] += duration
            total_duration += duration

        # Формирование сообщения
        stats_msg = f"📊 ОБЩАЯ СТАТИСТИКА 📊\n\n"
        stats_msg += f"Всего тренировок: {total_trainings}\n"
        stats_msg += f"Общая длительность: {total_duration:.1f} минут\n"
        stats_msg += f"Средняя длительность: {total_duration/total_trainings:.1f} минут\n\n"
        stats_msg += "📈 ПО ТИПАМ ТРЕНИРОВОК:\n"
        stats_msg += "-" * 30 + "\n"

        for training_type, stats in sorted(type_stats.items()):
            stats_msg += f"\n{training_type}:\n"
            stats_msg += f"  • Количество: {stats['count']}\n"
            stats_msg += f"  • Общая длительность: {stats['total_duration']:.1f} мин\n"
            stats_msg += f"  • Средняя длительность: {stats['total_duration']/stats['count']:.1f} мин\n"

        messagebox.showinfo("Статистика тренировок", stats_msg)

    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except:
                self.trainings = []
        else:
            self.trainings = []

    def save_data(self):
        """Сохранение данных в JSON"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
