# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard2',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'}
                                    ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i}' for i in range(0, 10001, 2500)},
                                    value=[min_payload, max_payload]
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # For all sites, show the total successful launches by site
        success_counts = filtered_df[filtered_df['class'] == 1].groupby('Launch Site').size().reset_index(name='counts')
        fig = px.pie(success_counts, values='counts', 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
        return fig
    else:
        # Filter the dataframe for the selected site
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # Calculate success and failure counts
        success_failure_counts = filtered_site_df['class'].value_counts().reset_index()
        success_failure_counts.columns = ['class', 'counts']
        # Map class values to 'Success' and 'Failed'
        success_failure_counts['class'] = success_failure_counts['class'].map({1: 'Success', 0: 'Failed'})
        fig = px.pie(success_failure_counts, values='counts', 
                     names='class', 
                     title=f'Total Success Launches for site {entered_site}')
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
def update_scatter_chart(entered_site, payload_range):
    # Filter data based on the payload range
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        # For all sites, show the scatter plot for all data within the payload range
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites',
            hover_data=['Launch Site'])
        return fig
    else:
        # Filter data for the selected site
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # Generate scatter plot for the selected site
        fig = px.scatter(
            filtered_site_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}',
            hover_data=['Launch Site'])
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
