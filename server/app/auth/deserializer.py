from app.auth.token import SessionToken


class Deserializer:
    def __init__(self, payload: dict):
        self.payload = payload

    def deserialize(self) -> SessionToken:
        return SessionToken(
            sub=self.payload["sub"],
            scope=self.payload.get("scope", ""),
            permissions=self.payload.get("permissions", []),
            iss=self.payload.get("iss"),
            aud=self.payload.get("aud"),
            exp=self.payload.get("exp"),
            iat=self.payload.get("iat"),
        )
