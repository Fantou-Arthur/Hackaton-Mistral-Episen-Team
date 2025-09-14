import base64, json
def _claims(token: str):
    p = token.split(".")[1] + "=" * (-len(token.split(".")[1]) % 4)
    return json.loads(base64.urlsafe_b64decode(p).decode())

# après avoir obtenu le token :
t = self._get_token()
c = _claims(t)
print("DEBUG claims:", {"has_scp": "scp" in c, "scp": c.get("scp"), "has_roles": "roles" in c})