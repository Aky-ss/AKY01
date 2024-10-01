import os
import random
from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar, OptionMenu, Checkbutton, BooleanVar, Toplevel, Entry
from tkinter import ttk
from translator import translate_multiple_files, translate_files_in_directory
from threading import Thread

correct_answers = 0
incorrect_answers = 0


def select_files_and_translate(src_lang, dest_lang, reverse_arabic, exclude_keys):
    file_paths = filedialog.askopenfilenames(filetypes=[("All files", "*.*"), ("JSON files", "*.json"), ("Text files", "*.txt"), ("Python files", "*.py"), ("Word files", "*.docx")])
    if file_paths:
        show_waiting_screen(file_paths, src_lang, dest_lang, reverse_arabic, is_directory=False, exclude_keys=exclude_keys)

def select_directory_and_translate(src_lang, dest_lang, reverse_arabic):
    directory_path = filedialog.askdirectory()
    if directory_path:
        show_waiting_screen(directory_path, src_lang, dest_lang, reverse_arabic, is_directory=True)

def show_waiting_screen(path, src_lang, dest_lang, reverse_arabic, is_directory, exclude_keys):
    waiting_screen = Toplevel()
    waiting_screen.title("الرجاء الانتظار")
    waiting_screen.geometry("400x300")
    waiting_screen.configure(bg='#2e2e2e')

    label = ttk.Label(waiting_screen, text="جاري الترجمة، الرجاء الانتظار...", background='#2e2e2e', foreground='#ffffff')
    label.pack(pady=10)

    game_label = ttk.Label(waiting_screen, text="لعبة حساب الأرقام: أدخل الإجابة الصحيحة", background='#2e2e2e', foreground='#ffffff')
    game_label.pack(pady=10)

    def generate_question():
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        return num1, num2, num1 * num2

    def check_answer(entry, correct_answer):
        global correct_answers, incorrect_answers
        try:
            user_answer = int(entry.get())
            if user_answer == correct_answer:
                correct_answers += 1
                correct_label.config(text=f"✅ صحيح: {correct_answers}")
            else:
                incorrect_answers += 1
                incorrect_label.config(text=f"❌ خطأ: {incorrect_answers}")
        except ValueError:
            incorrect_answers += 1
            incorrect_label.config(text=f"❌ خطأ: {incorrect_answers}")

        entry.delete(0, 'end')
        ask_question()

    def ask_question():
        num1, num2, correct_answer = generate_question()
        question_label.config(text=f"{num1} * {num2} = ?")
        submit_button.config(command=lambda: check_answer(answer_entry, correct_answer))

    question_label = ttk.Label(waiting_screen, text="", background='#2e2e2e', foreground='#ffffff')
    question_label.pack(pady=10)

    answer_entry = Entry(waiting_screen, width=10)
    answer_entry.pack(pady=5)

    submit_button = ttk.Button(waiting_screen, text="تأكيد")
    submit_button.pack(pady=5)

    correct_label = ttk.Label(waiting_screen, text="✅ صحيح: 0", background='#2e2e2e', foreground='#ffffff')
    correct_label.pack(pady=5)

    incorrect_label = ttk.Label(waiting_screen, text="❌ خطأ: 0", background='#2e2e2e', foreground='#ffffff')
    incorrect_label.pack(pady=5)

    ask_question()

    def translate():
        if is_directory:
            translate_files_in_directory(path, src_lang, dest_lang, reverse_arabic, exclude_keys)
        else:
            translate_multiple_files(path, src_lang, dest_lang, reverse_arabic, exclude_keys)
        waiting_screen.destroy()
        show_results()

    Thread(target=translate).start()

def show_results():
    result_screen = Toplevel()
    result_screen.title("نتائج الترجمة")
    result_screen.geometry("300x200")
    result_screen.configure(bg='#2e2e2e')

    global correct_answers, incorrect_answers

    result_label = ttk.Label(result_screen, text=f"✅ صحيح: {correct_answers}\n❌ خطأ: {incorrect_answers}", background='#2e2e2e', foreground='#ffffff')
    result_label.pack(pady=10)

    if correct_answers > incorrect_answers:
        message = "تهانينا! لقد أجبت على معظم الأسئلة بشكل صحيح!"
    else:
        message = "أعد مراجعة ذكائك! لقد أخطأت في معظم الأسئلة."

    message_label = ttk.Label(result_screen, text=message, background='#2e2e2e', foreground='#ffffff')
    message_label.pack(pady=10)

def create_gui():
    root = Tk()
    root.title("Materials Arabic Translator")
    root.geometry("400x400")
    root.configure(bg='#2e2e2e')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', background='#2e2e2e', foreground='#ffffff')
    style.configure('TButton', background='#4a4a4a', foreground='#ffffff', borderwidth=1)
    style.map('TButton', background=[('active', '#6e6e6e')])
    style.configure('TCheckbutton', background='#2e2e2e', foreground='#ffffff')
    style.configure('TOptionMenu', background='#4a4a4a', foreground='#ffffff')

    label = ttk.Label(root, text="اختر ملفات أو مجلد لترجمته")
    label.pack(pady=10)

    src_lang_label = ttk.Label(root, text="لغة المصدر:")
    src_lang_label.pack()
    src_lang_var = StringVar(root)
    src_lang_var.set("en")  # اللغة الافتراضية
    src_lang_menu = ttk.OptionMenu(root, src_lang_var, "en", "en", "fr", "es", "de", "it", "ar")
    src_lang_menu.pack()

    dest_lang_label = ttk.Label(root, text="لغة الوجهة:")
    dest_lang_label.pack()
    dest_lang_var = StringVar(root)
    dest_lang_var.set("ar")  # اللغة الافتراضية
    dest_lang_menu = ttk.OptionMenu(root, dest_lang_var, "ar", "en", "fr", "es", "de", "it", "ar")
    dest_lang_menu.pack()

    reverse_arabic_var = BooleanVar()
    reverse_arabic_check = ttk.Checkbutton(root, text="(RTL)قلب النص العربي", variable=reverse_arabic_var)
    reverse_arabic_check.pack()

    exclude_keys_label = ttk.Label(root, text="المفاتيح المستثناة (افصلها بفواصل):")
    exclude_keys_label.pack(pady=10)

    exclude_keys_var = StringVar()
    exclude_keys_entry = Entry(root, textvariable=exclude_keys_var, width=50)
    exclude_keys_entry.pack(pady=5)

      # نص إرشادي
    def on_focus_in(event):
        if exclude_keys_var.get() == "أدخل المفاتيح المستثناة هنا. مثال:(id,name...)":
            exclude_keys_var.set("")
            exclude_keys_entry.config(fg='black')

    exclude_keys_entry.bind("<FocusIn>", on_focus_in)
    exclude_keys_var.set("أدخل المفاتيح المستثناة هنا. مثال:(id,name...)")  # نص إرشادي

    def on_translate_files():
        src_lang = src_lang_var.get()
        dest_lang = dest_lang_var.get()
        reverse_arabic = reverse_arabic_var.get()
        exclude_keys = exclude_keys_var.get().split(",")  # تحويل السلسلة إلى قائمة
        select_files_and_translate(src_lang, dest_lang, reverse_arabic, exclude_keys)

    def on_translate_directory():
        src_lang = src_lang_var.get()
        dest_lang = dest_lang_var.get()
        reverse_arabic = reverse_arabic_var.get()
        
        select_directory_and_translate(src_lang, dest_lang, reverse_arabic)

    translate_files_button = ttk.Button(root, text="اختر ملفات", command=on_translate_files)
    translate_files_button.pack(pady=10)

    translate_directory_button = ttk.Button(root, text="اختر مجلد", command=on_translate_directory)
    translate_directory_button.pack(pady=10)

    root.mainloop()

# بدء واجهة المستخدم
create_gui()
