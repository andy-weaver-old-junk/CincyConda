TECH_CONTACTS_API_ENDPOINT = "http://localhost:5000/api/get-tech-contacts"

import requests
import json

def get_tech_contacts():
    """
    Get the technical contacts for the CincyConda project.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        A dictionary of technical contacts for the CincyConda project.
    """
    response = requests.get(TECH_CONTACTS_API_ENDPOINT)
    return json.loads(response.text)
        