import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://fec-2023-opencv-concept-default-rtdb.firebaseio.com/"
})

ref = db.reference('Cadastro')

data = {
    "05219034": {
        "nome": "Vitor Regatieri Capelane",
        "curso": "Engenharia de Computacao",
        "semestre_curso": 10,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    },
    "05219020": {
            "nome": "Wallace Sinatra",
            "curso": "Engenharia de Computacao",
            "semestre_curso": 10,
            "ultima_deteccao": "2023-08-29 21:51:00",
            "vezes_detectado": 0
        },
    "05219024": {
        "nome": "Nicole Alves",
        "curso": "Engenharia de Computacao",
        "semestre_curso": 10,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    },
    "05223004": {
        "nome": "Eduardo Ortolani Turco",
        "curso": "Engenharia de Computacao",
        "semestre_curso": 2,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    },
    "05220550": {
        "nome": "Peter Júnior Lemes Marcucci",
        "curso": "Engenharia de Computacao",
        "semestre_curso": 10,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    },
    "05219033": {
        "nome": "Adrian Lucas Tavares da Piedade",
        "curso": "Engenharia de Computacao",
        "semestre_curso": 10,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    },
    "00000000": {
        "nome": "João Henrique Gião Borges",
        "curso": "",
        "semestre_curso": 0,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    },
    "00000001": {
        "nome": "Arthur",
        "curso": "Desing Digital",
        "semestre_curso": 0,
        "ultima_deteccao": "2023-08-29 21:51:00",
        "vezes_detectado": 0
    }
}

for key, value in data.items():
    ref.child(key).set(value)
