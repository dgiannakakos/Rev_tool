Description of app's API:

In views.py
1) function get_kpis dynamically loads and returns all data in kpi_data package (the predefined KPIs the user will choose from)
2) function submit_kpi_data calculates and returns the results of the chosen and added user kpis
3) function get_barriers dynamically loads and returns all data in Barriers_Disadvantages.py file (the barries/disadvantages the user will choose from)
4) function submit_barriers_data returns results
5) function get_climate_vulnerability dynamically loads and returns all data in Climate_vulnerability.py (the climate vulnerability variables the user will choose from)
6) function submit_climate_vulnerability returns the description of the chosen variables
7) function get_weather_variables dynamically loads all data in Weather_variables.py (the descriptions of the weather variables to be presented to the user)

You can test the endpoints in tests.py where there are examples of the required json structure of POST request functions 
   Test the API by navigating in REV_readiness, running server and running tests.py file
