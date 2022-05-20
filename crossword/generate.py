import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            words = self.domains[var].copy()
            for word in words:
                if len(word) != var.length:
                    self.domains[var].remove(word)
        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        # If no overlap - x and y are consistent
        if overlap is None:
            return False
        revised = False
        words = self.domains[x].copy()
        for x_word in words:
            consistent_y_value = False
            # Check word in x against all words in y
            for y_word in self.domains[y]:
                if x_word[overlap[0]] == y_word[overlap[1]]:
                    consistent_y_value = True
            if not consistent_y_value:
                self.domains[x].remove(x_word)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            # Add all overlaps to the queue
            queue = [k for k, v in self.crossword.overlaps.items() if v is not None]
        else:
            queue = arcs.copy()
        while len(queue) > 0:
            arc = queue.pop()
            if self.revise(arc[0], arc[1]):
                # If variable arc[0] was revised check if its domain is not empty
                if len(self.domains[arc[0]]) == 0:
                    return False
                # Add all variable arc[0]'s neighbors to the queue if they are not already there
                for neighbor in self.crossword.neighbors(arc[0]):
                    if (arc[0], neighbor) not in queue:
                        queue.append((arc[0], neighbor))
                    if (neighbor, arc[0]) not in queue:
                        queue.append((neighbor, arc[0]))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        all_values = []
        for var, word in assignment.items():
            all_values.append(word)
            # Word length check
            if var.length != len(word):
                return False
            # Conflicting characters check
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if word[overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
        # Distinct values check
        if len(set(all_values)) != len(all_values):
            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Make a list of all neighboring variables that were not already assigned a value
        neighbors = [v for v in self.crossword.neighbors(var) if v not in assignment]
        words_ruled_out = dict.fromkeys(self.domains[var], 0)
        for word in self.domains[var]:
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                for possible_choice in self.domains[neighbor]:
                    # If words can't fit together add to the ruled out counter
                    if word[overlap[0]] != possible_choice[overlap[1]]:
                        words_ruled_out[word] += 1
        return sorted(self.domains[var], key=lambda x: words_ruled_out[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_dict = {}
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_dict[var] = len(self.domains[var])
        # Find the variable/s with the minimum number of remaining values
        lowest_value = min(unassigned_dict.values())
        lowest_list = [k for k, v in unassigned_dict.items() if v == lowest_value]
        # If more than 1 variable has the minimum value number - choose one with larger degree
        if len(lowest_list) > 1:
            lowest_list.sort(key=lambda x: len(self.crossword.neighbors(x)), reverse=True)
        return lowest_list[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check if crossword is complete
        if self.assignment_complete(assignment):
            return assignment
        # Choose a var
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = word
            # If value is consistent with assignment keep it
            if self.consistent(new_assignment):
                # Inference
                prev_domains = self.domains.copy()
                self.ac3({(x, var) for x in self.crossword.neighbors(var)})
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
                self.domains = prev_domains
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
