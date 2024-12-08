import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# All launch sites
all_launch_sites = dict(zip(spacex_df['Launch Site'], spacex_df['Launch Site']))
all_launch_sites['All Sites'] = 'ALL'

launch_sites_dropdown_options = [{'label': k, 'value': v} for k, v in all_launch_sites.items()]

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # Launch Site Dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=launch_sites_dropdown_options,
                 value='ALL',
                 placeholder='Select a Launch Site',
                 searchable=True),
    html.Br(),
    
    # Pie Chart for Success vs Failure
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload Range Slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 1000: '1000'},
                    value=[min_payload, max_payload]),

    # Scatter Chart for Payload vs Success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df = spacex_df
        class_counts = df.groupby('Launch Site')['class'].mean()
        fig = px.pie(df, values=class_counts.values, names=class_counts.index, title='Total Success Launches By Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        class_counts = df['class'].value_counts()
        fig = px.pie(df, values=class_counts.values, names=class_counts.index, title=f'Total Success Launches for {entered_site} Site')
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='payload-slider', component_property='value'),
              Input(component_id='site-dropdown', component_property='value'))

def get_scatter_plot(entered_payload, entered_site):
    # Apply the payload filter based on the selected range
    df = spacex_df[spacex_df['Payload Mass (kg)'].between(entered_payload[0], entered_payload[1])]

    # If a specific site is selected, filter by Launch Site as well
    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]

    # Check if the dataframe is empty after filtering
    if df.empty:
        return {
            'data': [],
            'layout': {
                'title': 'No data available for the selected filters',
                'xaxis': {'title': 'Payload Mass (kg)'},
                'yaxis': {'title': 'Launch Success'}
            }
        }

    # Scatter plot for payload mass vs. success (class)
    fig = px.scatter(
        df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",  # Color by booster version
        hover_data=['Launch Site'],
        title=f'Correlation Between Payload and Success for {entered_site if entered_site != "ALL" else "All Sites"}'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8090)
