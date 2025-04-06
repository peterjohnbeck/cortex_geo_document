/* 
        
        Script 1 - creates WH, database, schema and stage 
        After running this, load files 
        * Geocoded_Buildings_Sample_Of_50_W_Only_Inspections.csv 
        * borough_boundaries_geojson.json 
        * building_inspections.yaml
        
        ...into the stage NYC_DATA_STAGE_SSE

*/

/*CREATE OR REPLACE WAREHOUSE COMPUTE_WH WAREHOUSE_SIZE='X-SMALL';*/
USE WAREHOUSE COMPUTE_WH;
CREATE OR REPLACE DATABASE NYC_DATA_V2;
USE DATABASE NYC_DATA_V2;
CREATE OR REPLACE SCHEMA SOURCE_DATA_V2;
USE SCHEMA SOURCE_DATA_V2;

CREATE STAGE NYC_DATA_STAGE_SSE 
	DIRECTORY = ( ENABLE = true ) 
	ENCRYPTION = ( TYPE = 'SNOWFLAKE_SSE' ) 
	COMMENT = 'Server Side Encrypted stage for demo data';

