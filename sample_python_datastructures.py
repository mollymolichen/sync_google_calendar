from collections import Counter, defaultdict
from itertools import groupby
from operator import itemgetter
import heapq

'''
Option + Up/Down: Move line up/down
Cmd + Shift + K: Delete a line
Shift + Option + A: Block comment/uncomment
Activate Python Virtual Env: source .venv/bin/activate
'''

'''
ADDING DATA
List: append()
Set: add()
Dict: assignment
Default Dict: whichever the data type is
Tuple: add()
'''

def lists():
    # creating
    nums = [5, 2, 8, 1, 3, 10]
    
    # accessing
    print(nums[5])

    # adding
    nums.append(69)                                         # append a SINGLE item to end of list
    nums.insert(2, 20)                                      # insert(index, element)
    nums2 = [100, 33, 205]                                  # append an iterable to the end of list
    nums.extend(nums2)                                      
    nums3 = [300, -33, 5]                                   # creates a new list, doesn't modify existing list
    nums = nums + nums3
    print("After adding to nums: ", nums)

    # sorting
    print(f"list.sort(): {nums.sort(reverse = True)}")      # list.sort() returns None
    print(f"sorted(list): {sorted(nums,reverse=True)}")     # sorted() returns a new sorted list
    print(f"list.reverse(): {nums.reverse()}")              # list.reverse() returns None
    print(f"list[::-1]: {nums[::-1]}")                      # splicing returns a new reversed list

    # top K
    nums.sort(reverse=True)
    print(f"Top 3 items: {nums[0:3]}")  

    # list comprehension, looping
    print(f"Sorted even numbers: {sorted([n for n in nums if n % 2 == 0])}")  # even numbers sorted

    # slicing [start : end : step]
    print(f"Numbers from index 1-3: {nums[1:4]}")  # elements from index 1 to 3

    # deleting
    try:
        nums.remove(69)     # raises ValueError - once you exit a try-block because of an exception, there is no way back in.
    except ValueError:
        print("Value not found.")
    except IndexError:
        print("Index out of range.")
    finally:                # https://docs.python.org/3/tutorial/errors.html#defining-clean-up-actions
        del nums[6]         # raises ValueError
        nums.pop(7)         # raises IndexError
        del nums[0:1]       # deletes 5
        print(nums)         # [2, 8, 1, 3, 10]

def dictionary():
    # iteration
    fruits = ['apple', 'cherry', 'date', 'banana', 'cherry', 'cherry', 'date']

    # create from dictionary literal {} if you know key-value pairs
    # dict has key uniqueness, so this will reduce to {'apple' : 5, 'cherry' : 6, 'date' : 4, 'banana' : 6}
    fruits_dict = {'apple' : 5, 'cherry' : 6, 'date' : 4, 'banana' : 6, 'cherry': 6, 'cherry' : 6, 'date' : 4}

    # create from dict() constructor using list of key-value tuples
    # fruits_dict = dict([('apple' : 5), ('cherry' : 6), ('date' : 4), ('banana' : 6), ('cherry': 6), ('cherry' : 6), ('date' : 4)])

    # create from list
    # for fruit in fruits:
        # fruits_len_dict[fruit] = len(fruit)
    # create from dictionary literal {}
    fruit_len_dict = {fruit : len(fruit) for fruit in fruits} # apple: 5, cherry: 6, date: 4, banana: 6
    
    print(f"Initial dictionary: {fruit_len_dict}")

    # adding multiple key-value pairs
    fruit_len_dict.update({ 'mangosteen' : len('mangosteen')}, { 'mango' : len('mango')})

    # lookup (index or .get())
    # get() handles it gracefully if key not found with optional default value
    print(f"Get length of banana using [key]: {fruit_len_dict['banana']}")
    """ try:
        print(f"Get length of elderberry using [key]: {fruit_len_dict['elderberry']}")
    except KeyError:
        print("Key not found.") """
    print(f"Get length of banana using .get(): {fruit_len_dict.get('banana')}")
    print(f"Get length of elderberry (.get(default)): {fruit_len_dict.get('elderberry', 'not found')}")

    # update
    fruit_len_dict['date'] = 4    

    # delete (pass key to del or pop)
    del fruit_len_dict['cherry']    # doesn't return the reference
    print(f"After deleting cherry: {fruit_len_dict}")
    fruit_len_dict.pop('date')      # returns the reference, easier to test with
    print("After deleting date: ", fruit_len_dict)

    # creating a Counter of dict/Counter is pretty pointless
    # “Count frequencies of items in a list.”
    print(f"Counter: {Counter(fruit_len_dict)}")

    # dict vs Counter; prioritize Counter
    """ s = "abracadabra"
    print({char : s.count(char) for char in set(s)}) # unsorted (random order)
    print(Counter(s)) """

def sets():
    emails = ["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com"]

    # membership checks
    print("a@x.com" in set(emails))
    print("a@x2.com" in set(emails))

    # deduping
    print(set(emails))

    # return unique elements while preserving order
    print(sorted(set(emails)))

'''
The Counter in Python is a specialized dictionary subclass 
found within the collections module. 
It is designed for efficiently counting hashable objects 
(like elements in a list, characters in a string, or words in a sentence).
You can initialize a Counter in several ways:
From an iterable: Counter(['apple', 'banana', 'apple', 'orange'])
From a mapping (dictionary): Counter({'apple': 2, 'banana': 1})
From keyword arguments: Counter(apple=2, banana=1)
An empty Counter: Counter()'''
def counter():
    # Create a Counter from a list
    fruits = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']
    fruit_counts = Counter(fruits)
    print(f"Initial counts: {fruit_counts}")

    # Access the count of a specific fruit
    print(f"Count of 'apple': {fruit_counts['apple']}")

    # Update the counter with more data
    more_fruits = ['grape', 'apple', 'orange']
    fruit_counts.update(more_fruits)
    print(f"Counts after update: {fruit_counts}")

    # Find the most common fruits
    print(f"Two most common fruits: {fruit_counts.most_common(2)}")

    # Find the least common fruits
    print(f"Least common fruit: {fruit_counts.most_common()[::-1][0]}")

    # Subtract counts
    order = Counter({'apple': 1, 'banana': 1})
    fruit_counts.subtract(order)    # subtract counts based on another Counter
    print(f"Counts after subtraction: {fruit_counts}")
    
'''VERY IMPORTANT for interviews!!!'''
def default_dict():
    # defaultdict(int): Counting, numerical aggregation
    # Group by count
    counts = defaultdict(int)
    counts['apple'] += 1
    counts['banana'] += 2
    counts['apple'] += 10
    print("Group words by count: ", counts)
    
    # defaultdict(list) for grouping or accumulating items
    # Group by first letter of word
    words = ["apple", "cat", "book", "ape", "banana", "berry", "dino", "kiwi"]
    dd_list = defaultdict(list)
    for word in words:
        dd_list[word[0]].append(word)   
    print("Group by first letter of word: ", dd_list)

    # defaultdict(set): Storing unique items
    # Group numbers by even vs odd (needed sorting)
    numbers = [6, 1, 2, 8, 3, 4, 5, 6, 2, 7]
    sorted(numbers)
    grouped_by_even_odd = defaultdict(set)                          # remove duplicates
    for key, group in groupby(numbers, key=lambda x: "Even" if x%2==0 else "Odd"):  # only two groups, Even and Odd  
        for item in group:
            grouped_by_even_odd[key].add(item)                      # add all items in Even group to a new dict in the grouped dict, then all items in Odd group to another dict in the grouped dict
        # grouped_by_even_odd[key] = list(group)                    # didn't work
        # grouped_by_even_odd[key].extend(list(group))              # didn't work
        # print(key, list(group))                                       
        # new_data = {key : list(group)}                            # didn't work
        # grouped_by_even_odd.update(new_data)                      
    print(f"Group unique numbers by even vs odd: {grouped_by_even_odd}")

    # defaultdict(dict): Nested dictionaries
    # nested_data = defaultdict(dict)
    nested_data = { 
        "EMEA" : { "region": "Middle East", "cost_per_query" : 0.1, "languages": ["Arabic"]}, 
        "USEST" : { "region": "US East", "cost_per_query" : 0.15 }, 
        "USWST" : { "region": "US West", "cost_per_query" : 0.2 },
        "LATAM" : { "region": "Latin America", "cost_per_query" : 0.1, "languages": ["Spanish", "Portuguese"] }
    }
    nested_data["APAC"] = {}
    nested_data["APAC"]["region"] = "Asia Pacific"
    nested_data["APAC"]["cost_per_query"] = 0.05
    nested_data["APAC"]["languages"] = ["Mandarin", "Cantonese"]
    print("Nested dictionary: ", nested_data)

'''VERY IMPORTANT for interviews!!!'''
def grouping():
    # Example 0 - Group by consecutive identical elements
    my_list = [1, 1, 2, 3, 3, 3, 4, 4, 5]
    grouped_list = []
    for key, group in groupby(my_list):     # no need to pass key
        grouped_list.append(list(group))
    print("Group by consective identical elements: ", grouped_list)

    # Example 1 - Group a grocery list by a specific key (ex. category or price)
    groceries = [
        {'name': 'Apple', 'category': 'Fruit', 'price': 2},
        {'name': 'Carrot', 'category': 'Vegetable', 'price': 3},
        {'name': 'Banana', 'category': 'Fruit', 'price': 1},
        {'name': 'Broccoli', 'category': 'Vegetable', 'price': 5},
        {'name': 'Orange', 'category': 'Fruit', 'price': 2},
        {'name': 'Tomato', 'category': 'Fruit', 'price': 1.5},
        {'name': 'Tomato', 'category': 'Vegetable', 'price': 1},
    ]
    '''
    entire object grouped by category: 
        Fruit: [{'name: 'Apple', 'category': 'Fruit', 'price': 2}, {'name': 'Banana', 'category': 'Fruit', 'price': 1}, ...]
        Vegetable: [{'name': 'Carrot', 'category': 'Vegetable', 'price': 3}, {'name': 'Broccoli', 'category': 'Vegetable', 'price': 5}, ...]
    '''

    # Option 1 (best): defaultdict(list)
    grouped_items = defaultdict(list)
    for item in groceries:
        grouped_items[item['category']].append(item['name'])    # append directly to empty category (defaultdict)
    print("Option 1: Grouped items using defaultdict(list): ", grouped_items)

    # Option 2: Manual grouping using dict
    grouped_items = {}
    for item in groceries:
        category = item['category']
        if category not in grouped_items:                       # can't append directly to empty category (dict)
            grouped_items[category] = []
        grouped_items[category].append(item['name'])
    print("Option 2: Grouped items using regular dict: ", grouped_items) 

    # Option 3: itertools.groupby(): use to group CONSECUTIVE identical elements in an iterable (sort beforehand)
    grouped_items = {}
    # Sort the items by category first so itertools.groupby() can handle consecutive elements
    sorted_items = sorted(groceries, key=itemgetter('category'))
    for key, group in groupby(sorted_items, key=itemgetter('category')):   # group by category
        grouped_items[key] = [item['name'] for item in group]              # assign all list elements under key (category) at once
    print("Option 3: Grouped items using groupby: ", grouped_items)
    
    # Example 2: Grouping by the first and last letter of strings (worked w/o sorting?)
    words = ["apple", "banana", "cat", "dog", "ant", "bat"]

    grouped_by_first_letter = defaultdict(list)
    for key, group in groupby(words, key=lambda x: x[0]):
        grouped_by_first_letter[key] = list(group)
    print(f"Grouped by first letter: {grouped_by_first_letter}")

    grouped_by_last_letter = defaultdict(list)
    for key, group in groupby(words, key=lambda x: x[len(x)-1]):
        grouped_by_last_letter[key] = list(group)
    print(f"Grouped by last letter: {grouped_by_last_letter}")

    # Example 3: Grouping into sublists of a fixed size
    my_list = list(range(10))
    chunk_size = 3
    chunked_list = [my_list[i:i + chunk_size] for i in range(0, len(my_list), chunk_size)]
    print("Grouped into sublists of fixed size using chunking: ", chunked_list)     

'''Immutable: Tuples are unchangeable; their elements cannot be altered after creation.
count(): Returns the number of elements in the tuple.
index(n): Get nth item from the tuple.'''
def tuples():
    # tuple unpacking
    logs = [
        ("alice", "login"),
        ("bob", "login"),
        ("alice", "logout"),
        ("alice", "login"),
    ]
    user_actions = defaultdict(list)
    unique_user_actions = defaultdict(set)
    # user_actions_tuple_count = defaultdict(list)
    user_actions_tuple_count = defaultdict(tuple)

    # “Group transactions by user.”
    for user, action in logs:
        user_actions[user].append(action)
    print(user_actions)

    # "Group unique transactions by user."
    for user, action in logs:
        unique_user_actions[user].add(action)
    print(unique_user_actions)

    # “Count occurrences of user transactions.”
    for log in logs:
        # using tuples as keys
        user_actions_tuple_count[log] = logs.count(log)
    print(user_actions_tuple_count)

'''Here are some key functions provided by the heapq module:
heapify(list): Transforms a regular list into a heap in-place.
heappush(heap, item): Inserts an item into the heap while maintaining the heap property.
heappop(heap): Removes and returns the smallest item from the heap (for a min-heap) while maintaining the heap property.
heappushpop(heap, item): Pushes an item onto the heap, then pops and returns the smallest item. This is more efficient than separate heappush and heappop calls.
heapreplace(heap, item): Pops and returns the smallest item, then pushes the new item. This differs from heappushpop in the order of operations.
nlargest(n, iterable, key=None): Returns a list with the n largest elements from the iterable.
nsmallest(n, iterable, key=None): Returns a list with the n smallest elements from the iterable.'''
def minheap():
    nums = [10, 4, 7, 2, 9, 1]
    heapq.heapify(nums)
    print(f"Heapified list: ", nums)

    # top K
    print(f"Smallest 3 items in the heap: ", heapq.nsmallest(3, nums))
    print(f"Largest 2 items in the heap: ", heapq.nlargest(2, nums))

    # pushing
    heapq.heappush(nums, 69)
    print(f"After pushing: ", nums)

    # peeking
    print(f"Peek smallest item: ", nums[0])

    # popping
    heapq.heappop(nums)
    print(f"After popping: ", nums)

    # pushpop - pushes a new element, then pops the smallest element
    # use when preserving top K
    heapq.heappushpop(nums, 5)
    print(f"After pushpop: ", nums)

    # replace - pops the smallest element, then pushes a new element, size doesn't change 
    # use when you need to keep the new element in the heap
    # "poppush"
    heapq.heapreplace(nums, 69)
    print(f"After replace: ", nums)

# maintaining a fixed-size heap
def add_to_fixed_size_minheap(heap, element, max_size):
    """ 
    # pop if max size exceeded
    while len(heap) > max_size:
        heapq.heappushpop(heap, element) # if i didn't need the new element in the heap
        heapq.heapreplace(heap, element) # if i do need the new element in the heap

    # try to add element to heap
    heapq.heappush(element) """

    if len(heap) < max_size:
        heapq.heappush(element)
    else:
        heapq.heappushpop(heap, element)

    return heap

'''A max-heap is a specialized tree-based data structure that satisfies the max-heap property:
In a max-heap, for any given node C, if P is a parent node of C, then the key (the value) of P is greater than or equal to the key of C.
This property ensures that the largest element is always at the root of the heap. Max-heaps are commonly 
used to implement priority queues, where the highest priority element (the largest element) is'''
class MaxHeap:
    def __init__(self):
        self._heap = []

    def push(self, item):
        # Store the negative of the item to simulate a max-heap
        heapq.heappush(self._heap, -item)

    def pop(self):
        # Retrieve the item and negate it back to its original value
        if not self._heap:
            raise IndexError("pop from empty max heap")
        return -heapq.heappop(self._heap)

    def peek(self):
        # Peek at the largest element without removing it
        if not self._heap:
            raise IndexError("peek from empty max heap")
        return -self._heap[0]

    def is_empty(self):
        return len(self._heap) == 0

    def size(self):
        return len(self._heap)

    '''
    # Example usage:
    max_heap = MaxHeap()
    max_heap.push(10)
    max_heap.push(5)
    max_heap.push(20)
    max_heap.push(15)

    print(f"Max heap size: {max_heap.size()}") # Output: Max heap size: 4
    print(f"Largest element: {max_heap.peek()}") # Output: Largest element: 20

    print(f"Popped: {max_heap.pop()}") # Output: Popped: 20
    print(f"Popped: {max_heap.pop()}") # Output: Popped: 15
    print(f"Largest element after pops: {max_heap.peek()}") # Output: Largest element after pops: 10
    '''

if __name__ == "__main__":
    