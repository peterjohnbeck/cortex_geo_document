
import snowflake.connector
from snowflake.snowpark import Session
from snowflake.cortex import complete
import modin.pandas as spd
import snowflake.snowpark.modin.plugin
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import json
import warnings 
from typing import Dict, List, Any, Optional

DATABASE = "NYC_DATA_V2"
SCHEMA = "SOURCE_DATA_V2"
STAGE = "NYC_DATA_STAGE_V2"
FILE = "building_inspections.yaml"
WAREHOUSE = "COMPUTE_WH"
ACCOUNT = "[your account]"
USER = "[your user id]"
PASSWORD = "[your password]"

connection_parameters = {
    "user": USER,
    "password": PASSWORD,
    "account": ACCOUNT,
    "warehouse": WAREHOUSE,
    "database": DATABASE,
    "schema": SCHEMA
}

# need this because snowflake python connector may throw a warning in VSCode related to the toml file otherwise
# this is a documented bug: https://github.com/snowflakedb/snowflake-connector-python/issues/1978

warnings.filterwarnings(
    action='ignore',
    category=UserWarning,
    module='snowflake.connector')

# hide client errors

st.set_option('client.showErrorDetails', False)

if 'CONN' not in st.session_state or st.session_state.CONN is None:
    st.session_state.CONN= snowflake.connector.connect(
    user=USER,
    password=PASSWORD,
    account=ACCOUNT,
    warehouse=WAREHOUSE,
    database=DATABASE,
    schema=SCHEMA
    )

if 'SNOWPARK_SESSION' not in st.session_state or st.session_state.SNOWPARK_SESSION is None:
    st.session_state.SNOWPARK_SESSION = Session.builder.configs({"connection": st.session_state.CONN}).create()

st.set_page_config(layout="wide")
st.title("Cortex Analyst Mapping")
st.markdown(f"Semantic Model: `{FILE}`")

col1, col2 = st.columns([.7,.3], border=True)

def send_message(prompt: str) -> Dict[str, Any]:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }
    resp = requests.post(
        #url=f"https://{HOST}/api/v2/cortex/analyst/message",
        f"https://{ACCOUNT}.snowflakecomputing.com/api/v2/cortex/analyst/message",
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{st.session_state.CONN.rest.token}"',
            "Content-Type": "application/json",
        },
    )
    request_id = resp.headers.get("X-Snowflake-Request-Id")
    if resp.status_code < 400:
        return {**resp.json(), "request_id": request_id}  # type: ignore[arg-type]
    else:
        raise Exception(
            f"Failed request (id: {request_id}) with status {resp.status_code}: {resp.text}"
        )

def process_message(prompt: str) -> None:
    """Processes a message and output the results"""
    st.session_state.query = {"role": "user", "content": [{"type": "text", "text": prompt}]}
    with col2:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response = send_message(prompt=prompt)
                request_id = response["request_id"]
                content = response["message"]["content"]
                display_content(content=content, request_id=request_id)  # type: ignore[arg-type]
    st.session_state.result = {"role": "assistant", "content": content, "request_id": request_id}
    #)
    
@st.cache_data()
def load_borough():
    df = spd.read_snowflake(f"SELECT TO_JSON(BOUNDARIES) AS BOUNDARIES FROM BOROUGH_BOUNDARIES_v2").to_pandas()
    borough_shapes_data = json.loads(df["BOUNDARIES"][0])

    # Color each of the boroughs

    borough_shapes_data["features"][0]["properties"]["DisplayColor"]=[100,100,150,20]
    borough_shapes_data["features"][1]["properties"]["DisplayColor"]=[50,75,150,20]
    borough_shapes_data["features"][2]["properties"]["DisplayColor"]=[25,50,150,20]
    borough_shapes_data["features"][3]["properties"]["DisplayColor"]=[200,25,150,20]
    borough_shapes_data["features"][4]["properties"]["DisplayColor"]=[0,0,150,20]

    return borough_shapes_data

shapes = load_borough()

# display the content of a returned Cortex Analyst query
# put it in column 2
def display_content(
    content: List[Dict[str, str]],
    request_id: Optional[str] = None,
) -> None:
    """Displays a content item for a message."""
    with col2:
        if request_id:
            with st.expander("Request ID", expanded=False):
                st.markdown(request_id)
        for item in content:
            if item["type"] == "text":
                st.markdown(item["text"])
            elif item["type"] == "suggestions":
                with st.expander("Suggestions", expanded=True):
                    for suggestion_index, suggestion in enumerate(item["suggestions"]):
                        st.button(suggestion, key=f"{suggestion_index}", on_click=query_suggestion, kwargs=dict(query = suggestion))   
            elif item["type"] == "sql":
                with st.expander("SQL Query", expanded=False):
                    st.code(item["statement"], language="sql")
                with st.expander("Results", expanded=True):
                    with st.spinner("Running SQL..."):
                        df = spd.read_snowflake(item["statement"][:-1]).to_pandas()
                        st.dataframe(df)
                        st.session_state["returned_data"] =  df

# callback for handling a suggestion                        
def query_suggestion(query):
    with col2:
        process_message(query)

# map the content of the results of the query
def map_content(data=pd.DataFrame(), ):
    if 'borough_layer' not in st.session_state or st.session_state.borough_layer is None:
        Borough_Layer = pdk.Layer(
             "GeoJsonLayer",
                data = shapes,
                filled = True,
                get_fill_color = '[properties.DisplayColor[0],properties.DisplayColor[1],properties.DisplayColor[2],properties.DisplayColor[3]]', 
                getLineColor = [0,0,0],
                getLineWidth = 50
        )
        st.session_state.borough_layer = Borough_Layer
    if not data.empty:
        if {'LATITUDE','LONGITUDE', 'ADDRESS'}.issubset(data.columns):
            df2 = pd.DataFrame().assign(LATITUDE =data['LATITUDE'], LONGITUDE=data['LONGITUDE'], ADDRESS=data['ADDRESS'])
            Scatterplot_Layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=df2,
                        get_position="[LONGITUDE, LATITUDE]",
                        get_color="[200, 30, 0, 160]",
                        get_radius='100',
                        pickable = True,
                        auto_highlight=True,
                        id="buildings",)
    else:
        Scatterplot_Layer =  pdk.Layer(
                    "ScatterplotLayer",
                    )
    map = pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=40.63, 
            longitude=-73.94,
            zoom=12,
            pitch=50,
        ),
        layers=[
            Scatterplot_Layer, st.session_state.borough_layer
        ],
        tooltip={"text": "Location: \n Lat:{LATITUDE}\n Lon:{LONGITUDE} \n {ADDRESS}"}
    )
    st.session_state.map = map
    with col1:
       st.pydeck_chart(st.session_state['map'], height=800, on_select=map_click, key='building_map',selection_mode='multi-object')

# Take a given list of addresses and provide an summary of the building inspections
# assocatied with those buildings. Uses the GET_BLDG_INSPECTION_TEXT function 
# to extract the building inspection text, concatenates all the text together, and 
# passes to an LLM
def analyse_inspections(addresses):
    with col2:
        with st.spinner("Generating analysis of building inspections for the following location(s):"):
            all_inspection_text = ''
            for building in addresses:
                st.write(building["ADDRESS"])
                #building_inspection_text = pd.read_sql(f"SELECT GET_BLDG_INSPECTION_TEXT({building['LATITUDE']},{building['LONGITUDE']}) AS INSPECTION_TEXT",st.session_state.CONN)
                #all_inspection_text = all_inspection_text + building_inspection_text["INSPECTION_TEXT"][0]
                building_inspection_text = spd.read_snowflake(f"SELECT GET_BLDG_INSPECTION_TEXT_V2({building['LATITUDE']},{building['LONGITUDE']}) AS INSPECTION_TEXT")
                all_inspection_text = all_inspection_text + building_inspection_text["INSPECTION_TEXT"][0]

            inspection_text = all_inspection_text.replace("'","")

            # build a question for the LLM

            qry = f'Write a brief summary of the following building inspection reports. \
                The summary should include an overview. The overview should include the number of \
                buildings in the reports. There should then be then a short summary for each inspection \
                report that was provided. Include the address, general condition, main defects, and expected repair costs in each section.\
                Here are the reports: {inspection_text}'
            
            # call 'complete' on the question using llama3.1-405b
        
            summarized_building_inspection_text = complete('snowflake-llama-3.3-70b',qry,session=st.session_state.SNOWPARK_SESSION, stream=False)  
            
            st.write(summarized_building_inspection_text)

# build a list of buildings to analyse
def map_click():
    with col2:
        st.write("You have selected the following locations:")
        buttonDisabled=True
        if 'buildings' in st.session_state['building_map']['selection']['objects']:
            for building in st.session_state['building_map']['selection']['objects']['buildings']:
                st.write(building["ADDRESS"])
            
            buttonDisabled=False

            st.button("Analyse Inspections", on_click=analyse_inspections, key="AnalyseInspections", disabled=buttonDisabled, kwargs=dict(addresses = st.session_state['building_map']['selection']['objects']['buildings']))        
        
with col2:
    if user_input := st.chat_input("Search for buildings..."):
        process_message(prompt=user_input)

if "returned_data" in st.session_state:
    map_content(data=st.session_state['returned_data'])
else:
    map_content()