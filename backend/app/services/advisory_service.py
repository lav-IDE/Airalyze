def generate_advisory(ward_id: str):
    advisories = {
        "anand_vihar": {
            "risk": "High",
            "message": "Avoid outdoor exercise. Wear an N95 mask if going outside.",
            "color": "red"
        },
        "mandir_marg": {
            "risk": "Moderate",
            "message": "Sensitive groups should reduce prolonged outdoor activity.",
            "color": "yellow"
        }
    }

    return advisories.get(ward_id)