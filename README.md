# cortex_geo_document

## Demo of mapping attributes of a document to a map

Includes **3** SQL scripts. Run the scripts in order

- 1_create_map_demo_database.sql


**After script 1 is run, load the following files to the stage NYC_DATA_STAGE_SSE through the Snowsight UI**
- Geocoded_Buildings_Sample_Of_50_W_Only_Inspections.csv
- borough_boundaries_geojson.json into NYC_DATA_STAGE_SSE
- building_inspections.yaml

Then run:

* 2_create_load_map_demo_table.sql
* 3_LLM_Update_Attributes.sql

The applicatation python file is **cortex_analyst_map.py**. This uses Streamlit. It can be invoked by 
> streamlit run cortex_analyst_map.py