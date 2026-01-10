import requests
import time
from bs4 import BeautifulSoup
import logging
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

timeout = 10
session = requests.Session()

class LoginError(Exception):
    pass
class RequestError(Exception):
    pass
class UnknownError(Exception):
    pass

def login(username: str, password: str):

    """
    Function to log in to the web agent.
    Returns current_key and current_user upon successful login.
    If login fails, raises LoginError.
    If a request exception occurs, raises RequestError.
    If current_key or current_user is missing, raises UnknownError.
    If an unknown error occurs, raises UnknownError.
    
    :param username: Username for login
    :type username: str
    :param password: Password for login
    :type password: str
    :return: current_key and current_user
    :rtype: tuple[str, str]
    """
    data = {
    "user": username,
    "password_user": password,
    "login_ts": int(time.time()),
    "form_login": "true"
    }
    import json
    try:
        with open(resource_path("config.json"), 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logging.error("Configuration file not found: config.json")
        raise FileNotFoundError("Configuration file not found")
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from config.json")
        raise ValueError("Error decoding JSON from configuration file")
    try:
        response_login = session.post(config["api"], data=data, timeout=timeout)
    except requests.exceptions.RequestException as e:
        logging.error(f"Login request failed: {e}")
        raise RequestError("Request exception during login")
    except Exception as e:
        logging.error(f"Unexpected error during login: {e}")
        raise UnknownError("Unknown error during login")
    soup = BeautifulSoup(response_login.text, 'html.parser')
    title = soup.find("title")
    title = title.text.strip() if title else ""
    if "Login" in title:
        logging.error("Login failed: Invalid credentials")
        raise LoginError("Invalid credentials")
    current_key_input = soup.find('input', {'name': 'current_key'})
    current_key = current_key_input['value'] if current_key_input else None 
    current_user_input = soup.find('input', {'name': 'current_user'})
    current_user = current_user_input['value'] if current_user_input else None
    if not current_key or not current_user:
        logging.error("Login failed: Missing session parameters")
        raise UnknownError("Missing session parameters after login")
    return current_key, current_user

def voti(current_key: str, current_user: str):
    """
    Function to retrieve grades from the web agent.
    Returns a list of dictionaries containing grades information.
    The list is ordered from oldest to newest grade.
    If session is invalid, raises LoginError.
    If a request exception occurs, raises RequestError.
    If no grades are found, returns an empty list.
    If an unknown error occurs, raises UnknownError.

    :param current_key: Current session key(from login)
    :type current_key: str
    :param current_user: Current user identifier(from login)
    :type current_user: str
    :return: List of grades information
    :rtype: list[dict]
    """
    data = {
    "form_stato": "studente",
    "stato_principale": "voti",
    "current_user": current_user,
    "current_key": current_key,
    "header": "SI",
    }
    with open(resource_path("config.json"), 'r') as f:
        import json
        config = json.load(f)
    try:
        response_voti = session.post(config["api"], data=data, timeout=timeout)
    except requests.exceptions.RequestException as e:
        logging.error(f"Voti request failed: {e}")
        raise RequestError("Request exception during voti retrieval")
    except Exception as e:
        logging.error(f"Unexpected error during voti retrieval: {e}")
        raise UnknownError("Unknown error during voti retrieval")
    soup = BeautifulSoup(response_voti.text, 'html.parser')
    title = soup.find("title")
    title = title.text.strip() if title else ""
    if "Login" in title:
        logging.error("Session invalid: Wrong/expired session")
        raise LoginError("Wrong/expired session")
    righe_voti = soup.find_all('tr', attrs={'data-tipo': 'voto'})
    risultati = []
    for riga in righe_voti:
        if not riga.find_all("td"):
            continue
        if len(riga.find_all("td")) < 3:
            continue
        td_materia = riga.find_all("td")[2]
        td_voto = riga.find_all("td")[0]
        strong_tag = td_voto.find("strong")
        if not strong_tag:
            continue        
        try:
            voto = float(strong_tag.text.strip())
        except (ValueError, AttributeError):
            continue        
        materia_strong = td_materia.find("strong")
        if not materia_strong:
            continue
        materia = materia_strong.text.strip()
        peso_div = td_voto.find("div", class_="margin-top-small small border round padding-xsmall")
        if peso_div:
            testo = peso_div.get_text()
            peso = int("".join(c for c in testo if c.isdigit()) or "100")
        else:
            peso = 100
        risultati.append({
        "voto": voto,
        "materia": materia,
        "peso": peso
        })
    return risultati[::-1]