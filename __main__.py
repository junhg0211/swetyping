import tkinter
from time import time
from tkinter import ttk, filedialog, messagebox

from util import get_language, get_command_key, get_length, strawberrify

PADDING = 12


class MainWindow:
    def __init__(self):
        self.tk = tkinter.Tk()

        # === status bar
        status_bar = tkinter.Frame(self.tk)
        # now types
        tkinter.Label(status_bar, text=get_language('main.status_bar.now_types')).grid(row=0, column=0)
        tkinter.Label(status_bar, text=get_language('main.status_bar.types_unit')).grid(row=0, column=2)
        # end types
        tkinter.Label(status_bar, text=get_language('main.status_bar.accuracy')).grid(row=1, column=0)
        tkinter.Label(status_bar, text='%').grid(row=1, column=2)
        # types per minute
        tkinter.Label(status_bar, text=get_language('main.status_bar.types_per_minute')) \
            .grid(row=0, column=4, sticky=tkinter.W)
        tkinter.Label(status_bar, text=get_language('main.status_bar.types_per_minute_unit')) \
            .grid(row=0, column=6, sticky=tkinter.W)
        # progress
        tkinter.Label(status_bar, text=get_language('main.status_bar.progress')).grid(row=1, column=4, sticky=tkinter.W)
        tkinter.Label(status_bar, text='%').grid(row=1, column=6, sticky=tkinter.W)

        self.now_types = tkinter.Label(status_bar, text='0')
        self.now_types.grid(row=0, column=1, sticky=tkinter.E)
        self.accuracy = tkinter.Label(status_bar, text='0')
        self.accuracy.grid(row=1, column=1, sticky=tkinter.E)
        self.types_per_minute = tkinter.Label(status_bar, text='0')
        self.types_per_minute.grid(row=0, column=5, sticky=tkinter.E)
        self.progress = tkinter.Label(status_bar, text='0')
        self.progress.grid(row=1, column=5, sticky=tkinter.E)

        status_bar.columnconfigure(1, weight=1)
        status_bar.columnconfigure(3, weight=1)
        status_bar.columnconfigure(5, weight=1)
        status_bar.pack(padx=PADDING, pady=PADDING, side=tkinter.TOP, fill=tkinter.X)

        # === horizontal separator
        ttk.Separator(self.tk, orient=tkinter.HORIZONTAL).pack(fill=tkinter.X, pady=5)

        # === main frame
        main_frame = tkinter.Frame(self.tk)

        previous_frame = tkinter.Frame(main_frame)
        self.previous_line = tkinter.Label(previous_frame, text='')
        self.previous_line.grid(row=0, column=0, sticky=tkinter.W)
        self.previous_line_typed = tkinter.Label(previous_frame, text='')
        self.previous_line_typed.grid(row=1, column=0, sticky=tkinter.W)
        previous_frame.pack(fill=tkinter.X)

        current_frame = tkinter.Frame(main_frame)
        self.current_line = tkinter.Text(current_frame, height=1, state=tkinter.DISABLED)
        self.current_line.pack(fill=tkinter.X)
        self.current_line_typed = tkinter.Text(current_frame, height=1)
        self.current_line_typed.pack(fill=tkinter.X)
        current_frame.pack(fill=tkinter.X, expand=True)

        self.next_lines_elements = []
        next_lines = 2
        for i in range(next_lines):
            next_frame = tkinter.Frame(main_frame)
            next_line = tkinter.Label(next_frame, text='')
            next_line.grid(row=0, column=0, sticky=tkinter.W)
            next_line_typed = tkinter.Label(next_frame, text='')
            next_line_typed.grid(row=1, column=0, sticky=tkinter.W)
            next_frame.pack(fill=tkinter.X, expand=i + 1 != next_lines)
            self.next_lines_elements.append((next_line, next_line_typed))

        main_frame.pack(padx=12, pady=12, side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)

        # === type handler
        self.tk.bind_all('<KeyPress>', self.typed)

        # === menubar
        menubar = tkinter.Menu(self.tk)
        command = get_command_key()

        # == file menu
        file_menu = tkinter.Menu(menubar, tearoff=0)
        # open command
        file_menu.add_command(label=get_language('main.menubar.file.open'), command=self.open_file,
                              accelerator=f'{command}+O')
        self.tk.bind_all(f'<{command}-o>', lambda _: self.open_file())
        # quit command
        file_menu.add_command(label=get_language('main.menubar.file.quit'), command=self.tk.quit,
                              accelerator=f'{command}+W')
        self.tk.bind_all(f'<{command}-w>', lambda _: self.tk.quit())

        menubar.add_cascade(label=get_language('main.menubar.file.label'), menu=file_menu)

        self.tk.config(menu=menubar)

        # === change the caption
        self.tk.title(get_language('main.title'))
        self.current_line_typed.tag_configure('red', foreground='red')

        # === centering the window
        self.tk.update_idletasks()
        screen_width = self.tk.winfo_screenwidth()
        screen_height = self.tk.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.tk.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # === file io
        self.lines = None
        self.current_line_index = 0
        self.tk.bind_all('<Return>', self.return_line)

        # record
        self.all_type_count = 0
        self.typed_count = 0
        self.wrong_typed_count = 0
        self.this_line_typed_count = 0
        self.this_line_wrong_typed_count = 0
        self.record_start_timestamp = 0

    def reset(self):
        self.now_types.config(text='0')
        self.accuracy.config(text='0')
        self.types_per_minute.config(text='0')
        self.progress.config(text='0')
        self.previous_line.config(text='')
        self.previous_line_typed.config(text='')
        self.current_line.config(state=tkinter.NORMAL)
        self.current_line.delete('1.0', tkinter.END)
        self.current_line.config(state=tkinter.DISABLED)
        self.current_line_typed.delete('1.0', tkinter.END)
        for next_line, next_line_typed in self.next_lines_elements:
            next_line.config(text='')
            next_line_typed.config(text='')
        self.lines = None
        self.current_line_index = 0
        self.all_type_count = 0
        self.typed_count = 0
        self.wrong_typed_count = 0
        self.this_line_typed_count = 0
        self.this_line_wrong_typed_count = 0
        self.record_start_timestamp = 0

    def typed(self, *_):
        if self.lines is None:
            return

        typed = self.current_line_typed.get("1.0", tkinter.END)[:-1]
        aim = self.lines[self.current_line_index]
        if len(typed) - 1 == len(aim):
            self.return_line()
            return

        self.current_line_typed.tag_remove('red', '1.0', tkinter.END)
        self.this_line_wrong_typed_count = 0
        self.this_line_typed_count = get_length(typed)
        for i, letter in enumerate(typed):  # coloring the wrong types
            if i >= len(aim) or letter != aim[i]:
                self.current_line_typed.tag_add('red', f'1.{i}', f'1.{i + 1}')
                try:
                    self.this_line_wrong_typed_count += len(''.join(strawberrify(letter)))
                except ValueError:
                    self.this_line_wrong_typed_count += 1

        self.now_types.configure(text=str(until_typed_count := self.typed_count + self.this_line_typed_count))
        if not self.record_start_timestamp and until_typed_count:
            self.record_start_timestamp = time()

        try:
            self.types_per_minute.configure(
                text=format(until_typed_count / (time() - self.record_start_timestamp) * 60, '.2f'))
            self.accuracy.configure(
                text=format(100 * (1 - (self.wrong_typed_count + self.this_line_wrong_typed_count) / until_typed_count),
                            '.2f'))
        except ZeroDivisionError:
            self.types_per_minute.configure(text='-')
            self.accuracy.configure(text='-')

        self.progress.configure(
            text=format(100 * ((self.current_line_index + (self.this_line_typed_count / get_length(aim)))
                               / len(self.lines)), '.2f'))

    def start(self):
        self.tk.mainloop()

    def open_file(self):
        self.reset()

        filename = filedialog.askopenfilename()
        self.previous_line.config(text=filename)

        if filename:
            with open(filename, 'r', encoding='utf-8') as file:
                self.lines = list(map(lambda x: x.strip(), file.readlines()))
            self.current_line_index = 0
            self.update_lines()

    def end_game(self):
        end_timestamp = time()
        delta = end_timestamp - self.record_start_timestamp

        speed = self.typed_count / delta * 60
        accuracy = 1 - self.wrong_typed_count / self.typed_count
        messagebox.showinfo(get_language('notification.end.title'), get_language('notification.end.message').format(
            format(speed, '.2f'),
            format(100 * accuracy, '.2f'),
            format(delta, '.2f'),
            format(speed * accuracy**2, '.2f')
        ))

    def update_lines(self):
        if (line_index := self.current_line_index - 1) >= 0:
            self.previous_line.configure(text=self.lines[line_index])
        else:
            self.previous_line.configure(text='')

        self.current_line.configure(state=tkinter.NORMAL)
        self.current_line.delete("1.0", tkinter.END)
        self.current_line.insert("1.0", self.lines[self.current_line_index])
        self.current_line.configure(state=tkinter.DISABLED)

        if (line_index := self.current_line_index + 1) < len(self.lines):
            self.next_lines_elements[0][0].configure(text=self.lines[line_index])
        else:
            self.next_lines_elements[0][0].configure(text='')

        if (line_index := line_index + 1) < len(self.lines):
            self.next_lines_elements[1][0].configure(text=self.lines[line_index])
        else:
            self.next_lines_elements[1][0].configure(text='')

    def return_line(self, _=None):
        if not self.lines:
            return

        self.typed_count += max(self.this_line_typed_count, get_length(self.lines[self.current_line_index]))
        self.wrong_typed_count += self.this_line_wrong_typed_count + abs(self.this_line_typed_count - get_length(
            self.lines[self.current_line_index]))

        if self.current_line_index < len(self.lines) - 1:
            self.current_line_index += 1
            self.update_lines()
            self.previous_line_typed.configure(text=self.current_line_typed.get("1.0", tkinter.END))
            self.current_line_typed.delete("1.0", tkinter.END)
        else:
            self.end_game()


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.start()
