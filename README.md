# REV Readiness Assessment fastAPI

This project provides the endpoints and functionality of REV readiness assessment tool in a FastAPI-based backend 

- KPIs: User chooses any of the available KPIs and can add some of his own (must belong in existing categories e.g. social etc.)
- A score is calculated for each KPI category
- User can edit or delete any of the added KPIs

- Barriers and disadvantages: User chooses any of the available barriers 
- A score is calculated for each barrier persona (category) and different incentives for each chosen barrier are presented 

- Climate vulnerability: User chooses any of the available assets and weather variables and gets insights    

- Weather variables: User gets a description of all available weather variables
##  Features

- @app.get("/kpis")
  Gets all KPI items  

- @app.get("/barriers_disadvantages")
  Gets all barriers and disadvantages items 

- @app.get("/weather_variables")
  Gest all weather variables items

- @app.get("/climate_vulnerability")
  Gets all climate vulnerability items

- @app.get("/custom_kpis")
  Gets all KPIs added by the user

- @app.get("/kpi/{category}/{kpi_id}")
  Gets one specific KPI from existing/added

- @app.get("/barrier/{persona}/{barrier_id}")
  Gets one specific barrier

- @app.get("/weather_variable/{variable_name}")
  Gets one specific weather variable

- @app.post("/add_custom_kpi")
  Adds a custom (user added) KPI to one of the existing categories (social, economic etc.)

- @app.post("/kpis_score")
  Calculates the score of the KPI categories

- @app.post("/barriers_score")
  Calculates the score of the barriers personas and returns incentives

- @app.post("/climate_vulnerability_text")
  Posts the climate vulnerability insights of the chosen assets

- @app.put("/edit_custom_kpi/{category}/{subcategory}/{kpi_id}")
  Edits one of the custom (user added) KPIs

- @app.delete("/delete_custom_kpi/{category}/{subcategory}/{kpi_id}")
  Deletes one of the added (user added) KPIs 

##  Requirements

See requirements.txt file

## Test the endpoints through FastAPI - Swagger UI
- Run in terminal:  "python -m uvicorn main:app --reload" OR "py -m uvicorn main:app --reload"
- Visit URL in which uvicorn runs
- add "/docs" at the end of the URL
