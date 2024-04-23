import streamlit as st
import pandas as pd
import plotly.express as px

def app():
    # Website title
    st.title('Example Database')

    # Add info button
    st.button('Instructions', help='1. First input sample parameters with filters on left. \n 2. If a graph is ideal, then'
                                    ' adjust the x-axis to fit sample type and y-axis for gene selection. Then select what variable to categorize by color.'
                                    ' \n 3. If a heatmap is ideal, then select a color scale, the samples, and the desired genes.')

    # Load data
    df = pd.read_csv('fake_data.csv', encoding='ISO-8859-1')

    # removed column that doesn't work (THIS SHOULD BE RESOLVED)

    # Add unique identifier for each sample, by fusing case number and sample number
    df['Name'] = df['Case_Number'].astype(str) + '/' + df['Stage_Number'].astype(str)
    name = df['Name']
    df = df.drop(columns=['Name'])
    df.insert(loc=1, column='Name', value=name)

    # Filter the data
    st.sidebar.header('Filters')
    SurgeryType = st.sidebar.multiselect('Select Surgery Type: (Required)',
                                   options=df['Case_Name'].unique(),
                                   )
    
    if len(SurgeryType) == 0:
        SurgeryType = list(df['Case_Name'].unique())
        

    StageNum = st.sidebar.multiselect('Select Stage: (Required)',
                                  options=df['Stage_Name'].unique(),
                                  )
    if len(StageNum) == 0:
        StageNum = list(df['Stage_Name'].unique())
        

    Surgeon = st.sidebar.multiselect('Select Surgeon: ',
                                    options=df['Surgeon'].unique(),
                                    )
    if len(Surgeon) == 0:
        Surgeon = list(df['Surgeon'].unique())
        

    # Make dataframe of selected data
    df_selection = df.query(
        f'Case_Name == {SurgeryType} & Stage_Name == {StageNum} & Surgeon == {Surgeon}'
    )

    # delete previous dataframe to save memory
    del df

    # Include subheading: Create Graph of interest
    st.subheader('Produce Graph of Interest')

    # make an interactive plot to check data
    def interactive_plot():
        col1, col2, col3 = st.columns(3)

        x_axis_val = col1.selectbox('Select the X-axis', options=df_selection.columns)
        y_axis_val = col2.selectbox('Select the Y-axis', options=df_selection.columns)
        col = col3.selectbox('Color by', options=['Case_Name', 'Stage_Name', 'Surgeon'])

        plot = px.scatter(df_selection, x=x_axis_val, y=y_axis_val, color=col, template="simple_white")
        # plot.update_traces(marker=dict(color=col))
        st.plotly_chart(plot, use_container_width=True)

    def histogram():
        x_axis_val = st.selectbox('Select the X-axis for Histogram', options=df_selection.columns)
        hist_plot = px.histogram(df_selection, x=x_axis_val, template="simple_white")
        st.plotly_chart(hist_plot, use_container_width=True)

    st.sidebar.title('Navigation')
    options = st.sidebar.radio('Select what you want to display:', ['Interactive Plots', 'Histogram'])

    if options == 'Interactive Plots':
        interactive_plot()
    elif options == 'Histogram':
        histogram()
