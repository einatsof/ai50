import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # When the number of cells equal count all cells are mines
        if len(self.cells) == self.count:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # When count is 0 all cells are safe
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # Remove mine cell from sentence and reduce count by 1
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # Remove safe cell from sentence
            self.cells.remove(cell)

    def is_equal_sentences(self, s):
        """
        Checks if 2 sentences are equal
        """
        if self.cells.difference(s.cells) == set() and s.cells.difference(self.cells) == set():
            return True
        return False


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1. Mark cell as a move that has been made
        self.moves_made.add(cell)
        # 2. Mark cell as safe and update sentences containing the cell
        self.mark_safe(cell)
        # Update knowledge
        self.basic_knowledge_check()

        # 3. Add a new sentence to the AI's knowledge base with info about surrounding cells
        surrounding_cells = self.find_surrounding_cells(cell)
        undetermined_surrounding_cells = surrounding_cells.copy()
        for current_cell in surrounding_cells:
            if current_cell in self.safes:
                undetermined_surrounding_cells.remove(current_cell)
            elif current_cell in self.mines:
                undetermined_surrounding_cells.remove(current_cell)
                count -= 1
        # If there are undetermined surrounding cells - create a new sentence
        if len(undetermined_surrounding_cells) > 0:
            new_sentence = Sentence(undetermined_surrounding_cells, count)
            # Add new sentence to knowledge only if it's not already there
            if not self.is_sentence_in_knowledge(new_sentence, self.knowledge):
                self.knowledge.append(new_sentence)
                # 4. Mark cells as safe or mines if possible and update knowledge
                self.basic_knowledge_check()

        # 5. Make new inferences
        self.find_new_inferences()
        self.basic_knowledge_check()
        for s in self.knowledge:
            print(s)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe_move in self.safes:
            if safe_move not in self.moves_made:
                return safe_move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_possible_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    all_possible_moves.add(cell)
        if len(all_possible_moves) > 0:
            return random.sample(all_possible_moves, 1)[0]
        else:
            return None

    def find_surrounding_cells(self, cell):
        """
        Return a set of all surrounding cells of input cell
        """
        cells_around = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Add to cells set if cell in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    cells_around.add((i, j))
        return cells_around

    def basic_knowledge_check(self):
        """
        Checks if any of the sentences indicate obvious mines or safes and if there are doubles
        """
        self.remove_empty()
        self.remove_duplicates()
        for sentence in self.knowledge:
            # Check for all-mine sentences, mark them and remove from knowledge
            known_mines = sentence.known_mines()
            if len(known_mines) > 0:
                self.knowledge.remove(sentence)
                for cell in known_mines:
                    self.mark_mine(cell)
                self.basic_knowledge_check()
                return
            # Check for all-safe sentences, mark them and remove from knowledge
            known_safes = sentence.known_safes()
            if len(known_safes) > 0:
                self.knowledge.remove(sentence)
                for cell in known_safes:
                    self.mark_safe(cell)
                self.basic_knowledge_check()
                return

    def find_new_inferences(self):
        """
        Iterate over all sentences and find if any sentence is a subset of another to make new inferences
        """
        for sentence in self.knowledge:
            for other_sentence in self.knowledge:
                # Don't check a sentence with itself
                if sentence == other_sentence:
                    continue
                if sentence.cells.issubset(other_sentence.cells):
                    new_sentence = Sentence(other_sentence.cells.difference(sentence.cells), other_sentence.count - sentence.count)
                    # If this new inference was already made before or empty - move on
                    if not self.is_sentence_in_knowledge(new_sentence, self.knowledge) and len(new_sentence.cells) > 0:
                        self.knowledge.append(new_sentence)
                        self.basic_knowledge_check()
                        # When a new sentence is added to the knowledge restart the function
                        self.find_new_inferences()
                        return

    def is_sentence_in_knowledge(self, s, list):
        """
        Checks if a sentence is in a list
        """
        for sentence in list:
            if s.is_equal_sentences(sentence):
                return True
        return False

    def remove_duplicates(self):
        """
        Remove duplicated sentences
        """
        unique_knowledge = []
        for sentence in self.knowledge:
            if not self.is_sentence_in_knowledge(sentence, unique_knowledge):
                unique_knowledge.append(sentence)
        self.knowledge = unique_knowledge

    def remove_empty(self):
        """
        Remove empty sentences
        """
        valid_knowledge = []
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                continue
            valid_knowledge.append(sentence)
        self.knowledge = valid_knowledge
