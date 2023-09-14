import os

import streamlit as st
import pandas as pd
import os.path as osp
import sys
import copy


sys.path.append('../')
from utilities import load_files_noext

NEW_PRODUCT_TEMPLATE = {
    'Product Name': '',
    'Product Type': '',
    'Expected Outcome': '',
    'URL/Website': ''
}


PRODUCTS_DIR = './products'

if 'NEW_PRODUCT_MODE' not in st.session_state:
    st.session_state.NEW_PRODUCT_MODE = False


def build_product_filepath(product_name):
    filename = product_name+'.xlsx'
    return osp.join(PRODUCTS_DIR, filename)

def new_product():
    st.session_state.NEW_PRODUCT_MODE = True
    print(f'New Product: {st.session_state.NEW_PRODUCT_MODE}')
    return

def load_product(product_name):
    filepath = build_product_filepath(product_name)
    product_data = pd.read_excel(filepath)
    product_dict = product_data.to_dict()
    print(product_dict)

    product_dict_refined = {}
    for key, val in product_dict.items():
        if key == 'Unnamed: 0': continue
        product_dict_refined[key] = val[0]
    return product_dict_refined

def save_product():
    #TODO: validate product values, ex: name must not be blank
    product_df = pd.DataFrame(st.session_state.curr_product_data, index=[0])
    #product_df = pd.DataFrame(st.session_state.curr_product_data.items(), columns=st.session_state.curr_product_data.keys())

    out_path = osp.join(PRODUCTS_DIR, st.session_state.curr_product_data['Product Name']+'.xlsx')
    print(f'Save to {out_path}')
    product_df.to_excel(out_path)

    st.session_state.curr_product_data = None
    # if product is a new product, flip off new product mode
    if st.session_state.NEW_PRODUCT_MODE:
        st.session_state.NEW_PRODUCT_MODE = False
    print(f'New Prod Save: {st.session_state.NEW_PRODUCT_MODE}')
    return

def delete_product():
    filepath = build_product_filepath(st.session_state.curr_product)
    os.remove(filepath)
    st.session_state.current_product_data = None
    st.session_state.curr_product = 'None Selected'
    return

def cancel_new_product():
    st.session_state.curr_product = 'None Selected'
    st.session_state.current_product_data = None
    st.session_state.NEW_PRODUCT_MODE = False
    return


def main():

    product_options = load_files_noext(PRODUCTS_DIR)

    st.title('Products')

    st.session_state.curr_product = st.selectbox("Select Product", options=sorted(['None Selected'] + product_options))
    st.button('New Product', on_click=new_product)

    if st.session_state.curr_product != 'None Selected' and not st.session_state.NEW_PRODUCT_MODE:
        st.session_state.curr_product_data = load_product(st.session_state.curr_product)
        for key, val in st.session_state.curr_product_data.items():
            st.session_state.curr_product_data[key] = st.text_input(key, val)

        button_col_1, button_col_2 = st.columns(2)
        button_col_1.button('Delete', on_click=delete_product)
        button_col_2.button('Save', on_click=save_product)
    elif st.session_state.NEW_PRODUCT_MODE:
        st.header('New Product')
        st.session_state.curr_product_data = copy.deepcopy(NEW_PRODUCT_TEMPLATE)
        for key, val in st.session_state.curr_product_data.items():
            st.session_state.curr_product_data[key] = st.text_input(key, val)
        button_col_1, button_col_2 = st.columns(2)
        button_col_1.button('Cancel', on_click=cancel_new_product)
        button_col_2.button('Save', on_click=save_product)


    return

if __name__ == '__main__':
    main()