import secrets
import string

from database.models import Player, Judge


async def generate_verification_code():
    characters = string.ascii_uppercase + string.digits
    code = "".join(secrets.choice(characters) for _ in range(4))
    existed_code_player = Player.filter(verify_code=code).exists()
    existed_code_judge = Judge.filter(verify_code=code).exists()
    if existed_code_player or existed_code_judge:
        await generate_verification_code()
    return code
