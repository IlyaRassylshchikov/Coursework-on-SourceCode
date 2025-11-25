"""
AudioRedactor - Базовый аудиоредактор БЕЗ FFmpeg
Работает только с WAV файлами
Версия: 1.0
Автор: IlyaRassylshchikov
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import wave
import struct
import math
import os


class AudioProcessor:
    """Класс для обработки WAV аудиофайлов без внешних зависимостей"""

    def __init__(self, file_path):
        """
        Инициализация процессора аудио

        Args:
            file_path (str): Путь к WAV файлу
        """
        self.file_path = file_path
        self.load_wav(file_path)
        self.original_duration = self.get_duration()

    def load_wav(self, file_path):
        """Загрузка WAV файла"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension != '.wav':
            raise ValueError("Поддерживаются только WAV файлы!")

        with wave.open(file_path, 'rb') as wav_file:
            self.channels = wav_file.getnchannels()
            self.sample_width = wav_file.getsampwidth()
            self.frame_rate = wav_file.getframerate()
            self.n_frames = wav_file.getnframes()
            self.frames = wav_file.readframes(self.n_frames)

    def get_duration(self):
        """Получить длительность в секундах"""
        return self.n_frames / float(self.frame_rate)

    def get_channels(self):
        """Получить количество каналов (1=моно, 2=стерео)"""
        return self.channels

    def get_sample_rate(self):
        """Получить частоту дискретизации в Гц"""
        return self.frame_rate

    def trim(self, start_sec, end_sec):
        """
        Обрезка аудио

        Args:
            start_sec (float): Начало в секундах
            end_sec (float): Конец в секундах
        """
        if start_sec < 0:
            raise ValueError("Начало не может быть отрицательным")
        if end_sec <= start_sec:
            raise ValueError("Конец должен быть больше начала")

        duration = self.get_duration()
        if start_sec > duration:
            raise ValueError(f"Начало ({start_sec}с) превышает длительность ({duration:.2f}с)")

        # Ограничиваем end_sec длительностью файла
        end_sec = min(end_sec, duration)

        start_frame = int(start_sec * self.frame_rate)
        end_frame = int(end_sec * self.frame_rate)

        bytes_per_frame = self.sample_width * self.channels
        start_byte = start_frame * bytes_per_frame
        end_byte = end_frame * bytes_per_frame

        self.frames = self.frames[start_byte:end_byte]
        self.n_frames = end_frame - start_frame

    def change_volume(self, db_change):
        """
        Изменение громкости

        Args:
            db_change (float): Изменение в децибелах (+10 = громче, -10 = тише)
        """
        # Коэффициент изменения громкости
        factor = math.pow(10, db_change / 20.0)

        # Определяем формат данных
        fmt_map = {1: 'b', 2: 'h', 4: 'i'}
        if self.sample_width not in fmt_map:
            raise ValueError(f"Неподдерживаемая ширина сэмпла: {self.sample_width}")

        fmt = fmt_map[self.sample_width]
        num_samples = len(self.frames) // self.sample_width

        # Распаковываем байты в список значений
        samples = list(struct.unpack(f'{num_samples}{fmt}', self.frames))

        # Максимальное значение для данной разрядности
        max_val = 2 ** (8 * self.sample_width - 1) - 1
        min_val = -max_val - 1

        # Применяем изменение громкости с ограничением
        samples = [int(max(min(s * factor, max_val), min_val)) for s in samples]

        # Упаковываем обратно в байты
        self.frames = struct.pack(f'{len(samples)}{fmt}', *samples)

    def save(self, output_path):
        """
        Сохранение аудио в WAV файл

        Args:
            output_path (str): Путь для сохранения
        """
        file_extension = os.path.splitext(output_path)[1].lower()
        if file_extension != '.wav':
            output_path += '.wav'

        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.frame_rate)
            wav_file.writeframes(self.frames)

    def get_audio_info(self):
        """Получить информацию об аудио"""
        return {
            'duration': self.get_duration(),
            'channels': self.get_channels(),
            'sample_rate': self.get_sample_rate(),
            'sample_width': self.sample_width,
            'bit_depth': self.sample_width * 8,
            'original_duration': self.original_duration
        }


class AudioRedactorGUI:
    """Графический интерфейс AudioRedactor"""

    def __init__(self, root):
        self.root = root
        self.root.title("AudioRedactor - Простой аудиоредактор (только WAV)")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # Устанавливаем иконку (если есть)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        self.audio_processor = None
        self.current_file_path = None

        self._create_widgets()
        self._set_colors()

    def _set_colors(self):
        """Установка цветовой схемы"""
        self.bg_color = "#f5f5f5"
        self.root.configure(bg=self.bg_color)

    def _create_widgets(self):
        """Создание элементов интерфейса"""

        # Заголовок
        title_frame = tk.Frame(self.root, bg="#2196F3", pady=15)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="🎵 AudioRedactor",
            font=("Arial", 20, "bold"),
            bg="#2196F3",
            fg="white"
        ).pack()

        tk.Label(
            title_frame,
            text="Простой аудиоредактор для WAV файлов",
            font=("Arial", 10),
            bg="#2196F3",
            fg="white"
        ).pack()

        # Информационное сообщение
        info_frame = tk.Frame(self.root, bg="#FFF9C4", pady=8)
        info_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            info_frame,
            text="ℹ️ Эта версия работает только с WAV файлами",
            bg="#FFF9C4",
            fg="#F57F17",
            font=("Arial", 9)
        ).pack()

        # Фрейм для загрузки файла
        load_frame = tk.LabelFrame(
            self.root,
            text="📁 1. Загрузка аудиофайла",
            padx=15,
            pady=15,
            font=("Arial", 10, "bold")
        )
        load_frame.pack(fill="x", padx=20, pady=10)

        self.file_label = tk.Label(
            load_frame,
            text="Файл не загружен",
            fg="gray",
            font=("Arial", 9)
        )
        self.file_label.pack(side="left", padx=5)

        load_button = tk.Button(
            load_frame,
            text="Выбрать WAV файл",
            command=self.load_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            pady=5,
            cursor="hand2"
        )
        load_button.pack(side="right")

        # Информация о файле
        self.info_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 9),
            fg="#1976D2"
        )
        self.info_label.pack(pady=5)

        # Фрейм для обрезки
        trim_frame = tk.LabelFrame(
            self.root,
            text="✂️ 2. Обрезка аудио",
            padx=15,
            pady=15,
            font=("Arial", 10, "bold")
        )
        trim_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            trim_frame,
            text="Начало (сек):",
            font=("Arial", 9)
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.start_entry = tk.Entry(trim_frame, width=15, font=("Arial", 10))
        self.start_entry.grid(row=0, column=1, padx=10, pady=5)
        self.start_entry.insert(0, "0")

        tk.Label(
            trim_frame,
            text="Конец (сек):",
            font=("Arial", 9)
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.end_entry = tk.Entry(trim_frame, width=15, font=("Arial", 10))
        self.end_entry.grid(row=1, column=1, padx=10, pady=5)

        trim_button = tk.Button(
            trim_frame,
            text="Обрезать",
            command=self.trim_audio,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=20,
            cursor="hand2"
        )
        trim_button.grid(row=0, column=2, rowspan=2, padx=20)

        # Фрейм для изменения громкости
        volume_frame = tk.LabelFrame(
            self.root,
            text="🔊 3. Изменение громкости",
            padx=15,
            pady=15,
            font=("Arial", 10, "bold")
        )
        volume_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            volume_frame,
            text="Изменение (dB):",
            font=("Arial", 9)
        ).pack(side="left", padx=5)

        self.volume_var = tk.StringVar(value="+10")
        volume_spinbox = tk.Spinbox(
            volume_frame,
            from_=-50,
            to=50,
            textvariable=self.volume_var,
            width=10,
            font=("Arial", 10)
        )
        volume_spinbox.pack(side="left", padx=10)

        tk.Label(
            volume_frame,
            text="(+10 = громче, -10 = тише)",
            font=("Arial", 8),
            fg="gray"
        ).pack(side="left", padx=5)

        volume_button = tk.Button(
            volume_frame,
            text="Применить",
            command=self.change_volume,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            cursor="hand2"
        )
        volume_button.pack(side="right", padx=5)

        # Фрейм для сохранения
        save_frame = tk.LabelFrame(
            self.root,
            text="💾 4. Сохранение результата",
            padx=15,
            pady=15,
            font=("Arial", 10, "bold")
        )
        save_frame.pack(fill="x", padx=20, pady=10)

        save_button = tk.Button(
            save_frame,
            text="Сохранить как WAV...",
            command=self.save_file,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=30,
            pady=8,
            cursor="hand2"
        )
        save_button.pack()

        # Статус бар
        self.status_bar = tk.Label(
            self.root,
            text="Готов к работе | Версия 1.0",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e0e0",
            font=("Arial", 8)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_file(self):
        """Загрузка аудиофайла"""
        file_path = filedialog.askopenfilename(
            title="Выберите WAV аудиофайл",
            filetypes=[
                ("WAV файлы", "*.wav"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                self.audio_processor = AudioProcessor(file_path)
                self.current_file_path = file_path

                filename = os.path.basename(file_path)
                self.file_label.config(text=filename, fg="black", font=("Arial", 9, "bold"))

                info = self.audio_processor.get_audio_info()

                info_text = (
                    f"Длительность: {info['duration']:.2f} сек | "
                    f"Каналы: {info['channels']} | "
                    f"Частота: {info['sample_rate']} Гц | "
                    f"Разрядность: {info['bit_depth']} бит"
                )
                self.info_label.config(text=info_text)

                # Установить конец по умолчанию
                self.end_entry.delete(0, tk.END)
                self.end_entry.insert(0, str(int(info['duration'])))

                self.status_bar.config(text=f"✓ Загружен: {filename}")

            except ValueError as e:
                messagebox.showerror("Ошибка формата", str(e))
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
                messagebox.showerror("Ошибка", "Неверные значения времени!\nКонец должен быть больше начала.")
                return

            self.audio_processor.trim(start, end)

            info = self.audio_processor.get_audio_info()
            info_text = (
                f"Длительность: {info['duration']:.2f} сек | "
                f"Каналы: {info['channels']} | "
                f"Частота: {info['sample_rate']} Гц | "
                f"Разрядность: {info['bit_depth']} бит"
            )
            self.info_label.config(text=info_text)

            self.status_bar.config(text=f"✓ Обрезка выполнена: {start}с - {end}с")
            messagebox.showinfo("Успех", f"Аудио успешно обрезано!\nС {start}с до {end}с")

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
                    f"Изменение громкости на {db_change} dB может привести к искажениям звука.\n\nПродолжить?"
                ):
                    return

            self.audio_processor.change_volume(db_change)

            sign = "+" if db_change >= 0 else ""
            self.status_bar.config(text=f"✓ Громкость изменена: {sign}{db_change} dB")
            messagebox.showinfo("Успех", f"Громкость успешно изменена на {sign}{db_change} dB")

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
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                self.audio_processor.save(file_path)
                filename = os.path.basename(file_path)
                self.status_bar.config(text=f"✓ Сохранено: {filename}")
                messagebox.showinfo("Успех", f"Файл успешно сохранён:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = AudioRedactorGUI(root)

    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()