import importlib.util
import os

from django.http import JsonResponse
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
import math

def load_kpi_data():
    """Dynamically loads all KPI data files from kpi_data/."""
    kpi_folder = os.path.join(settings.BASE_DIR, 'kpis', 'kpi_data')
    kpi_data = {}

    for file in os.listdir(kpi_folder):
        if file.endswith("_KPIs.py"):
            module_name = file[:-3]
            module_path = os.path.join(kpi_folder, file)

            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, module_name):
                    kpi_data[module_name] = getattr(module, module_name)
            except Exception as e:
                print(f"Error loading {file}: {e}")

    return kpi_data

def get_kpis(request):
    """Endpoint to return all KPIs."""
    kpi_data = load_kpi_data()
    return JsonResponse(kpi_data, safe=False)

@csrf_exempt
def submit_kpi_data(request):
    """Endpoint return KPI results (selected and added)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Get alpha and beta
            alpha = data.get('alpha')
            beta = data.get('beta')

            if not alpha or not beta:
                return JsonResponse({'error': 'Missing alpha and/or beta value'}, status=400)

            if not isinstance(alpha, int) or not isinstance(beta, int) or not (3 <= alpha <= 5) or not (3 <= beta <= 5):
                raise ValueError(f'alpha and beta must be integers between 3 and 5')

            a = alpha
            b = beta


            predefined_kpis = load_kpi_data()
            existing_kpi_ids = {kpi_id for category in predefined_kpis.values() for kpi_id in category.keys()}

            for category_dict in predefined_kpis.values():
                for subcategory in category_dict.values():
                    existing_kpi_ids.update(subcategory.keys())

            category_totals = {
                "Social": [],
                "Technological": [],
                "Environmental": [],
                "Co_benefits": [],
                "Economic": []
            }

            # Categories allowed
            allowed_categories = set(category_totals.keys())

            if not data.get('kpis', {}) and not data.get('added_kpis', []):
                return JsonResponse({'error': 'Must choose or add at least one KPI'}, status=400)

            # Store encountered KPI IDs to ensure uniqueness
            encountered_added_kpi_ids = set()

            # Process selected KPIs
            for category, kpis in data.get('kpis', {}).items():
                if category not in allowed_categories:
                    return JsonResponse({'error': f'Invalid category: {category}'}, status=400)

                for kpi_id, values in kpis.items():

                    # Check if KPI ID exists
                    if kpi_id not in existing_kpi_ids:
                        return JsonResponse({'error': f'Invalid KPI ID: {kpi_id} in category {category}'}, status=400)

                    process_kpi(category, kpi_id, values, category_totals, a, b)


            # Process added KPIs
            for category, kpis in data.get('added_kpis', {}).items():
                if category not in allowed_categories:
                    return JsonResponse({'error': f'Invalid category: {category}'}, status=400)

                for kpi_id, values in kpis.items():
                    if kpi_id in existing_kpi_ids:
                        return JsonResponse({'error': f'KPI ID {kpi_id} not available'}, status=400)

                    if kpi_id in encountered_added_kpi_ids:
                        return JsonResponse({'error': f'KPIs IDs must be unique: {kpi_id}'}, status=400)
                    encountered_added_kpi_ids.add(kpi_id)

                    try:
                        process_kpi(category, kpi_id, values, category_totals, a, b)
                    except ValueError as e:
                        return JsonResponse({'error': str(e)}, status=400)

            # Calculate averages for each category
            category_averages = {category: (sum(distances) / len(distances)) if distances else "No KPIS chosen/added for that category"
                                 for category, distances in category_totals.items()}

            return JsonResponse(category_averages)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def process_kpi(category, kpi_id, values, category_totals, a, b):
    """Helper function to check for invalid KPI values and calculate results."""
    current_value = values.get('current_value')
    target_value = values.get('target_value')
    current_date = values.get('current_date')
    target_date = values.get('target_date')
    data_quality = values.get('data_quality')

    # Validation
    if None in [current_value, target_value, current_date, target_date, data_quality]:
        raise ValueError(f'Missing values for KPI {kpi_id}')

    if not isinstance(current_date, int) or current_date <= 0:
        raise ValueError(f'Invalid current date for KPI {kpi_id}')

    if not isinstance(target_date, int) or target_date <= current_date:
        raise ValueError(f'Target date must be greater than current date for KPI {kpi_id}')

    if not isinstance(data_quality, int) or not (1 <= data_quality <= 5):
        raise ValueError(f'Data quality must be an integer between 1 and 5 for KPI {kpi_id}')

    # Calculate distance
    if current_value > target_value:
        distance = abs(target_value - current_value) / current_value
    else:
        distance = abs(target_value - current_value) / target_value
    time_adjusted_distance = distance * math.exp(-(current_date / target_date) ** a)
    final_distance = time_adjusted_distance * (data_quality / 5) ** (1 / b)

    # Store final distance in category totals
    category_totals[category].append(final_distance)


def load_barriers_data():
    """Dynamically loads the Barriers_Disadvantages.py file."""
    file_path = os.path.join(settings.BASE_DIR, 'kpis', 'Barriers_Disadvantages.py')
    module_name = "Barriers_Disadvantages"

    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "Barriers_disadvantages"):
            return getattr(module, "Barriers_disadvantages")

    except Exception as e:
        print(f"Error loading Barriers_Disadvantages.py: {e}")

    return {}

def get_barriers(request):
    """Endpoint to return all barriers and disadvantages."""
    barriers_data = load_barriers_data()
    return JsonResponse(barriers_data, safe=False)

@csrf_exempt
def submit_barriers_data(request):
    """Endpoint to return risk scores."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if not data.get('barriers', {}):
                return JsonResponse({'error': 'Choose at least one barrier.'}, status=400)

            # Load barriers from the file
            barriers_data = load_barriers_data()

            # Structure to store results
            persona_totals = {
                "Resource Scarcity": {'sum_likelihood_x_impact': 0, 'sum_impact': 0, 'sum_likelihood': 0},
                "Public Resistance": {'sum_likelihood_x_impact': 0, 'sum_impact': 0, 'sum_likelihood': 0},
                "Short-Term Focus": {'sum_likelihood_x_impact': 0, 'sum_impact': 0, 'sum_likelihood': 0},
                "Regulatory Delay": {'sum_likelihood_x_impact': 0, 'sum_impact': 0, 'sum_likelihood': 0}
            }

            for persona, barriers in data.get('barriers', {}).items():
                if persona not in barriers_data:
                    return JsonResponse({'error': f'Invalid persona: {persona}'}, status=400)

                valid_barriers = barriers_data[persona]  # Get valid barrier IDs for this persona

                for barrier_id, values in barriers.items():

                    if barrier_id not in valid_barriers:
                        return JsonResponse({'error': f'Invalid barrier ID: {barrier_id} for {persona}.'}, status=400)


                    likelihood = values.get('likelihood')
                    impact = values.get('impact')

                    if likelihood is None or impact is None:
                        return JsonResponse({'error': f'Missing values for {barrier_id} in {persona}.'}, status=400)

                    if not (isinstance(likelihood, int) and 1 <= likelihood <= 5) or not (
                            isinstance(impact, int) and 1 <= impact <= 5):
                        return JsonResponse({'error': f'Likelihood and Impact must be integers between 1 and 5 for {barrier_id} in {persona}.'},status=400)

                    # Update calculations for the persona
                    persona_totals[persona]['sum_likelihood_x_impact'] += likelihood * impact
                    persona_totals[persona]['sum_impact'] += impact
                    persona_totals[persona]['sum_likelihood'] += likelihood

            # Compute final risk scores for each persona
            persona_results = {}
            for persona, totals in persona_totals.items():
                if totals['sum_impact'] == 0 or totals['sum_likelihood'] == 0:
                    continue  # Avoid division by zero

                likelihood = totals['sum_likelihood_x_impact'] / totals['sum_impact']
                impact = totals['sum_likelihood_x_impact'] / totals['sum_likelihood']
                risk_score = likelihood * impact

                persona_results[persona] = {
                    'Likelihood': round(likelihood, 2),
                    'Impact': round(impact, 2),
                    'Risk Score': round(risk_score, 2)
                }

            return JsonResponse(persona_results)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def load_climate_vulnerability_data():
    """Dynamically load the Climate_vulnerability.py file."""
    file_path = os.path.join(settings.BASE_DIR, 'kpis', 'Climate_vulnerability.py')
    module_name = "Climate_vulnerability"

    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "Climate_vulnerability"):
            return getattr(module, "Climate_vulnerability")
    except Exception as e:
        print(f"Error loading Climate_vulnerability.py: {e}")

    return {}


def get_climate_vulnerability(request):
    """Endpoint to return all climate vulnerability options."""
    climate_data = load_climate_vulnerability_data()
    return JsonResponse(climate_data, safe=False)


@csrf_exempt
def submit_climate_vulnerability(request):
    """Endpoint to return descriptions of user-selected climate vulnerabilities."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_items = data.get('selected_vulnerabilities', {})

            if not selected_items:
                return JsonResponse({'error': 'Please select at least one vulnerability.'}, status=400)

            climate_data = load_climate_vulnerability_data()
            result = {}

            for category, items in selected_items.items():
                if category not in climate_data:
                    return JsonResponse({'error': f'Invalid category: {category}'}, status=400)

                result[category] = {}

                for subcategory, conditions in items.items():
                    if subcategory not in climate_data[category]:
                        return JsonResponse({'error': f'Invalid subcategory: {subcategory}'}, status=400)

                    result[category][subcategory] = {}

                    for condition in conditions:
                        if condition not in climate_data[category][subcategory]:
                            return JsonResponse({'error': f'Invalid condition: {condition}'}, status=400)

                        result[category][subcategory][condition] = climate_data[category][subcategory][condition]

            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def load_weather_variables_data():
    """Dynamically load the Weather_variables.py file."""
    file_path = os.path.join(settings.BASE_DIR, 'kpis', 'Weather_variables.py')
    module_name = "Weather_variables"

    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "Weather_variables"):
            return getattr(module, "Weather_variables")
    except Exception as e:
        print(f"Error loading Weather_variables.py: {e}")

    return {}

def get_weather_variables(request):
    """Endpoint to return all weather variables."""
    weather_variables_data = load_weather_variables_data()
    return JsonResponse(weather_variables_data, safe=False)