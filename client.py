import json
import urllib2
import urllib
import functools


def common(err_msg):
    def new_func(func):
        def wraped(*args, **kwargs):
            try:
                code, data = func(*args, **kwargs)
                if code//100 in [1, 2]:
                    data = json.loads(data)
                    if 'error' in data:
                        return False, data['error']
                    else:
                        return True, data
                else:
                    return False, err_msg
            except:
                return False, err_msg
        return wraped
    return new_func


class Client(object):

    CODING = 'UTF-8'
    PING = u'/pyttleship'
    NEW_GAME = u'/new_game'
    CONNECT_TO_GAME = u'/connect_game'
    SHOW_GAMES = u'/show_games'
    SET_SHIP = u'/set_ship'
    GET_STATE = u'/get_state'
    SHOT = u'/shot'

    def __init__(self, address, port):
        code, data = self.request(address, port, self.PING)
        if code == 200:
            self.address = address
            self.port = port
            self.request = functools.partial(self.request,
                                             self.address,
                                             self.port)
        else:
            raise ValueError('PyttleShip server not found')

    @staticmethod
    def request(address, port, command, data=''):
        if data != '':
            data = json.dumps(data)
            data = urllib.quote(data.encode(Client.CODING))
        url = "http://{0}:{1}{2};{3}".format(address, port, command, data)
        response = urllib2.urlopen(url)
        return response.code, response.read()

    @common('Unable to create new game')
    def new_game(self, game_name):
        json_data = {'name': game_name}
        return self.request(self.NEW_GAME, json_data)

    @common('Unable to connect to the game')
    def connect_to_game(self, game_id):
        json_data = {'id': game_id}
        return self.request(self.CONNECT_TO_GAME, json_data)

    @common('Unable to get list of games')
    def show_games(self):
        return self.request(self.SHOW_GAMES)

    @common('Unable to set ship')
    def set_ship(self, game_id, user, coord):
        json_data = {'id': game_id,
                     'user': user,
                     'coordinates': coord}
        return self.request(self.SET_SHIP, json_data)

    @common('Unable to get state')
    def get_state(self, game_id, user):
        json_data = {'id': game_id,
                     'user': user}
        return self.request(self.GET_STATE, json_data)

    @common('Unable to make shot')
    def shot(self, game_id, user, coord):
        json_data = {'id': game_id,
                     'user': user,
                     'coordinates': coord}
        return self.request(self.SHOT, json_data)
