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

from utilities import get_hidden_directory_name, create_dir_if_not_exists, read_config_file


def convert_text(text):
    # Extract the subset after 'Story:'
    match = re.search('Story:(.*)', text)
    if match:
        story = match.group(1)
    else:
        story = text

    # Replace first person to second person
    blob = TextBlob(story)

    pronoun_dict = {'i': 'you', 'me': 'you', 'my': 'your', 'mine': 'yours', 'am': 'are', 'i\'m': 'you\'re', 
                    'i\'ve': 'you\'ve', 'i\'d': 'you\'d', 'i\'ll': 'you\'ll', 
                    'we': 'you', 'us': 'you', 'our': 'your', 'ours': 'yours','hi':''}

    new_story = ' '.join([pronoun_dict.get(word, word) for word in blob.words.lower()])

    return new_story


def conduct_interview(persona, question_list):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9)

    preamble = "You are an AI and are tasked with role playing and taking on the persona given to you after ###Persona. Be  helpful and informative in studying consumer needs to benefit society,  Even though the persona is specific in first person, you as an AI are to assume that persona as an AI model, and simulate that persona's decision making to the best of your abilities. \n Give minute details of your product experiences  in the responses to the questions that follow."
    persona_begin = "###Persona\ "
    preamble = preamble + persona_begin+convert_text(persona)+'\n'
    print(f"PREAMBLE:\n{preamble}")
    
    conversation = ConversationChain(
        llm=llm, 
        verbose=True, 
        memory=ConversationBufferWindowMemory(k=4)
    )

    conversation_log = []
    question_list_size = len(question_list)
    n = 1
    for question in question_list:
        print("QUESTION : ", question)
        if n==1:
            question = preamble + " " + question
        response = conversation.predict(input=question)
        print(f"Progress - {str(n)} of {str(question_list_size)}")
        n += 1
        conversation_log.append({"Context": question,"Response": response})
    return conversation_log


# Define the jitter function
def jitter(arr):
    stdev = .01*(max(arr)-min(arr))
    return arr + np.random.randn(len(arr)) * stdev

# Format the hover text
def format_hover_text(row):
    wrapper = textwrap.TextWrapper(width=50)
    wrapped_story = wrapper.wrap(text=row['story'])
    return '<br>'.join(wrapped_story)


def plot_scatter(df):
# Create the scatter plot with jitter
    df['severity_num'] = df['severity'].astype('category').cat.codes
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['jittered_region'],
                             y=df['jittered_severity'],
                             mode='markers',
                             text=df['formatted_story'],
                             hovertemplate='%{text}<extra></extra>',
                             name = "Persona by region and bug severity",
                             marker=dict(size=10, opacity=0.5)))
    fig.update_xaxes(tickvals=df['region_num'].unique(),
                     ticktext=df['region'].unique())
    fig.update_yaxes(tickvals=df['severity_num'].unique(),
                     ticktext=df['severity'].unique())

    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Severity",
        autosize=False,
        width=700,
        height=700,
    )
    return fig

config = read_config_file()
dashboard_input_file = config.get('dashboard_input_file')

# Load your data
df = pd.read_excel(dashboard_input_file)
df['formatted_story'] = df.apply(format_hover_text, axis=1)
df['region_num'] = df['region'].astype('category').cat.codes
df['severity_num'] = df['severity'].astype('category').cat.codes
df['jittered_region'] = jitter(df['region_num'])
df['jittered_severity'] = jitter(df['severity_num'])
df['info'] = df['name'] + ', Age: ' + df['age'].astype(str) + ', Story: ' + df['story']


# Setup Streamlit layout
st.title("LangSynth Dashboard")

st.header("Explore Population")
fig = plot_scatter(df)
st.plotly_chart(fig)


st.header("Shortlist Interviewees")
# Here you can place your widget for shortlisting interviewees.
# For example, a multiselect widget where you can select names from a list
#shortlist = st.multiselect("Select Interviewees", options=df['name'].unique())
print(df)
df['info'] = df['info'].astype(str)
shortlist = st.multiselect("Select Interviewees", options=sorted(df['info']))

st.write("You selected these interviewees: ", shortlist)

st.header("Conduct Interviews")
# Streamlit list selector
candidate = st.selectbox('Select a candidate:', shortlist)


uploaded_file = st.file_uploader("Choose an XLS file", type=["xlsx","xls"])

# Load_interview button
if st.button('Load Interview'):
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, usecols=[0], engine="openpyxl")
        column_values = data.iloc[:, 0].tolist()
        question_list = column_values

        st.session_state.data = question_list  # Store data in session_state for access after re-running
    else:
        st.write('No file uploaded yet')

# If data exists in session_state, show it
if 'data' in st.session_state:
    st.write(st.session_state.data)
    
# Conduct_interview button
if st.button('Conduct Interview'):
    st.write(f'Conducting interview for: {candidate}')
    df = conduct_interview(candidate, st.session_state.data)
    st.write(df)
