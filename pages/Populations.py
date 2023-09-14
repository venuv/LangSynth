import os

import streamlit as st
import pandas as pd
import os.path as osp
import sys
import copy
import json


sys.path.append('../')
from utilities import load_files_noext

NEW_POPULATION_TEMPLATE = {
    'Name': '',
    'Attributes': [],
}

NEW_ATTRIBUTE_TEMPLATE = {
    'Name': 'New Attribute',
    'Has_Labels': False,
    'Labels': None,
    'Is_Implied': False,
    'Implied_By': None,
    'Has_Clarifiers': False,
    'Clarifiers': None
}


POPULATIONS_DIR = './populations'

if 'NEW_POP_MODE' not in st.session_state:
    st.session_state.NEW_POP_MODE = False


def build_population_filepath(population_name):
    filename = population_name+'.json'
    return osp.join(POPULATIONS_DIR, filename)

def new_population():
    st.session_state.NEW_POP_MODE = True
    print(f'New Population: {st.session_state.NEW_POP_MODE}')
    st.session_state.curr_pop_data = copy.deepcopy(NEW_POPULATION_TEMPLATE)
    return

def new_pop_attr():
    print(f'Template: {NEW_ATTRIBUTE_TEMPLATE}')
    new_attr_data = copy.deepcopy(NEW_ATTRIBUTE_TEMPLATE)
    st.session_state.curr_pop_data['Attributes'].append(new_attr_data)
    return

def load_population(population_name):
    filepath = build_population_filepath(population_name)
    json_file = open(filepath)
    population_data = json.load(json_file)
    json_file.close()
    #population_dict = population_data.to_dict()
    population_dict = population_data
    print(population_dict)

    st.session_state.curr_pop_data = population_data
    return population_data

def save_population():
    #TODO: validate pop values, ex: name must not be blank
    #population_df = pd.DataFrame(st.session_state.curr_pop_data, index=[0])
    #population_df = pd.DataFrame(st.session_state.curr_pop_data.items(), columns=st.session_state.curr_pop_data.keys())

    out_path = osp.join(POPULATIONS_DIR, st.session_state.curr_pop_data['Name']+'.json')
    print(f'Save to {out_path}')
    json_file = open(out_path, 'w')
    json.dump(st.session_state.curr_pop_data, json_file, indent=2)
    json_file.close()
    #population_df.to_excel(out_path)
    #st.session_state.curr_pop =
    #st.session_state.curr_pop_data = None
    # if population is a new population, flip off new population mode
    if st.session_state.NEW_POP_MODE:
        st.session_state.NEW_POP_MODE = False
    print(f'New Prod Save: {st.session_state.NEW_POP_MODE}')
    return

def delete_population():
    filepath = build_population_filepath(st.session_state.curr_pop)
    os.remove(filepath)
    st.session_state.curr_pop_data = None
    st.session_state.curr_pop = 'None Selected'
    return

def cancel_new_population():
    st.session_state.curr_pop = 'None Selected'
    st.session_state.curr_pop_data = None
    st.session_state.NEW_POP_MODE = False
    return

def flip_attr_val(attribute, key):
    attribute[key] = not attribute[key]
    return

def set_state_all_attr_names():
    attr_names = []
    for attr in st.session_state.curr_pop_data['Attributes']:
        attr_names.append(attr['Name'])
    st.session_state.all_attr_names = attr_names
    return

def pop_list_changed():
    if st.session_state.curr_pop_selection == 'None Selected': return
    st.session_state.curr_pop = st.session_state.curr_pop_selection
    load_population(st.session_state.curr_pop)
    return


def main():

    population_options = load_files_noext(POPULATIONS_DIR)

    st.title('Populations')

    st.session_state.curr_pop = st.selectbox("Select Product", options=sorted(['None Selected'] + population_options), on_change=pop_list_changed, key='curr_pop_selection')
    st.button('New Population', on_click=new_population)

    if st.session_state.curr_pop != 'None Selected' and not st.session_state.NEW_POP_MODE:

        if 'curr_pop_data' not in st.session_state:
            pop_list_changed()

        st.session_state.curr_pop_data['Name'] = st.text_input('Name', st.session_state.curr_pop_data['Name'])
        #st.session_state.curr_pop_data = copy.deepcopy(NEW_POPULATION_TEMPLATE)
        print(f'Pop State: {st.session_state.curr_pop_data}')

        if 'all_attr_names' not in st.session_state:
            set_state_all_attr_names()

        counter = 0
        for attribute in st.session_state.curr_pop_data['Attributes']:
            print(f'Attr_{counter} {attribute}')
            print(f'{attribute["Name"]}')
            attr_expander = st.expander(attribute['Name'])
            attribute['Name'] = attr_expander.text_input('Name', attribute['Name'], key=f'attr_name_{counter}', on_change=set_state_all_attr_names)

            attr_expander.checkbox('Has Labels', attribute['Has_Labels'], key=f'attr_has_labels_{counter}', on_change=flip_attr_val, args=(attribute, 'Has_Labels'))
            attribute['Labels'] = attr_expander.text_area('Labels (separated by comma)', attribute['Labels'], key=f'attr_labels_{counter}', disabled=not attribute['Has_Labels'])

            #attribute['Has_Clarifiers'] = attr_expander.checkbox('Has Clarifiers', attribute['Has_Clarifiers'], key=f'attr_has_clarifiers_{counter}')
            attr_expander.checkbox('Has Clarifiers', attribute['Has_Clarifiers'], key=f'attr_has_clarifiers_{counter}', on_change=flip_attr_val, args=(attribute, 'Has_Clarifiers'))
            attribute['Clarifiers'] = attr_expander.text_area('Clarifiers (separated by comma)', attribute['Clarifiers'], key=f'attr_clarifiers_{counter}', disabled=not attribute['Has_Clarifiers'])

            attr_expander.checkbox('Is_Implied', attribute['Is_Implied'], key=f'attr_is_implied_{counter}', on_change=flip_attr_val, args=(attribute, 'Is_Implied'))
            attribute['Implied_By'] = attr_expander.selectbox('Implied By', options=st.session_state.all_attr_names, disabled=not attribute['Is_Implied'], key=f'attr_id_implied_{counter}')

            counter += 1

        button_col_1, button_col_2, button_col_3 = st.columns(3)
        button_col_1.button('Delete', on_click=delete_population)
        button_col_2.button('Add Attribute', on_click=new_pop_attr)
        button_col_3.button('Save', on_click=save_population)
    elif st.session_state.NEW_POP_MODE:
        st.header('New Population')
        st.session_state.curr_pop_data['Name'] = st.text_input('Name', st.session_state.curr_pop_data['Name'])
        #st.session_state.curr_pop_data = copy.deepcopy(NEW_POPULATION_TEMPLATE)
        print(f'Pop State: {st.session_state.curr_pop_data}')

        if 'all_attr_names' not in st.session_state:
            set_state_all_attr_names()

        counter = 0
        for attribute in st.session_state.curr_pop_data['Attributes']:
            print(f'Attr_{counter} {attribute}')
            print(f'{attribute["Name"]}')
            attr_expander = st.expander(attribute['Name'])
            attribute['Name'] = attr_expander.text_input('Name', attribute['Name'], key=f'attr_name_{counter}', on_change=set_state_all_attr_names)

            attr_expander.checkbox('Has Labels', attribute['Has_Labels'], key=f'attr_has_labels_{counter}', on_change=flip_attr_val, args=(attribute, 'Has_Labels'))
            attribute['Labels'] = attr_expander.text_area('Labels (separated by comma)', attribute['Labels'], key=f'attr_labels_{counter}', disabled=not attribute['Has_Labels'])

            #attribute['Has_Clarifiers'] = attr_expander.checkbox('Has Clarifiers', attribute['Has_Clarifiers'], key=f'attr_has_clarifiers_{counter}')
            attr_expander.checkbox('Has Clarifiers', attribute['Has_Clarifiers'], key=f'attr_has_clarifiers_{counter}', on_change=flip_attr_val, args=(attribute, 'Has_Clarifiers'))
            attribute['Clarifiers'] = attr_expander.text_area('Clarifiers (separated by comma)', attribute['Clarifiers'], key=f'attr_clarifiers_{counter}', disabled=not attribute['Has_Clarifiers'])

            attr_expander.checkbox('Is_Implied', attribute['Is_Implied'], key=f'attr_is_implied_{counter}', on_change=flip_attr_val, args=(attribute, 'Is_Implied'))
            attribute['Implied_By'] = attr_expander.selectbox('Implied By', options=st.session_state.all_attr_names, disabled=not attribute['Is_Implied'], key=f'attr_id_implied_{counter}')

            counter += 1
        button_col_1, button_col_2, button_col_3 = st.columns(3)
        button_col_1.button('Cancel', on_click=cancel_new_population)
        button_col_2.button('Add Attribute', on_click=new_pop_attr)
        button_col_3.button('Save', on_click=save_population)


    return

if __name__ == '__main__':
    main()