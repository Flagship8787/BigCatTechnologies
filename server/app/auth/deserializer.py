from app.auth.token import TokenData


class Deserializer:
    def __init__(self, payload: dict):
        self.payload = payload

    def deserialize(self) -> TokenData:
        return TokenData(
            sub=self.payload["sub"],
            scope=self.payload.get("scope", ""),
            iss=self.payload.get("iss"),
            aud=self.payload.get("aud"),
            exp=self.payload.get("exp"),
            iat=self.payload.get("iat"),
        )
