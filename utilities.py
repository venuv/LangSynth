from langchain.chains import SimpleSequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import random
import string
import re
import os
from langchain.chat_models import PromptLayerChatOpenAI



def build_story_prompt(product, persona_elements, interview_questions):
    story_query = (
        # story preamble
        f'for each {{persona}} that has an awareness of {product["name"]} '
        f'they should first state their full persona details {", ".join(persona_elements)}'

        # personal details
        f'they should then tell their {product["name"]} ({product["product_type"]}, {product["url"] if "url" in product.keys() else ""}) story.  the story should be narrated in first person. i repeat all stories should be in first person starting off with Hi, I am ... every persona story should be in a single contiguous paragraph. should end the story with two carriage returns (aka newlines).'
        f'it should contain the following elements and be a single paragraph with no carriage returns- it should start off with all the persona details {", ".join(persona_elements)} '

        # interview questions
        f'{"? ".join(interview_questions)}'

        # negative case e.g., no knowledge of product.
        f'for persona\'s who do not have an awareness of {product["name"]}, the story should simply state in first person that they are not aware of {product["name"]} and also share the products they use for {product["outcome"]}.'
    )
    return story_query

# we may need to conditionally remove the "person" prefix to the attr_name in this prompt template. Need to see how this performs and check the results.
#TODO: write a test that iterates over the generalized and non-generalized functions and confirm that all pairs return the same value for a given attribute
def extract_attr(llm, intro, attr_name, attr_options=None, prompt_inputs={}, implied_by_key=None):
    # the attr that implies the attr we seek MUST be present in the prompt inputs, otherwise we cannot pass it in
    if implied_by_key is not None and implied_by_key not in prompt_inputs.keys():
        print(f'Error: implied_by_key specified but key is not present in prompt inputs (inputs argument)')
        #TODO: replace w/ exception

    # lots of conditional string building
    prompt_template = (
        # standard preamble
        f'return the person {attr_name} mentioned in {{intro}}'
        
        # only included if there is an implying attribute
        f'{", or implied by the {{0}}.".format(implied_by_key) if implied_by_key is not None else ""}. '
        
        # only included if attribute options are limited
        f'{"{0} can be - {1}.".format(attr_name, ", ".join(attr_options)) if attr_options is not None else ""}'
        
        # closing is based on whether there is a potential implying attribute or not
        f'{"if you are absolutely sure you cannot figure it out" if implied_by_key is not None else "if you are absolutely sure it is not present in the {intro}"}, return None'
    )

    extract_prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = LLMChain(llm=llm, prompt=extract_prompt)

    # combine our inputs with our intro
    prompt_inputs.update({'intro': intro})

    # get the response and return
    res = chain.run(prompt_inputs)
    return res

def extract_name(lm, intro):
    pt = "return the person name mentioned in  {intro}. if you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    name = chain.run(intro)
    return name

def extract_age(lm, intro):
    pt = "return the person age mentioned in  {intro}. if you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    age = chain.run(intro)
    return age

def extract_city(lm, intro):
    pt = "return the city mentioned in  {intro}. if you are absolutely sure it is not present in the {intro}, return None"
    xtract_prompt = ChatPromptTemplate.from_template(pt)
    chain = LLMChain(llm=lm, prompt=xtract_prompt)
    city = chain.run(intro)
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

    '''
    # Remove newlines from stories collective
    stories_without_newlines = stories.replace("\n", " ")
    #print(f"stories without newlines is {stories_without_newlines}")
    stories = re.split(r'(?=Hi, I am)', stories_without_newlines)
    '''

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


def set_api_key_from_file():
    key_file = open('./api_key.txt')
    line = key_file.readline()
    key = line.strip()
    print(f'Setting OPENAI API Key to {key}')
    os.environ["OPENAI_API_KEY"] = key
    os.environ["PROMPTLAYER_API_KEY"] = key
    return

def load_files_noext(from_dir):
    loaded_files = os.listdir(from_dir)
    loaded_files = [os.path.splitext(filename)[0] for filename in loaded_files]
    return loaded_files

# creates a population based on a popualtion, a product, and a survey
# TODO: explore the coupling of these 3 things and see how much we can untangle them for re-use

def generate_population_2(lm, demo_chain, stories_chain, seed_prompt, collection):
    story_chain = SimpleSequentialChain(
        chains=[demo_chain, stories_chain],
        verbose=True
    )

    raw_stories = story_chain.run(seed_prompt)
    #stories = process_stories(raw_stories, lm, collection)

    return raw_stories

# TODO: we need a way to target certain demos (ex: BigTape for construction workers
def build_pop_joining(product, population_params, survey, n=5, temperature=0.9):
    #llm = PromptLayerChatOpenAI(pl_tags=["langchain"], temperature=0.9, return_pl_id=True)
    llm = PromptLayerChatOpenAI(pl_tags=["langchain"], temperature=temperature, return_pl_id=True)

    demo_attr_strings = []
    for attribute in population_params['Attributes']:
        attr_string = attribute["Name"]
        if attribute['Has_Labels']:
            print(f'attr labels: {attribute["Labels"]}')
            attr_string = attr_string + ' - ' + attribute['Labels'] + ','
        demo_attr_strings.append(attr_string)
    joined_demo_attr_strs = '\n'.join(demo_attr_strings)
    print(f'Built demo attr strings:\n {joined_demo_attr_strs}')

    pt = f'Generate {n} persona and their demographic profiles as JSON strings with the following demographic information {{demographic}}'
    demographic_prompt = ChatPromptTemplate.from_template(pt)
    chain_one = LLMChain(llm=llm, prompt=demographic_prompt, output_key="persona")

    interview_questions = survey['Questions']
    story_query = (
        # story preamble
        f'for each {{persona}} that has an awareness of {product["Product Name"]} '
        f'they should first state their full persona details {", ".join(demo_attr_strings)}'

        # personal details
        f'they should then tell their {product["Product Name"]} ({product["Product Type"]}, {product["URL/Website"] if "URL/Website" in product.keys() else ""}) story.  the story should be narrated in first person. i repeat all stories should be in first person starting off with Hi, I am ... every persona story should be in a single contiguous paragraph. should end the story with two carriage returns (aka newlines).'
        f'it should contain the following elements and be a single paragraph with no carriage returns- it should start off with all the persona details {", ".join(demo_attr_strings)} '

        # interview questions
        f'{"? ".join(interview_questions)}'

        # negative case e.g., no knowledge of product.
        f'for persona\'s who do not have an awareness of {product["Product Name"]}, the story should simply state in first person that they are not aware of {product["Product Name"]} and also share the products they use for {product["Expected Outcome"]}.'
    )
    stories_prompt = ChatPromptTemplate.from_template(story_query)
    chain_two = LLMChain(llm=llm, prompt=stories_prompt, output_key="story")

    population = generate_population_2(llm, chain_one, chain_two, joined_demo_attr_strs, None)
    return

def build_population_joining(product, population, survey):
    demo_attr_strings = build_demographic_prompt(population)
    return
