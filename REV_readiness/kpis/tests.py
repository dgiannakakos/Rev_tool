from django.test import TestCase

# Create your tests here.

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"


# Function to test GET request
def test_get_kpis():
    response = requests.get(f"{BASE_URL}/kpis/")
    print("GET KPIs Response:", response.status_code, response.json())


# Function to test POST request for submitting KPI data
def test_submit_kpis():

    data = {
        "alpha": 3,
        "beta": 5,
            "kpis": {
                "Social": {
                    "SCE1": {
                        "current_value": 100,
                        "target_value": 1,
                        "current_date": 1,
                        "target_date": 2,
                        "data_quality": 1
                    },
                    "SCE2": {
                        "current_value": 100,
                        "target_value": 1,
                        "current_date": 1,
                        "target_date": 2,
                        "data_quality": 2
                    }
                }
            },
            "added_kpis": {
                "Economic": {
                    "ECON1": {
                        "current_value": 1000,
                        "target_value": 1,
                        "current_date": 1,
                        "target_date": 100,
                        "data_quality": 3,
                    },
                },
                "Technological": {
                    "SOC1": {
                        "current_value": 1000,
                        "target_value": 999,
                        "current_date": 1,
                        "target_date": 2,
                        "data_quality": 5,
                    }
                }
            }
        }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/submit_kpis/", data=json.dumps(data), headers=headers)
    print("POST Submit KPIs Response:", response.status_code, response.json())

# Function to test GET request for barriers
def test_get_barriers():
    response = requests.get(f"{BASE_URL}/barriers/")
    print("GET Barriers Response:", response.status_code, response.json())


# Function to test POST request for submitting barriers data
def test_submit_barriers():
    data = {
        "barriers": {
            "Public Resistance": {
                "PR01": {
                    "likelihood": 1,
                    "impact": 5,
                },
                "PR02" : {
                    "likelihood": 1,
                    "impact": 5
                }
            },
            "Resource Scarcity": {
                "RS01": {
                    "likelihood": 2,
                    "impact": 5,
                },
            }
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/submit_barriers/", data=json.dumps(data), headers=headers)
    print("POST Submit Barriers Response:", response.status_code, response.json())


# Function to test GET request for climate vulnerability
def test_get_climate_vulnerability():
    response = requests.get(f"{BASE_URL}/climate_vulnerability/")
    print("GET Climate Vulnerability Response:", response.status_code, response.json())


# Function to test POST request for submitting climate vulnerability data
def test_submit_climate_vulnerability():
    data = {
        "selected_vulnerabilities": {
            "Residential assets": {
                "Air-conditioning": ["Temperature"],
                "Heat pumps": ["Temperature", "Frozen precipitation"]
            },
            "Renewable energy sources": {
                "Solar photovoltaic plants": ["Temperature", "Liquid precipitation"]
            }
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/submit_climate_vulnerability/", data=json.dumps(data), headers=headers)
    print("POST Submit Climate Vulnerability Response:", response.status_code, response.json())

def test_get_weather_variables():
    response = requests.get(f"{BASE_URL}/weather_variables/")
    print("GET Weather variables Response:", response.status_code, response.json())

# Run all tests
if __name__ == "__main__":
    #test_get_kpis()
    #test_submit_kpis()
    #test_get_barriers()
    test_submit_barriers()
    #test_get_climate_vulnerability()
    #test_submit_climate_vulnerability()
    #test_get_weather_variables()
