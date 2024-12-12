# Follow bluesky followers & Unfollow unfollowers

## Descrição
Dois scripts em Python: O script follow_back_bsky.py utilizado para seguir de volta usuários que passaram a seguir o usuário/password definido na variável de ambiente USERNAME_BSKY e o script unfollow_bsky.py utilizado para deixar de seguir usuários que seguiam, mas deixaram de seguir.

Os scripts confiam na existência de três arquivos: WHITELIST.bsky, BLACKLIST.bsky e KEYWORDS.bsky os quais são usados para não deixar de seguir um usuário mesmo que ele não esteja seguindo, não seguir um usuário de volta e não seguir caso a descrição, status ou o handle contenham algumas palavras-chave ou trechos. Além disso o script não seguirá usuários que possuam certa quantidade de números no handle, número de posts etc. (em evolução).

Esses arquivos acima mencionandos precisam ser criados ou o script irá falhar (em algum momento o script será atualizado para verificar graciosamente se existem ou não). :)

Ainda não criei o requirements para o Python, mas é fácil descobrir. Vou criar "logo" também, assim como as instruções de uso. :)


