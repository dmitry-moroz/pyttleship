import curses
import time
import sys
import subprocess
from multiprocessing import Manager, Process, Event
from client import Client



class Game(object):
    #curses.endwin()
    #pdb.set_trace()
    err_msg_delay = 2
    refresh_delay = 5

    def __init__(self):
        self.port = ''
        self.address = ''
        self.game_id = None
        self.user = None
        self.client = None
        self.battlefield = None
        self.ships = None
        self.enemy = None
        self.state = None
        self.current = None
        height, width = subprocess.check_output(['stty', 'size']).split()
        self.height = int(height)
        self.width = int(width)

    def create_game_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 30, "New BATTLE!")
        screen.addstr(3, 1, "="*(self.width - 2))
        screen.addstr(18, 1, "  0 - Back to main menu")
        screen.addstr(19, 1, "="*(self.width - 2))
        screen.addstr(21, 1, "  Enter a game name:")
        screen.refresh()

    def create_game(self):
        self.game_id = None
        self.user = None
        self.battlefield = None
        self.ships = None
        self.enemy = None
        self.state = None
        self.current = None
        key = ''
        while key != '0':
            key = screen.getstr(21, 22)
            if key == '0':
                return False
            elif self.client is None:
                screen.addstr(22, 1, "  Server address is not specified, "
                                     "specify the server address...")
                screen.refresh()
                time.sleep(self.err_msg_delay)
                self.create_game_screen()
            else:
                result, data = self.client.new_game(key)
                if result:
                    self.battlefield = data['battlefield']
                    self.user = data['user']
                    self.game_id = data['id']
                    return True
                else:
                    screen.addstr(22, 1, "  Error: {0}".format(data))
                    screen.refresh()
                    time.sleep(self.err_msg_delay)
                    self.create_game_screen()

    def connect_to_game_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 30, "Choose BATTLE!")
        screen.addstr(3, 1, "="*(self.width - 2))
        screen.addstr(4, 1, " ID")
        screen.addstr(4, 20, " NAME")
        screen.addstr(5, 1, "-"*(self.width - 2))
        screen.addstr(18, 1, "  0 - Back to main menu")
        screen.addstr(19, 1, "="*(self.width - 2))
        screen.addstr(21, 1, "  Enter a game id:")
        if self.client is not None:
            result, data = self.client.show_games()
            if result:
                if len(data) != 0:
                    for n, i in enumerate(xrange(6, 17)):
                        if n < len(data):
                            screen.addstr(i, 1,
                                          "  {0}".format(data[n]['id']))
                            screen.addstr(i, 20,
                                          "  {0}".format(data[n]['name']))
                        else:
                            break
                else:
                    screen.addstr(6, 1, "  No any games :(")
            else:
                screen.addstr(6, 1, "  Error: {0}".format(data))
        else:
            screen.addstr(6, 1, "  Server address is not specified, "
                                "specify the server address...")
        screen.refresh()

    def connect_to_game(self):
        key = ''
        while key != '0':
            key = screen.getstr(21, 20)
            if key == '0':
                return False
            else:
                result, data = self.client.connect_to_game(key)
                if result:
                    self.battlefield = data['battlefield']
                    self.ships = data['ships']
                    self.user = data['user']
                    self.game_id = data['id']
                    return True
                else:
                    screen.addstr(22, 1, "  Error: {0}".format(data))
                    screen.refresh()
                    time.sleep(self.err_msg_delay)
                    self.connect_to_game_screen()

    def prepare_ships_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 30, "Prepare your ARMY!")
        screen.addstr(3, 1, "="*(self.width - 2))
        screen.addstr(5, 1, "  A B C D E F G H I J")
        screen.addstr(6, 2, "0")
        screen.addstr(7, 2, "1")
        screen.addstr(8, 2, "2")
        screen.addstr(9, 2, "3")
        screen.addstr(10, 2, "4")
        screen.addstr(11, 2, "5")
        screen.addstr(12, 2, "6")
        screen.addstr(13, 2, "7")
        screen.addstr(14, 2, "8")
        screen.addstr(15, 2, "9")
        screen.addstr(17, 1, "  Coordinates examples: A1A2,B4D4,H1")
        screen.addstr(18, 1, "  \"exit\" - Exit to main menu")
        screen.addstr(19, 1, "="*(self.width - 2))
        for i, l in enumerate(self.battlefield):
            for j, n in enumerate(l):
                m = n if n < 4 else 0
                screen.addstr(6 + i, 3 + (j*2), '[', curses.color_pair(m))
                screen.addstr(6 + i, 4 + (j*2), ']', curses.color_pair(m))
        screen.addstr(21, 1, "  Enter coordinates:")
        screen.refresh()

    def prepare_ships(self):
        key = ''
        while key != 'exit':
            if self.ships == []:
                screen.addstr(22, 1, "  OK, your army is ready!")
                screen.refresh()
                time.sleep(self.err_msg_delay)
                return True
            key = screen.getstr(21, 22)
            if key == 'exit':
                return False
            result, data = self.client.set_ship(self.game_id, self.user, key)
            if result:
                self.battlefield = data['battlefield']
                self.ships = data['ships']
                self.state = data['state']
            else:
                screen.addstr(22, 1, "  Error: {0}".format(data))
                screen.refresh()
                time.sleep(self.err_msg_delay)
            self.prepare_ships_screen()

    def set_server_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 20, "Specify the server address and port")
        screen.addstr(3, 1, "="*(self.width - 2))
        screen.addstr(4, 1, "  Address: {0}".format(self.address))
        screen.addstr(5, 1, "  Port: {0}".format(self.port))
        screen.addstr(7, 1, "  1 - Set address")
        screen.addstr(8, 1, "  2 - Set port")
        screen.addstr(9, 1, "  3 - Reconnect")
        screen.addstr(18, 1, "  0 - Back to main menu")
        screen.addstr(19, 1, "="*(self.width - 2))
        screen.addstr(21, 1, "  Enter a selection:")
        screen.refresh()

    def set_server(self):
        key = ''
        while key != ord('0'):
            key = screen.getch(21, 22)
            if key == ord('1'):
                screen.addstr(21, 1, "  Enter PyttleShip server address:")
                self.address = screen.getstr(21, 36)
            elif key == ord('2'):
                screen.addstr(21, 1, "  Enter PyttleShip server port:")
                self.port = screen.getstr(21, 33)
            elif key == ord('3'):
                pass
            else:
                continue
            if self.address != '' and self.port != '':
                try:
                    self.client = Client(self.address, self.port)
                    screen.addstr(22, 1, "  OK, PyttleShip server is found")
                    screen.refresh()
                    time.sleep(self.err_msg_delay)
                except:
                    screen.addstr(22, 1, "  Error: {0}. Set other address."
                                  .format(sys.exc_info()[1]))
                    screen.refresh()
                    time.sleep(self.err_msg_delay)
            self.set_server_screen()

    @staticmethod
    def state_refresher(self, d, event):
        while True:
            result, data = self.client.get_state(self.game_id, self.user)
            if result:
                msg = ''
                if data['state'] == 1:
                    msg = 'Wait for the enemy connect...'
                elif data['state'] == 3:
                    msg = 'Wait for the enemy\'s army prepare...'
                elif data['state'] == 4:
                    if data['current']:
                        msg = 'Your turn.'
                    else:
                        msg = 'Wait for enemy turn...'
                screen.addstr(20, 1, " "*(self.width - 2))
                screen.addstr(20, 1, "  {0}".format(msg))
            else:
                screen.addstr(20, 1, "  Error: {0}".format(data))
            screen.addstr(21, 22, "")
            screen.refresh()
            d['state'] = data['state']
            d['current'] = data['current']
            d['enemy'] = data['enemy']
            d['battlefield'] = data['battlefield']
            event.set()
            time.sleep(self.refresh_delay)

    @staticmethod
    def input_waiter(self, v, event):
        while True:
            v.value = screen.getstr(21, 22)
            screen.addstr(21, 22, " "*(self.width - 24))
            screen.addstr(21, 22, " "*(self.width - 24))
            screen.refresh()
            event.set()

    def wait_for_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 30, "Wait please")
        screen.addstr(3, 1, "="*(self.width - 2))
        screen.addstr(18, 1, "  \"exit\" - Exit to main menu")
        screen.addstr(19, 1, "="*(self.width - 2))
        screen.addstr(21, 1, "  Enter selection:  ")
        screen.refresh()

    def wait_for(self, key, value):
        d = Manager().dict()
        d[key] = None
        v = Manager().Value('s', ' ')
        e = Event()

        p_state = Process(target=self.state_refresher, args=(self, d, e))
        p_input = Process(target=self.input_waiter, args=(self, v, e))
        p_state.start()
        p_input.start()

        while v.value != 'exit' and dict(d.items())[key] != value:
            e.wait()
            e.clear()

        self.state = d['state']
        self.current = d['current']
        self.enemy = d['enemy']
        self.battlefield = d['battlefield']

        p_state.terminate()
        p_input.terminate()
        curses.endwin()
        p_state.join()
        p_input.join()

        return True if dict(d.items())[key] == value else False

    def battle_screen(self, is_current=None):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 30, "Let's BATTLE!")
        screen.addstr(3, 1, "="*(self.width - 2))

        screen.addstr(5, 1, "  A B C D E F G H I J")
        screen.addstr(6, 2, "0")
        screen.addstr(7, 2, "1")
        screen.addstr(8, 2, "2")
        screen.addstr(9, 2, "3")
        screen.addstr(10, 2, "4")
        screen.addstr(11, 2, "5")
        screen.addstr(12, 2, "6")
        screen.addstr(13, 2, "7")
        screen.addstr(14, 2, "8")
        screen.addstr(15, 2, "9")

        screen.addstr(5, 36, "  A B C D E F G H I J")
        screen.addstr(6, 37, "0")
        screen.addstr(7, 37, "1")
        screen.addstr(8, 37, "2")
        screen.addstr(9, 37, "3")
        screen.addstr(10, 37, "4")
        screen.addstr(11, 37, "5")
        screen.addstr(12, 37, "6")
        screen.addstr(13, 37, "7")
        screen.addstr(14, 37, "8")
        screen.addstr(15, 37, "9")

        screen.addstr(17, 1, "  Coordinates examples: A1,B4,H1")
        screen.addstr(18, 1, "  \"exit\" - Exit to main menu")
        screen.addstr(19, 1, "="*(self.width - 2))

        if is_current is not None:
            if is_current:
                screen.addstr(20, 1, "  Your turn.")
            else:
                screen.addstr(20, 1, "  Wait for enemy turn...")

        for i, l in enumerate(self.battlefield):
            for j, n in enumerate(l):
                m = n if n < 4 else 0
                screen.addstr(6 + i, 3 + (j*2), '[', curses.color_pair(m))
                screen.addstr(6 + i, 4 + (j*2), ']', curses.color_pair(m))

        for i, l in enumerate(self.enemy):
            for j, n in enumerate(l):
                m = n if n < 4 else 0
                screen.addstr(6 + i, 38 + (j*2), '[', curses.color_pair(m))
                screen.addstr(6 + i, 39 + (j*2), ']', curses.color_pair(m))

        screen.addstr(21, 1, "  Enter coordinates:")
        screen.refresh()

    def battle(self):
        while True:
            if self.current or self.wait_for('current', True):
                self.battle_screen(is_current=self.current)
                if self.state == 4:
                    coord = screen.getstr(21, 22)
                    if coord == 'exit':
                        break
                    result, data = self.client.shot(self.game_id, self.user,
                                                    coord)
                    if result:
                        self.battlefield = data['battlefield']
                        self.enemy = data['enemy']
                        self.state = data['state']
                        self.current = data['current']
                    else:
                        screen.addstr(22, 1, "  Error: {0}".format(data))
                        screen.refresh()
                        time.sleep(self.err_msg_delay)
                    self.battle_screen(is_current=self.current)
                elif self.state == 5:
                    self.battle_screen()
                    if any(map(lambda l: 1 in l, self.battlefield)):
                        result = "Congratulations! You are winner!"
                        color = 1
                    else:
                        result = "You are loser :("
                        color = 2
                    msg = "{0}{1}{0}".format(
                        " "*((self.width - len(result))/2 - 1), result)
                    screen.addstr(21, 1, msg, curses.color_pair(color))
                    screen.getch()
                    break
            else:
                break


    def not_ready_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "It is not yet ready.")
        screen.refresh()
        screen.getch()

    def main_menu_screen(self):
        screen.erase()
        screen.border(0)
        screen.addstr(1, 1, "="*(self.width - 2))
        screen.addstr(2, 30, "-= PyttleShip =-")
        screen.addstr(3, 1, "="*(self.width - 2))
        screen.addstr(4, 1, "  1 - Create new game")
        screen.addstr(5, 1, "  2 - Connect to existing game")
        screen.addstr(6, 1, "  3 - Specify the server address")
        screen.addstr(18, 1, "  0 - Exit :(")
        screen.addstr(19, 1, "="*(self.width - 2))
        screen.addstr(21, 1, "  Enter a selection:")
        screen.refresh()

    def main_menu(self):
        key = ''
        while key != ord('0'):
            key = screen.getch(21, 22)
            screen.addch(21, 22, key)
            do_game = False

            if key == ord('1'):
                self.create_game_screen()
                do_game = self.create_game()

            elif key == ord('2'):
                self.connect_to_game_screen()
                do_game = self.connect_to_game()

            elif key == ord('3'):
                self.set_server_screen()
                self.set_server()

            if do_game:
                self.prepare_ships_screen()
                if self.prepare_ships():
                    self.wait_for_screen()
                    if self.wait_for('state', 4):
                        self.battle_screen(is_current=self.current)
                        self.battle()

            self.main_menu_screen()


#  MAIN LOOP
if __name__ == '__main__':
    try:
        screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, -1, curses.COLOR_GREEN)
        curses.init_pair(2, -1, curses.COLOR_RED)
        curses.init_pair(3, -1, curses.COLOR_YELLOW)
        game = Game()
        game.address = 'localhost'
        game.port = '8080'
        game.main_menu_screen()
        try:
            game.client = Client(game.address, game.port)
            screen.addstr(22, 1, "  OK, PyttleShip server is found")
            screen.refresh()
            time.sleep(game.err_msg_delay)
        except:
            screen.addstr(22, 1, "  Error: {0}. Set other address."
                          .format(sys.exc_info()[1]))
            screen.refresh()
            time.sleep(game.err_msg_delay)
        game.main_menu_screen()
        game.main_menu()
    finally:
        curses.endwin()

