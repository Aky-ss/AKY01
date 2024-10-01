import os
import json
from googletrans import Translator
from docx import Document
from concurrent.futures import ThreadPoolExecutor
import arabic_reshaper
from bidi.algorithm import get_display

def translate_text(text, src_lang='en', dest_lang='ar', reverse_arabic=False, max_retries=3):
    if not text or text.strip() == "":  # التحقق من أن النص ليس فارغًا
        return text  # إذا كان النص فارغًا، إرجاعه كما هو

    translator = Translator()

    # المحاولات المتعددة في حال فشل الترجمة
    for attempt in range(max_retries):
        try:
            # ترجمة النص
            translated = translator.translate(text, src=src_lang, dest=dest_lang, timeout=10).text
            break  # الخروج من الحلقة إذا نجحت الترجمة
        except Exception as e:
            print(f"Error translating text (Attempt {attempt + 1}/{max_retries}): {text}. Error: {e}")
            if attempt == max_retries - 1:
                return text  # إذا فشلت جميع المحاولات، إرجاع النص الأصلي

    if reverse_arabic and dest_lang == 'ar':
        try:
            # إعادة تشكيل النصوص العربية
            reshaped_text = arabic_reshaper.reshape(translated)
            # تحويل النص ليظهر من اليمين إلى اليسار
            translated = get_display(reshaped_text)
        except Exception as e:
            print(f"Error reshaping Arabic text: {translated}. Error: {e}")
            return text  # في حال حدوث خطأ أثناء إعادة تشكيل النص العربي

    return translated



def translate_json_content(content, src_lang='en', dest_lang='ar', reverse_arabic=False, exclude_keys=None):
    if exclude_keys is None:
        exclude_keys = ['id']

    data = json.loads(content)

    def translate_value(value):
        if isinstance(value, str):
            return translate_text(value, src_lang, dest_lang, reverse_arabic)
        elif isinstance(value, list):
            return [translate_value(item) for item in value]
        elif isinstance(value, dict):
            return {key: translate_value(val) if key not in exclude_keys else val for key, val in value.items()}
        return value  # إذا لم تكن قيمة قابلة للترجمة

    translated_data = translate_value(data)
    return json.dumps(translated_data, ensure_ascii=False, indent=4)  # الاحتفاظ بالمفاتيح الأصلية

def translate_docx_content(file_path, src_lang='en', dest_lang='ar', reverse_arabic=False):
    doc = Document(file_path)
    for para in doc.paragraphs:
        para.text = translate_text(para.text, src_lang, dest_lang, reverse_arabic)
    doc.save(file_path)

def translate_txt_content(content, src_lang='en', dest_lang='ar', reverse_arabic=False):
    # تقسم المحتويات إلى سطور
    lines = content.split('\n')
    
    # الترجمة سطرًا بسطر مع التحقق من وجود سطر فارغ أو تعليقات
    translated_lines = []
    for line in lines:
        if line.strip():  # التحقق من أن السطر ليس فارغًا
            translated_line = translate_text(line, src_lang, dest_lang, reverse_arabic)
            translated_lines.append(translated_line)
        else:
            translated_lines.append('')  # الاحتفاظ بالسطر الفارغ كما هو

    # إعادة ضم السطور المترجمة
    return '\n'.join(translated_lines)


def translate_python_content(content, src_lang='en', dest_lang='ar', reverse_arabic=False):
    lines = content.split('\n')
    translated_lines = [translate_text(line, src_lang, dest_lang, reverse_arabic) if not line.startswith('#') else line for line in lines]
    return '\n'.join(translated_lines)

def translate_localization_content(content, src_lang='en', dest_lang='ar', reverse_arabic=False):
    # معاملة ملفات .localization كملفات نصية عادية
    return translate_txt_content(content, src_lang, dest_lang, reverse_arabic)

def read_file(file_path):
    encodings = ['utf-8', 'latin-1', 'utf-16']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Unable to decode the file: {file_path}")

def translate_file(file_path, src_lang='en', dest_lang='ar', reverse_arabic=False, exclude_keys=None):
    ext = os.path.splitext(file_path)[1].lower()  # استخدام الامتداد بالحروف الصغيرة
    content = read_file(file_path)

    if ext == '.json':
        translated_content = translate_json_content(content, src_lang, dest_lang, reverse_arabic, exclude_keys)
    elif ext == '.docx':
        translate_docx_content(file_path, src_lang, dest_lang, reverse_arabic)
        return
    elif ext == '.py':
        translated_content = translate_python_content(content, src_lang, dest_lang, reverse_arabic)
    # ترجمة ملف TXT أو ملف LOCALIZATION
    elif ext in ['.txt', '.localization']:
        translated_content = translate_txt_content(content, src_lang, dest_lang, reverse_arabic)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)

    else:
        print(f"Unsupported file type: {ext}")

def translate_multiple_files(file_paths, src_lang='en', dest_lang='ar', reverse_arabic=False, exclude_keys=None):
    if exclude_keys is None:
        exclude_keys = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(translate_file, file_path, src_lang, dest_lang, reverse_arabic, exclude_keys) for file_path in file_paths]
        for future in futures:
            future.result()

def translate_files_in_directory(directory_path, src_lang='en', dest_lang='ar', reverse_arabic=False, exclude_keys=None):
    for root, _, files in os.walk(directory_path):
        file_paths = [os.path.join(root, file) for file in files if file.endswith(('.json', '.txt', '.py', '.docx', '.localization'))]
        translate_multiple_files(file_paths, src_lang, dest_lang, reverse_arabic, exclude_keys)
