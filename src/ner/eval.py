import evaluate
from datasets import load_from_disk
from transformers import (
    AutoModelForTokenClassification,
    Trainer,
    DataCollatorForTokenClassification,
    AutoTokenizer,
    EvalPrediction
)

from configuration.config import *
from configuration import config

test_dataset = load_from_disk(config.DATA_DIR / 'ner' / 'processed' / 'test')

model = AutoModelForTokenClassification.from_pretrained(
    config.CHECKPOINT_DIR / 'ner' / 'best_model'
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True
)

seqeval = evaluate.load("seqeval")


def compute_metrics(prediction: EvalPrediction) -> dict:
    logits = prediction.predictions
    preds = logits.argmax(axis=-1)
    labels = prediction.label_ids

    true_predictions = [
        [
            model.config.id2label[p]
            for p, l in zip(pred_seq, label_seq)
            if l != -100
        ]
        for pred_seq, label_seq in zip(preds, labels)
    ]

    true_labels = [
        [
            model.config.id2label[l]
            for l in label_seq
            if l != -100
        ]
        for label_seq in labels
    ]

    return seqeval.compute(
        predictions=true_predictions,
        references=true_labels
    )


trainer = Trainer(
    model=model,
    # tokenizer=tokenizer,
    eval_dataset=test_dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

metrics = trainer.evaluate()
print("评估结果", metrics)