from enum import Enum
from typing import Optional
import pandas as pd
import os
import json
import random
from pydantic import BaseModel
import openai
import json
from dotenv import load_dotenv, find_dotenv
import pandas as pd

_ = load_dotenv(find_dotenv())

client = openai.Client()

class Ticket(BaseModel):    
    modal_type: str
    model_config = {"extra": "allow"}

# Trafega
class History(BaseModel):
    tickets: list = []
    model_config = {"extra": "allow"}

# Trafega
class Player(BaseModel):   
    client_id: Optional[str] = ''
    tickets: list = []
    type: str = ''
    nick: str = None
    color: str
    current_spot: int = 0
    position: dict
    model_config = {"extra": "allow"}

class Route:
  def __init__(self, modal_type: str, spot_1: int, spot_2: int):
    modal_enum = modal_type  # throw KeyError

    if spot_1 == spot_2:
      raise Exception("Spot 1 and Spot 2 cannot be the same!")
    
    self.modal_type = modal_type
    self.spot_1 = spot_1
    self.spot_2 = spot_2

  def __eq__(self, other):
      if isinstance(other, Route):
          return (self.modal_type == other.modal_type and 
                  {self.spot_1, self.spot_2} == {other.spot_1, other.spot_2})
      return False

  def __hash__(self):
      return hash((self.modal_type, frozenset((self.spot_1, self.spot_2))))

  def __repr__(self):
      return f"Route({self.modal_type}, {self.spot_1}, {self.spot_2})"

class Spot:  
    def __init__(self, number: int, x: float, y: float):
        self.number = int(number)
        self.x = x
        self.y = y

class SpotManager:
    def __init__(self):
        self.routes = set()  
        self.spots = set()  

    def add_route(self, new_route: Route):
        if new_route in self.routes:
            raise Exception("This path already exists in the collection!")
        self.routes.add(new_route)

    def list_routes(self):
        return list(self.routes)

class Board:
    players_list = []
    spot_manager = SpotManager()
    history = History()
    status: str = 'not started'
    current_player: Player = None

    colors = [ "red", "purple", "magenta", "orange", "blue",]
    visible_rounds = [3, 8, 13, 18, 24]
    lista_de_dicionarios = []

    def __init__(self):
        # Current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        self.player_x_visible = False
        self.spot_list = []
        df = pd.read_csv(os.path.join(script_dir, "routes.csv"))
        for index, row in df.iterrows():    
            route = Route(row.MODAL, row.SPOT1, row.SPOT2)
            self.spot_manager.add_route(route)        
        df = pd.read_csv(os.path.join(script_dir, "sites.csv"))
        for index, row in df.iterrows():    
            spot = Spot(row.SPOT, row.X, row.Y)
            self.__add_spot(spot)        
        self.__load_config()


    def __carregar_percursos(self):
        # Current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))        
        nomeArquivo = os.path.join(script_dir, "routes.json")
        with open(nomeArquivo, 'r', encoding='utf-8') as f:
            retorno = json.load(f)
        return retorno

    def __consulta_privada(self, posicao):
        retorno = []
        print(f"Onde estou: {posicao}")
        print(f"Len da lista de dict: {len(self.lista_de_dicionarios)}")
        for dicionario in self.lista_de_dicionarios:
            valores = list(dicionario.values())
            modal, posicao1, posicao2 = valores
            print(f"Modal: {modal}, Posição 1: {posicao1}, Posição 2: {posicao2}") 
            posicaoEncontrada = ''        
            if posicao == str(posicao1):
                print(f"Encontrou na posição 1: {posicao2}")
                posicaoEncontrada = str(posicao2)
            elif posicao == str(posicao2):
                print(f"Encontrou na posição 2: {posicao1}")
                posicaoEncontrada = str(posicao1)
            if posicaoEncontrada != '':
                percurso = {"posicao": posicaoEncontrada, "modal": modal}
                print(f"Segundo encontrado, dá pra ir para esses lugares: {percurso}")
                retorno.append(percurso)
        
        print(f"Percursos retornados: {len(retorno)}")
        return json.dumps(retorno, ensure_ascii=False)


    def consultar_percurso(self, posicao):
        return self.__consulta_privada(posicao)


    tools = [
        {
            "type": "function",
            "function": {
                "name": "consultar_percurso",
                "description": "Obtem os percursos possíveis para a posição atual",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "posicao": {
                            "type": "string",
                            "description": "A posição atual. Ex. 124",
                        },
                    },
                    "required": ["posicao"]
                },
            },            
        }
    ]

    funcoes_disponiveis = {
        "consultar_percurso": consultar_percurso
    }

    def __check_player(self, nick: str):
        players = [player for player in self.players_list if player.nick == nick]
        if len(players) != 0:
            return True
        return False

    def __load_config(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "config.json"), "r", encoding="utf-8") as file:
            data = json.load(file)  

        self.max_players = data["MaxPlayers"]
        # Tickets for "Detective"
        self.detective_taxi_tickets = data["InitialTickets"]["Detective"]["Taxi"]
        self.detective_bus_tickets = data["InitialTickets"]["Detective"]["Bus"]
        self.detective_metro_tickets = data["InitialTickets"]["Detective"]["Metro"]
        # Tickets for "x"
        self.x_taxi_tickets = data["InitialTickets"]["x"]["Taxi"]
        self.x_bus_tickets = data["InitialTickets"]["x"]["Bus"]
        self.x_metro_tickets = data["InitialTickets"]["x"]["Metro"]
        self.x_hidden_tickets = data["InitialTickets"]["x"]["Hidden"]
        if self.x_hidden_tickets == "MaxPlayers":
            players = len([player for player in self.players_list if player.type == 'Detective'])
        else:
            players = int(data["InitialTickets"]["x"]["Hidden"])
        self.x_hidden_tickets = players
        self.play_twice = data["InitialTickets"]["x"]["PlayTwice"]

    def __sort_color(self):
        if len(self.colors) == 0:
            raise Exception("There's no more colors available")
        else:
            i = random.randint(0, len(self.colors) - 1)
            return self.colors.pop(i)

    def add_player(self, player: Player):
        try:
            print(f'{player.nick} just entered!')
            if self.__check_player(player.nick):
                raise Exception('There’s already a player with that nickname.')
            if self.status != "not started":
                raise Exception('Players can only be added before the match starts!')

            if player.type == 'X':
                if [player for player in self.players_list if player.type == 'X'] != []:
                    raise Exception('Only one player of type X is allowed.')

                for i in range(self.x_taxi_tickets):
                    player.tickets.append(Ticket(modal_type="TAXI"))
                for i in range(self.x_bus_tickets):
                    player.tickets.append(Ticket(modal_type="BUS"))
                for i in range(self.x_metro_tickets):
                    player.tickets.append(Ticket(modal_type="METRO"))
                if self.x_hidden_tickets == "":
                    for i in range(self.x_hidden_tickets):
                        player.tickets.append(Ticket(modal_type="HIDDEN"))
                player.color = "black"
                # X needs to be the first in the list
                self.players_list.insert(0, player)
            else:
                if len([player for player in self.players_list if player.type == 'Detective']) == self.max_players:
                    raise Exception(f'The maximum number of players ({self.max_players}) cannot be exceeded.')

                for i in range(self.detective_taxi_tickets):
                    player.tickets.append(Ticket(modal_type="TAXI"))
                for i in range(self.detective_bus_tickets):
                    player.tickets.append(Ticket(modal_type="BUS"))
                for i in range(self.detective_metro_tickets):
                    player.tickets.append(Ticket(modal_type="METRO"))
                player.color = self.__sort_color()
                self.players_list.append(player)            
            player.position = {"x": float(f"0.{len(self.players_list)}"), "y": 0}
            return_str = {"message": 'Player added!!!', "player": player}
        except Exception as e:            
            return_str = {"message": f'{e}', "player": None}
        finally:
            return return_str 

    def __add_spot(self, spot: Spot):
        self.spot_list.append(spot)

    def __get_player_in_spot(self, spot):
        player = next((player for player in self.players_list if player.current_spot == spot), None)
        if player:
            return player
        return None

    def __is_x_accessible(self, spot: int):
        for player in [p for p in self.players_list if p.type == "Detective"]:
            for modal_type in ["TAXI", "BUS", "METRO"]:
                filtered_routes = list(
                    filter(lambda route: {route.spot_1, route.spot_2} == {player.current_spot, spot} and route.modal_type == modal_type, self.spot_manager.list_routes())
                    )
                if len(filtered_routes) > 0:
                    return True
        return False    

    def start_match(self, player: Player):
        try:
            return_str = ''
            if self.__check_player(player.nick):
                raise Exception("Player doesn't exist!")
            if player.type != 'X':
                raise Exception('Player X is the only one allowed to start the match.')
            if self.status != "not started":
                raise Exception('The match has already been started!')
            if len(self.players_list) < 2:
                raise Exception('The game can only be started with at least two players.')
            for p in self.players_list:
                print(f"Player nickname: {p.nick}")
            self.current_player = self.players_list[0]
            # Initial cards 
            sort_list=[112,138,197,50,132,91,103,117,155,174,13,34,26,94,29,198,53,141]
            for player in self.players_list:
                item = random.randint(1, len(sort_list)) - 1
                initial_spot = sort_list.pop(item)
                player.current_spot = initial_spot
                spot = next((s for s in self.spot_list if s.number == initial_spot), None)
                player.position['x'] = spot.x
                player.position['y'] = spot.y
            self.status = "started"
            return_str = 'Match started'
        except Exception as e:
            return_str = f'{e}'
        finally:
            return return_str 

    def borrow_ticket(self, borrower: Player, lender: Player, modal_type):
        for ticket in borrower.tickets:
            if ticket.modal_type == modal_type:
                ticket = borrower.tickets.pop(borrower.tickets.index(ticket))
                break
        lender.tickets.append(ticket)

    def config(self):
        ret = f"detective_taxi {self.detective_taxi_tickets}, detective_taxi: {self.detective_bus_tickets}, detective_metro: {self.detective_metro_tickets}"
        return ret

    def is_x_hidden(self):
        return not len(self.history.tickets) in self.visible_rounds

    def get_history(self):
        messageSocket = ""
        for item in range(24):
            first_letter = " "
            if item < len(self.history.tickets):
                first_letter = str(self.history.tickets[item].modal_type)[0]
            mark = ""
            if (item + 1) in self.visible_rounds:
                mark = "*"
            messageSocket += f"[{mark + first_letter + mark}]" 
        return messageSocket

    def reset(self,player: Player):
        try:            
            self.status = "not started"
            for player in self.players_list:
                player.current_spot = 0
                player.position = {"x": 0, "y": 0}
            return_str = "Game restarted."
        except Exception as e:
            return_str = f'{e}'
            player = None
        finally:
            return {"message": return_str, "player": player}


    def remove_player(self, client_id: int):

        playerRemoved = None
        for p in self.players_list:
            print(f"Client ID for {p.nick}: {p.client_id}") 
            if p.client_id == client_id:
                playerRemoved = p
                exit

        if playerRemoved != None:
            if self.current_player.client_id == playerRemoved.client_id:
                self.__set_next(playerRemoved)
            self.players_list.remove(playerRemoved) 

    def __set_next(self, player: Player):
        if (self.players_list.index(player) + 1) >= len(self.players_list):
            self.current_player = self.players_list[0]
        else:
            self.current_player = self.players_list[self.players_list.index(self.current_player) + 1]

    def move(self, player: Player, new_spot, modal_type):
        try:
            return_str = ''
            if self.status == "not started":
                raise Exception(f"Players cannot be moved before the match has started.")
            if self.status == "finished":
                raise Exception(f"Players cannot be moved after the match has ended.")
            if player.type == "X" and len(self.history.tickets) == 24:
                self.status = "finished"
                raise Exception(f"Game over — you are the winner!")

            if player.nick != self.current_player.nick:
                raise Exception(f"Wait for your turn to play.")
            else:
                player = next((p for p in self.players_list if p.nick == player.nick), None)

            if modal_type == "HIDDEN":
                filtered_routes = list(
                    filter(lambda route: {route.spot_1, route.spot_2} == {player.current_spot, new_spot}, self.spot_manager.list_routes())
                    )
            else:
                filtered_routes = list(
                    filter(lambda route: {route.spot_1, route.spot_2} == {player.current_spot, new_spot} and route.modal_type == modal_type, self.spot_manager.list_routes())
                    )
            if len(filtered_routes) == 0:
                raise Exception(f"This path CANNOT be taken: {player.current_spot} -> {new_spot} by {modal_type}")

            for ticket in player.tickets:
                if ticket.modal_type == modal_type:
                    ticket = player.tickets.pop(player.tickets.index(ticket))
                    break
            
            pd = self.__get_player_in_spot(new_spot)

            if player.type == "X":
                if pd != None:
                    raise Exception(f"Another player is already in this spot!")

                self.history.tickets.append(ticket)

                if len(self.history.tickets) == 24:
                    if not self.__is_x_accessible(new_spot):
                        return_str = ' You are the winner, X! Congrats. Game over.'
                        self.status = "finished"
                
            else:
                if pd:
                    if pd.type == "X":
                        return_str = " You’ve taken down X! Game over"
                        self.status = "finished"
                    else:
                        raise Exception(f"Another player is already in this spot!")

                # Search for X and add
                p = next((player for player in self.players_list if player.type == 'X'), None)
                p.tickets.append(ticket)

            player.current_spot = new_spot
            spot = next((s for s in self.spot_list if s.number == new_spot), None)
            player.position["x"] = spot.x
            player.position["y"] = spot.y

            self.__set_next(player)

            return_str = "Movement successful." + return_str
        except Exception as e:
            return_str = f'{e}'
            player = None
        finally:
            return {"message": return_str, "player": player}

    def ask_ai(self, position):
        self.lista_de_dicionarios = self.__carregar_percursos()
        print(f"Tamanho da lista: {len(self.lista_de_dicionarios)}")
        print("Assistant: Bem vindo ao seu assistente. \n")

        mensagens = [{
            "role": "user",
            "content": f"A partir da posição '{position}', posso alcançar quais posições?\n"
        }]

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=mensagens,
            tools=self.tools,
            tool_choice="auto"
        )    

        print(f"Quantidade de choices: {len(resposta.choices)}")
        print(f"Lista de calls: {resposta.choices[0].message.tool_calls}")

        mensagem_resp = resposta.choices[0].message
        tool_call = mensagem_resp.tool_calls[0]
        function_name = tool_call.function.name
        function_to_call = self.funcoes_disponiveis[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            self, posicao=function_args.get("posicao")
        )

        # Adiciona a requisição do assistente
        mensagem_resp = resposta.choices[0].message.tool_calls
        call_id = mensagem_resp[0].id
        function_name = mensagem_resp[0].function.name
        args = mensagem_resp[0].function.arguments
        mensagens.append({
            "role": "assistant",
            "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {
                "name": function_name,
                "arguments": args
                }
            }
            ]
        })

        mensagem_resp = resposta.choices[0].message
        tool_call = mensagem_resp.tool_calls[0]
        function_name = tool_call.function.name
        function_to_call = self.funcoes_disponiveis[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            self, posicao=function_args.get("posicao")
        )

        # executa todas as chamadas às funções
        for tool_call in mensagem_resp.tool_calls:
            function_name = tool_call.function.name
            function_to_call = self.funcoes_disponiveis[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                self, posicao=function_args.get("posicao")
            )
            mensagens.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        # Realiza a segunda chamada
        segunda_resposta = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=mensagens,
        )

        resposta = segunda_resposta.choices[0].message.content
        print(f"\nAssistente: {resposta}\n" )
        return resposta



if __name__ == "__main__":
    board = Board()
    x = board._Board__carregar_percursos()
    print(f" len {len(x)}")

    # b = Player(color="red", type='Detective', nick="first", position={"x": 0, "y": 0})
    # b.current_spot = 62
    # c = Player(color="red", type='Detective', nick="second", position={"x": 0, "y": 0})
    # c.current_spot = 47
    # # l = Player()
    # # g = Player()
    # # board.history.tickets.append(Ticket(modal_type="TAXI"))
    # # board.history.tickets.append(Ticket(modal_type="BUS"))
    # # board.history.tickets.append(Ticket(modal_type="METRO"))
    # # board.history.tickets.append(Ticket(modal_type="HIDDEN"))
    # # board.history.tickets.append(Ticket(modal_type="BUS"))

    # board.add_player(b)
    # board.add_player(c)
    # # board.add_player(l)
    # # board.add_player(g)

    # # ret = board._Board__is_x_accessible(46)

    # print(board.get_history())
