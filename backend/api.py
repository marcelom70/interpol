import json
from interpol.game import *
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

game = Board()
connections = [] 

class MoveRequest(BaseModel):
    player: Player
    new_spot: int
    modal_type: str

    model_config = {
        "extra": "allow"
    }


@app.get("/")
async def read_root():    
    return {"message": f"Interpol API already running. Match {'' if game.status == 'not started' else 'not '}started"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()            
            print(f"Received data: {data}")
            websocket.client_id = json.loads(data)["id"]
    except WebSocketDisconnect:
        if hasattr(websocket, "client_id"):
            game.remove_player(websocket.client_id)
        connections.remove(websocket)

@app.post("/add-player")
async def add_player(player: Player, response: Response):
    message = game.add_player(player)
    print(f"Player: {message['player'] == None}")
    if message["player"] == None:
        response.status_code = 500
    else:
        response.status_code = 200
    return message

@app.get("/players")
def list_players(response: Response):
    return {"players": len(game.players_list)}  

@app.post("/start-match")
async def start_match(player: Player, response: Response):
    print(f"Cliente ID on start_match: {player.client_id}")
    message = game.start_match(player)
    if message == "Match started":
        response.status_code = 200
        for player in game.players_list:
            messageSocket = ''
            for p in game.players_list:
                if p.nick == game.current_player.nick:
                    messageSocket += f'*{p.nick}* '
                else:
                    messageSocket += f'{p.nick} '
            
            messageSocket += " - " + game.get_history()

            content = json.dumps({"message": messageSocket, "player": player.model_dump()})
            if player.type == "X":
                print(f"Player client id: {player.client_id}")
                xSocket = next((s for s in connections if s.client_id == player.client_id), None)
                if xSocket == None:
                    print("Socket is none")
                else:
                    print("Socket notified")
                    await xSocket.send_text(content)
            else:
                for conn in connections:
                    await conn.send_text(content)
    else:
        response.status_code = 500

    return {"message": message}

@app.post("/move")
async def move_player(request: MoveRequest, response: Response):
    message = game.move(request.player, request.new_spot, request.modal_type)
    player: Player = message["player"]
    if player == None:
        response.status_code = 500
    else:
        messageSocket = ''
        for p in game.players_list:
            if p.nick == game.current_player.nick:
                messageSocket += f'*{p.nick}* '
            else:
                messageSocket += f'{p.nick} '
            
        messageSocket += " - " + game.get_history()

        if player.type == 'X':
            content_4_x = json.dumps({"message": messageSocket, "player": player.model_dump()})
            print(f"content_4_x: {content_4_x}")
            if game.is_x_hidden():
                print("Hidden!")
                player.position = {"x": 0, "y": 0}
            else:
                print("Not hidden!")
            # content_4_all = json.dumps(player.model_dump())
            content_4_all = json.dumps({"message": messageSocket, "player": player.model_dump()})
            print(f"content_4_all: {content_4_all}")

            xSocket = next((s for s in connections if s.client_id == player.client_id), None)
            await xSocket.send_text(content_4_x)

            for conn in (s for s in connections if s.client_id != player.client_id):
                await conn.send_text(content_4_all)
        else:
            # content_4_all = json.dumps(player.model_dump())
            content_4_all = json.dumps({"message": messageSocket, "player": player.model_dump()})
            for conn in connections:
                await conn.send_text(content_4_all)

        response.status_code = 200
    return message

@app.post("/reset")
async def reset(request: MoveRequest, response: Response):
    message = game.reset(request.player)

    if message == "Game restarted":
        response.status_code = 200
    else:
        response.status_code = 500
    return message

@app.post("/ask-ai")
async def ask_ai(request: Player, response: Response):
    message = game.ask_ai(request.current_spot)

    if message == "Game restarted":
        response.status_code = 200
    else:
        response.status_code = 500
    return message



@app.get("/config")
def list_config(response: Response):
    return {"config": game.config()}  
