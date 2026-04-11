from datetime import datetime


def get_time_bucket():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "morning"

    if 12 <= hour < 17:
        return "afternoon"

    if 17 <= hour < 21:
        return "evening"

    if 21 <= hour < 24:
        return "night"

    return "late_night"

ENERGY_WEIGHTS = {

    "morning": {
        "career": 1.4,
        "skill": 1.3,
        "fitness": 1.0,
        "misc": 0.9
    },

    "afternoon": {
        "career": 1.2,
        "skill": 1.2,
        "fitness": 1.0,
        "misc": 1.0
    },

    "evening": {
        "career": 0.9,
        "skill": 1.0,
        "fitness": 1.5,
        "misc": 1.1
    },

    "night": {
        "career": 0.8,
        "skill": 1.0,
        "fitness": 0.8,
        "misc": 1.2
    },

    "late_night": {
        "career": 0.5,
        "skill": 0.7,
        "fitness": 0.5,
        "misc": 1.3
    }
}
def apply_energy_weight(goal):

    bucket = get_time_bucket()

    goal_type = goal.get("normalized_type", "misc")

    weight = ENERGY_WEIGHTS.get(bucket, {}).get(goal_type, 1.0)

    return weight, bucket