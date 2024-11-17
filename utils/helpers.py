import secrets
import string

from database.models import Player, Judge


async def generate_verification_code():
    characters = string.ascii_uppercase + string.digits
    code = "".join(secrets.choice(characters) for _ in range(4))

    existed_code_player = await Player.get_or_none(verify_code=code)
    existed_code_judge = await Judge.get_or_none(verify_code=code)

    if not existed_code_player and not existed_code_judge:
        return code
    else:
        return await generate_verification_code()
