import string

EMPTY = 0
CROSS = 1
CIRCLE = 2

class Board:
    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns

        self.contents: list[list[int]] = [[EMPTY for _ in range(columns)] for _ in range(rows)]

    def display(self) -> None:
        for row in self.contents:
            print('|'.join(map(
                lambda i: [' ', 'X', 'O'][i],
                row
            )))

        print(('-+'*(self.columns))[:-1])
        print('|'.join(string.ascii_uppercase[:self.columns]))

    def play_on(self, column: int, player: int) -> None:
        column_contents: list[int] = [self.contents[i][column] for i in range(self.rows)][::-1]
        lowest: int = self.rows - column_contents.index(EMPTY) - 1

        self.contents[lowest][column] = player

    def check_win(self) -> int:
        for row in range(self.rows):
            for i in range(self.columns - 3):
                contents = set(self.contents[row][i:i+4])
                if len(contents) == 1 and contents != {EMPTY}:
                    return list(contents)[0]

        for column in range(self.columns):
            for i in range(self.rows - 3):
                contents = {self.contents[j][column] for j in range(i, i+4)}
                if len(contents) == 1 and contents != {EMPTY}:
                    return list(contents)[0]

        for column in range(self.columns - 3):
            for row in range(self.rows - 3):
                contents = {self.contents[row+i][column+i] for i in range(4)}
                if len(contents) == 1 and contents != {EMPTY}:
                    return list(contents)[0]

        for column in range(self.columns - 1, 2, -1):
            for row in range(self.rows - 3):
                contents = {self.contents[row+i][column-i] for i in range(4)}
                if len(contents) == 1 and contents != {EMPTY}:
                    return list(contents)[0]

        return EMPTY

    def game(self) -> None:
        while not self.check_win():
            self.display()

            cross_move: int = string.ascii_uppercase.index(input(">>> "))
            self.play_on(cross_move, CROSS)
            self.display()

            if self.check_win():
                break

            circle_move: int = string.ascii_uppercase.index(input(">>> "))
            self.play_on(circle_move, CIRCLE)

board = Board(5, 10).game()
