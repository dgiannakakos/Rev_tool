from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, conint, confloat
from typing import List, Dict, Optional
import math
from enum import Enum


# data imports
from Co_benefits_KPIs import Co_benefits_KPIs
from Economic_KPIs import Economic_KPIs
from Environmental_KPIs import Environmental_KPIs
from Social_KPIs import Social_KPIs
from Technological_KPIs import Technological_KPIs

from Barriers_Disadvantages import Barriers_disadvantages

from Climate_vulnerability import Climate_vulnerability

from Weather_variables import Weather_variables


from incentives_mapping import incentives_mapping
from incentives import incentives
from incentives_id import incentives_id

# All KPIs in one dictionary
KPI_CATEGORIES = {
    "Co_benefits_KPIs": Co_benefits_KPIs,
    "Economic_KPIs": Economic_KPIs,
    "Environmental_KPIs": Environmental_KPIs,
    "Social_KPIs": Social_KPIs,
    "Technological_KPIs": Technological_KPIs
}

custom_kpis: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = {}



app = FastAPI()

## MODELS ##

class EditCustomKPIInput(BaseModel):
    name: Optional[str] = None
    primary_use: Optional[str] = None
    units: Optional[str] = None
    description: Optional[str] = None

class KPICategory(str, Enum):
    co_benefits = "Co_benefits_KPIs"
    economic = "Economic_KPIs"
    environmental = "Environmental_KPIs"
    social = "Social_KPIs"
    technological = "Technological_KPIs"

class BarriersCategory(str, Enum):
    Resource_Scarcity = "Resource Scarcity"
    Public_Resistance = "Public Resistance"
    Short_Term_Focus = "Short-Term Focus"
    Regulatory_Delay = "Regulatory Delay"

class WeatherVariables(str, Enum):
    temperature = "Temperature"
    liquid_precipitation = "Liquid precipitation"
    frozen_precipitation = "Frozen precipitation"
    wind_speeds_and_direction = "Wind speeds and directions"
    drought = "Drought"
    flooding = "Flooding"
    wildfires = "Wildfires"
    extreme_weather_events = "Extreme weather events"
    lighting = "Lightning"

class KPIInput(BaseModel):
    category: KPICategory
    subcategory: str
    id: str
    current_value: confloat(ge=0)
    target_value: confloat(ge=0)
    current_date: conint(ge=1)
    target_date: conint(ge=1)
    data_quality: conint(ge=1, le=5)

class CustomKPIInput(BaseModel):
    category: KPICategory
    subcategory: str
    name: Optional[str] = None
    primary_use: Optional[str] = None
    units: Optional[str] = None
    description: Optional[str] = None


class KPIRequest(BaseModel):
    selected_kpis: List[KPIInput]
    a: conint(ge=3, le=5)
    b: conint(ge=3, le=5)


class BarriersInput(BaseModel):
    persona: BarriersCategory
    id: str
    likelihood: conint(ge=1, le=5)
    impact: conint(ge=1, le=5)


class BarriersRequest(BaseModel):
    selected_barriers: List[BarriersInput]


class VulnerabilitySelection(BaseModel):
    main_category: str
    sub_category: str
    impact_type: str


class VulnerabilityRequest(BaseModel):
    selected_vulnerabilities: List[VulnerabilitySelection]


# ================================
#           Utilities
# ================================

def calculate_kpi_score(
    current_value: float, target_value: float,
    current_date: int, target_date: int,
    data_quality: int, a: int, b: int
    ) -> float:

    if current_value > target_value:
        distance = target_value / current_value

    else:
        if target_value == 0:
            raise ValueError("Target value cannot be zero.")
        distance = current_value / target_value

    time_adjusted_distance = distance * math.exp(-(current_date / target_date) ** a)
    final_distance = time_adjusted_distance * (data_quality / 5) ** (1 / b)
    return round(final_distance, 2)


def determine_kpi_level(score: float) -> str:
    if 0 <= score < 0.2:
        return "Very Low"
    elif score < 0.4:
        return "Low"
    elif score < 0.6:
        return "Medium"
    elif score < 0.8:
        return "High"
    elif score <= 1:
        return "Very High"
    return "Invalid"


def determine_risk_level(score: float) -> str:
    if 1 <= score < 5:
        return "Very Low"
    elif score < 10:
        return "Low"
    elif score < 15:
        return "Medium"
    elif score < 20:
        return "High"
    elif score <= 25:
        return "Very High"
    return "Invalid"




@app.get("/kpis")
def get_kpis():
    combined = {}

    # First copy predefined KPIs
    for category, subcats in KPI_CATEGORIES.items():
        combined[category] = dict(subcats)  # deep copy

    # Then add custom ones
    for category, subcats in custom_kpis.items():
        if category not in combined:
            combined[category] = {}
        for subcat, items in subcats.items():
            if subcat not in combined[category]:
                combined[category][subcat] = {}
            combined[category][subcat].update(items)

    return combined


@app.get("/barriers_disadvantages")
def get_barriers_disadvantages():
    return Barriers_disadvantages


@app.get("/weather_variables")
def get_weather_variables():
    return Weather_variables


@app.get("/climate_vulnerability")
def get_climate_vulnerability():
    return Climate_vulnerability


@app.get("/custom_kpis")
def get_custom_kpis():
    return custom_kpis

@app.get("/kpi/{category}/{kpi_id}")
def get_single_kpi(category: KPICategory, kpi_id: str):
    # Search predefined KPIs
    kpis = KPI_CATEGORIES.get(category.value)
    if kpis:
        for subcat, items in kpis.items():
            if kpi_id in items:
                return {kpi_id: items[kpi_id]}

    # Search custom KPIs
    custom = custom_kpis.get(category.value, {})
    for subcat, items in custom.items():
        if kpi_id in items:
            return {kpi_id: items[kpi_id]}

    raise HTTPException(status_code=404, detail=f"KPI ID '{kpi_id}' not found in category '{category.value}'")


@app.get("/barrier/{persona}/{barrier_id}")
def get_single_barrier(persona: BarriersCategory, barrier_id: str):
    barriers = Barriers_disadvantages.get(persona.value)
    if not barriers:
        raise HTTPException(status_code=404, detail=f"Persona '{persona.value}' not found.")

    if barrier_id in barriers:
        return {barrier_id: barriers[barrier_id]}

    raise HTTPException(status_code=404, detail=f"Barrier ID '{barrier_id}' not found in persona '{persona.value}'")


@app.get("/weather_variable/{variable_name}")
def get_single_weather_variable(variable_name: WeatherVariables):
    description = Weather_variables.get(variable_name)
    if not description:
        raise HTTPException(status_code=404, detail=f"Weather variable '{variable_name}' not found.")
    return {variable_name: description}


@app.post("/add_custom_kpi")
def add_custom_kpi(kpi: CustomKPIInput):
    category = kpi.category.value
    subcategory = kpi.subcategory

    # Initialize category if missing
    if category not in custom_kpis:
        custom_kpis[category] = {}
    if subcategory not in custom_kpis[category]:
        custom_kpis[category][subcategory] = {}

    # Generate new unique ID
    existing_ids = list(custom_kpis[category][subcategory].keys())
    new_id_num = len(existing_ids) + 1
    new_id = f"added_KPI_{new_id_num}"

    # Add KPI metadata
    custom_kpis[category][subcategory][new_id] = {
        "Name": kpi.name or "",
        "Primary use": kpi.primary_use or "",
        "Units of measurement": kpi.units or "",
        "Description": kpi.description or ""
    }

    return {"message": f"Custom KPI added under {category}/{subcategory} with ID '{new_id}'."}


@app.post("/kpis_score")
def calculate_kpi_scores(data: KPIRequest):
    category_scores: Dict[str, List[float]] = {}
    seen_ids = set()

    for kpi in data.selected_kpis:
        # Ensure unique IDs
        if kpi.id in seen_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate KPI ID found: '{kpi.id}'. Each KPI must be unique."
            )
        seen_ids.add(kpi.id)

        # Ensure valid date logic
        if kpi.target_date <= kpi.current_date:
            raise HTTPException(
                status_code=400,
                detail=f"target_date ({kpi.target_date}) must be greater than current_date ({kpi.current_date}) for KPI '{kpi.id}'"
            )

        # Ensure the ID exists in the correct category
        predefined_data = KPI_CATEGORIES.get(kpi.category.value, {})
        custom_data = custom_kpis.get(kpi.category.value, {})

        id_exists = any(kpi.id in subcat for subcat in predefined_data.values()) or \
                    any(kpi.id in subcat for subcat in custom_data.values())

        if not id_exists:
            raise HTTPException(
                status_code=400,
                detail=f"KPI ID '{kpi.id}' not found under category '{kpi.category.value}'."
            )

        try:
            score = calculate_kpi_score(
                kpi.current_value, kpi.target_value,
                kpi.current_date, kpi.target_date,
                kpi.data_quality, data.a, data.b
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        category_scores.setdefault(kpi.category.value, []).append(score)

    result = {
        category: {
            "score": round(sum(scores) / len(scores), 2),
            "level": determine_kpi_level(round(sum(scores) / len(scores), 2))
        }
        for category, scores in category_scores.items()
    }

    return {"category_scores": result}



# barrier → incentive IDs
barrier_to_incentive_ids = {
    item["barrier"].strip(): item["incentives"]
    for item in incentives_id
}

# incentive name → full incentive object
incentive_name_to_obj = {i["incentive"]: i for i in incentives}

# barrier → incentive names (from incentives_mapping)
barrier_to_incentive_names = {
    item["barrier"].strip(): item["incentives"]
    for item in incentives_mapping
}

# Build a fallback if you want incentive objects via ID
id_to_incentive = {i["id"]: i for i in incentives}


@app.post("/barriers_score")
def calculate_barriers_scores(data: BarriersRequest):
    seen_ids = set()
    category_data = {}

    for barrier in data.selected_barriers:
        persona = barrier.persona.value
        barrier_id = barrier.id

        # Validate
        if barrier_id in seen_ids:
            raise HTTPException(400, f"Duplicate barrier ID: {barrier_id}")
        seen_ids.add(barrier_id)

        if persona not in Barriers_disadvantages:
            raise HTTPException(400, f"Invalid persona: {persona}")
        if barrier_id not in Barriers_disadvantages[persona]:
            raise HTTPException(400, f"Barrier ID '{barrier_id}' not in persona '{persona}'")

        # Barrier info
        description = Barriers_disadvantages[persona][barrier_id]
        score = barrier.likelihood * barrier.impact

        # Prepare category slot
        if persona not in category_data:
            category_data[persona] = {
                "sum_numerator": 0.0,
                "sum_likelihood": 0.0,
                "sum_impact": 0.0
            }

        cat = category_data[persona]
        cat["sum_numerator"] += score
        cat["sum_likelihood"] += barrier.likelihood
        cat["sum_impact"] += barrier.impact

        # Try to find matching incentives
        barrier_name = description.strip()
        matched_ids = barrier_to_incentive_ids.get(barrier_name, [])
        incentives_full = [id_to_incentive[i] for i in matched_ids if i in id_to_incentive]

        # Store barrier info
        cat[barrier_id] = {
            "description": description,
            "likelihood": barrier.likelihood,
            "impact": barrier.impact,
            "incentives": incentives_full  # <-- or [i["incentive"] for i in incentives_full] for names only
        }

    # Final calculation
    result = {}

    for persona, values in category_data.items():
        a = values["sum_numerator"] / values["sum_likelihood"] if values["sum_likelihood"] else 0
        b = values["sum_numerator"] / values["sum_impact"] if values["sum_impact"] else 0
        c = a * b

        # Cleanup helpers
        for k in ["sum_numerator", "sum_likelihood", "sum_impact"]:
            values.pop(k)

        values["Persona impact"] = round(a, 2)
        values["Persona likelihood"] = round(b, 2)
        values["Persona Risk score"] = round(c, 2)
        values["Risk level"] = determine_risk_level(c)

        result[persona] = values

    return result


@app.post("/climate_vulnerability_text")
def get_climate_vulnerability_text(data: VulnerabilityRequest):
    descriptions = []
    seen_keys = set()

    for v in data.selected_vulnerabilities:
        # Uniqueness check
        key = (v.main_category, v.sub_category, v.impact_type)
        if key in seen_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate vulnerability entry: {key}"
            )
        seen_keys.add(key)

        # Main category check
        main = Climate_vulnerability.get(v.main_category)
        if main is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid main_category: '{v.main_category}'"
            )

        # Subcategory check
        sub = main.get(v.sub_category)
        if sub is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sub_category: '{v.sub_category}' under main_category: '{v.main_category}'"
            )

        # Impact type check
        impact_text = sub.get(v.impact_type)
        if impact_text is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid impact_type: '{v.impact_type}' under sub_category: '{v.sub_category}' in main_category: '{v.main_category}'"
            )

        descriptions.append({
            "main_category": v.main_category,
            "sub_category": v.sub_category,
            "impact_type": v.impact_type,
            "description": impact_text
        })

    return {"vulnerability_descriptions": descriptions}


@app.put("/edit_custom_kpi/{category}/{subcategory}/{kpi_id}")
def edit_custom_kpi(
        category: KPICategory,
        subcategory: str,
        kpi_id: str,
        data: EditCustomKPIInput
):
    cat = category.value

    if cat not in custom_kpis or subcategory not in custom_kpis[cat]:
        raise HTTPException(status_code=404, detail=f"Custom KPI path '{cat}/{subcategory}' not found.")

    if kpi_id not in custom_kpis[cat][subcategory]:
        raise HTTPException(status_code=404, detail=f"KPI ID '{kpi_id}' not found under '{cat}/{subcategory}'.")

    kpi_data = custom_kpis[cat][subcategory][kpi_id]

    # Only update fields that are not None
    if data.name is not None:
        kpi_data["Name"] = data.name
    if data.primary_use is not None:
        kpi_data["Primary use"] = data.primary_use
    if data.units is not None:
        kpi_data["Units of measurement"] = data.units
    if data.description is not None:
        kpi_data["Description"] = data.description

    return {"message": f"KPI '{kpi_id}' updated successfully under '{cat}/{subcategory}'.", "updated_kpi": kpi_data}


@app.delete("/delete_custom_kpi/{category}/{subcategory}/{kpi_id}")
def delete_custom_kpi(category: KPICategory, subcategory: str, kpi_id: str):
    cat = category.value

    if cat not in custom_kpis or subcategory not in custom_kpis[cat]:
        raise HTTPException(status_code=404, detail=f"Custom KPI path '{cat}/{subcategory}' not found.")

    if kpi_id not in custom_kpis[cat][subcategory]:
        raise HTTPException(status_code=404, detail=f"KPI ID '{kpi_id}' not found under '{cat}/{subcategory}'.")

    del custom_kpis[cat][subcategory][kpi_id]

    # Clean up if the subcategory is now empty
    if not custom_kpis[cat][subcategory]:
        del custom_kpis[cat][subcategory]

    # Clean up if the category is now empty
    if not custom_kpis[cat]:
        del custom_kpis[cat]

    return {"message": f"KPI '{kpi_id}' deleted successfully from '{cat}/{subcategory}'."}
