import streamlit as st
import pandas as pd
import plotly.express as px

def app():

    #include a picture of an OR
    from PIL import Image
    ORpic = Image.open('OR pic.png')
    st.image(ORpic, caption='')

    # Website title
    st.title('Real Database')

    # Add info button
    st.button('Instructions', help='1. First input desired parameters with the filters on left. \n 2. Choose the axes you wish to graph'
                                    ' \n 3. Select any variable to categorize by color.')

    # Load data from XLSX
    all_data_df = pd.read_excel('All Time Data328.xlsx', sheet_name='All Time Data', engine='openpyxl')
    registry_df = pd.read_excel('All Time Data328.xlsx', sheet_name='Registry', engine='openpyxl')
    comments_df = pd.read_excel('All Time Data328.xlsx', sheet_name='Case Notes', engine='openpyxl')


    # Filter to include only rows where "Entry Type" is "Stage"
    all_data_df = all_data_df[all_data_df['Entry Type'] == 'Stage']

    # removed column that doesn't work (THIS SHOULD BE RESOLVED)

    # Add unique identifier for each sample, by fusing case number, stage name, and start time
    all_data_df['Name'] = all_data_df['Case ID'].astype(str) + '/' + all_data_df['Stage'].astype(str)  + '/' + all_data_df['Stage Start Time'].astype(str)
    name = all_data_df['Name']
    all_data_df = all_data_df.drop(columns=['Name'])
    all_data_df.insert(loc=1, column='Name', value=name)


#EDITING TIME DATA: Calculate times for each stage (in minutes) and combine duplicate stages
    # Convert the 'Time' column to datetime objects
    all_data_df['Stage Start Time'] = pd.to_datetime(all_data_df['Stage Start Time'], format='%H:%M:%S')

    # Sort the dataframe by 'Case ID' and 'Time'
    all_data_df = all_data_df.sort_values(by=['Case ID', 'Stage Start Time'])

    # Group by 'Case ID' and shift the time values down by one within each group
    all_data_df['Next Time'] = all_data_df.groupby('Case ID')['Stage Start Time'].shift(-1)

    # Calculate the time until the next stage
    all_data_df['Stage Duration (min)'] = all_data_df['Next Time'] - all_data_df['Stage Start Time']

    # Convert the time difference to minutes
    all_data_df['Stage Duration (min)'] = all_data_df['Stage Duration (min)'].dt.total_seconds() / 60

    # Drop the intermediate 'Next Time' column
    all_data_df.drop(columns=['Next Time'], inplace=True)

    # Find rows where 'Case ID' and 'Stage' match
    duplicate_rows = all_data_df.duplicated(subset=['Case ID', 'Stage'], keep=False)

    # Sum the times for duplicate rows
    all_data_df.loc[duplicate_rows, 'Stage Duration (min)'] = all_data_df.loc[duplicate_rows].groupby(['Case ID', 'Stage'])['Stage Duration (min)'].transform('sum')

    # Remove the duplicate rows
    all_data_df = all_data_df.drop_duplicates(subset=['Case ID', 'Stage'], keep='last')




    # Merge dataframes based on 'Case ID' and 'Case #'
    all_data_df = pd.merge(all_data_df, registry_df, how='left', left_on='Case ID', right_on='Case #')
    all_data_df = pd.merge(all_data_df, comments_df, how='left', left_on='Case ID', right_on='Case#')


#FILTERING THE DATA

    st.sidebar.markdown("# Filters")


    st.sidebar.subheader('Case Selection (by level)')


  #1  Filter options for Cer/Thor/Lum
    checkbox_col1, checkbox_col2, checkbox_col3 = st.sidebar.columns(3)

    include_cervical = checkbox_col1.checkbox('Cervical', value=False)
    include_thoracic = checkbox_col2.checkbox('Thoracic', value=False)
    include_lumbar = checkbox_col3.checkbox('Lumbar', value=False)


    # Apply filters based on user selection
    if include_cervical:
        all_data_df = all_data_df[all_data_df['Cer'] == 1]

    if include_thoracic:
        all_data_df = all_data_df[all_data_df['Thor'] == 1]

    if include_lumbar:
        all_data_df = all_data_df[all_data_df['Lum'] == 1]


  #2  Filter options for Post Inst./Lam/TLIF/ACDF/Corp/Cyst


    st.sidebar.subheader('Case Selection (by procedure)')

    include_posti = st.sidebar.checkbox('Posterior Insrumentation', value=False)
    include_lam = st.sidebar.checkbox('Laminectomy', value=False)
    include_tlif = st.sidebar.checkbox('TLIF', value=False)
    include_acdf = st.sidebar.checkbox('ACDF', value=False)
    include_corp = st.sidebar.checkbox('Corpectomy', value=False)
    include_disc = st.sidebar.checkbox('Discectomy', value=False)
    include_cyst = st.sidebar.checkbox('Cyst', value=False)


     # Apply filters based on user selection
     
    if include_posti:
        all_data_df = all_data_df[all_data_df['Post_Inst'] == 1]

    if include_lam:
        all_data_df = all_data_df[all_data_df['Lam'] == 1]

    if include_tlif:
        all_data_df = all_data_df[all_data_df['TLIF'] == 1]
        
    if include_acdf:
        all_data_df = all_data_df[all_data_df['ACDF'] == 1]

    if include_corp:
        all_data_df = all_data_df[all_data_df['Corp'] == 1]

    if include_disc:
        all_data_df = all_data_df[all_data_df['Disc_corp'] == 1]
        
    if include_cyst:
        all_data_df = all_data_df[all_data_df['Cyst'] == 1]



  #3 MAKE A SLIDER FOR VERTEBRAL LEVELS

    # Define the vertebral levels
    vertebral_levels = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", 
                    "T6", "T7", "T8", "T9", "T10", "T11", "T12", "L1", "L2", "L3", "L4", "L5", "S1", "S2"]


    # Filter options for vertebral levels
    selected_levels = st.sidebar.select_slider(
            "Select Vertebral Levels",
            options=vertebral_levels,  # Display vertebral levels as options
            value=("C1", "S2"),  # Default selected levels
        )

    # Apply the filter based on the positions of UIV and LIV
    selected_positions = (vertebral_levels.index(selected_levels[0]), vertebral_levels.index(selected_levels[1]))

    all_data_df = all_data_df[(all_data_df['UIV'].apply(vertebral_levels.index) >= selected_positions[0]) & 
                (all_data_df['LIV'].apply(vertebral_levels.index) <= selected_positions[1])]


        

  #4  Make a Slider  for # Levels
    if all_data_df.empty:
            st.subheader("")
    else:     
            st.sidebar.subheader('How many levels?')
            min_levels = int(min(all_data_df['Levels Exposed']))
            max_levels = int(max(all_data_df['Levels Exposed'])) + 1
            selected_levels = st.sidebar.slider('Number of Levels', min_value=min_levels, max_value=max_levels, value=(min_levels, max_levels), step=1)


            # Apply filters based on selected levels
            all_data_df = all_data_df[(all_data_df['Levels Exposed'] >= selected_levels[0]) & (all_data_df['Levels Exposed'] <= selected_levels[1])]



  #5 Sort by other characteristics, such as title, stage, or surgeon
    
        

    Stage = st.sidebar.multiselect('Select Stage: (Required)',
                                  options=all_data_df['Stage'].unique(),
                                  )
    if len(Stage) == 0:
        Stage = list(all_data_df['Stage'].unique())
        

    Surgeon = st.sidebar.multiselect('Select Surgeon: ',
                                    options=all_data_df['Surgeon'].unique(),
                                    )
    if len(Surgeon) == 0:
        Surgeon = list(all_data_df['Surgeon'].unique())
        

#this part is not needed right now
    # Make dataframe of selected data
    df_selection = all_data_df.query(
        f"`Stage` == {Stage} & `Surgeon` == {Surgeon}"
    )




#MAKE GRAPHS

    # Check if the filtered DataFrame is empty
    if df_selection.empty:
            st.subheader("There is no data that meets your selections.")
            
    else:
            
            # Include subheading: Create Graph of interest
            st.subheader('Produce Graph of Interest')

            # make an interactive plot to check data
            def interactive_plot():
                col1, col2, col3 = st.columns(3)

                x_axis_val = col1.selectbox('Select the X-axis', options=['Case ID', 'Surgeon', '3rd_rod', 'Procedure Title', 'Stage', 'Stage Duration (min)',
                                                                          'Levels Exposed', 'Levels Instrumented', '# of Pedicle Screws', '# of Pelvic Screws',
                                                                          '# Levels with Laminectomy', '# Levels with TLIF', '# Levels ACDF'])
                y_axis_val = col2.selectbox('Select the Y-axis', options=['Case ID', 'Surgeon', '3rd_rod', 'Procedure Title', 'Stage', 'Stage Duration (min)',
                                                                          'Levels Exposed', 'Levels Instrumented', '# of Pedicle Screws', '# of Pelvic Screws',
                                                                          '# Levels with Laminectomy', '# Levels with TLIF', '# Levels ACDF'])
                col = col3.selectbox('Color by', options=['Stage', 'Surgeon', 'TLIF', 'Post_Inst', '3rd_rod', '# of Pelvic Screws', 'Lam', 'Durotomy', 'Revision',
                                                          'Tether', 'Navigation', 'Cyst', 'Corp', '# of Pedicle Screws'])

                
                plot = px.scatter(df_selection, x=x_axis_val, y=y_axis_val, color=col, hover_data=['Procedure Title', 'Case ID'], template="simple_white")

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


   # Generate summary table for surgeons
    surgeon_summary = pd.DataFrame(index=['Total Cases', 'Total Time in OR (min)', 'Total Levels Exposed', 'Total TLIF', 'Average Case Duration (min)'])

    # Calculate total TLIF, total time in OR, total levels exposed, total cases, and average case duration for each surgeon
    for surgeon in Surgeon:
        surgeon_data = df_selection[df_selection['Surgeon'] == surgeon]

        unique_cases = surgeon_data.drop_duplicates(subset=['Case ID'])

        total_cases = len(unique_cases)
        total_time_in_or = int(surgeon_data['Stage Duration (min)'].sum())
        total_levels_exposed = int(unique_cases['Levels Exposed'].sum())
        total_tlif = int(surgeon_data[surgeon_data['Stage'] == 'TLIF'].shape[0])
        average_case_duration = int(surgeon_data['Stage Duration (min)'].sum() / total_cases) if total_cases > 0 else 0

        surgeon_summary[surgeon] = [total_cases, total_time_in_or, total_levels_exposed, total_tlif, average_case_duration]

    # Display summary table
    st.subheader('Surgeon Summary')
    st.table(surgeon_summary)



    # Define the vertebral levels in the desired order
    vertebral_levels_ordered = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", 
                                "T6", "T7", "T8", "T9", "T10", "T11", "T12", "L1", "L2", "L3", "L4", "L5", "S1", "S2"]

    # Count the occurrences of each level between UIV and LIV inclusively
    level_counts = all_data_df.apply(lambda row: vertebral_levels[vertebral_levels.index(row['UIV']):vertebral_levels.index(row['LIV']) + 1], axis=1).explode().value_counts()

    # Create a dataframe for level counts
    level_counts_df = pd.DataFrame(level_counts, columns=['Count']).reset_index()
    level_counts_df.columns = ['Level', 'Count']

    # Convert the "Level" column to categorical with the desired order
    level_counts_df['Level'] = pd.Categorical(level_counts_df['Level'], categories=vertebral_levels_ordered, ordered=True)


         # Generate heatmap
    heatmap = px.imshow(pd.crosstab(level_counts_df['Level'], level_counts_df['Level'], values=level_counts_df['Count'], aggfunc='sum'),
                        labels=dict(x="Level"),
                        x=vertebral_levels_ordered,
                        title='Level Operations Frequency',
                        origin='lower',
                        aspect='auto',
                        color_continuous_scale='viridis')

    heatmap.update_xaxes(side="bottom", categoryorder='array', categoryarray=vertebral_levels_ordered)
    heatmap.update_yaxes(side="left", categoryorder='array', categoryarray=vertebral_levels_ordered)
    heatmap.update_layout(yaxis_title="Level", xaxis_title="Level")  # Set axis titles

    # Display heatmap
    st.subheader('Level Operations Heatmap')
    st.plotly_chart(heatmap, use_container_width=True)
