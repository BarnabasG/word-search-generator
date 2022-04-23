# word-search-generator
An implementation of a word search generator in python 

## Generate from a list of words:
```
ws = wordsearch()
easter_words = ["easter", "bunny", "egg", "hunt", "chocolate", "spring", "basket", "bonnet", "chick",
                "sunday", "daffodil", "duckling", "holiday", "lent"]
maxx, maxy = 10, 10
grid = ws.generate(maxx, maxy, word_list=easter_words, debug=True)
if ws.valid_grid(grid):
    ws.print_array_clear(grid)
```
![image](https://user-images.githubusercontent.com/57625180/164917048-3d8b98f6-095f-4f00-a0b4-ef33d30e15d3.png)

## Generate from a topic:
```
ws = wordsearch()
maxx, maxy = 10, 10
grid = ws.generate(maxx, maxy, topic='christmas', word_count=12, debug=True)
if ws.valid_grid(grid):
    ws.print_array_clear(grid)
```
![image](https://user-images.githubusercontent.com/57625180/164917156-a5e3f511-6b84-4238-a0f8-dc1c97c98875.png)

### Debug mode:
```
grid = ws.generate(maxx, maxy, word_list=easter_words, debug=True)
```
![image](https://user-images.githubusercontent.com/57625180/164916996-94ae75c8-49c2-42c0-8e8f-e37b60ed9725.png)

### Unicode grid:
```
ws.print_array_grid(grid)
```
![image](https://user-images.githubusercontent.com/57625180/164917200-641e93f7-00d1-4917-9227-9a9945e928fa.png)
