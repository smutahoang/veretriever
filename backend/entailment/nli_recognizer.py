from langdetect import detect_langs, DetectorFactory
from vncorenlp import VnCoreNLP
import torch
import warnings

warnings.filterwarnings("ignore")


class NliPredictor:
    """

    """

    def __init__(self, vi_tokenizer, model_type, model_path, device='cuda', silent=True, label_map=None):

        DetectorFactory.seed = 0
        self.vi_tokenizer = vi_tokenizer
        if model_type == 'xlmroberta':
            from transformers import XLMRobertaTokenizerFast, XLMRobertaForSequenceClassification
            self.nli_model = XLMRobertaForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = XLMRobertaTokenizerFast.from_pretrained(model_path)
        elif model_type == 'bert':
            from transformers import BertForSequenceClassification, BertTokenizerFast
            self.nli_model = BertForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = BertTokenizerFast.from_pretrained(model_path)
        if label_map:
            self.label_map = label_map
        else:
            self.label_map = {'Agree': 0, 'Neutral': 1, 'Disagree': 2}

        self.id_to_label = {value: key for key, value in self.label_map.items()}

        self.nli_model.to(device)
        self.nli_model.eval()
        self.device = device

    def language_detect(self, text):

        langs = detect_langs(text)

        if langs[0].lang == 'vi':
            return 'vi'
        else:
            return 'en'

    def predict(self, text1, text2):

        encode_input = self.makeInputEncode(self.makeInputText(text1, text2))

        batch = {k: v.to(self.device) for k, v in encode_input.items()}
        with torch.no_grad():
            outputs = self.nli_model(batch['input_ids'], token_type_ids=None, attention_mask=batch['attention_mask'])
            logits = outputs.logits

        predictions = torch.argmax(logits, dim=-1)
        predictions = predictions.detach().clone().cpu().numpy()

        return self.id_to_label[predictions[0]]

    def makeInputText(self, text1, text2):
        note = 'The model only supports vi and en languages'

        lang1 = self.language_detect(text1)

        lang2 = self.language_detect(text2)
        input_text = []
        if lang1 == 'vi':
            text1 = self.vi_tokenizer.tokenize(text1)
            text1 = ' '.join([' '.join(x) for x in text1])
        if lang2 == 'vi':
            text2 = self.vi_tokenizer.tokenize(text2)
            text2 = ' '.join([' '.join(x) for x in text2])

        if lang2 == 'en':
            input_text = [text2 + ' [SEP] ' + text1]
        else:
            input_text = [text1 + ' [SEP] ' + text2]

        return input_text

    def makeInputEncode(self, inputText):
        encode_input = self.tokenizer(inputText, return_tensors="pt", padding=True, truncation=True, max_length=128)

        for k in encode_input:
            encode_input[k] = torch.tensor(encode_input[k])

        return encode_input


def toy():
    text1 = 'Các bác sĩ BVĐK Đồng Nai vừa phẫu thuật cứu sống một bé trai 5 tuổi bị chấn thương, vỡ sọ não.'
    text2 = 'Nam thanh niên đã được chuyển tới Bệnh viện Đa Khoa tỉnh Đồng Nai trong tình trạng chấn thương sọ não nhưng do mất máu quá nhiều nên cậu đã không qua khỏi.'

    rdrsegmenter = VnCoreNLP(r"../../../PhoBERT/vncorenlp/VnCoreNLP-1.1.1.jar",
                             annotators="wseg", max_heap_size='-Xmx500m')

    model_type = 'xlmroberta'
    model_path = 'full_data_xlm_model_20_epoch'
    nli_predictor = NliPredictor(rdrsegmenter, model_type, model_path, device='cuda')

    print("sen pair:")
    print(text1)
    print(text2)
    print('Result:', nli_predictor.predict(text1, text2))
