/* 

    Script 3 - Updates SAMPLE_50_BLDGS_V2 with various attributes 
    based on the building inspection report by using an LLM  

*/

USE DATABASE NYC_DATA_V2;
USE SCHEMA SOURCE_DATA_V2;

UPDATE SAMPLE_50_BLDGS_V2
SET ELECTRICAL_SYSTEM_CONDITION = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: You are generating a classification of the condition of the electrical system of the building in this report.
    Based in this report provide a one-word rating of either POOR, FAIR, GOOD or EXCELLENT to describe the condition of the electrical system.
    Do include any other words.
     Here is the report :<BLDGS>:',BLDG_INSPECTION,'<BLDGS>'));
     
UPDATE SAMPLE_50_BLDGS_V2
SET ELECTRICAL_SYSTEM_DESCRIPTION = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: You are generating answers to a question about building in a building condition report.
    Based in this report, answer the following question: describe the buildings electrical system. quote directly from the report.
     Here is the report :<BLDGS>:',BLDG_INSPECTION,'<BLDGS>')); 

UPDATE SAMPLE_50_BLDGS_V2
SET ELECTRICAL_REPAIR_COSTS = 
     TRY_CAST(SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
        CONCAT('
        INSTRUCTION: You are generating numeric answers to a question about building in a building condition report.
        Based in this report, answer the following question: 
        what are the total aggregated estimated costs for repairs or upgrades to the electrical system.
        Reply with only a number. 
        * First find each electrical system estimated cost and then aggregate the costs
        * Do not include any other informmation or comment. 
        * Do not return text. Do not include dollar signs or other symbols. 
        * Do not unclude commas.        
        * Only return a number. 
        * If you cannot provide a discrete numberic value do not return anything. 
        * Only return numeric values. 
         Here is the report :<BLDGS>:',BLDG_INSPECTION,'<BLDGS>'))AS NUMERIC); 

UPDATE SAMPLE_50_BLDGS_V2
SET PLUMBING_SYSTEM_CONDITION = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: You are generating a classification of the condition of the plumbing system of the building in this report.
    Based in this report provide a one-word rating of either POOR, FAIR, GOOD or EXCELLENT to describe the condition of the plumbing system.
    Do include any other words.
     Here is the report :<BLDGS>:',BLDG_INSPECTION,'<BLDGS>'));

UPDATE SAMPLE_50_BLDGS_V2
SET PLUMBING_SYSTEM_DESCRIPTION = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: You are generating answers to a question about building in a building condition report.
    Based in this report, answer the following question: describe the buildings plumbing system. quote directly from the report.
     Here is the report :<BLDGS>:',BLDG_INSPECTION,'<BLDGS>')); 

UPDATE SAMPLE_50_BLDGS_V2
SET PLUMBING_REPAIR_COSTS = 
     TRY_CAST(SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
        CONCAT('
        INSTRUCTION: You are generating numeric answers to a question about building in a building condition report.
        Based in this report, answer the following question: 
        what are the total aggregated estimated costs for repairs or upgrades to the plumbing system.
        Reply with only a number. 
        * First find each plumbing system estimated cost and then aggregate the costs
        * Do not include any other informmation or comment. 
        * Do not return text. Do not include dollar signs or other symbols. 
        * Do not unclude commas.        
        * Only return a number. 
        * If you cannot provide a discrete numberic value do not return anything. 
        * Only return numeric values. 
         Here is the report :<BLDGS>:',BLDG_INSPECTION,'<BLDGS>'))AS NUMERIC); 
     


UPDATE SAMPLE_50_BLDGS_V2
SET DEMOGRAPHICS = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: You are generating a demographic report on a specific address. 
    The report should include:
    * the name of the neighborhood
    * the relative income of the neighborhood
    * the racial demographics of the neighborhood
    * the educational demographics of the neighborhood
    * the age demographics of the neighborhood
    
     Here is the address:<BLDGS>:',ADDRESS,'<BLDGS>'));


UPDATE SAMPLE_50_BLDGS_V2
SET NEIGHBORHOOD = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: Use the following demographic analysis report to determine the neighborhood of the building at the address.
    Only include the neighborhood name. Do not include any other information,
    Here is the report:<BLDGS>:',DEMOGRAPHICS,'<BLDGS>'));

UPDATE SAMPLE_50_BLDGS_V2
SET INCOME_RELATIVE_TO_NYC = SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: Use the following demographic analysis report to determine if the median househod income of the neighborhood is higher 
    or lower than the median income of New York City, which is 75000. Do not include any other information. 
    Example answers are "higher", "slightly higher", "lower", "slightly lower", "much higher", "much lower". The answer should only be a 
    maximum of two words. Do not include any explanation.
    Here is the report:<BLDGS>:',DEMOGRAPHICS,'<BLDGS>'));

UPDATE SAMPLE_50_BLDGS_V2
SET INCOME = TRY_CAST(
    SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: Use the following demographic analysis report find
    the approximate median household income of the neighborhood
    Do not include any other information. Do not include a $ dollar sign at the beginning of the answer.
    Remove any $ dollar sign from the answer. Do not include commas "," in the answer. Remove any commas "," from the answer.
    Only respond with a numeric answer.
    Do not include any explanation
    Here is the report:<BLDGS>:',DEMOGRAPHICS,'<BLDGS>')) AS NUMERIC);

UPDATE SAMPLE_50_BLDGS_V2
SET COUNT_OF_BUILDINGS = 1;

UPDATE SAMPLE_50_BLDGS_V2
SET INSPECTION_DATE = TRY_CAST(SNOWFLAKE.CORTEX.COMPLETE('llama3.1-405b', 
    CONCAT('
    INSTRUCTION: Use the following demographic analysis report find
    the inspection date of the building. Do not include anything other than the date.
    Only respond with an answer in date format. The date should be in YYYY-MM-DD format.
    Do not include any explanation. 
    Here is the report:<BLDGS>:',BLDG_INSPECTION,'<BLDGS>')) AS DATE);
    
