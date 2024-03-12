class Board:
    def __init__(self) -> None:
        self.game = [[-1 for _ in range(3)] for _ in range(3)]
        self.start_game()

    def verify_move(self, move):
        x, y = divmod(move-1, 3)
        return self.game[x][y] == -1

    def make_move(self, character, move):
        x, y = divmod(move-1, 3)
        self.game[x][y] = character

    def check_winner(self):
        for row in self.game:
            checks = [row[0], row[1], row[2]]
            if len(set(checks)) == 1 and checks[0] != -1:
                return checks[0]
            
        for i in range(3):
            checks = [self.game[i][j] for j in range(3)]
            if len(set(checks)) == 1 and checks[0] != -1:
                return checks[i]
        
        checks = [self.game[i][i] for i in range(3)]
        if len(set(checks)) == 1 and checks[0] != -1:
            return checks[0]
        
        checks = [self.game[2-i][i] for i in range(3)]
        if len(set(checks)) == 1 and checks[0] != -1:
            return checks[0]
        
        return False

    def check_draw(self):
        if not all([i != -1 for row in self.game for i in row]):
            return False  # Board is not full
        
        return self.check_winner()  # If the board is full, there's either a winner, or there's not.

    def display_board(self):
        for i, row in enumerate(self.game):
            print(' | '.join([character if character != -1 else ' ' for character in row]))
            if i != 2:
                print('='*9)

    def start_game(self):
        while not self.check_winner() and not self.check_draw():
            for character in ['O', 'X']:
                print(f"{character}! It's your chance!")
                self.display_board()

                move = int(input("Where to make the move? "))
                while not self.verify_move(move):
                    print('Invalid!')
                    move = int(input("Where to make the move? "))

                self.make_move(character, move)

                if self.check_winner() or self.check_draw():
                    break

        if (winner := self.check_winner()):
            print(f"{winner} won!")
            return
        
        if self.check_draw():
            print('Draw!')
            return

Board()

