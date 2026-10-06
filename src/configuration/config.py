import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
NER_DIR = 'ner'
RAW_DATA_DIR = DATA_DIR /NER_DIR/'raw'
PROCESSED_DATA_DIR = DATA_DIR /NER_DIR/'processed'

LOGS_DIR = ROOT_DIR / 'logs'
CHECKPOINT_DIR = ROOT_DIR / 'checkpoints'
# web静态目录
WEB_STATIC_DIR = ROOT_DIR / 'src'/'web'/'static'

RAW_DATA_FILE=str(RAW_DATA_DIR / 'data.json')
MODEL_NAME='google-bert/bert-base-chinese'

BATCH_SIZE=8
EPOCHS=5
LEARNING_RATE=1e-5
SAVE_STEPS=20

LABELS=['B','I','O']

MYSQL_CONFIG={
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': 'gmall',
}
NEO4J_CONFIG={
    'uri':"neo4j://localhost:7687",
    'auth':("neo4j", os.environ.get("NEO4J_PASSWORD", "")),
}

API_KEY=os.environ.get("DEEPSEEK_API_KEY", "")

