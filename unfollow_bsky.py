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

USERNAME_B64 = os.getenv('USERNAMEBSKY')
PASSWORD_B64 = os.getenv('PASSWORDBSKY')

decoded_user_bytes = base64.b64decode(USERNAME_B64)
decoded_pass_bytes = base64.b64decode(PASSWORD_B64)

decoded_user_text = decoded_user_bytes.decode("utf-8")
decoded_pass_text = decoded_pass_bytes.decode("utf-8")

USERNAME=decoded_user_text
PASSWORD=decoded_pass_text

def load_whitelist(filename='WHITELIST.bsky'):
    try:
        with open(filename, 'r') as file:
            whitelist = [line.strip() for line in file.readlines()]
        return whitelist
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        return []

def authenticate(client):
    client.login(USERNAME, PASSWORD)

def get_all_followers(client, username):
    followers = []
    cursor = None

    while True:
        response = client.get_followers(actor=username, cursor=cursor, limit=100)

        followers.extend(response.followers)

        if not response.cursor:
            break

        cursor = response.cursor
        time.sleep(0.1)

    return followers

def get_all_following(client, username):
    following = []
    cursor = None

    while True:
        response = client.get_follows(actor=username, cursor=cursor, limit=100)

        following.extend(response.follows)

        if not response.cursor:
            break

        cursor = response.cursor
        time.sleep(0.1)

    return following

def unfollow_non_followers(client, whitelist):
    followers = get_all_followers(client, USERNAME)
    following = get_all_following(client, USERNAME)

    followers_dids = {follower.did for follower in followers}
    following_dids = {follow.did for follow in following}

    users_to_unfollow = following_dids - followers_dids
    qtd_users_to_unfollow=len(users_to_unfollow) - len(whitelist)
    if(qtd_users_to_unfollow <=0):
        print(f"\nSeguidores: {len(followers)} Seguidos: {len(following)} Diferença: {abs(len(followers)-len(following))}")
        print(f"\nSem usuários para deixar de seguir.")
        exit(1)

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    whitelisted_found=0
    deixando_seguir=0
    # Deixar de seguir os usuários que não te seguem de volta, exceto os da whitelist
    with open("BLACKLIST.bsky", "a") as blacklist_file:
         for user_did in users_to_unfollow:
             try:
                 profile = client.get_profile(actor=user_did)

                 if profile.handle in whitelist:
                     whitelisted_found+=1
                     continue  # Pula para o próximo usuário

                 if(client.unfollow(profile.viewer.following)):
                     blacklist_file.write(f"{profile.handle}\n")
                     deixando_seguir+=1
                     print(f'Deixou de seguir: {user_did} (handle: {profile.handle})')

             except Exception as e:
                 print(f"Erro ao tentar deixar de seguir {user_did}: {e}")

    print(f"\nDeixando de seguir {deixando_seguir} usuários. Encontrados {whitelisted_found} seguidores na lista branca (continuar seguindo).")
    print(f"\nSeguidores: {len(followers)} Seguidos: {len(following)} Diferença: {abs(len(followers)-len(following))}\n\n")

def main():
    client = Client()

    try:
        whitelist = load_whitelist()

        authenticate(client)

        unfollow_non_followers(client, whitelist)

    except Exception as e:
        print(f'Erro: {e}')

# Executar o script
if __name__ == '__main__':
    main()
