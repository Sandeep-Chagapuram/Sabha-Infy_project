from datetime import timedelta
from typing import Optional
from livekit import api
from app.core.config import settings

class LiveKitService:
    """
    LiveKit Real-Time WebRTC Media Server Integration:
    - Server-side Room creation
    - Short-lived scoped participant AccessTokens (audio/video publish & subscribe)
    - Participant identity matching authenticated user
    """

    @classmethod
    def generate_token(
        cls,
        room_name: str,
        participant_identity: str,
        participant_name: str,
        can_publish: bool = True,
        can_subscribe: bool = True,
        is_admin: bool = False
    ) -> str:
        """
        Generates a secure, short-lived JWT token for joining the LiveKit room.
        """
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        token.with_identity(participant_identity)
        token.with_name(participant_name)
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=can_publish,
                can_subscribe=can_subscribe,
                room_admin=is_admin
            )
        )
        token.with_ttl(timedelta(hours=2))
        return token.to_jwt()
