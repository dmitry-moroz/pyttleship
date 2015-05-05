import string
import sqlite3
import random
import json


def common(err_msg):
    def new_func(func):
        def wraped(*args, **kwargs):
            try:
                return True, func(*args, **kwargs)
            except:
                return False, err_msg
        return wraped
    return new_func


class Battle(object):

    DB_NAME = 'games.db'
    TABLE = 'games'
    NUM = 0

    def __init__(self, game_id, user_id):
        self.connection = sqlite3.connect(self.DB_NAME)
        self.cursor = self.connection.cursor()
        self.cursor.execute('SELECT * FROM {0} WHERE id={1}'
                            .format(self.TABLE, game_id))
        row = self.cursor.fetchone()
        if row:
            if user_id == row[3]:
                self.user_n = 0
            elif user_id == row[4]:
                self.user_n = 1
            else:
                self.connection.close()
                raise ValueError('Nonexistent user ID')
            self.id = game_id
            self.name = row[1]
            self.state = int(row[2])
            self.user = user_id
            self.enemy_name = row[4 - self.user_n]
            self.battlefield = json.loads(row[5 + self.user_n])
            self.enemy = json.loads(row[6 - self.user_n])
            self.ships = json.loads(row[7 + self.user_n])
            self.current = row[9]
        else:
            self.connection.close()
            raise ValueError('Nonexistent game ID')

    def __del__(self):
        self.connection.close()

    @common('Unable to commit changes to database')
    def save(self):
        battlefield_j = json.dumps(self.battlefield)
        enemy_j = json.dumps(self.enemy)
        ships_j = json.dumps(self.ships)
        self.cursor.execute('UPDATE {0} SET '
                            'state={1},'
                            'battlefield{2}="{3}",'
                            'battlefield{4}="{5}",'
                            'ships{2}="{6}",'
                            'current="{7}" '
                            'WHERE id={8}'
                            .format(self.TABLE,
                                    self.state,
                                    1 + self.user_n, battlefield_j,
                                    2 - self.user_n, enemy_j,
                                    ships_j,
                                    self.current,
                                    self.id))
        self.connection.commit()

        for i, l in enumerate(self.enemy):
            for j, n in enumerate(l):
                if n not in [0, 2, 3]:
                    self.enemy[i][j] = 0

        current = (self.current == self.user or self.state == 5)

        return {'id': self.id,
                'user': self.user,
                'state': self.state,
                'ships': self.ships,
                'battlefield': self.battlefield,
                'enemy': self.enemy,
                'current': current}

    @common('Unable to get state')
    def get_state(self):
        for i, l in enumerate(self.enemy):
            for j, n in enumerate(l):
                if n not in [0, 2, 3]:
                    self.enemy[i][j] = 0

        current = (self.current == self.user or self.state == 5)

        return {'id': self.id,
                'user': self.user,
                'state': self.state,
                'ships': self.ships,
                'battlefield': self.battlefield,
                'enemy': self.enemy,
                'current': current}

    @staticmethod
    @common('Unable to create new game')
    def new_game(game_name):
        connection = sqlite3.connect(Battle.DB_NAME)
        cursor = connection.cursor()
        Battle.NUM += 1
        user1 = ''.join(random.choice(string.hexdigits)
                        for i in xrange(20))
        user2 = ''.join(random.choice(string.hexdigits)
                        for i in xrange(20))
        current = random.choice([user1, user2])
        battlefield = []
        for i in xrange(0, 10):
            battlefield.append([0 for j in xrange(10)])
        battlefield_j = json.dumps(battlefield)
        ships = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        #ships = [2, 3]
        ships_j = json.dumps(ships)
        cursor.execute(
            'INSERT INTO {7} '
            '(id, name, state, user1, user2, battlefield1, battlefield2, '
            'ships1, ships2, current) '
            'VALUES({0}, "{1}", 0, "{2}", "{3}", "{4}", "{4}", '
            '"{5}", "{5}", "{6}")'
            .format(Battle.NUM, game_name, user1, user2, battlefield_j,
                    ships_j, current, Battle.TABLE)
        )
        connection.commit()
        connection.close()
        current = current == user1
        return {'id': Battle.NUM,
                'name': game_name,
                'state': 0,
                'user': user1,
                'ships': ships,
                'battlefield': battlefield,
                'enemy': battlefield,
                'current': current}

    @staticmethod
    @common('Unable to connect to the game')
    def connect_to_game(game_id):
        connection = sqlite3.connect(Battle.DB_NAME)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM {0} WHERE id={1} AND (state=0 OR state=1)'
                       .format(Battle.TABLE, game_id))
        row = cursor.fetchone()
        if row:
            game_id = game_id
            game_name = row[1]
            state = int(row[2]) + 2
            user = row[4]
            battlefield = json.loads(row[6])
            ships = json.loads(row[8])
            current = row[9]
            cursor.execute('UPDATE {0} SET state={1} '
                           'WHERE id={2}'.format(Battle.TABLE, state, game_id))
            connection.commit()
            connection.close()
            current = current == user
            return {'id': game_id,
                    'name': game_name,
                    'state': state,
                    'user': user,
                    'ships': ships,
                    'battlefield': battlefield,
                    'enemy': battlefield,
                    'current': current}
        else:
            return {'error': 'No such game'}

    @staticmethod
    @common('Unable to get list of games')
    def show_games():
        connection = sqlite3.connect(Battle.DB_NAME)
        cursor = connection.cursor()
        cursor.execute('SELECT id, name FROM {0} WHERE state=0 OR state=1'
                       .format(Battle.TABLE))
        rows = cursor.fetchall()
        connection.close()
        result = []
        if rows:
            for game_id, name in rows:
                result.append({'id': int(game_id), 'name': name})
        return result

    @staticmethod
    @common('Unable to prepare database table')
    def prepare_table():
        connection = sqlite3.connect(Battle.DB_NAME)
        cursor = connection.cursor()
        cursor.execute('SELECT tbl_name FROM sqlite_master WHERE type="table"')
        if Battle.TABLE in str(cursor.fetchall()):
            cursor.execute('DROP TABLE {0}'.format(Battle.TABLE))
            connection.commit()
        cursor.execute('CREATE TABLE {0} '
                       '(id INTEGER PRIMARY KEY, '
                       'name VARCHAR(32), '
                       'state BIT, '
                       'user1 VARCHAR(32), '
                       'user2 VARCHAR(32), '
                       'battlefield1 VARCHAR(1024), '
                       'battlefield2 VARCHAR(1024), '
                       'ships1 VARCHAR(32), '
                       'ships2 VARCHAR(32), '
                       'current VARCHAR(32))'.format(Battle.TABLE))
        connection.commit()
        connection.close()
