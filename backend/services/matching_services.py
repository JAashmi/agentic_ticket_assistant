import math
import pickle
import os

# 🔹 MODEL PATH
MODEL_PATH = "ai_models/matching_model.pkl"


# 🔹 LOAD ML MODEL (OPTIONAL)
def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                print("✅ ML model loaded")
                return pickle.load(f)
        except Exception:
            print("⚠️ Failed to load ML model")
    return None


model = load_model()


# 🔹 DISTANCE (HAVERSINE - INDUSTRY STANDARD)
def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in KM

    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ==============================
# 🔥 ORGANIZATION SCORING
# ==============================

def rule_based_org_score(org, donation):
    """
    Rule-based org scoring:
    - closer distance = better
    - higher demand = higher priority
    """

    distance = calculate_distance(
        donation.lat,
        donation.lng,
        org.lat,
        org.lng
    )

    demand = org.required_quantity or 0

    # Normalize demand impact
    demand_score = -demand * 0.01  # negative because more demand = better

    return (distance * 0.6) + (demand_score * 0.4)


def calculate_org_score(org, donation):
    """
    Hybrid org scoring (Rule + ML)
    """

    base_score = rule_based_org_score(org, donation)

    # 🔹 If no ML model → fallback
    if model is None:
        return base_score

    distance = calculate_distance(
        donation.lat,
        donation.lng,
        org.lat,
        org.lng
    )

    demand = org.required_quantity or 0

    features = [[distance, demand]]

    try:
        ml_score = model.predict(features)[0]

        # 🔥 HYBRID COMBINATION
        final_score = (base_score * 0.6) + (ml_score * 0.4)

        return final_score

    except Exception:
        return base_score


def sort_organizations_by_priority(orgs, donation):
    """
    Sort organizations using hybrid scoring
    """
    return sorted(
        orgs,
        key=lambda org: calculate_org_score(org, donation)
    )


# ==============================
# 🔥 DELIVERY AGENT SCORING
# ==============================

def rule_based_agent_score(agent, donation, quantity):
    """
    Rule-based agent scoring:
    - nearer agent = better
    - better capacity usage = better
    """

    distance = calculate_distance(
        donation.lat,
        donation.lng,
        agent.lat,
        agent.lng
    )

    capacity_ratio = quantity / agent.capacity

    return (distance * 0.7) + (capacity_ratio * 0.3)


def calculate_agent_score(agent, donation, quantity):
    """
    Hybrid agent scoring (Rule + ML)
    """

    base_score = rule_based_agent_score(agent, donation, quantity)

    if model is None:
        return base_score

    distance = calculate_distance(
        donation.lat,
        donation.lng,
        agent.lat,
        agent.lng
    )

    capacity_ratio = quantity / agent.capacity

    features = [[distance, capacity_ratio]]

    try:
        ml_score = model.predict(features)[0]

        final_score = (base_score * 0.6) + (ml_score * 0.4)

        return final_score

    except Exception:
        return base_score


# ==============================
# 🔹 FILTERING UTILITIES
# ==============================

def filter_valid_agents(agents, quantity):
    """
    Return agents who can handle given quantity
    """
    return [
        agent for agent in agents
        if agent.capacity >= quantity
    ]