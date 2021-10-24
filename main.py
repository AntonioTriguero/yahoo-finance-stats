from datetime import datetime

import pandas as pd
import numpy as np
import altair as alt

import ui as ui
from data import Stock

ui.init(font='Poppins', title='Yahoo Finance Stats', favicon='./icons8-yahoo-48.png')
stock = Stock(ui.input_widget('text_input', 'Stock', 'MSFT'))

with ui.expander('Settings'):
    interval = ui.input_widget('selectbox', 'Interval', ('1 day', '5 days', '1 week', '1 month', '3 months'), index=0)
    start_date, end_date = ui.input_widget('slider', 'Date range', value=(datetime(1986, 3, 13), datetime(2021, 10, 23)), format='MM/DD/YYYY')

with ui.container('History'):
    col1, _, col2 = ui.columns([1.0, 0.1, 1.0], ['Price', '', 'Volume'])
    
    source1 = stock.history(period='max', interval=interval, start=start_date, end=end_date)
    source2 = stock.indicators(period='max', interval=interval, start=start_date, end=end_date)

    with col1:
        with ui.expander('Filters'):
            selection = ui.input_widget('multiselect', 'Indicators', source2.columns)

        data = source1['Close']
        if len(selection) > 0:
            data = pd.concat([data, source2[selection]], axis=1)
            
        ui.chart('line_chart', data)

    with col2:
        ui.chart('line_chart', source1['Volume'])

with ui.container('Price change'):
    col1, _, col2 = ui.columns([1.0, 0.1, 1.0], ['History', '', 'Histogram'])

    source = stock.change(period='max', interval=interval, start=start_date, end=end_date)

    with col1:
        ui.chart('line_chart', source)

    with col2:
        with ui.expander('Filters'):
            min_value, max_value = ui.input_widget('slider', "Percent range", min_value=-15.0, max_value=15.0, value=(-100.0, 100.0), step=0.01)
            bin_size = ui.input_widget('slider', 'Bin size', min_value=0.5, max_value=max_value - min_value, value=0.5, step=0.01)

        ui.histogram(source, min_value, max_value, bin_size)

with ui.container('News'):
    col1, _, col2 = ui.columns([1.01, 0.1, 1.0], ['Headlines', '', 'Sentiment Analysis'])

    source = stock.news()

    with col1:
        ui.display('dataframe', source['Headline'])

    with col2:
        def highlight(s, colors):
            props = lambda index: f'background-color: {colors[index]}'
            condition = lambda value: (type(value) == int or type(value) == float) and value > 0
            return np.array([props(idx) if condition(value) else '' for idx, value in enumerate(s)])
        
        ui.display('dataframe', source.style.apply(highlight, axis=1, colors=['', 'red', '', 'green', '']))

with ui.container('Recommendations'):
    col1, _, col2 = ui.columns([1.01, 0.1, 1.0], ['Timeline', '', 'Firms'])

    domains = ['Buy', 'Sell', 'Neutral']
    color_range = ['green', 'red', 'gray']

    with col1:
        source = stock.actions_recommendations(period='max', interval=interval, start=start_date, end=end_date, columns=domains)

        legend_selection = alt.selection_multi(fields=['Recommendation'], bind='legend')
        line = alt.Chart(source).mark_line().encode(
            x='Date',
            y='Close',
            tooltip=['Date', 'Close'],
        )
        text = line.mark_point().encode(
            color=alt.Color('Recommendation', scale=alt.Scale(domain=domains, range=color_range)),
            size=alt.condition(~legend_selection, alt.value(1), alt.value(3)),
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2)),
        ).add_selection(
            legend_selection
        )

        ui.chart('altair_chart', (line + text).interactive(), use_container_width=True)
    
    with col2:
        def highlight_text(v):
            for domain, color in zip(domains, color_range):
                if v == domain:
                    return f"background-color: {color}"

        source = stock.recommendations[['Firm', 'From Grade', 'To Grade', 'Action']]

        ui.display('dataframe', source.style.applymap(highlight_text))

with ui.container('Intitutional holders'):
    source = stock.institutional_holders

    chart = alt.Chart(source).mark_bar().encode(
        x='Shares',
        y='Holder',
        tooltip=['Holder', 'Shares']
    )
    ui.chart('altair_chart', chart, use_container_width=True)

with ui.container('Financial data'):
    col1, _, col2 = ui.columns([1.0, 0.1, 1.0], ['Slopes', '', 'Data'])

    with col1:
        source = stock.financials_slopes()

        legend_selection = alt.selection_multi(fields=['Stat'], bind='legend')
        lines = alt.Chart(source).mark_line(point=True).encode(
            x='Date',
            y='Value',
            color='Stat',
            size=alt.condition(~legend_selection, alt.value(1), alt.value(3)),
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2)),
            tooltip=['Value', 'Stat']
        ).add_selection(
            legend_selection
        )
        ui.chart('altair_chart', lines, use_container_width=True)
    with col2:
        source = stock.financials()

        ui.display('dataframe', source)