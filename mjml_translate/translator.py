import os
import re
import subprocess
import logging
from google import genai
from google.genai import types


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=API_KEY)

langMapping = {
    "es": "Spanish",
    "fr": "French",
    "id": "Indonesian",
    "vi": "Vietnamese",
    "pt": "Portuguese",
    "pt-br": "Portuguese-Brazilian",
    "ru": "Russian",
    "ro": "Romanian",
    "uk": "Ukrainian"
}

def gemini_call(language: str, lang_code: str, templateContent: str):
    try:
        sys_instruct = (
            f"Convert the following MJML code to {language} (also identified by language code: {lang_code}). "
            "Don't provide any filler content or explanations, just pure code! Never add any attributes to "
            "the starting tag, i.e., '<mjml>' or its closing tag at EOF </mjml> (regardless of language). "
            "I'm only going to be fetching the code enclosed between <mjml> and </mjml> so it better follow this exact format."
        )
        response = genai.generate_content(
            model="gemini-1.5-flash",
            contents=[templateContent],
            generation_config=types.GenerationConfig(
                system_instruction=sys_instruct
            )
        )
        content = response.text
        logging.info(f"Received response from Gemini for {language}")

        match = re.search(r'(?i)<mjml>.*?</mjml>', content, re.DOTALL)
        final_file = match.group(0) if match else None
        if not final_file:
            logging.warning(f"No <mjml> content found in Gemini response for {language}")
        return final_file
    except Exception as e:
        logging.error(f"Error during gemini_call for {language}: {e}")
        return None

def get_changed_mjml_files():
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        files = result.stdout.strip().split('\n')
        mjml_files = [f for f in files if f.endswith(".mjml")]
        logging.info(f"Changed MJML files: {mjml_files}")
        return mjml_files
    except subprocess.CalledProcessError as e:
        logging.error(f"Git diff command failed: {e.stderr}")
        return []

def translate_changed_mjml_files():
    changed_files = get_changed_mjml_files()
    if not changed_files or changed_files == ['']:
        logging.info("No MJML files changed. Exiting.")
        return []

    new_files = []

    for filepath in changed_files:
        if not os.path.isfile(filepath):
            logging.warning(f"File {filepath} not found, skipping.")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logging.error(f"Failed to read {filepath}: {e}")
            continue

        folder = os.path.dirname(filepath)
        base_filename = os.path.splitext(os.path.basename(filepath))[0]

        if '_' in base_filename:
            base, original_lang = base_filename.rsplit('_', 1)
        else:
            base = base_filename
            original_lang = 'en'

        for code, language in langMapping.items():
            if code == original_lang:
                continue

            translated = gemini_call(language, code, content)
            if translated is None:
                logging.warning(f"No translation for {filepath} in {language}, skipping.")
                continue

            new_filename = os.path.join(folder, f"{base}_{code}.mjml")
            try:
                with open(new_filename, "w", encoding="utf-8") as out_f:
                    out_f.write(translated)
                logging.info(f"Saved {new_filename}")
                new_files.append(new_filename)
            except Exception as e:
                logging.error(f"Failed to write {new_filename}: {e}")

    return new_files
