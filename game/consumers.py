from channels.consumer import AsyncConsumer
from .models import Game, GameMatrix
from channels.db import database_sync_to_async
from .helper import *
from channels.exceptions import StopConsumer
import json

# Per-game turn state: kiski baari hai? ('null' / 'on')
# key: game_code
TURN_STATE = {}  # { "790743": "null", ... }


def _initial_turn():
    """
    First move kiski hogi?
    Yahan 'null' wale player ko (host / code share karne wala) X maana gaya hai.
    """
    return "null"


def _toggle_turn(current):
    """
    'null' -> 'on'
    'on'   -> 'null'
    """
    return "on" if current != "on" else "null"


class GameConsumer(AsyncConsumer):
    async def websocket_connect(self, event):

        self.game_code = self.scope['url_route']['kwargs']['game_code']
        self.game_matrix_id = self.scope['url_route']['kwargs']['game_matrix_id']
        self.player_name = self.scope['url_route']['kwargs']['player_name']
        self.player_type = self.scope['url_route']['kwargs']['player_type']  # 'null' ya 'on'

        # Check game / player existence (original logic)
        game_object = await database_sync_to_async(Game.objects.filter)(game_code=self.game_code)
        game_exists = await database_sync_to_async(game_object.exists)()
        player_object = await database_sync_to_async(
            Game.objects.filter
        )(game_code=self.game_code, game_opponent='to-be-decided')
        player_exists = await database_sync_to_async(player_object.exists)()

        # Group join (original condition)
        if (not game_exists or player_exists):
            await self.channel_layer.group_add(self.game_code, self.channel_name)

        # Turn state init: har game_code ke liye sirf ek baar
        if self.game_code not in TURN_STATE:
            TURN_STATE[self.game_code] = _initial_turn()

        # Game setup DB side (original helper)
        self.game_id = await setup_game(
            self.game_code, self.game_matrix_id, self.player_name, self.player_type
        )

        await self.send({
            'type': 'websocket.accept',
        })

    async def websocket_receive(self, event):
        """
        Yahan pehle check karenge ki kya yeh player ki baari hai.
        Agar nahi → move ignore / message bhej do.
        """

        box_id = event.get('text')
        if not box_id:
            return

        # Kiski baari chal rahi hai?
        current_turn = TURN_STATE.get(self.game_code, _initial_turn())

        # Agar abhi jiski baari hai uska player_type == current_turn
        # to hi move allow karo, warna ignore
        if self.player_type != current_turn:
            # Optional info message: frontend chahe to handle kare
            await self.send({
                'type': 'websocket.send',
                'text': json.dumps({
                    "msg_type": "info",
                    "msg": "Not your turn yet. Please wait for opponent."
                })
            })
            return

        # ✅ Ab yaha se move valid hai (correct player's turn)

        # Matrix update & winner check (original logic)
        await update_matrix(self.game_matrix_id, box_id, self.player_type)
        self.result = await check_winner(self.game_matrix_id)

        # Result handling (original style)
        if (self.result == 44):
            await self.channel_layer.group_send(self.game_code, {
                'type': 'send.message',
                'message': json.dumps({"msg_type": "result", "msg": self.player_name})
            })
        elif (self.result == 11):
            await self.channel_layer.group_send(self.game_code, {
                'type': 'send.message',
                'message': json.dumps({"msg_type": "result", "msg": self.player_name})
            })
        elif (self.result == False):
            await self.channel_layer.group_send(self.game_code, {
                'type': 'send.message',
                'message': json.dumps({"msg_type": "result", "msg": "game drawn"})
            })

        # Har valid move ke baad chance broadcast (original)
        await self.channel_layer.group_send(self.game_code, {
            'type': 'send.message',
            'message': json.dumps({
                "msg_type": "chance",
                "position": box_id,
                "symbol": self.player_type  # 'null' / 'on' -> JS side X/O bnata hai
            })
        })

        # Sirf tab turn change karo jab game khatam NA ho:
        # result == 44 / 11 => winner; result == False => draw (tumhare helper ke hisaab se)
        if self.result not in (44, 11, False):
            TURN_STATE[self.game_code] = _toggle_turn(current_turn)
        else:
            # Game over hai, optional: turn state delete kar sakte hain
            # TURN_STATE.pop(self.game_code, None)
            pass

    async def send_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['message']
        })

    async def websocket_disconnect(self, event):

        game_matrix = await database_sync_to_async(GameMatrix.objects.get)(id=self.game_matrix_id)
        await database_sync_to_async(game_matrix.delete)()

        # Game khatam / disconnect par turn state clean karna optional:
        # TURN_STATE.pop(self.game_code, None)

        raise StopConsumer()
