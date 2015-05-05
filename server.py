import time
import subprocess
import sys
import string
import urllib
import json
import BaseHTTPServer
from urlparse import urlparse
from SocketServer import ThreadingMixIn
from db_worker import Battle

HOST_NAME = 'localhost'
PORT_NUMBER = 8080


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    CODING = 'UTF-8'
    PING = u'/pyttleship'
    SHELL = u'/shell'
    NEW_GAME = u'/new_game'
    CONNECT_TO_GAME = u'/connect_game'
    SHOW_GAMES = u'/show_games'
    SET_SHIP = u'/set_ship'
    GET_STATE = u'/get_state'
    SHOT = u'/shot'

    def response(self, code, msg=None):
        """Sends specified return code and provides header.
        code: return code for sending
        """
        self.send_response(code)
        self.send_header("Content-type",
                         "text/html; charset={0}".format(self.CODING))
        self.end_headers()
        if msg is not None:
            msg = json.dumps(msg)
            self.wfile.write(msg.encode(self.CODING))

    def run_cmd(self, cmd):
        """Performs command into subprocess routine and returns stdout,
        stderr and return code.
        cmd: target command for performing
        """
        cmd = cmd.encode(sys.stdin.encoding)
        process_cmd = subprocess.Popen(cmd, shell=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        output, stderr = process_cmd.communicate()
        return (output.decode(sys.stdout.encoding),
                stderr.decode(sys.stdout.encoding),
                process_cmd.returncode)

    def shell(self, cmd):
        out, err, code = self.run_cmd(cmd)
        if not code:
            self.response(200)
            self.wfile.write(out.encode(self.CODING))
        else:
            self.response(418)
            self.wfile.write(err.encode(self.CODING))

    def new_game(self, game_name):
        result, data = Battle.new_game(game_name)
        if result:
            self.response(200, data)
        else:
            self.response(500)

    def connect_to_game(self, game_id):
        result, data = Battle.connect_to_game(game_id)
        if result:
            self.response(200, data)
        else:
            self.response(500)

    def show_games(self):
        result, data = Battle.show_games()
        if result:
            self.response(200, data)
        else:
            self.response(500)

    @staticmethod
    def _index_converter(data):
        symbols = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4,
                   'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9}

        if len(data) != 2 or not data[1].isdigit() or not data[0].isalpha():
            raise ValueError()

        if (data[0].upper() not in symbols or
                    int(data[1]) not in symbols.values()):
            raise ValueError()

        index = []
        index.append(symbols[data[0].upper()])
        index.append(int(data[1]))
        return index

    @staticmethod
    def _cell_counter(battlefield, value):
        count = 0
        for i, l in enumerate(battlefield):
            for j, n in enumerate(l):
                if n == value:
                    count += 1
        return True if count == 20 else False

    def set_ship(self, data):
        try:
            game_id = data['id']
            user = data['user']
            coordinates = data['coordinates']
            B = Battle(game_id, user)

            if len(coordinates) == 2:
                p1 = self._index_converter(coordinates)
                p2 = self._index_converter(coordinates)
            elif len(coordinates) == 4:
                p1 = self._index_converter(coordinates[:2])
                p2 = self._index_converter(coordinates[2:])
            else:
                raise ValueError()

            min0 = min(p1[0], p2[0])
            max0 = max(p1[0], p2[0])
            min1 = min(p1[1], p2[1])
            max1 = max(p1[1], p2[1])

            if p1[0] == p2[0]:
                l = max1 - min1 + 1
                for i in xrange(min1, max1 + 1):
                    if B.battlefield[i][p1[0]] != 0:
                        raise ValueError()
                B.ships.remove(l)
                for i in xrange(min1, max1 + 1):
                    B.battlefield[i+1 if i < 9 else i][p1[0]] = 4
                    B.battlefield[i-1 if i > 0 else i][p1[0]] = 4
                    B.battlefield[i][p1[0]+1 if p1[0] < 9 else p1[0]] = 4
                    B.battlefield[i][p1[0]-1 if p1[0] > 0 else p1[0]] = 4
                    (B.battlefield[i+1 if i < 9 else i]
                     [p1[0]+1 if p1[0] < 9 else p1[0]]) = 4
                    (B.battlefield[i+1 if i < 9 else i]
                     [p1[0]-1 if p1[0] > 0 else p1[0]]) = 4
                    (B.battlefield[i-1 if i > 0 else i]
                     [p1[0]+1 if p1[0] < 9 else p1[0]]) = 4
                    (B.battlefield[i-1 if i > 0 else i]
                     [p1[0]-1 if p1[0] > 0 else p1[0]]) = 4
                for i in xrange(min1, max1 + 1):
                    B.battlefield[i][p1[0]] = 1

            elif p1[1] == p2[1]:
                l = max0 - min0 + 1
                for i in xrange(min0, max0 + 1):
                    if B.battlefield[p1[1]][i] != 0:
                        raise ValueError()
                B.ships.remove(l)
                for i in xrange(min0, max0 + 1):
                    B.battlefield[p1[1]+1 if p1[1] < 9 else p1[1]][i] = 4
                    B.battlefield[p1[1]-1 if p1[1] > 0 else p1[1]][i] = 4
                    B.battlefield[p1[1]][i+1 if i < 9 else i] = 4
                    B.battlefield[p1[1]][i-1 if i > 0 else i] = 4
                    (B.battlefield[p1[1]+1 if p1[1] < 9 else p1[1]]
                     [i+1 if i < 9 else i]) = 4
                    (B.battlefield[p1[1]+1 if p1[1] < 9 else p1[1]]
                     [i-1 if i > 0 else i]) = 4
                    (B.battlefield[p1[1]-1 if p1[1] > 0 else p1[1]]
                     [i+1 if i < 9 else i]) = 4
                    (B.battlefield[p1[1]-1 if p1[1] > 0 else p1[1]]
                     [i-1 if i > 0 else i]) = 4
                for i in xrange(min0, max0 + 1):
                    B.battlefield[p1[1]][i] = 1

            else:
                raise ValueError()

            if self._cell_counter(B.battlefield, 1):
                B.state += 1

            result, data = B.save()
            if result:
                self.response(200, data)
            else:
                self.response(500)
        except:
            self.response(400)

    def get_state(self, data):
        try:
            game_id = data['id']
            user = data['user']
            B = Battle(game_id, user)
            result, data = B.get_state()
            if result:
                self.response(200, data)
            else:
                self.response(500)
        except:
            self.response(400)

    def shot(self, data):
        try:
            game_id = data['id']
            user = data['user']
            coordinates = data['coordinates']
            B = Battle(game_id, user)

            if B.current != user or B.state != 4:
                AssertionError()

            if len(coordinates) == 2:
                x, y = self._index_converter(coordinates)
            else:
                raise ValueError()

            if B.enemy[y][x] in [2, 3]:
                raise ValueError()

            elif B.enemy[y][x] in [0, 4]:
                B.enemy[y][x] = 3
                B.current = B.enemy_name

            elif B.enemy[y][x] == 1:
                B.enemy[y][x] = 2
                if y + 1 <= 9 and x + 1 <= 9:
                    B.enemy[y + 1][x + 1] = 3
                if y - 1 >= 0 and x - 1 >= 0:
                    B.enemy[y - 1][x - 1] = 3
                if y + 1 <= 9 and x - 1 >= 0:
                    B.enemy[y + 1][x - 1] = 3
                if y - 1 >= 0 and x + 1 <= 9:
                    B.enemy[y - 1][x + 1] = 3

                i = 1
                ship = [2]
                ends = []
                if y + 1 <= 9 and B.enemy[y + 1][x] not in [1, 2]:
                    ends.append([y + 1, x])
                if y - 1 >= 0 and B.enemy[y - 1][x] not in [1, 2]:
                    ends.append([y - 1, x])
                if x + 1 <= 9 and B.enemy[y][x + 1] not in [1, 2]:
                    ends.append([y, x + 1])
                if x - 1 >= 0 and B.enemy[y][x - 1] not in [1, 2]:
                    ends.append([y, x - 1])

                y1 = True; y2 =True; x1 = True; x2 = True
                while True:
                    l = len(ship) + len(ends)

                    if y1 and y + i <= 9 and B.enemy[y + i][x] in [1, 2]:
                        ship.append(B.enemy[y + i][x])
                        if (y + i + 1 <= 9 and
                                B.enemy[y + i + 1][x] not in [1, 2]):
                            ends.append([y + i + 1, x])
                    else:
                        y1 = False

                    if y2 and y - i >= 0 and B.enemy[y - i][x] in [1, 2]:
                        ship.append(B.enemy[y - i][x])
                        if (y - i - 1 >= 0 and
                                B.enemy[y - i - 1][x] not in [1, 2]):
                            ends.append([y - i - 1, x])
                    else:
                        y2 = False

                    if x1 and x + i <= 9 and B.enemy[y][x + i] in [1, 2]:
                        ship.append(B.enemy[y][x + i])
                        if (x + i + 1 <= 9 and
                                B.enemy[y][x + i + 1] not in [1, 2]):
                            ends.append([y, x + i + 1])
                    else:
                        x1 = False

                    if x2 and x - i >= 0 and B.enemy[y][x - i] in [1, 2]:
                        ship.append(B.enemy[y][x - i])
                        if (x - i - 1 >= 0 and
                                B.enemy[y][x - i - 1] not in [1, 2]):
                            ends.append([y, x - i - 1])
                    else:
                        x2 = False

                    if l == len(ship) + len(ends):
                        break

                    i += 1

                if 1 not in ship:
                    for p in ends:
                        B.enemy[p[0]][p[1]] = 3

            if self._cell_counter(B.enemy, 2):
                B.state += 1

            result, data = B.save()
            if result:
                self.response(200, data)
            else:
                self.response(500)
        except:
            self.response(400)

    def do_GET(self):
        """Respond to a GET request.
        """
        request = urllib.unquote(self.path).decode('UTF-8')
        try:
            request = urlparse(request)
            data = ''
            #if request.params:
                #data = json.loads(request.params)

            if request.path == self.SHELL:
                self.shell(request.params)

            elif request.path == self.PING:
                self.response(200, {'info': 'PyttleShip server is running'})

            elif request.path == self.NEW_GAME:
                if len(request.params) <= 32:
                    data = json.loads(request.params)
                    self.new_game(data['name'])
                else:
                    self.response(414)

            elif request.path == self.CONNECT_TO_GAME:
                if len(request.params) <= 32:
                    data = json.loads(request.params)
                    self.connect_to_game(data['id'])
                else:
                    self.response(414)

            elif request.path == self.SHOW_GAMES:
                self.show_games()

            elif request.path == self.SET_SHIP:
                data = json.loads(request.params)
                self.set_ship(data)

            elif request.path == self.GET_STATE:
                data = json.loads(request.params)
                self.get_state(data)

            elif request.path == self.SHOT:
                data = json.loads(request.params)
                self.shot(data)


            else:
                self.response(404)
        except:
            self.response(400)


class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread.
    """


if __name__ == '__main__':
    httpd = ThreadedHTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "PyttleShip Server Starts - {0}:{1}".format(
        HOST_NAME, PORT_NUMBER)
    try:
        Battle.prepare_table()
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "PyttleShip Server Stops - {0}:{1}".format(
        HOST_NAME, PORT_NUMBER)
