"""
Projeto: unfollow_bsky.py


Direitos Autorais (C) 2024 : Ricardo Tavares 

  Data: 2024-10-10
Versão: 20241010.01

AVISO: 
       Este software é fornecido "como está", sem garantias de qualquer tipo, expressas ou implícitas, 
       e em nenhum caso o autor ou os detentores dos direitos autorais serão responsáveis por quaisquer reivindicações, 
       danos ou outras responsabilidades, seja em uma ação de contrato, tortura ou outra ação decorrente de, 
       fora de ou em conexão com o software ou o uso ou outras negociações no software.

RESTRIÇÕES:
- Este software pode ser copiado, distribuído, ou modificado livremente.
"""

import time
import base64
import os
from atproto import Client, models
from datetime import datetime

# Informações da conta vindas de variáveis de ambiente
USERNAME_B64 = os.getenv('USERNAMEBSKY')
PASSWORD_B64 = os.getenv('PASSWORDBSKY')

# Decodificar strings base64
decoded_user_bytes = base64.b64decode(USERNAME_B64)
decoded_pass_bytes = base64.b64decode(PASSWORD_B64)

# Converter bytes para strings (UTF-8)
decoded_user_text = decoded_user_bytes.decode("utf-8")
decoded_pass_text = decoded_pass_bytes.decode("utf-8")

USERNAME=decoded_user_text
PASSWORD=decoded_pass_text

# Função para ler a whitelist de um arquivo TXT
def load_whitelist(filename='WHITELIST.bsky'):
    try:
        with open(filename, 'r') as file:
            # Ler cada linha do arquivo e remover espaços em branco e quebras de linha
            whitelist = [line.strip() for line in file.readlines()]
        return whitelist
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        return []

# Função para autenticar a conta
def authenticate(client):
    client.login(USERNAME, PASSWORD)

# Função para buscar todos os seguidores utilizando paginação com cursor
def get_all_followers(client, username):
    followers = []
    cursor = None

    while True:
        # Chama a API de get_followers com o cursor
        response = client.get_followers(actor=username, cursor=cursor, limit=100)

        # Adiciona os seguidores da resposta à lista de followers
        followers.extend(response.followers)

        # Se não houver mais cursor, significa que não há mais páginas de seguidores
        if not response.cursor:
            break

        # Atualiza o cursor para a próxima página
        cursor = response.cursor
        time.sleep(0.1)

    return followers

# Função para buscar todos os seguidos utilizando paginação com cursor
def get_all_following(client, username):
    following = []
    cursor = None

    while True:
        # Chama a API de get_follows com o cursor
        response = client.get_follows(actor=username, cursor=cursor, limit=100)

        # Adiciona os seguidos da resposta à lista de following
        following.extend(response.follows)

        # Se não houver mais cursor, significa que não há mais páginas de seguidos
        if not response.cursor:
            break

        # Atualiza o cursor para a próxima página
        cursor = response.cursor
        time.sleep(0.1)

    return following

# Função para deixar de seguir os usuários que não te seguem de volta
def unfollow_non_followers(client, whitelist):
    # Obter a lista de todos os seguidores e seguidos utilizando paginação
    followers = get_all_followers(client, USERNAME)
    following = get_all_following(client, USERNAME)

    # Converter listas para sets de DIDs (identificadores descentralizados)
    followers_dids = {follower.did for follower in followers}
    following_dids = {follow.did for follow in following}

    # Encontrar seguidos que não estão te seguindo de volta
    users_to_unfollow = following_dids - followers_dids
    qtd_users_to_unfollow=len(users_to_unfollow) - len(whitelist)
    if(qtd_users_to_unfollow <=0):
        # Imprimir a quantidade de seguidores e seguidos
        print(f"\nSeguidores: {len(followers)} Seguidos: {len(following)} Diferença: {abs(len(followers)-len(following))}")
        print(f"\nSem usuários para deixar de seguir.")
        exit(1)

    # Obter a data e hora atual no formato ISO 8601 exigido
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    whitelisted_found=0
    deixando_seguir=0
    # Deixar de seguir os usuários que não te seguem de volta, exceto os da whitelist
    with open("BLACKLIST.bsky", "a") as blacklist_file:
         for user_did in users_to_unfollow:
             try:
                 # Obter o perfil para pegar o handle
                 profile = client.get_profile(actor=user_did)

                 # Verificar se o handle está na whitelist
                 if profile.handle in whitelist:
#                     print(f"Usuário {profile.handle} está na whitelist. Não será deixado de seguir.")
                     whitelisted_found+=1
                     continue  # Pula para o próximo usuário

                 # Deixar de seguir o usuário
                 if(client.unfollow(profile.viewer.following)):
                     # Imprimir o DID e o handle
                     blacklist_file.write(f"{profile.handle}\n")
                     deixando_seguir+=1
                     print(f'Deixou de seguir: {user_did} (handle: {profile.handle})')

             except Exception as e:
                 # Em caso de erro, como o "InvalidRequest", exibir uma mensagem de erro e continuar
                 print(f"Erro ao tentar deixar de seguir {user_did}: {e}")

    # Imprimir a quantidade de usuários que precisam ser seguidos de volta
    print(f"\nDeixando de seguir {deixando_seguir} usuários. Encontrados {whitelisted_found} seguidores na lista branca (continuar seguindo).")
    print(f"\nSeguidores: {len(followers)} Seguidos: {len(following)} Diferença: {abs(len(followers)-len(following))}\n\n")

# Função principal
def main():
    client = Client()

    try:
        # Carregar a whitelist do arquivo
        whitelist = load_whitelist()

        # Autenticar o usuário
        authenticate(client)

        # Deixar de seguir os usuários que não te seguem de volta
        unfollow_non_followers(client, whitelist)

    except Exception as e:
        print(f'Erro: {e}')

# Executar o script
if __name__ == '__main__':
    main()
