from langchain.chains import SimpleSequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import random
import string
import re
import json
import os

def partial_template_resolver(var, value, target):
    return target.replace(f'{{{var}}}', value)

def read_config_file(file_name=".langsynth"):
    with open(file_name, 'r') as f:
        config = json.load(f)

    return config

def get_hidden_directory_name(base_name):
    return "./." + base_name

def create_dir_if_not_exists(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
def extract_name(lm, intro):
    pt = "return the person name mentioned in  {intro}. it is the word after the words I am. if you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    name = chain.run(intro)
    print(f"[EXTRACT_NAME] {name}: {intro}")
    return name

def extract_age(lm, intro):
    pt = "return the person age mentioned in  {intro}. it is a number based word like 35, or a word with dashes like 35-44.if you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    age = chain.run(intro)
    print(f"[EXTRACT_AGE] {age}:{intro}")
    return age

def extract_city(lm, intro):
    pt = "return the city mentioned in  {intro}. if you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    city = chain.run(intro)
    print(f"[EXTRACT_CITY] {city}:{intro}")    
    return city

def extract_region(lm, intro, city):
    pt = "return the region mentioned in  {intro}, or implied by the {city}. regions can be - northeast, midwest, souteast, south, southwest, west and northwest. if you are absolutely sure you cannot figure it out, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    region = chain.run({'intro':intro,'city':city})
    return region

def extract_home_type(lm, intro):
    pt = "return the home type if  mentioned in  {intro}. home type is - apartment, condo, or single family homeif you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    hometype = chain.run(intro)    
    return hometype

def generate_random_string(length):
    # Choose from all uppercase and lowercase letters and digits
    chars = string.ascii_letters + string.digits

    # Use a list comprehension to generate a list of 'length' random characters
    random_string = ''.join(random.choice(chars) for _ in range(length))

    return random_string


def process_stories(stories,lm,collection):

    lm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0) # a more deterministic LLM for compilin story!
    
    stories = re.split(r'(?=Hi, I am)', stories)
    stories = [story for story in stories if re.search('[a-zA-Z]', story)]

    ids = []
    metadatas = []
    documents = []
    for story in stories:
        intro_sentence = story.split(".")[0]
        city=extract_city(lm, intro_sentence)
        person_info = {
            'name':extract_name(lm, intro_sentence),
            'age':extract_age(lm,intro_sentence),
            'city':city,
            'region':extract_region(lm, intro_sentence,city),
            'hometype':extract_home_type(lm, intro_sentence)
            }
        id = generate_random_string(8)
        documents.append(story)
        metadatas.append(person_info)
        ids.append(id)
        print(f"Metadata--{person_info}")
        
    collection.add(documents=documents,
                   metadatas=metadatas,
                   ids=ids)
    return stories
              
# generate population - generate stories. extract metadata. persist to vectordb - populate collection. save collection. return stories
def generate_population(lm, demo_chain, stories_chain, seed_prompt,collection):
    story_chain = SimpleSequentialChain(
        chains=[demo_chain,stories_chain],
        verbose=True
    )

    raw_stories = story_chain.run(seed_prompt)
    stories = process_stories(raw_stories,lm,collection)
    
    return stories
