from datasets import load_dataset
from transformers import AutoTokenizer

from configuration.config import *

from src.configuration.config import RAW_DATA_FILE


def process():
    """
     load_dataset会将data内部转换为
DatasetDict({train: Dataset({ features: ['text', 'id', 'label', 'annotator', 'annotation_id', ...],
        num_rows: 2  # 你有2条数据})
})
然后只取train的部分
    """
    dataset = load_dataset('json',data_files=RAW_DATA_FILE)['train']
    dataset=dataset.remove_columns(['id', 'annotator', 'annotation_id', 'created_at', 'updated_at', 'lead_time'])
    dataset_dict=dataset.train_test_split(test_size=0.2)
    dataset_dict['test'],dataset_dict['valid']=dataset_dict['test'].train_test_split(test_size=0.5).values()
    tokenizer=AutoTokenizer.from_pretrained(MODEL_NAME)
    def encode(example):
        tokens=list(example['text'])#example指的是单条数据
        inputs=tokenizer(tokens,is_split_into_words=True,truncation=True)
        entities=example['label']
        labels=[LABELS.index('O')]*len(tokens)
        for entity in entities:
            start=entity['start']
            end=entity['end']
            labels[start:end]=[LABELS.index('B')]+[LABELS.index('I')]*(end-start-1)
        labels=[-100]+labels+[-100]
        inputs['labels']=labels #前面出现过
        return inputs
    dataset_dict=dataset_dict.map(encode,remove_columns=['text','label'])#map对数据集中的每条数据应用函数
    print(dataset_dict['train'][0])
    dataset_dict.save_to_disk(PROCESSED_DATA_DIR)

if __name__ == "__main__":
    process()