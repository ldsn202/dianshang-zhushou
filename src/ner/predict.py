# graph/src/models/ner/predict.py

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

from configuration import config
from pathlib import Path


class Predictor:
    def __init__(self, model, tokenizer, device):
        self.model = model.to(device)
        self.model.eval()
        self.tokenizer = tokenizer
        self.device = device

    def predict(self, inputs: str | list, batch_size=8):
        is_str = isinstance(inputs, str)

        if is_str:
            inputs = [inputs]

        predictions = []

        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]

            # 按字切分
            batch_tokens = [list(text) for text in batch]

            # tokenizer
            batch_inputs = self.tokenizer(
                batch_tokens,
                return_tensors="pt",
                padding=True,
                truncation=True,
                is_split_into_words=True
            )
            # 将value（张量）移动到self.
            batch_inputs = {k: v.to(self.device) for k, v in batch_inputs.items()}

            with torch.no_grad():
                outputs = self.model(**batch_inputs)
                logits = outputs.logits
                batch_preds = torch.argmax(logits, dim=-1).tolist()

            # 对齐 + 去掉 [CLS]
            for tokens, pred in zip(batch_tokens, batch_preds):
                pred = pred[1:1 + len(tokens)]
                pred = [self.model.config.id2label[i] for i in pred]
                predictions.append(pred)

        return predictions[0] if is_str else predictions

    def extract(self, inputs: str | list):
        is_str = isinstance(inputs, str)

        if is_str:
            inputs = [inputs]

        inputs = [text.replace(" ", "") for text in inputs]

        pred_results = self.predict(inputs)

        results = []
        for text, labels in zip(inputs, pred_results):
            results.append(self._bio_to_entities(text, labels))

        return results[0] if is_str else results

    def _bio_to_entities(self, tokens, labels):
        entities = []
        entity = ""

        for token, label in zip(tokens, labels):
            if label == "B":
                # 刚开始entity为空
                if entity:
                    entities.append(entity)
                entity = token

            elif label == "I":
                if entity:
                    entity += token

            else:  # O
                if entity:
                    entities.append(entity)
                    entity = ""
# B,I在最后
        if entity:
            entities.append(entity)

        return entities


if __name__ == '__main__':
    model_path = r"E:\PythonProject5\checkpoints\ner\best_model"
    model = AutoModelForTokenClassification.from_pretrained(str(model_path))
    tokenizer=AutoTokenizer.from_pretrained(str(model_path))

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    predictor = Predictor(model, tokenizer, device)

    inputs = [
        "2018秋冬季新款韩版平底高帮鞋女休闲二棉鞋加绒运动厚底高邦鞋潮",
        "2018秋冬季新款韩版平底高帮鞋女休闲二棉鞋加绒运动厚底高邦鞋潮"
    ]

    result = predictor.extract(inputs)
    print(result)