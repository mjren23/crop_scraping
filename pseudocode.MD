# Pseudocode Algorithm 

## Objectives 
### Goal: Scrape data on cropping patterns for 5 years, for all states, districts, and tehsils for 10 crops and all social groups 

#### Specifically: 
- 2001, 2015, 2016, 2005, 2010
- paddy, wheat, maize, soybean, cotton, groundnut, rapeseed and mustard, bajra, sugarcane, and jowar  

#### Save data as:
- YEAR_STATENAME_DISTRICTNAME_TEHSILNAME_CROPNAME.xlsx
  - Or, .csv file 
- Also keep track of files that are succesful and those that fail 

## Algorithm 

### High level:

- For each year: 
  - Get all states, districts, and tehsils, for each:
    - Loop through 10 crops, for each:
      - Get table data 
      - Parse table 
      - Save file 
        - Check if not successfully saved

### Lower level:

- For year in [2001, 2015, 2016, 2005, 2010]:
  - Create session 
  - Make call to homepage, get ViewState info 
  - Make call to Get_ddlData (returns list of states for that year)
  - Parse list of states to get districts (or make call to getDistrict with the state)
  - For each district:
    - Make call to getTehsil (returns list of tehsils)
    - For each tehsil:
      - For each crop in [paddy, wheat, maize, soybean, cotton, groundnut, rapeseed and mustard, bajra, sugarcane, jowar]:
        - Make POST to GetSession with form data 
        - Make POST to homepage with ViewState info 
        - Make GET to tktabledisplay to get EventValidation info 
        - Make POST to tktabledisplay, get table back 
          - Or error back if no data 
        - Parse table contents 
        - Save to file 

### Things to think about 
- Error handling 
- Running script unsupervised 
- Pausing in between scrapes
