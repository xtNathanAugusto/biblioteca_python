import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import request, jsonify, g

# Boas práticas de segurança: chave forte via variável de ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "BIBLIOTECA-FATEC-CHAVE-SECRETA-DEV")
HORAS_EXPIRACAO = 2


def gerar_token(id_bibliotecario: int, email: str) -> str:
    """Gera um token JWT com expiração de 2 horas."""
    payload = {
        "id_bibliotecario": id_bibliotecario,
        "email": email,
        # Corrigido: timedelta(...) com parênteses chamando a função
        "exp": datetime.now(timezone.utc) + timedelta(hours=HORAS_EXPIRACAO),
        "iat": datetime.now(timezone.utc),  # Adicionado: data de emissão
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        cabecalho = request.headers.get("Authorization", "")

        # Validação do cabeçalho de autorização no padrão 'Bearer <token>'
        if not cabecalho.startswith("Bearer "):
            return jsonify({"erro": "Token não informado ou mal formatado"}), 401

        partes = cabecalho.split(" ", 1)
        if len(partes) != 2:
            return jsonify({"erro": "Formato de token inválido"}), 401

        token = partes[1]

        try:
            # Corrigido: bloco try/except e parâmetro algorithms em lista
            dados_decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.bibliotecario = dados_decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado. Faça login novamente."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401

        return funcao(*args, **kwargs)

    return wrapper