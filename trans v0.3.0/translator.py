import os
import json
from googletrans import Translator
from docx import Document
from concurrent.futures import ThreadPoolExecutor
import arabic_reshaper
from bidi.algorithm import get_display

def translate_text(text, src_lang='en', dest_lang='ar', reverse_arabic=False):
    translator = Translator()
    translated = translator.translate(text, src=src_lang, dest=dest_lang).text
    if reverse_arabic and dest_lang == 'ar':
        # إعادة تشكيل النصوص العربية
        reshaped_text = arabic_reshaper.reshape(translated)
        # تحويل النص ليظهر من اليمين إلى اليسار
        translated = get_display(reshaped_text)
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
    return json.dumps({**data, **translated_data}, ensure_ascii=False, indent=4)  # الاحتفاظ بالمفاتيح الأصلية


def translate_docx_content(file_path, src_lang='en', dest_lang='ar', reverse_arabic=False):
    doc = Document(file_path)
    for para in doc.paragraphs:
        if para.text.startswith('#'):
            para.text = translate_text(para.text, src_lang, dest_lang, reverse_arabic)
    doc.save(file_path)

def translate_txt_content(content, src_lang='en', dest_lang='ar', reverse_arabic=False):
    lines = content.split('\n')
    translated_lines = [translate_text(line, src_lang, dest_lang, reverse_arabic) if line.startswith('#') else line for line in lines]
    return '\n'.join(translated_lines)

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
    ext = os.path.splitext(file_path)[1]
    content = read_file(file_path)
    if ext == '.json':
        translated_content = translate_json_content(content, src_lang, dest_lang, reverse_arabic, exclude_keys)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
    elif ext == '.docx':
        translate_docx_content(file_path, src_lang, dest_lang, reverse_arabic, exclude_keys)
    else:
        translated_content = translate_txt_content(content, src_lang, dest_lang, reverse_arabic, exclude_keys)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)

def translate_multiple_files(file_paths, src_lang='en', dest_lang='ar', reverse_arabic=False, exclude_keys=None):
    if exclude_keys is None:
        exclude_keys = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(translate_file, file_path, src_lang, dest_lang, reverse_arabic, exclude_keys) for file_path in file_paths]
        for future in futures:
            future.result()

def translate_files_in_directory(directory_path, src_lang='en', dest_lang='ar', reverse_arabic=False):
    for root, _, files in os.walk(directory_path):
        file_paths = [os.path.join(root, file) for file in files]
        translate_multiple_files(file_paths, src_lang, dest_lang, reverse_arabic)
