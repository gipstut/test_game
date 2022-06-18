import asyncio
import websockets
import json
import secrets
import random

all_client = []
offer_game = {}


class Game:
    def __init__(self, userId, ntfId, match_token):
        self.userId = userId
        self.ntfId = ntfId
        self.match_token = match_token
        self.start_point_userId = 100
        self.start_point_ntfrId = 100
        self.count_step = 0

    def count_match_userId(self):
        self.start_point_userId = self.start_point_userId - random.randint(1, 20)
        self.count_step += 1

    def count_match_ntfId(self):
        self.start_point_ntfrId = self.start_point_ntfrId - random.randint(1, 20)
        print(self.start_point_ntfrId)
        self.count_step += 1

    def battles_move(self, token_match, userId, ntfId):
        if self.start_point_userId <= 0:
            response_to_move = {"UserId":"lost", "ntfId":"win"}
            return response_to_move

        elif self.start_point_ntfrId <= 0:
            response_to_move = {"UserId":"win", "ntfId":"lost"}
            return response_to_move

        elif userId == 'stone' and ntfId == 'scissors' or userId == 'scissors' and ntfId == 'paper' or  userId == 'paper' and ntfId == 'stone':
            self.count_match_ntfId()
            response_to_move = {"Win_userId_point_userId:":offer_game[token_match].start_point_userId, "ntfrId:":offer_game[token_match].start_point_ntfrId}
            return response_to_move

        elif ntfId == 'stone' and userId == 'scissors' or ntfId == 'scissors' and userId == 'paper' or ntfId == 'paper' and userId == 'stone':
            self.count_match_userId()
            response_to_move = {"Win_ntfId_point_userId:":offer_game[token_match].start_point_userId, "ntfrId:":offer_game[token_match].start_point_ntfrId}
            return response_to_move
        else:
            response_to_move = {"no one's, userId":offer_game[token_match].start_point_userId, "ntfrId":offer_game[token_match].start_point_ntfrId}
            return response_to_move

    def info(self, token_match):
        info_userId = offer_game[token_match].userId
        info_ntfrId = offer_game[token_match].ntfId
        poin_userId = offer_game[token_match].start_point_userId
        point_ntfr = offer_game[token_match].start_point_ntfrId
        count_step = offer_game[token_match].count_step
        event = {"userId":info_userId, "ntfrId":info_ntfrId, "point_UserId":poin_userId, "point_ntfrId":point_ntfr,"count_step":count_step}
        return event

async def new_client_connected(client_socket:websockets.WebSocketClientProtocol, path:str):
    while True:
        new_message = await client_socket.recv()
        all_client.append(client_socket)
        if path == '/battles_create':
            match_token = secrets.token_hex(16)          #Создание уникального токена выделенного по UserID1, NtfID1
            a = json.loads(new_message)                  #Перевод полученного JSON в dict
            userId = (a['userId'])                       #Получение значения словаря
            ntfId = (a['ntfId'])
            list_gamers = ['userId=' + str(userId), 'ntfId=' + str(ntfId)]
            event = {match_token:list_gamers}            #Формирование JSON ответа пара TOKEN матча, участники матча
            offer_game[match_token] = Game(userId=userId, ntfId=ntfId, match_token=match_token)
            await client_socket.send(json.dumps(event))


        elif path == '/battles_info':
            message_json = json.loads(new_message)
            token_match = (message_json['token_match'])
            event = offer_game[token_match].info(token_match)
            await client_socket.send(json.dumps(event))


        elif path == '/battles_move':
            message_json = json.loads(new_message)
            userId_step = (message_json['userId'])
            ntfId_step = (message_json['ntfId'])
            token_match = (message_json['token_match'])
            response_to_move = offer_game[token_match].battles_move(token_match=token_match, userId=userId_step, ntfId=ntfId_step)
            await client_socket.send(json.dumps(response_to_move))



async def start_server():
    await websockets.serve(new_client_connected, "localhost", 8001)


if __name__ == "__main__":
    event_loop=asyncio.get_event_loop()
    event_loop.run_until_complete(start_server())
    event_loop.run_forever()



