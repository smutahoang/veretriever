import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# from transformers import AutoModelForSequenceClassification
# import torch
# import time
# from langdetect import detect_langs

dict_map = {
    "òa": "oà",
    "Òa": "Oà",
    "ÒA": "OÀ",
    "óa": "oá",
    "Óa": "Oá",
    "ÓA": "OÁ",
    "ỏa": "oả",
    "Ỏa": "Oả",
    "ỎA": "OẢ",
    "õa": "oã",
    "Õa": "Oã",
    "ÕA": "OÃ",
    "ọa": "oạ",
    "Ọa": "Oạ",
    "ỌA": "OẠ",
    "òe": "oè",
    "Òe": "Oè",
    "ÒE": "OÈ",
    "óe": "oé",
    "Óe": "Oé",
    "ÓE": "OÉ",
    "ỏe": "oẻ",
    "Ỏe": "Oẻ",
    "ỎE": "OẺ",
    "õe": "oẽ",
    "Õe": "Oẽ",
    "ÕE": "OẼ",
    "ọe": "oẹ",
    "Ọe": "Oẹ",
    "ỌE": "OẸ",
    "ùy": "uỳ",
    "Ùy": "Uỳ",
    "ÙY": "UỲ",
    "úy": "uý",
    "Úy": "Uý",
    "ÚY": "UÝ",
    "ủy": "uỷ",
    "Ủy": "Uỷ",
    "ỦY": "UỶ",
    "ũy": "uỹ",
    "Ũy": "Uỹ",
    "ŨY": "UỸ",
    "ụy": "uỵ",
    "Ụy": "Uỵ",
    "ỤY": "UỴ",
}

tokenizer_vi2en = AutoTokenizer.from_pretrained("vinai/vinai-translate-vi2en", src_lang="vi_VN")
model_vi2en = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en")

tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi", src_lang="en_XX")
model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi")

device = torch.device('cuda:1')

model_en2vi.to(device)
model_vi2en.to(device)


def translate_en2vi(en_text: str) -> str:
    input_ids = tokenizer_en2vi(en_text, return_tensors="pt").input_ids.to(device)
    output_ids = model_en2vi.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
    )
    vi_text = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
    vi_text = " ".join(vi_text)
    return vi_text


def translate_vi2en(vi_text: str) -> str:
    for i, j in dict_map.items():
        vi_text = vi_text.replace(i, j)
    input_ids = tokenizer_vi2en(vi_text, return_tensors="pt").input_ids.to(device)
    output_ids = model_vi2en.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_vi2en.lang_code_to_id["en_XX"],
        num_return_sequences=1,
    )
    en_text = tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
    en_text = " ".join(en_text)
    return en_text


def batch_translate_vi2en(vi_texts: str, batch_size=64) -> str:
    normalized_vi_texts = []
    for vi_text in vi_texts:
        for i, j in dict_map.items():
            vi_text = vi_text.replace(i, j)
        normalized_vi_texts.append(vi_text)
    translated = []
    start = 0
    end = min(start + batch_size, len(normalized_vi_texts))
    while end <= len(normalized_vi_texts):
        batch = normalized_vi_texts[start:end]
        input_ids = tokenizer_vi2en(batch, return_tensors="pt", padding=True).input_ids.to(device)
        output_ids = model_vi2en.generate(
            input_ids,
            do_sample=True,
            top_k=100,
            top_p=0.8,
            decoder_start_token_id=tokenizer_vi2en.lang_code_to_id["en_XX"],
            num_return_sequences=1,
        )
        en_text = tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
        translated.extend(en_text)
        if end < len(normalized_vi_texts):
            start = end
            end = min(start + batch_size, len(normalized_vi_texts))
        else:
            break

    return translated
