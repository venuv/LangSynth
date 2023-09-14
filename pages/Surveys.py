import os
import streamlit as st
import os.path as osp
import sys
import copy
import json


sys.path.append('../')
from utilities import load_files_noext

NEW_SURVEY_TEMPLATE = {
    'Name': '',
    'Questions': []
}

SURVEY_DIR = './surveys'

if 'NEW_SURVEY_MODE' not in st.session_state:
    st.session_state.NEW_SURVEY_MODE = False

def build_survey_filepath(survey_name):
    filename = survey_name+'.json'
    return osp.join(SURVEY_DIR, filename)


def new_survey():
    st.session_state.NEW_SURVEY_MODE = True
    st.session_state.curr_survey_data = copy.deepcopy(NEW_SURVEY_TEMPLATE)
    return


def new_survey_question():
    st.session_state.curr_survey_data['Questions'].append('')
    return


def load_survey():
    survey_name = st.session_state.curr_survey_selection
    filepath = build_survey_filepath(survey_name)
    json_file = open(filepath)
    survey_data = json.load(json_file)
    json_file.close()
    return survey_data

def load_survey_wname(survey_name):
    filepath = build_survey_filepath(survey_name)
    json_file = open(filepath)
    survey_data = json.load(json_file)
    json_file.close()
    return survey_data


def save_survey():
    survey_name = st.session_state.curr_survey_data['Name']
    filepath = build_survey_filepath(survey_name)
    json_file = open(filepath, "w")
    json.dump(st.session_state.curr_survey_data, json_file)
    json_file.close()
    return

def delete_survey():

    return

def cancel_new_survey():

    return

def survey_list_changed():
    if st.session_state.curr_survey_selection != 'None Selected':
        st.session_state.curr_survey_data = load_survey()
    else:
        st.session_state.curr_survey_data = None
    return







def main():
    survey_options = load_files_noext(SURVEY_DIR)

    st.title('Surveys')

    st.session_state.curr_survey = st.selectbox("Select Survey", options=['None Selected'] + sorted(survey_options), key='curr_survey_selection', on_change=survey_list_changed)

    st.button('New Survey', on_click=new_survey)

    if st.session_state.curr_survey != 'None Selected' and not st.session_state.NEW_SURVEY_MODE:
        st.session_state.curr_survey_data['Name'] = st.text_input('Name', st.session_state.curr_survey_data['Name'])
        for i in range(len(st.session_state.curr_survey_data['Questions'])):
            st.session_state.curr_survey_data['Questions'][i] = st.text_area(f'Question {i+1}', st.session_state.curr_survey_data['Questions'][i], key=f'survey_q_{i}')
        button_col_1, button_col_2, button_col_3 = st.columns(3)
        button_col_1.button('Delete', on_click=delete_survey)
        button_col_2.button('Add Question', on_click=new_survey_question)
        button_col_3.button('Save', on_click=save_survey)
    elif st.session_state.NEW_SURVEY_MODE:
        st.session_state.curr_survey_data['Name'] = st.text_input('Name', st.session_state.curr_survey_data['Name'])
        for i in range(len(st.session_state.curr_survey_data['Questions'])):
            st.session_state.curr_survey_data['Questions'][i] = st.text_area(f'Question {i + 1}', st.session_state.curr_survey_data['Questions'][i], key=f'survey_q_{i}')
        button_col_1, button_col_2, button_col_3 = st.columns(3)
        button_col_1.button('Cancel', on_click=cancel_new_survey)
        button_col_2.button('Add Question', on_click=new_survey_question)
        button_col_3.button('Save', on_click=save_survey)


    return



if __name__ == '__main__':
    main()