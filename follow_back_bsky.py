"""
Projeto: follow_back_bsky.py


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
import re
from atproto import Client, models
from datetime import datetime

USERNAME_B64 = os.getenv('USERNAMEBSKY')
PASSWORD_B64 = os.getenv('PASSWORDBSKY')

# Decodificar strings base64
decoded_user_bytes = base64.b64decode(USERNAME_B64)
decoded_pass_bytes = base64.b64decode(PASSWORD_B64)

decoded_user_text = decoded_user_bytes.decode("utf-8")
decoded_pass_text = decoded_pass_bytes.decode("utf-8")

USERNAME=decoded_user_text
PASSWORD=decoded_pass_text

def is_valid_bsky_handle(handle: str, max_num_length: int = 2) -> bool:
    """
    Verifica se a parte antes do '@' no handle do Bluesky é composta por letras,
    possivelmente seguida por números, onde o comprimento da parte numérica deve
    ser menor ou igual ao valor máximo especificado.

    Args:
        handle (str): O handle a ser verificado, por exemplo, 'joao@bsky.social'.
        max_num_length (int, optional): O comprimento máximo permitido para a parte numérica. Default é 2.

    Returns:
        bool: True se o handle for válido de acordo com as regras, False caso contrário.
    """
    try:
        username, domain = handle.split('.', 1)
    except ValueError:
        return False  # Handle inválido se não houver '@'

    letters_part = ''.join(filter(str.isalpha, username))  # Apenas letras
    numbers_part = ''.join(filter(str.isdigit, username))  # Apenas números
    # Regras de validação:
    # 1. Se não houver números, o handle é válido.
    # 2. Se houver números, o comprimento da parte numérica deve ser <= max_num_length.
    #return letters_part.isalpha() and (len(numbers_part) == 0 or len(numbers_part) <= max_num_length)
    return letters_part.isalpha() and (len(numbers_part) <= max_num_length)

def contains_keyword(keywords, text):
    if text is None:
        return False
    text = text.lower()
    for word in keywords:
        if text in word.lower():
            return True
    for word in keywords:
        if word.lower() in text:
            return True
    return False

def load_keywords(filename='KEYWORDS.bsky'):
    try:
        with open(filename, 'r') as file:
            keywords = [line.strip() for line in file.readlines()]
        return keywords
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        return []

def load_blacklist(filename='BLACKLIST.bsky'):
    try:
        with open(filename, 'r') as file:
            _blacklist = [line.strip() for line in file.readlines()]
        return _blacklist
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

def follow_back(client, blacklist, keywords):
    followers = get_all_followers(client, USERNAME)
    following = get_all_following(client, USERNAME)

    followers_dids = {follower.did for follower in followers}
    following_dids = {follow.did for follow in following}

    users_to_follow_back = followers_dids - following_dids

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    seguindo=0
    blacklisted_found=0
    with open("BLACKLIST.bsky", "a") as blacklist_file:
         print("")
         for user_did in users_to_follow_back:
             profile = client.get_profile(actor=user_did)

             if(profile.description is None):
                 description="Sem descrição"
             else:
                 description=profile.description

             if(profile.display_name is None):
                 display_name="Sem display name"
             else:
                 display_name=profile.display_name

             resultado_description  = contains_keyword(keywords, description)
             resultado_display_name = contains_keyword(keywords, display_name)
             resultado_handle = contains_keyword(keywords, profile.handle)
             valor_posts_count = profile.posts_count

             if profile.handle in blacklist:
                 print('Blacklist: {} ({}).'.format(profile.handle, (description[:30]).replace("\n", "")))
                 blacklisted_found+=1
                 continue  # Pula para o próximo usuário

             if(resultado_description or resultado_handle or resultado_display_name):
                 print(' Keywords: {} ({}).'.format(profile.handle, (description[:30]).replace("\n", "")))
                 blacklist_file.write(f"{profile.handle}\n")
                 continue

             status=(is_valid_bsky_handle(profile.handle))
             if not status:
                 print(' Suspeito: {} ({}).'.format(profile.handle, (description[:30]).replace("\n", "")))
                 blacklist_file.write(f"{profile.handle}\n")
                 continue 

             if profile.posts_count <= 10:
                 print('Não Posta: {} ({}) Posts: {}.'.format(profile.handle, (description[:30]).replace("\n", ""),profile.posts_count))
                 continue  # Pula para o próximo usuário

             seguindo+=1
             client.follow(user_did)

             print(' Seguindo: {} (handle: {} ({}))'.format(user_did, profile.handle, (description[:20]).replace("\n", "")))

    print(f"\nSeguindo de volta {seguindo} usuários. Encontrados {blacklisted_found} seguidores na lista negra (não seguir de volta).")
    print(f"\nSeguidores: {len(followers)} Seguidos: {len(following) + seguindo } Diferença: {abs(len(followers)-len(following)) + seguindo }\n\n")

def main():
    client = Client()

    try:
        keywords = load_keywords()
        blacklist = load_blacklist()

        authenticate(client)
        follow_back(client, blacklist, keywords)
    
    except Exception as e:
        print(f'Erro: {e}')

if __name__ == '__main__':
    main()

