from typing import List, Sequence, Union
import streamlit as st
import pandas as pd
import numpy as np

__charts_funcs = {
    'line_chart': st.line_chart,
    'area_chart': st.area_chart,
    'bar_chart': st.bar_chart,
    'pyplot': st.pyplot,
    'altair_chart': st.altair_chart,
    'vega_lite_chart': st.vega_lite_chart,
    'plotly_chart': st.plotly_chart,
    'bokeh_chart': st.bokeh_chart,
    'pydeck_chart': st.pydeck_chart,
    'graphviz_chart': st.graphviz_chart,
    'map': st.map,
}

__widgets_funcs = {
    'button': st.button,
    'download_button': st.download_button,
    'checkbox': st.checkbox,
    'radio': st.radio,
    'selectbox': st.selectbox,
    'multiselect': st.multiselect,
    'slider': st.slider,
    'select_slider': st.select_slider,
    'text_input': st.text_input,
    'number_input': st.number_input,
    'text_area': st.text_area,
    'date_input': st.date_input,
    'time_input': st.time_input,
    'file_uploader': st.file_uploader,
    'color_picker': st.color_picker,
}

__data_displays = {
    'dataframe': st.dataframe,
    'table': st.table,
    'metric': st.metric,
    'json': st.json,
}

def init(font: str = 'Montserrat', title: str = None, favicon: str = None):
    st.set_page_config(page_title=title, 
                        layout='wide', 
                        page_icon='https://img.icons8.com/color/48/000000/yahoo.png', 
                        initial_sidebar_state='auto')

    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    font_style = """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=""" + font + """:ital,wght@0,100;0,200;0,300;0,400;0,500;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap" rel="stylesheet"> 

        <style>
        * {
            font-family: '""" + font + """' !important;
        }
        </style>
    """
    st.markdown(font_style, unsafe_allow_html=True)

    if title:
        st.title(title)

def container(title: str = '') -> st.delta_generator.DeltaGenerator:
    c = st.container()
    c.header(title)
    return c

def columns(spec: Union[int, Sequence[Union[int, float]]] = 0, titles: List = []) -> st.delta_generator.DeltaGenerator:
    cols = []
    for idx, col in enumerate(st.columns(spec)):
        if idx < len(titles):
            col.subheader(titles[idx])
        cols.append(col)
    return cols

def expander(title='') -> st.delta_generator.DeltaGenerator:
    return st.expander(title)

def chart(char_type: str, *args, **kwargs):
    return __charts_funcs[char_type](*args, **kwargs)

def input_widget(input_widget_type: str, *args, **kwargs):
    return __widgets_funcs[input_widget_type](*args, **kwargs)

def display(data_display_type: str, *args, **kwargs):
    return __data_displays[data_display_type](*args, **kwargs)

def histogram(source: pd.DataFrame, min_value: float, max_value: float, bin_size: float):
    bins = np.around(np.arange(min_value, max_value, bin_size), decimals=2)
    hist, _ = np.histogram(source.to_numpy(), bins=bins)
    df = pd.DataFrame(hist, index=bins[:-1], columns=['Count'])
    chart('bar_chart', df)