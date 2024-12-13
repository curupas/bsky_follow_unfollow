# Follow bluesky followers & Unfollow unfollowers

## Descrição

Dois scripts em Python: O script follow_back_bsky.py utilizado para seguir de volta usuários que passaram a seguir o usuário/password definido na variável de ambiente USERNAME_BSKY e o script unfollow_bsky.py utilizado para deixar de seguir usuários que seguiam, mas deixaram de seguir.

## Usuário & Senha

O usuário é lido da variável de ambiente USERNAME_BSKY e a senha da variável de ambiente PASSWORD_BSKY. Elas são armazenadas em Base64 para dificultar a leitura por alguém que está ao seu lado no computador enquanto por algum motivo são listadas as variáveis de ambiente. Não é uma proteção criptográfica. Os scripts em Python irão ler essas variáveis e decodificar o Base64 antes de usá-los no login. Abaixo um exemplo da codificação em Base64 em um ambiente linux. Note que podem existir diferenças nessas codificações ao usar Windows. Em outro momento explico essas diferenças. Para tornar essas variáveis permanentes você deve colocar as mesmas em um arquivo .bashrc (por exemplo) ou no Windows configurar apropriadamente nas propriedades/variáveis de ambiente de seu computador. Em algum momento futuro eu coloco um passo a passo aqui. :)

![2024-12-13 18_27_35-1_ Notifications — Bluesky — Navegador Yandex](https://github.com/user-attachments/assets/3d4c659f-3fe9-48bc-9ed0-a49cd7d1f3b7)


## Arquivos Adicionais

Os scripts confiam na existência de três arquivos: WHITELIST.bsky, BLACKLIST.bsky e KEYWORDS.bsky os quais são usados para não deixar de seguir um usuário mesmo que ele não esteja seguindo, não seguir um usuário de volta e não seguir caso a descrição, status ou o handle contenham algumas palavras-chave ou trechos. Além disso, o script não seguirá usuários que possuam certa quantidade de números no handle, número de posts etc. (em evolução).

### Exemplos

#### WHITELIST.bsky

legal.bsky.social<BR>
maislegal.bsky.social<BR>
joia.com.br<BR>

#### BLACKLIST.bsky

tosco.bsky.social<BR>
pilantra.bsky.social<BR>
safado.com.edu<BR>


#### KEYWORDS.bsky

venda<BR>
porn<BR>
sexo<BR>
promo<BR>

# ATENÇÃO!

Esses arquivos acima mencionandos precisam ser criados ou o script irá falhar (em algum momento o script será atualizado para verificar graciosamente se esses arquivos existem ou não). :)

