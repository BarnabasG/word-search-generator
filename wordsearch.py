import numpy as np
import random
from itertools import permutations
import requests
import logging
import time


class wordsearch():

    def generate(self, maxx, maxy, word_list=None, topic=None, word_count=None, debug=False):

        if word_list:
            if word_count:
                logging.warning("Word list specified - word count ignored")
            word_dict = self.validate_directions(word_list, maxx, maxy)
        elif topic:
            if not word_count:
                logging.warning("Word count must be specified for topic generated puzzle")
                return ("Impossible configuration", [])
            generated_words = self.get_related_words(topic, word_count, max(maxx, maxy))
            print(generated_words)
            word_dict = self.validate_directions(generated_words, maxx, maxy)

        valid = self.validate(word_dict, maxx, maxy)
        if not valid:
            return ("Impossible configuration", list(word_dict.keys()))

        grid = np.chararray((maxy, maxx))
        grid[:] = b''

        grid = self.populate(word_dict, grid, maxx, maxy, debug)
        if grid is None:
            return ("Impossible configuration", list(word_dict.keys()))

        return (grid,list(word_dict.keys()))

    def print_array_grid(self, grid):

        g = grid[0]
        words = grid[1]

        print("\u2554" + "\u2550\u2550\u2550\u2566"*(len(g[0])-1) + "\u2550\u2550\u2550\u2557")
        for row in range(len(g)):
            print("\u2551", end="")
            print(' '+' \u2551 '.join([self.get_string(x) if isinstance(x, bytes) else ' ' for x in g[row]])+' ', end="\u2551\n")
            if row < len(g)-1: print("\u2560" + f"\u2550\u2550\u2550\u256C"*(len(g[0])-1) + "\u2550\u2550\u2550\u2563", end="\n")

        print("\u255A" + f"\u2550\u2550\u2550\u2569"*(len(g[0])-1) + "\u2550\u2550\u2550\u255D")
        print()

        print("Words:")
        print(' '.join([w.upper() for w in words]))
        print()

    def print_array_clear(self, grid, debug_print=False):

        g = grid[0]
        words = grid[1]

        for row in range(len(g)):
            print(' '.join([self.get_string(x) if isinstance(x, bytes) else ' ' for x in g[row]])+' ', end="\n")

        print()

        if not debug_print:
            print("Words:")
            print(' '.join([w.upper() for w in words]))
            print()


    def valid_grid(self, grid):

        try:
            if not type(grid) is tuple:
                raise TypeError(f"Invalid Grid tuple - type {type(grid)}")
            if not (type(grid[0]) is np.chararray or type(grid[0]) is str):
                raise TypeError(f"Invalid Grid - type {type(grid[0])}")
            if not type(grid[1]) is list:
                raise TypeError(f"Invalid Word List - type {type(grid[1])}")
            if grid[0] == "Impossible configuration":
                print("Impossible configuration")
                raise TypeError("Invalid Grid")
        except Exception as e:
            logging.warning(f"Error: {e}")
            return False
        return True

        
    def populate(self, word_dict, grid, maxx, maxy, debug=False):

        self.possible_starts = {}
        possible_orders = permutations(word_dict.keys())
        if debug==True: s = time.time()

        while True:
            for order in possible_orders:
                valid = True
                working_grid = grid.copy()
                for word in order:
                    dirs = word_dict[word]
                    possibles = self.get_possible_starts(word, dirs, working_grid, maxx, maxy)
                    valid, working_grid = self.place_word(working_grid, word, possibles)
                    if not valid: break
                if valid: break
            if valid: break
        if not valid: return None

        if debug==True: print(f"time to generate = {time.time() - s}")

        grid = working_grid.copy()

        if debug==True: self.print_array_clear((grid, None), debug_print=True)

        grid = self.populate_other_letters(grid)

        return grid


    def get_possible_starts(self, word, dirs, grid, maxx, maxy):

        flat_grid = b''.join([(bytes('_', encoding="utf-8") if isinstance(x, str) else x)  for x in grid.flatten()]).decode("utf-8")

        p = self.possible_starts.get(flat_grid)
        if p: return p

        possible = {}
        for index, cell in np.ndenumerate(grid):
            possible[index] = []
            if cell not in (b'', word[0]):
                pass
            else:
                # f = forward (left to right/ top to bottom), b = backwards
                # horizontal
                if 'h' in dirs:
                    if index[1]+len(word) <= maxx:
                        possible[index].append(('hf'))
                    if index[1]-len(word)+1 >= 0:
                        possible[index].append(('hb'))
                # vertical
                if 'v' in dirs:
                    if index[0]+len(word) <= maxy:
                        possible[index].append(('vf'))
                    if index[0]-len(word)+1 >= 0:
                        possible[index].append(('vb'))
                # diagonal 1 (NW->SE)
                if 'd1' in dirs:
                    if index[1]+len(word) <= maxx and index[0]+len(word) <= maxy:
                        possible[index].append(('d1f'))
                    if index[1]-len(word)+1 >= 0 and index[0]-len(word)+1 >= 0:
                        possible[index].append(('d1b'))
                # diagonal 2 (SW->NE)
                if 'd2' in dirs:
                    if index[1]+len(word) <= maxx and index[0]-len(word)+1 >= 0:
                        possible[index].append(('d2f'))
                    if index[1]-len(word)+1 >= 0 and index[0]+len(word) <= maxy:
                        possible[index].append(('d2b'))

        self.possible_starts[flat_grid] = possible
        return possible

    def place_word(self, grid, word, placements):

        count = sum([len(x) for x in placements.values()])

        if count == 0:
            return False, grid

        attempt_order = random.sample(list(range(1,count+1)), count)
        attempts = 0

        found = False
        while not found:
            invalid = False
            placement_index = attempt_order[attempts]
            working_grid = grid.copy()
            for index, _ in np.ndenumerate(grid):
                inner_count = 0
                #for _ in range(int(value)):
                for _ in range(len(placements[index])):
                    placement_index -= 1
                    if placement_index == 0:
                        orientation = placements[index][inner_count]
                        valid, working_grid = self.insert_word(working_grid, word, index, orientation)
                        if valid:
                            found = True
                        else:
                            invalid = True
                            attempts += 1
                        break
                    if found or invalid: break
                    inner_count += 1
                if found or invalid: break
            if attempts == count and not found:
                return False, grid

        grid = working_grid.copy()

        return True, grid


    def insert_word(self, grid, word, index, orientation):

        orientation_mappings = {
            "hf": (1,0),
            "hb": (-1,0),
            "vf": (0,1),
            "vb": (0,-1),
            "d1f": (1,1),
            "d1b": (-1,-1),
            "d2f": (1,-1),
            "d2b": (-1,1)
        }

        step = orientation_mappings[orientation]

        for c in word:
            if self.get_string(grid[index]) not in ('', c.upper()):
                return False, grid

            grid[index] = c.upper()
            index = (index[0]+step[1], index[1]+step[0])

        return True, grid

    def validate(self, word_dict, maxx, maxy):

        if not all((word_dict.values())):
            return False
        elif not self.required_letters(word_dict, maxx, maxy):
            return False

        return True

    def get_string(self, input):

        if isinstance(input, bytes):
            return input.decode("utf-8")
        else:
            return str(input)


    def required_letters(self, word_dict, maxx, maxy):

        slots = maxx * maxy
        count = sum(len(x) for x in word_dict.keys())

        return count < slots


    def validate_directions(self, word_list, maxx, maxy):

        word_dict = {}
        for word in word_list:
            #d1 = NW->SE, d2 = SW->NE
            valid = ['d1', 'd2', 'v', 'h']
            if len(word) > maxx:
                valid.remove('h')
                valid.remove('d1')
                valid.remove('d2')
            if len(word) > maxy:
                if 'v' in valid: valid.remove('v')
                if 'd1' in valid: valid.remove('d1')
                if 'd2' in valid: valid.remove('d2')
            word_dict[word] = valid

        return word_dict

    def populate_other_letters(self, grid):

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for index, cell in np.ndenumerate(grid):
            if cell == b'':
                grid[index] = random.choice(letters)

        return grid

    def get_related_words(self, topic, word_count, max_len):

        parameters = {"rel_trg":topic, "topics":topic}
        response = requests.get(f"https://api.datamuse.com/words", parameters)

        l = self.filter_generated_words([topic] + list(x.get("word") for x in response.json()), max_len)

        if self.validate_generated_words(l, word_count):
            return l[:word_count]
    
    def validate_generated_words(self, word_list, required_count):

        if not word_list:
            return False
        if not type(word_list) is list:
            return False
        if len(word_list) < required_count:
            return False
        return True
    
    def filter_generated_words(self, word_list, max_len):

        exclude = {'a', 'an', 'the', 'of', 'their', 'they', 'and', 'or', 'if', 'because',
                   'that', 'so', 'than', 'no', 'this', 'some', 'his', 'hers', 'him', 'her', 'my', 'your',
                   'its', 'our', 'to', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'but', 'i', 'it',
                   'you', 'we', 'she', 'he', 'which', 'who', 'what', 'where', 'when', 'how', 'be', 'have',
                   'would', 'want', 'do', 'can', 'was', 'as', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                   'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'co',
                   'is', 'let', 'not', 'me', 'are', 'si', 'le', 'du', 'are', 'per', 'has', 'into', 'la', 'de',
                   'los', 'san', 'luis', 'de', 'fin', 'sic', 'had', 'la', 'cee', 'ii', 'bo', 'mya', 'xi', 'sac',
                   'ho', 'chi', 'ss'}
        
        valid = []
        print(word_list)
        for word in word_list:
            #print(word, word_list[:i])
            if word in exclude:
                print("Invalid (excluded):", word)
                continue
            elif len(word) > max_len:
                print("Invalid (too long):", word, len(word), max_len)
                continue
            elif any(x in word for x in valid):
                print("Invalid (dupe):", word, valid)
                continue
            valid.append(word)
        
        print(valid)
        return valid


def run():
    easter_words = ["easter", "bunny", "egg", "hunt", "chocolate", "spring", "basket", "bonnet", "chick",
                    "sunday", "daffodil", "duckling", "holiday", "lent"]
    maxx, maxy = 10, 10
    ws = wordsearch()

    #grid = ws.generate(maxx, maxy, word_list=easter_words, debug=True)
    grid = ws.generate(maxx, maxy, topic='christmas', word_count=12, debug=True)
    if ws.valid_grid(grid):
        ws.print_array_clear(grid)

if __name__ == "__main__":
    run()