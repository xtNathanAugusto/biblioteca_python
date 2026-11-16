import requests

BASE_URL = "http://127.0.0.1:5000/biblioteca"
TIMEOUT = 5  # segundos

_token = None
_usuario_logado = None


class ApiError(Exception):
    """Erro amigável para erros de API"""
    pass


def definir_sessao(token, bibliotecario):
    global _token, _usuario_logado
    _token = token
    _usuario_logado = bibliotecario


def limpar_sessao():
    global _token, _usuario_logado
    _token = None
    _usuario_logado = None


def obter_token():
    return _token


def obter_usuario_logado():
    return _usuario_logado


def esta_autenticado():
    return _token is not None


def request(method, endpoint, **kwargs):
    endpoint_formatado = endpoint.lstrip("/")
    url = f"{BASE_URL}/{endpoint_formatado}"

    headers = dict(kwargs.pop("headers", {}) or {})
    if _token and "Authorization" not in headers:
        headers["Authorization"] = f"Bearer {_token}"

    try:
        response = requests.request(method, url, timeout=TIMEOUT, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.ConnectionError:
        raise ApiError("Não foi possível conectar ao servidor. Verifique se o servidor está em execução.")
    except requests.exceptions.Timeout:
        raise ApiError("A solicitação excedeu o tempo limite. Tente novamente mais tarde.")
    except requests.exceptions.HTTPError as e:
        detalhes = e.response.text
        try:
            json_resp = e.response.json()
            if "erro" in json_resp:
                detalhes = json_resp["erro"]
        except Exception:
            pass
        raise ApiError(f"Erro na solicitação ({e.response.status_code}): {detalhes}")
    except ValueError:
        raise ApiError("Resposta inválida do servidor. Não foi possível decodificar o JSON.")


def listar(recurso):
    return request("GET", f"/{recurso}")


def buscar(recurso, id):
    return request("GET", f"/{recurso}/{id}")


def criar(recurso, dados):
    return request("POST", f"/{recurso}", json=dados)


def atualizar(recurso, id, dados):
    return request("PUT", f"/{recurso}/{id}", json=dados)


def deletar(recurso, id):
    return request("DELETE", f"/{recurso}/{id}")


def login(email, senha):
    resposta = request("POST", "/bibliotecarios/login", json={"email": email, "senha": senha})
    if resposta and "token" in resposta:
        definir_sessao(resposta["token"], resposta.get("bibliotecario"))
    return resposta


def logout():
    limpar_sessao()
