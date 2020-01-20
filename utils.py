import random, string, json, redis

rock, paper, scissors = 'rock', 'paper', 'scissors'

class Redis:
    fake = False

    def __init__(self, url):
        if url == None or url == "":
            print("faking redis")
            self.fake = True
            self.rooms = {}
            return

        self._redis = redis.from_url(url)
        self.setRooms({})

    def getRooms(self):
        if self.fake:
            return self.rooms
        return json.loads(self._redis.get('rooms'))

    def setRooms(self, rooms):
        if self.fake:
            self.rooms = rooms
            return
            
        self._redis.set('rooms', json.dumps(rooms))


def generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def RockPaperScissors(player1, player2): # determine winner, takes dictionary with id and move
    if player1['move'] == player2['move']:
        return None
    elif player1['move'] == rock:
        if player2['move'] == paper:
            return player2['id']
        else:
            return player1['id']
    elif player1['move'] == paper:
        if player2['move'] == scissors:
            return player2['id']
        else:
            return player1['id']
    elif player1['move'] == scissors:
        if player2['move'] == rock:
            return player2['id']            
        else:
            return player1['id']
