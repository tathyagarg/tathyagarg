import string

MESSAGES = [
    "Invalid position! Enter a location (Eg. A1): ",
    "Position already taken! Enter a location (Eg. A1): "
]

def delta_distance(location1: tuple[int, int], location2: tuple[int, int]) -> int:
    return max(abs(location1[0] - location2[0]), abs(location1[1] - location2[1])) + 1

def delta_range(location1: tuple[int, int], location2: tuple[int, int]) -> list[tuple[int, int]]:
    items = []
    direction = location1[0] == location2[0]
    print(f'{location1}, {location2}')

    if direction:
        start, end = min(location1[1], location2[1]), max(location1[1], location2[1])
        for i in range(start, end+1):
            items.append((location1[0], i))
    else:
        start, end = min(location1[0], location2[0]), max(location1[0], location2[0])
        for i in range(start, end+1):
            items.append((i, location1[1]))
    return items

def convert_letters_to_tuple_location(inp: str) -> tuple[int, int]:
    inp = inp.upper()
    try:
        assert inp[0] in string.ascii_uppercase[:10] and 0 < int(inp[1:]) <= 10
    except (ValueError, IndexError) as vie:
        raise vie

    return string.ascii_uppercase.index(inp[0])+1, int(inp[1:])

def convert_tuple_location_to_letters(inp: tuple[int, int]) -> str:
    assert 0 < inp[0] <= 10 and 0 < inp[1] <= 10

    return string.ascii_uppercase[inp[0]-1] + str(inp[1])

class Ship:
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        self.start = start_pos
        self.end = end_pos

        self.length: int = delta_distance(start_pos, end_pos)
        self.direction = int(self.start[0] == self.end[0])
        self.hit_spots: list[bool] = [False] * self.length
        self.range = delta_range(location1=start_pos, location2=end_pos)
        
    @property
    def is_destroyed(self) -> bool:
        return all(self.hit_spots)
    
    def exists_on(self, location: tuple[int, int]):
        return location in self.range
    
    def hit_on(self, location: tuple[int, int]):
        if not self.exists_on(location):
            raise ValueError("Trying to hit ship on spot where it does not exist")
        self.hit_spots[delta_distance(location, self.start)-1] = True
        return self.is_destroyed

class Board:
    TRANSLATOR = [' ', 'C', 'B', 'R', 'S', 'D']
    NAMES = ["ERROR", 'Carrier', 'Battleship', 'Cruiser', 'Submarine', 'Destroyer']
    LENGTH_MAP = {'C': 5, 'B': 4, 'R': 3, 'S': 3, 'D': 2}
    def __init__(self, carrier: Ship, battleship: Ship, cruiser: Ship, submarine: Ship, destroyer: Ship):
        try:
            self.run_checks(carrier=carrier, battleship=battleship, cruiser=cruiser, submarine=submarine, destroyer=destroyer)
        except AssertionError as ae:
            raise ae
        
        self.ships = {
            'carrier': carrier,
            'battleship': battleship,
            'cruiser': cruiser,
            'submarine': submarine,
            'destroyer': destroyer
        }
        self.tries = [[0 for _ in range(10)] for _ in range(10)]
        self.board = self.populate_board()

    @property
    def tried_locations(self):
        locations = []
        for y, row in enumerate(self.tries, 1):
            for x, tried in enumerate(row, 1):
                if tried: locations.append((x, y))                

        return locations

    def hits(self, location: tuple[int, int]) -> bool | Ship:
        for ship in self.ships.values():
            if ship.exists_on(location):
                return ship
        return False
    
    def populate_board(self) -> list[list[str]]:
        result = [[0 for _ in range(10)] for _ in range(10)]
        for name, ship in self.ships.items():
            for (x, y) in ship.range:
                result[y-1][x-1] = Board.TRANSLATOR.index(name[0].upper() if name != 'cruiser' else 'R')
        
        return result
    
    def shot(self, location: tuple[int, int]):
        x, y = location
        x, y = x - 1, y - 1
        if self.tries[y][x]:
            return -1
        if not (ship := self.hits(location)):
            self.tries[y][x] = 1
            return False
        self.tries[y][x] = 2
        is_destroyed = ship.hit_on(location)
        return int(is_destroyed) + 1

    def run_checks(self, carrier: Ship, battleship: Ship, cruiser: Ship, submarine: Ship, destroyer: Ship) -> bool:
        assert carrier.length == 5
        assert battleship.length == 4
        assert cruiser.length == 3
        assert submarine.length == 3
        assert destroyer.length == 2

    def display(self):
        print('   ' + '|'.join(string.ascii_uppercase[:10]))
        for i, row in enumerate(self.board, 1):
            print(f'{i:<2}', '|'.join(list(map(lambda item: Board.TRANSLATOR[item], row))))

    def display_shots(self):
        print('   ' + ' |'.join(string.ascii_uppercase[:10]))
        for i, row in enumerate(self.tries, 1):
            print(f"{i:<2}", "|".join(list(map(
                lambda item: ['🟦', '⬜', '🟥'][item],
                row
            ))))

class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.board: Board = self.make_board()
        self.opponent: Player = None

    @classmethod
    def link(cls, obj1, obj2):
        obj1.opponent = obj2
        obj2.opponent = obj1
    
    @property
    def is_alive(self) -> bool:
        return any([not ship.is_destroyed for ship in self.board.ships.values()])

    def accept_location(self, taken: list[tuple[int, int]] = None):
        taken = taken or []
        loop = False

        location = input("Enter a location (Eg. A1): ")
        try:
            converted = convert_letters_to_tuple_location(location)
            loop = converted in taken
            if loop: msg = 1
        except (AssertionError, ValueError, IndexError):
            loop, msg = True, 0
        while loop:
            loop = False
            location = input(MESSAGES[msg])
            try:
                converted = convert_letters_to_tuple_location(location)
                loop = converted in taken
                if loop: msg = 1
            except (AssertionError, ValueError, IndexError):
                loop, msg = True, 0

        return converted

    def turn(self):
        self.opponent.board.display_shots()
        location = self.accept_location(self.opponent.board.tried_locations)
        status = self.opponent.board.shot(location)
        if status is False:
            print('Miss.')
        elif status == 1:
            print('Hit!')
        elif status == 2:
            print('Destroyed a ship!')

    def make_board(self):
        def print_interim_board(board: list[list[int]]):
            print('   ' + '|'.join(string.ascii_uppercase[:10]))
            for i, row in enumerate(board, 1):
                print(f'{i:<2}', '|'.join(list(map(lambda item: Board.TRANSLATOR[item], row))))

        def get_ship_choice(not_placed: list[int]) -> str:
            choice = input("Choice: ").upper()
            choices = [Board.TRANSLATOR[i] for i in not_placed]
            while choice not in choices:
                choice = input("Invalid! Choice: ").upper()
            return choice
        
        def accept_location_selective(acceptable: list[tuple[int, int]]) -> tuple[int, int]:
            print(f'Your choices are: ')
            print('\n'.join([convert_tuple_location_to_letters(loc) for loc in acceptable]))
            location = input("Enter a location (Eg. A1): ")
            try:
                converted = convert_letters_to_tuple_location(location)
            except (AssertionError, ValueError, IndexError):
                converted = (-1, -1)

            while converted not in acceptable:
                location = input("Invalid! Enter a location (Eg. A1): ")
                try:
                    converted = convert_letters_to_tuple_location(location)
                except (AssertionError, ValueError, IndexError):
                    converted = (-1, -1)

            return converted

        def generate_valids_around(taken: list[tuple[int, int]], starting_location: tuple[int, int], ship_type: str) -> list[tuple[int, int]]:
            length = Board.LENGTH_MAP[ship_type] - 1
            locations = []
            if starting_location[0] - length > 0:
                if (loc_to_add := (starting_location[0] - length, starting_location[1])) not in taken:
                    locations.append(loc_to_add)

            if starting_location[0] + length <= 10:
                if (loc_to_add := (starting_location[0] + length, starting_location[1])) not in taken:
                    locations.append(loc_to_add)

            if starting_location[1] - length > 0:
                if (loc_to_add := (starting_location[0], starting_location[1] - length)) not in taken:
                    locations.append(loc_to_add)

            if starting_location[1] + length <= 10 :
                if (loc_to_add := (starting_location[0], starting_location[1] + length)) not in taken:
                    locations.append(loc_to_add)

            return locations

        def get_ship(taken: list[tuple[int, int]], ship_type: str) -> Ship:
            starting_location = self.accept_location(taken)
            ending_location = accept_location_selective(generate_valids_around(taken=taken, starting_location=starting_location, ship_type=ship_type))

            ship = Ship(start_pos=starting_location, end_pos=ending_location)

            return ship, delta_range(starting_location, ending_location)

        taken_locations = []

        print(f"Make a board!")
        not_placed = [1, 2, 3, 4, 5]
        board = [[0 for _ in range(10)] for _ in range(10)]
        placed = {
            'carrier': None,
            'destroyer': None,
            'cruiser': None,
            'submarine': None,
            'destroyer': None
        }

        while not_placed:
            print_interim_board(board)
            for idx in not_placed:
                print(f'({Board.TRANSLATOR[idx]}) {Board.NAMES[idx]}')

            choice = get_ship_choice(not_placed=not_placed)
            int_choice = Board.TRANSLATOR.index(choice)

            ship, new_taken_locations = get_ship(taken=taken_locations, ship_type=choice)
            taken_locations.extend(new_taken_locations)
            placed[Board.NAMES[int_choice].lower()] = ship
            not_placed.remove(int_choice)
            for (x, y) in new_taken_locations:
                board[y-1][x-1] = Board.TRANSLATOR.index(choice)

        return Board(**placed)

def main():
    player = Player(input('Enter player 1 name: '))
    player2 = Player(input("Enter player 2 name: "))

    Player.link(player, player2)

    while player.is_alive and player2.is_alive:
        print(f'{player.name}\'s turn')
        player.turn()
        if not player2.is_alive:
            break
        print("="*100)
        print(f'{player2.name}\'s turn')
        player2.turn()
        print("="*100)

    print([player, player2][player.is_alive].name, 'lost!')

if __name__ == '__main__':
    main()
