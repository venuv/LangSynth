from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.chat_models import PromptLayerChatOpenAI
import chromadb
from chromadb.config import Settings
import pandas as pd
from time import sleep
from transformers import pipeline
import re

from utilities import get_hidden_directory_name, create_dir_if_not_exists, read_config_file

llm = ChatOpenAI(temperature=0.2)

# Define the classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


# Define the labels
labels = ['Mild', 'Moderate', 'Severe', 'Very Severe']
def extract_severity(story):
    result = classifier(story, labels)
    predicted_label = result["labels"][result["scores"].index(max(result["scores"]))]
    print(f"Severity - {predicted_label}")
    return predicted_label

regions = ['Midwest', 'Southwest', 'Southeast', 'East', 'Northwest', 'Northeast','South','Southwest']
def region_fix_llm(sentence):
    result = classifier(sentence, regions)
    predicted_label = result["labels"][result["scores"].index(max(result["scores"]))]
    print(f"Severity - {predicted_label}")
    if predicted_label not in labels:
        predicted_label = "Moderate"
    return predicted_label

def correct_region(sentence):
    regions = ['Midwest', 'Southwest', 'Southeast', 'East', 'Northwest', 'Northeast']
    for region in regions:
        if re.search(fr'\b{region}\b', sentence, re.IGNORECASE):
            return region
    return region_fix_llm(sentence)


config = read_config_file()
db_dir = config.get('db_dir')
db_dir = get_hidden_directory_name(db_dir)
collection_name = config.get('collection_name')
dashboard_input_file = config.get('dashboard_input_file')

chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",persist_directory=db_dir))
collection = chroma_client.get_or_create_collection(name=collection_name)

size = collection.count()
foo = collection.get(
    include=["documents","metadatas"]
    
)
print(f"collection size is {size}")

# Convert each item in foo to a new dictionary where the keys of 'metadatas' are top-level
# and 'document' is replaced with 'story'.
expanded_foo = [
    {**metadata, 'story': document} for metadata, document in zip(foo['metadatas'], foo['documents'])
]


# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(expanded_foo)
df['severity'] = df['story'].apply(extract_severity)
df['region'] = df['region'].apply(correct_region)

print(f"Data being exported to {dashboard_input_file} is: \n {df}")
df.to_excel(dashboard_input_file, index=False)

