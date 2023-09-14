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
    return predicted_label

def correct_region(sentence):
    regions = ['Midwest', 'Southwest', 'Southeast', 'East', 'Northwest', 'Northeast']
    for region in regions:
        if re.search(fr'\b{region}\b', sentence, re.IGNORECASE):
            return region
    return region_fix_llm(sentence)

def predict_label_nli(story:str, labels:[str]):
    '''
    Uses an NLI model to predict a label (from the given sequence of labels) from the given story

    Parameters
    ----------
    story: text to predict label from
    labels: sequence of labels from which to predict

    Returns: the predicted label
    -------

    '''
    result = classifier(story, labels)
    predicted_label = result["labels"][result["scores"].index(max(result["scores"]))]
    return predicted_label


def parse_label_from_txt(sentence:str, labels:[str]):
    '''
    Searches a given sentence for any of [labels] and returns the first occuring label

    Parameters
    ----------
    sentence: sentence to search for [labels]
    labels: array of labels to search for

    Returns: first label from [labels] found
    -------

    '''
    for label in labels:
        if re.search(fr'\b{label}\b', sentence, re.IGNORECASE):
            return label
    return None


def get_label(sentence:str, labels:[str], skip_search:bool=False):
    '''
    Finds the label (from a selection of given labels) that most matches given a sentence.
    A simple regex search is performed first, and if no label is found then an NLI model is used to predict the label.
    The regex search can optionally be skipped.

    Parameters
    ----------
    sentence: text to search/predict label from
    labels: selection of labels to choose from
    skip_search: whether to skip the regex search (True to skip regex search and use NLI instead)

    Returns label given sentence
    -------

    '''
    label = None

    if not skip_search:
        label = parse_label_from_txt(sentence, labels)

    if label is None or skip_search:
        label = predict_label_nli(sentence, labels)

    return label



chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",persist_directory="./.zevo"))
collection = chroma_client.get_or_create_collection(name="zevo_raw")

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
#expanded_foo['severity'] = expanded_foo['story'].apply(extract_severity)
#size = expanded_foo.count()
#print(f"collection size is {size}")

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(expanded_foo)
df['severity'] = df['story'].apply(extract_severity)
df['region'] = df['region'].apply(correct_region)

print(df)
df.to_excel('zevo_population.xlsx', index=False)

