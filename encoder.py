import os
import cv2 as cv
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': "fec-2023-opencv-concept.appspot.com"
})

caminho_pasta = "recursos/rostos_usuarios"
lista_de_caminhos = os.listdir(caminho_pasta)
lista_rostos = []
lista_ra_ids = []

for caminho in lista_de_caminhos:
    lista_rostos.append(cv.imread(os.path.join(caminho_pasta, caminho)))
    lista_ra_ids.append(os.path.splitext(caminho)[0])

    nome_arquivo = f'{caminho_pasta}/{caminho}'
    bucket = storage.bucket()
    blob = bucket.blob(nome_arquivo)
    blob.upload_from_filename(nome_arquivo)

print(lista_ra_ids)


def gerar_encodings(lista_imagens):

    lista_encodes = []
    for rosto in lista_imagens:
        rosto = cv.cvtColor(rosto, cv.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(rosto)[0]
        lista_encodes.append(encode)

    return lista_encodes


print("Inicio do ENCODE!")
lista_encodes_conhecidos = gerar_encodings(lista_rostos)
lista_encodes_ids = [lista_encodes_conhecidos, lista_ra_ids]
print("Fim do ENCODE!")
print(lista_encodes_conhecidos)

file = open("EncodedFile.p", 'wb')
pickle.dump(lista_encodes_ids, file)
file.close()
print("Encode salvo!")
