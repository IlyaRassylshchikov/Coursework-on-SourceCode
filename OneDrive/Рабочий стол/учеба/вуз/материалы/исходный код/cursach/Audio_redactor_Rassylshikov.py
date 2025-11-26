import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from Audio_processor_Rassylshikov  import AudioProcessor


class AudioRedactorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AudioRedactor - Простой аудиоредактор")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.audio_processor = None
        self.current_file_path = None

        self._create_widgets()

    def _create_widgets(self):
        """Создание элементов интерфейса"""

        # Заголовок
        title_label = tk.Label(
            self.root,
            text="AudioRedactor",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()

        # Фрейм для загрузки файла
        load_frame = tk.LabelFrame(self.root, text="1. Загрузка аудиофайла", padx=10, pady=10)
        load_frame.pack(fill="x", padx=20, pady=10)

        self.file_label = tk.Label(load_frame, text="Файл не загружен", fg="gray")
        self.file_label.pack(side="left", padx=5)

        load_button = tk.Button(
            load_frame,
            text="Выбрать файл (WAV/MP3)",
            command=self.load_file,
            bg="#4CAF50",
            fg="white",
            padx=10
        )
        load_button.pack(side="right")

        # Информация о файле
        self.info_label = tk.Label(self.root, text="", font=("Arial", 9), fg="blue")
        self.info_label.pack()

        # Фрейм для обрезки
        trim_frame = tk.LabelFrame(self.root, text="2. Обрезка аудио", padx=10, pady=10)
        trim_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(trim_frame, text="Начало (сек):").grid(row=0, column=0, sticky="w", pady=5)
        self.start_entry = tk.Entry(trim_frame, width=15)
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)
        self.start_entry.insert(0, "0")

        tk.Label(trim_frame, text="Конец (сек):").grid(row=1, column=0, sticky="w", pady=5)
        self.end_entry = tk.Entry(trim_frame, width=15)
        self.end_entry.grid(row=1, column=1, padx=5, pady=5)

        trim_button = tk.Button(
            trim_frame,
            text="Обрезать",
            command=self.trim_audio,
            bg="#2196F3",
            fg="white",
            padx=10
        )
        trim_button.grid(row=0, column=2, rowspan=2, padx=20)

        # Фрейм для изменения громкости
        volume_frame = tk.LabelFrame(self.root, text="3. Изменение громкости", padx=10, pady=10)
        volume_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(volume_frame, text="Изменение (dB):").pack(side="left", padx=5)

        self.volume_var = tk.StringVar(value="+10")
        volume_spinbox = tk.Spinbox(
            volume_frame,
            from_=-50,
            to=50,
            textvariable=self.volume_var,
            width=10
        )
        volume_spinbox.pack(side="left", padx=5)

        volume_button = tk.Button(
            volume_frame,
            text="Применить",
            command=self.change_volume,
            bg="#FF9800",
            fg="white",
            padx=10
        )
        volume_button.pack(side="right", padx=5)

        # Фрейм для сохранения
        save_frame = tk.LabelFrame(self.root, text="4. Сохранение результата", padx=10, pady=10)
        save_frame.pack(fill="x", padx=20, pady=10)

        save_button = tk.Button(
            save_frame,
            text="Сохранить как...",
            command=self.save_file,
            bg="#9C27B0",
            fg="white",
            padx=20,
            pady=5
        )
        save_button.pack()

        # Статус бар
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#f0f0f0"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_file(self):
        """Загрузка аудиофайла"""
        file_path = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=[
                ("Аудио файлы", "*.wav *.mp3"),
                ("WAV файлы", "*.wav"),
                ("MP3 файлы", "*.mp3"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                self.audio_processor = AudioProcessor(file_path)
                self.current_file_path = file_path

                filename = os.path.basename(file_path)
                self.file_label.config(text=filename, fg="black")

                duration = self.audio_processor.get_duration()
                channels = self.audio_processor.get_channels()
                sample_rate = self.audio_processor.get_sample_rate()

                info_text = f"Длительность: {duration:.2f} сек | Каналы: {channels} | Частота: {sample_rate} Гц"
                self.info_label.config(text=info_text)

                # Установить конец по умолчанию
                self.end_entry.delete(0, tk.END)
                self.end_entry.insert(0, str(int(duration)))

                self.status_bar.config(text=f"Загружен: {filename}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def trim_audio(self):
        """Обрезка аудио"""
        if not self.audio_processor:
            messagebox.showwarning("Предупреждение", "Сначала загрузите аудиофайл!")
            return

        try:
            start = float(self.start_entry.get())
            end = float(self.end_entry.get())

            if start < 0 or end <= start:
                messagebox.showerror("Ошибка", "Неверные значения времени!")
                return

            self.audio_processor.trim(start, end)

            new_duration = self.audio_processor.get_duration()
            self.info_label.config(
                text=f"Длительность: {new_duration:.2f} сек | "
                     f"Каналы: {self.audio_processor.get_channels()} | "
                     f"Частота: {self.audio_processor.get_sample_rate()} Гц"
            )

            self.status_bar.config(text=f"Обрезка выполнена: {start}с - {end}с")
            messagebox.showinfo("Успех", f"Аудио обрезано: {start}с - {end}с")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обрезать аудио:\n{str(e)}")

    def change_volume(self):
        """Изменение громкости"""
        if not self.audio_processor:
            messagebox.showwarning("Предупреждение", "Сначала загрузите аудиофайл!")
            return

        try:
            db_change = float(self.volume_var.get())

            if abs(db_change) > 50:
                if not messagebox.askyesno(
                        "Предупреждение",
                        f"Изменение громкости на {db_change} dB может привести к искажениям. Продолжить?"
                ):
                    return

            self.audio_processor.change_volume(db_change)

            sign = "+" if db_change >= 0 else ""
            self.status_bar.config(text=f"Громкость изменена: {sign}{db_change} dB")
            messagebox.showinfo("Успех", f"Громкость изменена на {sign}{db_change} dB")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное числовое значение!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить громкость:\n{str(e)}")

    def save_file(self):
        """Сохранение аудиофайла"""
        if not self.audio_processor:
            messagebox.showwarning("Предупреждение", "Нет аудио для сохранения!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".wav",
            filetypes=[
                ("WAV файлы", "*.wav"),
                ("MP3 файлы", "*.mp3"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                self.audio_processor.save(file_path)
                filename = os.path.basename(file_path)
                self.status_bar.config(text=f"Сохранено: {filename}")
                messagebox.showinfo("Успех", f"Файл сохранён:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = AudioRedactorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()