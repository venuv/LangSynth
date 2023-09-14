import streamlit as st


import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap

from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI


import re
from textblob import TextBlob

import os

from utilities import set_api_key_from_file, load_files_noext, build_pop_joining
from pages.Products import load_product
from pages.Populations import load_population
from pages.Surveys import load_survey_wname


def click_generate():
    # load prod, pop, and survey
    prod_details = load_product(st.session_state.curr_product)
    pop_details = load_population(st.session_state.curr_population)
    survey_details = load_survey_wname(st.session_state.curr_survey)

    print(f'Loaded population: {pop_details}')

    result = build_pop_joining(prod_details, pop_details, survey_details, n=st.session_state.n_population, temperature=st.session_state.temp_population)

    return

def main():
    # set api key if needed
    if os.environ.get("OPENAI_API_KEY") is None:
        set_api_key_from_file()

    # load population file options
    population_options = load_files_noext('./populations')
    product_options = load_files_noext('./products')
    survey_options = load_files_noext('./surveys')

    # Setup Streamlit layout
    st.title("LangSynth")

    st.session_state.curr_product = st.selectbox("Select Product", options=sorted(product_options))
    st.session_state.curr_population = st.selectbox("Select Population", options=sorted(population_options))
    st.session_state.curr_survey = st.selectbox("Select Survey", options=sorted(survey_options))
    st.session_state.n_population = st.number_input("N (population)", min_value=1, value=5, step=1)
    st.session_state.temp_population = st.number_input("Temperature (population)", min_value=0.1, max_value=1.0, value=0.9, step=0.1)

    st.button('Generate Prod-Pop-Survey Stories', on_click=click_generate)

    #st.title(f'{curr_product} Synth Dashboard')

    return


if __name__ == '__main__':
    main()