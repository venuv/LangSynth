from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.chat_models import PromptLayerChatOpenAI
import chromadb
from chromadb.config import Settings


from utilities import generate_population


#llm = ChatOpenAI(temperature=0.9)
llm = PromptLayerChatOpenAI(pl_tags=["langchain"],temperature=0.9,return_pl_id=True)

#Chroma initialize
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",persist_directory="./.zevo"))
#pop = chroma_client.create_collection(name="population")

# Demographic Prompt Section
demo1 = """\
first name, gender, age, \
decile range of age starting from 25 to 64 (25-34, 35-44,45-54,55-64), \
region - SouthEast, Northwest, Midwest, East, West, \
city and state - generate a credible city and state in the US, \
home type - apartment, condo, single-family, \

"""
pt = "Generate 5 persona and their demographic profiles as JSON strings with the following demographic information {demographic}"
demographic_prompt = ChatPromptTemplate.from_template(pt)
chain_one = LLMChain(llm=llm, prompt=demographic_prompt,output_key="persona")

#Generate stories
pt2 = "for each {persona} that has an awareness of Zevo, they should first state their full persona details (name, gender, age, age decile, region, city, state, home type). they should then tell their Zevo (bug product, https://zevoinsect.com/all-products/) story.  the story should be narrated in first person. i repeat all stories should be in first person starting off with Hi, I am ... every persona story should be in a single contiguous paragarph. should end the story with two carriage returns (aka newlines). \
 \
it should contain the following elements and be a single paragraph with no carriage returns- it should start off with all the persona details (name, gender, age, age decile, city, region e.g. southeast, home type e.g. apartment/single family/). how bad is the bug problem in the area they live? when and how did he/she become aware of Zevo?  what made them go try Zevo (or not try it), and how may weeks had they been aware of the product before their first trial? what specific product(s) (competitor brand and product name really important!) were they previously using before they switched to Zevo.  did he/she use for bug management before Zevo? what was their first use experience with the Zevo- specifically what was the bug problem, what level of improvement were they expecting, did the product do well enough or truly delight? if delight, say more about how it delighted?? what specifically is the most difficult 'job' that Zevo has done for them (in which room of the house? what kind of bug? during what month of the year? how bad was it). how long have they been using Zevo and how frequently? is their bug problem seasonal and if so what months of the year? if they have slowed down or stopped using Zevo, is it for seasonal reasons or because they no longer find the product useful? have they been made aware of new products that may be alternatives to Zevo. \
for persona's who do not have an awareness of Zevo, the story should simply state in first person that they are not aware of Zevo and also share the products they use for bug and pest control. \
."


stories_prompt = ChatPromptTemplate.from_template(pt2)
chain_two = LLMChain(llm=llm, prompt=stories_prompt, 
                     output_key="story"
                    )

#stories = chain_two.run(pt2)

zevo_collection = chroma_client.get_or_create_collection(name="zevo_raw")
stories = generate_population(llm, chain_one, chain_two, demo1,zevo_collection)

print(f"\npeek at chroma collection -\n",zevo_collection.peek())

