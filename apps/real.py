import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import matplotlib.pyplot as plt



def app():

    #include a picture of an OR
    from PIL import Image
    ORpic = Image.open('OR pic.png')
    st.image(ORpic, caption='')

    # Website title
    st.title('Deformity Cases of 3 Surgeons')

    # Add info button
    st.button('Instructions', help='1. First input desired parameters with the filters on left. \n 2. Choose the axes you wish to graph'
                                    ' \n 3. Select any variable to categorize by color.')

    # Load data from XLSX
    all_data_df = pd.read_excel('All Time Data514.xlsx', sheet_name='All Time Data', engine='openpyxl')
    registry_df = pd.read_excel('All Time Data514.xlsx', sheet_name='Registry', engine='openpyxl')


    # Merge dataframes based on 'Case ID' and 'ST ID'
    all_data_df = pd.merge(all_data_df, registry_df, how='left', left_on='Case ID', right_on='ST ID')
    

    # Add unique identifier for each sample, by fusing case number, stage name, and start time
    all_data_df['Name'] = all_data_df['Case ID'].astype(str) + '/' + all_data_df['Stage'].astype(str)  + '/' + all_data_df['Stage Start Time'].astype(str)
    name = all_data_df['Name']
    all_data_df = all_data_df.drop(columns=['Name'])
    all_data_df.insert(loc=1, column='Name', value=name)



# Defining what week each surgery was in
    all_data_df['Date'] = pd.to_datetime(all_data_df['Date'], format='%m/%d/%Y', errors='coerce')
    # Find the start date of each week
    all_data_df['Week'] = all_data_df['Date'] - pd.to_timedelta(all_data_df['Date'].dt.dayofweek, unit='D')


#EDITING TIME DATA: Calculate times for each stage (in minutes) and combine duplicate stages
    # Convert the 'Time' column to datetime objects
    all_data_df['Stage Start Time'] = pd.to_datetime(all_data_df['Stage Start Time'], format='%H:%M')
    
    
    # Sort the dataframe by 'Case ID' and 'Time'
    all_data_df = all_data_df.sort_values(by=['Case ID', 'Stage Start Time'])

    # Group by 'Case ID' and shift the time values down by one within each group
    all_data_df['Next Time'] = all_data_df.groupby('Case ID')['Stage Start Time'].shift(-1)

    # Calculate the time until the next stage
    all_data_df['Stage Duration (min)'] = all_data_df['Next Time'] - all_data_df['Stage Start Time']

    # Convert the time difference to minutes
    all_data_df['Stage Duration (min)'] = all_data_df['Stage Duration (min)'].dt.total_seconds() / 60
    all_data_df['Stage Duration (min)'].fillna(0, inplace=True)
    all_data_df['Stage Duration (min)'] = all_data_df['Stage Duration (min)'].astype(int)

    duplicates_df = all_data_df.copy()


    # Drop the intermediate 'Next Time' column
    all_data_df.drop(columns=['Next Time'], inplace=True)

    # Find rows where 'Case ID' and 'Stage' match
    duplicate_rows = all_data_df.duplicated(subset=['Case ID', 'Stage'], keep=False)

    # Sum the times for duplicate rows
    all_data_df.loc[duplicate_rows, 'Stage Duration (min)'] = all_data_df.loc[duplicate_rows].groupby(['Case ID', 'Stage'])['Stage Duration (min)'].transform('sum')

    # Remove the duplicate rows
    all_data_df = all_data_df.drop_duplicates(subset=['Case ID', 'Stage'], keep='last')

    # Remove the "Done" rows
    all_data_df = all_data_df.drop(all_data_df[all_data_df['Stage'] == 'Done'].index)
    duplicates_df = duplicates_df.drop(duplicates_df[duplicates_df['Stage'] == 'Done'].index)
    



#FILTERING THE DATA

    st.sidebar.markdown("# Filters")


  #  st.sidebar.subheader('Case Selection (by level)')


##  #1  Filter options for Cer/Thor/Lum
##    checkbox_col1, checkbox_col2, checkbox_col3 = st.sidebar.columns(3)
##
##    include_cervical = checkbox_col1.checkbox('Cervical', value=False)
##    include_thoracic = checkbox_col2.checkbox('Thoracic', value=False)
##    include_lumbar = checkbox_col3.checkbox('Lumbar', value=False)
##
##
##    # Apply filters based on user selection
##    if include_cervical:
##        all_data_df = all_data_df[all_data_df['Cer'] == 1]
##
##    if include_thoracic:
##        all_data_df = all_data_df[all_data_df['Thor'] == 1]
##
##    if include_lumbar:
##        all_data_df = all_data_df[all_data_df['Lum'] == 1]


  #2  Filter options for Post Inst./TLIF/PSO/Laminectomy/ACDF





    st.sidebar.subheader('Case Selection (by procedure)')


    checkbox_col1, checkbox_col2 = st.sidebar.columns(2)

    include_posti = checkbox_col1.checkbox('Fusion', value=False)
    exclude_posti = checkbox_col2.checkbox('No Fusion', value=False)
    include_tlif = checkbox_col1.checkbox('TLIF', value=False)
    exclude_tlif = checkbox_col2.checkbox('No TLIF', value=False)
    include_pso = checkbox_col1.checkbox('PSO', value=False)
    exclude_pso = checkbox_col2.checkbox('No PSO', value=False)
    include_lam = checkbox_col1.checkbox('Laminectomy', value=False)
    exclude_lam = checkbox_col2.checkbox('No Lam', value=False)
    include_acdf = checkbox_col1.checkbox('ACDF', value=False)
    exclude_acdf = checkbox_col2.checkbox('No ACDF', value=False)
    include_pelvicfusion = checkbox_col1.checkbox('Pelvic Fusion', value=False)
    exclude_pelvicfusion = checkbox_col2.checkbox('No Pel Fusion', value=False)



    # Apply filters based on user selection
    if include_posti:
        all_data_df = all_data_df[all_data_df['Fusion'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['Fusion'] == 'Yes']


    if exclude_posti:
        all_data_df = all_data_df[all_data_df['Fusion'] == 'No']
        duplicates_df = duplicates_df[duplicates_df['Fusion'] == 'No']


    if include_tlif:
        all_data_df = all_data_df[all_data_df['TLIF'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['TLIF'] == 'Yes']

    if exclude_tlif:
        all_data_df = all_data_df[all_data_df['TLIF'] == 'No']
        duplicates_df = duplicates_df[duplicates_df['TLIF'] == 'No']

    if include_pso:
        all_data_df = all_data_df[all_data_df['PSO'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['PSO'] == 'Yes']

    if exclude_pso:
        all_data_df = all_data_df[all_data_df['PSO'] == 'No']
        duplicates_df = duplicates_df[duplicates_df['PSO'] == 'No']
        
    if include_lam:
        all_data_df = all_data_df[all_data_df['Laminectomy'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['Laminectomy'] == 'Yes']

    if exclude_lam:
        all_data_df = all_data_df[all_data_df['Laminectomy'] == 'No']
        duplicates_df = duplicates_df[duplicates_df['Laminectomy'] == 'No']

    if include_acdf:
        all_data_df = all_data_df[all_data_df['ACDF'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['ACDF'] == 'Yes']

    if exclude_acdf:
        all_data_df = all_data_df[all_data_df['ACDF'] == 'No']
        duplicates_df = duplicates_df[duplicates_df['ACDF'] == 'No']

    if include_pelvicfusion:
        all_data_df = all_data_df[all_data_df['Fusion_Pelvis'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['Fusion_Pelvis'] == 'Yes']

    if exclude_pelvicfusion:
        all_data_df = all_data_df[all_data_df['Fusion_Pelvis'] == 'Yes']
        duplicates_df = duplicates_df[duplicates_df['Fusion_Pelvis'] == 'Yes']


  #3 MAKE A SLIDER FOR VERTEBRAL LEVELS

    st.sidebar.subheader('Which levels?')


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

    duplicates_df = duplicates_df[(duplicates_df['UIV'].apply(vertebral_levels.index) >= selected_positions[0]) & 
                (duplicates_df['LIV'].apply(vertebral_levels.index) <= selected_positions[1])]
        

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
            duplicates_df = duplicates_df[(duplicates_df['Levels Exposed'] >= selected_levels[0]) & (duplicates_df['Levels Exposed'] <= selected_levels[1])]



  #5 Sort by other characteristics, such as Case, stage, or surgeon
    
    Case = st.sidebar.multiselect('Select Case: ',
                                  options=all_data_df['Case ID'].unique(),
                                  )
    if len(Case) == 0:
        Case = list(all_data_df['Case ID'].unique())
        


    Stage = st.sidebar.multiselect('Select Stage: ',
                                  options=all_data_df['Stage'].unique(),
                                  )
    if len(Stage) == 0:
        Stage = list(all_data_df['Stage'].unique())
        

    Surgeon = st.sidebar.multiselect('Select Surgeon: ',
                                    options=all_data_df['Surgeon'].unique(),
                                    )
    if len(Surgeon) == 0:
        Surgeon = list(all_data_df['Surgeon'].unique())
        

    # Make dataframe of selected data
        df_selection = all_data_df.query(
        f"`Stage` in {Stage} and "
        f"`Surgeon` in {Surgeon} and "
        f"`Case ID` in {Case}"
    )


#this part is not needed right now
    # Make dataframe of selected data
        duplicates_df = duplicates_df.query(
        f"`Stage` in {Stage} and "
        f"`Surgeon` in {Surgeon} and "
        f"`Case ID` in {Case}"
    )

        

    # Finding levels/week
    unique_cases = df_selection.drop_duplicates(subset=['Case ID'])
    levels_per_week = unique_cases.groupby('Week')['Levels Exposed'].sum().reset_index()
    levels_per_week['Levels/Week'] = levels_per_week['Levels Exposed']


    # Merge the 'Levels/Week' column back in'
    df_selection = pd.merge(df_selection, levels_per_week[['Week', 'Levels/Week']], on='Week', how='left')



#MAKE GRAPHS

    # Calculate Case Duration (hours) by summing up Stage Duration (min) for each case
    df_selection['Case Duration (hours)'] = df_selection.groupby('Case ID')['Stage Duration (min)'].transform('sum')/60
    unique_cases = df_selection.drop_duplicates(subset=['Case ID'])

    
    df_selection['Total OR Time (hours)'] = df_selection.groupby(['Surgeon', 'Week'])['Stage Duration (min)'].transform('sum')/60


    
    # Check if the filtered DataFrame is empty
    if df_selection.empty:
        st.subheader("There is no data that meets your selections.")
        
    else:
        # Include subheading: Create Graph of interest
        st.subheader('Produce Graph of Interest')

        # make an interactive plot to check data
        def interactive_plot(unique_cases):
            col1, col2, col3 = st.columns(3)

            x_axis_val = col1.selectbox('Select the X-axis', options=['Case ID', 'Surgeon', 'Fusion_Thirdrod', 'Case Name', 'Stage', 'Stage Duration (min)',
                                                                      'Levels Exposed', 'Fusion_levels', 'Fusion_Pediclescrews', 'Fusion_Pelvicscrews',
                                                                      'Laminectomy_levels', 'TLIF_levels', 'ACDF_levels',
                                                                      'Case Duration (hours)', 'Levels/Week', 'Week', 'Total OR Time (hours)'])
            y_axis_val = col2.selectbox('Select the Y-axis', options=['Case ID', 'Surgeon', 'Fusion_Thirdrod', 'Case Name', 'Stage', 'Stage Duration (min)',
                                                                      'Levels Exposed', 'Fusion_levels', 'Fusion_Pediclescrews', 'Fusion_Pelvicscrews',
                                                                      'Laminectomy_levels', 'TLIF_levels', 'ACDF_levels',
                                                                      'Case Duration (hours)', 'Levels/Week', 'Week', 'Total OR Time (hours)'])
            col = col3.selectbox('Color by', options=['Stage', 'Surgeon', 'TLIF', 'Fusion', 'Fusion_Thirdrod', 'Fusion_Pelvicscrews', 'Laminectomy', 'Durotomy', 'Revision',
                                                      'Fusion_Tether', 'Fusion_Nav', 'Fusion_Pediclescrews'])


            df_selection['Comments'] = df_selection['Comments'].apply(lambda x: f"<span style='font-size: 10px;'>{x}</span>")
            df_selection['Date'] = pd.to_datetime(df_selection['Date']).dt.strftime('%m/%d/%Y')

            plot = px.scatter(df_selection, x=x_axis_val, y=y_axis_val, color=col, hover_data=['Case Name', 'Case ID', 'Date', 'Comments'], template="simple_white")


            # plot.update_traces(marker=dict(color=col))
            st.plotly_chart(plot, use_container_width=True)


        def histogram():
            x_axis_val = st.selectbox('Select the X-axis for Histogram', options=df_selection.columns)
            hist_plot = px.histogram(df_selection, x=x_axis_val, template="simple_white")
            st.plotly_chart(hist_plot, use_container_width=True)

        st.sidebar.title('Navigation')
        options = st.sidebar.radio('Select what you want to display:', ['Interactive Plots', 'Histogram'])

        if options == 'Interactive Plots':
            interactive_plot(unique_cases)
        elif options == 'Histogram':
            histogram()

# Generate SUMMARY TABLE for surgeons

    surgeon_summary = pd.DataFrame(index=['Total Cases', 'Total Time in OR (min)', 'Average Case Duration (min)', 'Total Levels Exposed', 'Average Levels Exposed',
                                          'Total Pedicle Screws', 'Total Pelvic Screws', 'Cases with TLIF', 'Total TLIFs', 'Time/TLIF (min)', 'Total ACDF', 'Total Fusion_Pelvis'])

    # Calculate total TLIF, total time in OR, total levels exposed, total cases, and average case duration for each surgeon
    for surgeon in Surgeon:
        surgeon_data = df_selection[df_selection['Surgeon'] == surgeon]

        unique_cases = surgeon_data.drop_duplicates(subset=['Case ID'])

        total_cases = len(unique_cases)
        total_time_in_or = int(surgeon_data['Stage Duration (min)'].sum())
        average_case_duration = round(surgeon_data['Stage Duration (min)'].sum() / total_cases) if total_cases > 0 else 0
        total_levels_exposed = int(unique_cases['Levels Exposed'].sum())
        average_levels_exposed = round(unique_cases['Levels Exposed'].sum() / total_cases) if total_cases > 0 else 0
        total_pedicle_screws = int(unique_cases['Fusion_Pediclescrews'].sum())
        total_pelvic_screws = int(unique_cases['Fusion_Pelvicscrews'].sum())
        cases_with_tlif = (unique_cases['TLIF'] == 'Yes').sum()
        total_tlifs = int(unique_cases['TLIF_levels'].sum())
        average_tlif_duration = int(surgeon_data[surgeon_data['Stage'] == 'TLIF']['Stage Duration (min)'].sum() / total_tlifs) if total_tlifs > 0 else 0
        total_acdf = (unique_cases['ACDF'] == 'Yes').sum()                                                           # Sum up the relevant columns to count totals
        total_pelvic_fusion = (unique_cases['Fusion_Pelvis'] == 'Yes').sum()

        surgeon_summary[surgeon] = [total_cases, total_time_in_or, average_case_duration, total_levels_exposed, average_levels_exposed, total_pedicle_screws, total_pelvic_screws,
                                    cases_with_tlif, total_tlifs, average_tlif_duration, total_acdf, total_pelvic_fusion]

    # Display summary table
    st.subheader('Surgeon Summary')
    st.table(surgeon_summary)

    


#MAKE THE HEATMAP

    # Group data by surgeon and count occurrences of each level
    unique_cases = df_selection.drop_duplicates(subset=['Case ID'])

    if len(unique_cases) > 1:

        surgeon_level_counts = unique_cases.groupby('Surgeon').apply(
            lambda group: group.apply(lambda row: vertebral_levels[vertebral_levels.index(row['UIV']):vertebral_levels.index(row['LIV']) + 1], axis=1)
                                .explode().value_counts()
        )
        
        # Create a dataframe for level counts for each surgeon
        surgeon_level_counts_df = surgeon_level_counts.reset_index()
        surgeon_level_counts_df.columns = ['Surgeon', 'Level', 'Count']

        # Convert the "Level" column to categorical with the desired order
        surgeon_level_counts_df['Level'] = pd.Categorical(surgeon_level_counts_df['Level'], categories=vertebral_levels, ordered=True)

        # Calculate the total count for each level across all surgeons
      #  total_level_counts = surgeon_level_counts_df.groupby('Level')['Count'].sum().reset_index()
      #  total_level_counts['Surgeon'] = 'Total'  # Assign 'Total' as the surgeon for the summary row
        

        # Append the total level counts to the dataframe
      #  surgeon_level_counts_df = pd.concat([surgeon_level_counts_df, total_level_counts], ignore_index=True)


        # Generate heatmap
        heatmap = px.imshow(pd.crosstab(surgeon_level_counts_df['Surgeon'], surgeon_level_counts_df['Level'], 
                                        values=surgeon_level_counts_df['Count'], aggfunc='sum'),
                            labels=dict(x="Level", y="Surgeon"),
                            x=vertebral_levels,
                            y=surgeon_level_counts_df['Surgeon'].unique(),
                            origin='lower',
                            aspect='auto',
                            color_continuous_scale='viridis')

        heatmap.update_xaxes(side="bottom", categoryorder='array', categoryarray=vertebral_levels)
        heatmap.update_layout(xaxis_title="Level")  # Set axis title for the x-axis


    else:
        # Calculate surgeon level counts directly for the single case
        surgeon_level_counts = df_selection.apply(lambda row: vertebral_levels[vertebral_levels.index(row['UIV']):vertebral_levels.index(row['LIV']) + 1], axis=1).explode().value_counts()

        # Create a dataframe for level counts for the single surgeon
        surgeon_level_counts_df = pd.DataFrame({'Surgeon': ['Single Case'] * len(surgeon_level_counts), 'Level': surgeon_level_counts.index, 'Count': surgeon_level_counts.values})

        # Convert the "Level" column to categorical with the desired order
        surgeon_level_counts_df['Level'] = pd.Categorical(surgeon_level_counts_df['Level'], categories=vertebral_levels, ordered=True)

        # Generate heatmap for the single case
        heatmap = px.imshow(pd.crosstab(surgeon_level_counts_df['Surgeon'], surgeon_level_counts_df['Level'], 
                                        values=surgeon_level_counts_df['Count'], aggfunc='sum'),
                            labels=dict(x="Level", y="Surgeon"),
                            x=vertebral_levels,
                            y=surgeon_level_counts_df['Surgeon'].unique(),
                            origin='lower',
                            aspect='auto',
                            color_continuous_scale='viridis')

        heatmap.update_xaxes(side="bottom", categoryorder='array', categoryarray=vertebral_levels)
        heatmap.update_layout(xaxis_title="Level", yaxis_title="Surgeon")  # Set axis titles for the x-axis and y-axis

    # Display heatmap
    st.subheader('Operation Frequency by Vertebra')
    st.plotly_chart(heatmap, use_container_width=True)



# MAKE THE PIE CHARTS

    # Generate PIE CHARTS for each surgeon

    st.subheader('Breakdown by Surgeon')

    # Allow user to select the category for the pie chart
    category_for_pie_chart = st.selectbox('Select Category for Pie Chart', options=['Stage', 'Fusion', 'TLIF', 'PSO', 'Laminectomy', 'ACDF', 'Fusion_Pelvis'])

    # Generate pie charts for each surgeon based on the selected category
    for surgeon in Surgeon:
        st.subheader(f'Pie Chart for Surgeon: {surgeon}')
        surgeon_data = df_selection[df_selection['Surgeon'] == surgeon]
        
        if category_for_pie_chart == 'Stage':
            # Calculate total time in OR for the surgeon
            total_time_in_or = surgeon_data['Stage Duration (min)'].sum()

            # Calculate the time spent in each stage as a percentage of total time in OR
            stage_duration_by_surgeon = surgeon_data.groupby('Stage')['Stage Duration (min)'].sum()
            stage_percentages = (stage_duration_by_surgeon / total_time_in_or) * 100

            # Generate pie chart using the calculated percentages
            pie_chart = px.pie(names=stage_percentages.index, values=stage_percentages.values,
                                title=f'Breakdown of {category_for_pie_chart} for {surgeon}')
        else:
            pie_chart = px.pie(surgeon_data, names=category_for_pie_chart, title=f'Breakdown of {category_for_pie_chart} for {surgeon}')
            
        st.plotly_chart(pie_chart)




### MAKE THE GANTT2
##
##    def generate_stacked_histogram(df):
##        # Initialize lists to store data for the x and y axes
##        case_ids = []
##        durations = []
##        stage_names = df['Stage'].unique()
##
##        # Iterate over each case and extract its stage durations
##        for case_id in df['Case ID'].unique():
##            # Filter the DataFrame for the current case
##            case_df = df[df['Case ID'] == case_id]
##            # Extract the durations of each stage for the current case
##            stage_durations = []
##            for stage_name in stage_names:
##                stage_duration = case_df[case_df['Stage'] == stage_name]['Stage Duration (min)'].sum()
##                stage_durations.append(stage_duration)
##            # Append the case ID to the list for the y-axis
##            case_ids.append(case_id)
##            # Append the list of durations to the list for the x-axis
##            durations.append(stage_durations)
##
##        # Create separate traces for each stage
##        traces = []
##        for i, stage_name in enumerate(stage_names):
##            trace = go.Bar(y=case_ids, x=[durations[j][i] for j in range(len(durations))], orientation='h', name=stage_name)
##            traces.append(trace)
##
##        # Define the layout for the graph
##        layout = go.Layout(
##            title="Stacked Histogram of Stage Durations per Case",
##            xaxis=dict(title="Duration (min)"),
##            yaxis=dict(title="Case ID"),
##            barmode='stack',
##            bargap=0.2,
##            bargroupgap=0.1
##        )
##
####        print(case_ids)
####        print(durations)
####        print(traces)
##
##        # Create the figure
##        fig = go.Figure(data=traces, layout=layout)
##
##        # Show the figure
##        st.plotly_chart(fig, use_container_width=True)
##
##    # Generate the stacked histogram
##    generate_stacked_histogram(df_selection)


# MAKE THE GANTT2

    def generate_stacked_histogram(df):
        # Initialize lists to store data for the x and y axes
        case_ids = []
        durations = []
        stage_names = df['Stage'].unique()

        # Iterate over each case and extract its stage durations
        for case_id in df['Case ID'].unique():
            # Filter the DataFrame for the current case
            case_df = df[df['Case ID'] == case_id]
            # Extract the durations of each stage for the current case
            stage_durations = []
            for stage_name in stage_names:
                stage_duration = case_df[case_df['Stage'] == stage_name]['Stage Duration (min)'].sum()
                stage_durations.append(stage_duration)
            # Append the case ID to the list for the y-axis
            case_ids.append(case_id)
            # Append the list of durations to the list for the x-axis
            durations.append(stage_durations)

        # Create separate traces for each stage
        traces = []
        for i, stage_name in enumerate(stage_names):
            trace = go.Bar(y=case_ids, x=[durations[j][i] for j in range(len(durations))], orientation='h', name=stage_name)
            traces.append(trace)

        # Define the layout for the graph
        layout = go.Layout(
            title="Stacked Histogram of Stage Durations per Case",
            xaxis=dict(title="Duration (min)"),
            yaxis=dict(title="Case ID"),
            barmode='stack',
            bargap=0.2,
            bargroupgap=0.1
        )

##        print(case_ids)
##        print(durations)
##        print(traces)

        # Create the figure
        fig = go.Figure(data=traces, layout=layout)

        # Show the figure
        st.plotly_chart(fig, use_container_width=True)

    # Generate the stacked histogram
    generate_stacked_histogram(df_selection)


# MAKE THE GANTT2



    def assign_random_colors(df):
        # Get unique stage names
        unique_stages = df['Stage'].unique()
        # Generate a random color for each stage
        stage_colors = {stage: f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})' for stage in unique_stages}
        # Assign colors to each stage in the DataFrame
        df['Color'] = df['Stage'].map(stage_colors)
        return df, stage_colors

    def generat_stacked_histogram(df):
        # Assign random colors to each stage
        df_with_colors, stage_colors = assign_random_colors(df)

        # Sort DataFrame by Case ID and Stage Start Time
        df_sorted = df_with_colors.sort_values(by=['Case ID', 'Stage Start Time'])

        # Initialize lists to store data for the x and y axes
        x_data = df_sorted['Case ID']
        y_data = df_sorted['Stage Duration (min)']
        colors = df_sorted['Stage'].map(stage_colors)

        # Create the stacked histogram
        fig = go.Figure(go.Bar(
            x=x_data,
            y=y_data,
            marker=dict(color=colors),
            orientation='v',
            hoverinfo='text',
            text=[f"<b>Case:</b> {case}<br><b>Stage:</b> {stage}<br><b>Length:</b> {length} min" for case, stage, length in zip(df_sorted['Case ID'], df_sorted['Stage'], df_sorted['Stage Duration (min)'])],
            textfont=dict(color="rgba(0, 0, 0, 0)")  # Making text color transparent
        ))

        # Show both the graph and the key legend
        st.plotly_chart(fig, use_container_width=True)

    # Generate the stacked histogram
    generat_stacked_histogram(duplicates_df)
