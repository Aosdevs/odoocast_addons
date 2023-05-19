import requests
import json

def consultar_placa_fipe(placa):
    url = "https://api.placafipe.xyz/getplacafipe"
    headers = {
        "Content-Type": "application/json"
    }
    token = "1CD78B0C54849E565D2E42FFC2AE899ADD8A401200FA43683D0C42ED76BBAD5F"  # Insira seu token válido aqui
    
    payload = {
        "placa": placa,
        "token": token,
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Exemplo de uso
placa = input("Digite a placa do veículo: ")
resultado = consultar_placa_fipe(placa)

if resultado is not None:
    print(resultado)
else:
    print("Falha ao consultar a placa.")
