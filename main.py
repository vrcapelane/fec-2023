import os
import pickle
import time
import cv2 as cv
import cvzone as cvz
import face_recognition
import numpy as np
import datetime
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# Credenciais para o banco de dados e storage bucket da firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://fec-2023-opencv-concept-default-rtdb.firebaseio.com/",
    'storageBucket': "fec-2023-opencv-concept.appspot.com"

})

# Inicialização do bucket da firebase
bucket = storage.bucket()

# Inicio da captura e ajuste das dimenções
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)

# Carrega o background e frame de usuario
backgorund_img = cv.imread("recursos/background_fec2023.jpg")
frame_usuario = cv.imread("recursos/frame_usuario.jpg")

# Carrega o algoritmo haarcascade
haarcascade_frontalface = cv.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")

# Verifica se a captura/camera funciona
if not cap.isOpened():

    print("Não foi possível abrir a câmera")
    exit()

# Carrega os encodings dos rostos
print("Carregamento dos rostos conhecidos iniciado!")
file = open("EncodedFile.p", 'rb')
lista_encodes_ids_conhecidos = pickle.load(file)
file.close()
lista_encodes_conhecidos, lista_ids = lista_encodes_ids_conhecidos
print("Carregamento dos rostos conhecidos finalizado")

# Declação das flags de controle externos
reconhecimento_facial_cadastrado_ativo = 0
aux_timer = time.time()


# Declaração das funções de reconhecimento facial e haarcascade
def algoritmo_haarcascade(mr, frm):

    # As nossas operações sobre os frames vêm aqui
    gray = cv.cvtColor(frm, cv.COLOR_BGR2GRAY)
    face = haarcascade_frontalface.detectMultiScale(gray)

    # Cria os traços que irão envolver as faces encontradas
    for (x, y, l, a) in face:

        x_escalado = x * mr
        y_escalado = y * mr
        l_escalado = l * mr
        a_escalado = a * mr

        cvz.cornerRect(frame, (x_escalado, y_escalado, l_escalado, a_escalado), 2, 2, 3,
                       (0, 255, 0), (0, 255, 0))


def reconhecimento_faces_cadastradas(frm):

    # Operações de reconhecimento de faces cadastradas
    frame_rgb = cv.cvtColor(frm, cv.COLOR_BGR2RGB)
    rostos_in_frame = face_recognition.face_locations(frame_rgb)
    encode_rostos_frame = face_recognition.face_encodings(frame_rgb, rostos_in_frame)

    # Variaveis auxiliares
    ra_id = -1

    # Processamento e comparacao de rostos com os encodes conhecidos
    for encode_rosto, rosto_in_frame in zip(encode_rostos_frame, rostos_in_frame):

        correspondencias_rostos = face_recognition.compare_faces(lista_encodes_conhecidos, encode_rosto)
        probabilidade_correspondencia_rostos = face_recognition.face_distance(lista_encodes_conhecidos, encode_rosto)
        indice_correspondencia = np.argmin(probabilidade_correspondencia_rostos)

        if correspondencias_rostos[indice_correspondencia]:

            # Extrai o ra/id do usuário conhecido
            ra_id = lista_ids[indice_correspondencia]

            # Baixa os dados do usuário
            ref = db.reference(f'Cadastro/{ra_id}')
            dados_usuario = ref.get()

            # Coloca as informações do usuário na tela
            cv.putText(backgorund_img, f'R.A.: {ra_id}', (500, 543), cv.FONT_HERSHEY_SIMPLEX, 0.7,
                       (0, 0, 0), 1)
            cv.putText(backgorund_img, f'Nome: {dados_usuario["nome"]}', (500, 563), cv.FONT_HERSHEY_SIMPLEX, 0.7,
                       (0, 0, 0), 1)
            cv.putText(backgorund_img, f'Curso: {dados_usuario["curso"]}', (500, 583), cv.FONT_HERSHEY_SIMPLEX, 0.7,
                       (0, 0, 0), 1)
            cv.putText(backgorund_img, f'Semestre: {dados_usuario["semestre_curso"]}', (500, 603),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
            cv.putText(backgorund_img, f'Ultima deteccao em: {format(datetime.strptime(dados_usuario["ultima_deteccao"], "%Y-%m-%d %H:%M:%S"), "%H:%M %d/%m/%Y")}', (500, 623),
                       cv.FONT_HERSHEY_SIMPLEX, 0.64, (0, 0, 0), 1)
            cv.putText(backgorund_img, f'Numero de vezes detectado: {dados_usuario["vezes_detectado"]}', (500, 643),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

            # Baixa e exibe a imagem do usuário
            blob = bucket.get_blob(f'recursos/rostos_usuarios/{ra_id}.jpg')
            img_usuario = np.frombuffer(blob.download_as_string(), np.uint8)
            frame_usuario[6:6 + 125, 6:6 + 125] = cv.imdecode(img_usuario, cv.COLOR_BGRA2BGR)
            backgorund_img[518:518 + 137, 348:348 + 137] = frame_usuario

            # Atualiza a firebase com o momento de ultima detecção e incrementa o número de vezes detectado
            dados_usuario["vezes_detectado"] += 1
            ref.child("vezes_detectado").set(dados_usuario["vezes_detectado"])
            ref.child("ultima_deteccao").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# Loop principal de processamento
while True:

    # Declaração das flags de controle internas e variáveis auxiliares
    timer = time.time()

    # Timer para reduzir o custo computacional do reconhecimento facial de faces cadastradas
    if timer - aux_timer >= 10.0:

        if reconhecimento_facial_cadastrado_ativo == 0:

            reconhecimento_facial_cadastrado_ativo = 1

        else:

            reconhecimento_facial_cadastrado_ativo = 0

        aux_timer = timer

    # Captura frame a frame
    ret, frame = cap.read()

    # se a imagem for lida corretamente ret é True
    if not ret:

        print("Não é possível receber frames, Saindo ...")

        break

    # Frame adicional reduzido para reconhecimento dos rostos (Redução de custo computacional)
    frame_reduzido = cv.resize(frame, (0, 0), None, 0.25, 0.25)
    mult_res = 4

    algoritmo_haarcascade(mult_res, frame_reduzido)

    if reconhecimento_facial_cadastrado_ativo == 1:

        # Limpa a área de exibição de dados, caso haja um, e prosegue para verificar outro
        background_vazio = 255 * np.ones((169, 640, 3), dtype=np.uint8)
        backgorund_img[502:502 + 169, 332:332 + 640] = background_vazio

        # Verifica se há faces conhecidas no frame
        reconhecimento_faces_cadastradas(frame_reduzido)

    # Terminado as comparações com as faces conhecidas, desliga o modulo para economizar recursos
    reconhecimento_facial_cadastrado_ativo = 0

    # Visualiza os frames resultantes
    backgorund_img[94:94 + 360, 332:332 + 640] = frame
    cv.imshow('FEC UNIARA 2023', backgorund_img)

    if cv.waitKey(1) == ord('q'):

        break

# Quando tudo estiver pronto, libera a cap e fecha as janelas
cap.release()
cv.destroyAllWindows()
