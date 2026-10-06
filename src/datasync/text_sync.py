import torch
from transformers import AutoTokenizer,AutoModelForTokenClassification
from configuration import *
from utils import MysqlReader,Neo4jWriter
from ner.predict import Predictor
class TextSynchronizer:
    def __init__(self):
        self.reader=MysqlReader()
        self.writer=Neo4jWriter()
        self.extractor=self._init_extractor()

    def _init_extractor(self):
        model_path = r"E:\PythonProject5\checkpoints\ner\best_model"
        model = AutoModelForTokenClassification.from_pretrained(str(model_path))
        tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return Predictor(model, tokenizer, device)

    def sync_tag(self):
        sql="""
        select id,description
        from spu_info
        """
        spu_desc=self.reader.read(sql)#读出来是字典
        ids=[item['id'] for item in spu_desc]
        descs=[item['description'] for item in spu_desc]

        tags_list=self.extractor.extract(descs)
        tag_properties=[]
        relations=[]
        for id,tags in zip(ids,tags_list):
            for index,tag in enumerate(tags):
                tag_id='_'.join([str(id),str(index)])
                property={'id':tag_id,'name':tag}
                tag_properties.append(property)
                relation={'start_id':id,'end_id':tag_id}
                relations.append(relation)
        self.writer.write_nodes("Tag",tag_properties)
        self.writer.write_relations('Have','SPU','Tag',relations)
        #     print(id,tags)


if __name__ == "__main__":
    synchronizer=TextSynchronizer()
    synchronizer.sync_tag()
