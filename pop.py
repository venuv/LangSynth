from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.chat_models import PromptLayerChatOpenAI
import chromadb
from chromadb.config import Settings


from utilities import generate_population, get_hidden_directory_name, create_dir_if_not_exists, read_config_file, partial_template_resolver


llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.9)
# you can use PromptLayer to debug if you like
#llm = PromptLayerChatOpenAI(pl_tags=["langchain"],temperature=0.9,return_pl_id=True)

# read config file and populate necessary synth population parameters
config = read_config_file() # recommended practice is to use dot langsynth as the config file name
db_dir = config.get('db_dir')
db_dir = get_hidden_directory_name(db_dir)
pt1 = config.get("persona_prompt")
pt2 = config.get("product_prompt")
collection_name = config.get('collection_name')
print(f"db_dir, prompts - {db_dir}, \n {pt1},\n\n {pt2}")

#Chroma initialize
create_dir_if_not_exists(db_dir)
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",persist_directory=db_dir))
#pop = chroma_client.create_collection(name="population")

# Demographic Prompt Section
demo1 = """\
first name, gender, age, \
decile range of age starting from 25 to 64 (25-34, 35-44,45-54,55-64), \
region - SouthEast, Northwest, Midwest, East, West, \
city and state - generate a credible city and state in the US, \
home type - apartment, condo, single-family, \

"""
demographic_prompt = ChatPromptTemplate.from_template(pt1)
chain_one = LLMChain(llm=llm, prompt=demographic_prompt,output_key="persona")

#Generate stories
stories_prompt = ChatPromptTemplate.from_template(pt2)
chain_two = LLMChain(llm=llm, prompt=stories_prompt, 
                     output_key="story"
                    )
#print(f"\n\n*** stories_prompt is {stories_prompt}")

product_collection = chroma_client.get_or_create_collection(name=collection_name)

stories = generate_population(llm, chain_one, chain_two, demo1,product_collection)

print(f"\n**** peek at evolving chroma collection -\n",product_collection.peek())

