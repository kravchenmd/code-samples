import time
import timeit
from dataclasses import dataclass, field
from functools import partial, wraps
from typing import ClassVar
from datetime import datetime, timedelta

"""
Based on:
- https://www.geeksforgeeks.org/python-lru-cache/
- https://realpython.com/lru-cache-python/#adding-cache-expiration
"""


class Node:
    """
    Element of Doubly Linked List
    """

    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None


@dataclass(kw_only=True)
class LRUCache:
    """ `Pure` LRUCache (w/o cache TTL) """
    DEBUG: ClassVar[bool] = False
    func: callable
    max_size: int = 10
    cache = {}
    head = Node(0, 0)
    tail = Node(0, 0)
    head.next = tail
    tail.prev = head
    hits = 0
    misses = 0
    current_size = 0

    def __call__(self, *args, **kwargs):
        # The cache presents with the help
        # of Linked List
        if args in self.cache:
            self.llist(args)
            self.hits += 1

            if self.DEBUG:
                cache_list = [f"arg({k})->{v}" for k, v in self.cache.items()]
                return f"(DEBUG) Hit: {self.func.__name__}({self.cache[args]})\n\t\tCache: {' '.join(cache_list)}\n" \
                       f"\t\tCacheInfo: hits={self.hits}, misses={self.misses}, maxsize={self.max_size}, " \
                       f"currsize={self.current_size}"
            return self.cache[args]

        # The given cache keeps on moving.
        if self.max_size is not None:

            if len(self.cache) > self.max_size:
                n = self.head.next
                self.remove_node(n)
                del self.cache[n.key]

        # Compute and cache and node to see whether
        # the following element is present or not
        # based on the given input.
        result = self.func(*args, **kwargs)
        self.cache[args] = result
        node = Node(args, result)
        self.add_note(node)
        self.misses += 1
        if self.current_size < self.max_size:
            self.current_size += 1

        if self.DEBUG:
            cache_list = [f"arg({k})->{v}" for k, v in self.cache.items()]
            return f"(DEBUG) Missed: {self.func.__name__}({self.cache[args]})\n\t\tCache: {' '.join(cache_list)}\n" \
                   f"\t\tCacheInfo: hits={self.hits}, misses={self.misses}, maxsize={self.max_size}, " \
                   f"current_size={self.current_size}"
        return result

    @staticmethod
    def remove_node(node):
        """ Remove Node from double linked list """
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p

    def add_note(self, node):
        """ Add Node to double linked list """
        p = self.tail.prev
        p.next = node
        self.tail.prev = node
        node.prev = p
        node.next = self.tail

    # Over here the result task is being done
    def llist(self, args):
        current = self.head

        while True:
            if current.key == args:
                node = current
                self.remove_node(node)
                self.add_note(node)
                if self.DEBUG:
                    del self.cache[node.key]
                    self.cache[node.key] = node.val
                break
            else:
                current = current.next


@dataclass(kw_only=True)
class TimedLRUCache(LRUCache):
    """ LRUCache w/ cache TTL """
    ttl: int = None

    def __post_init__(self):
        if self.ttl is not None:
            self.lifetime = timedelta(seconds=self.ttl)
            self.exp_time = datetime.utcnow() + self.lifetime

    def __call__(self, *args, **kwargs):
        if self.ttl is not None:
            now = datetime.utcnow()
            if now >= self.exp_time:
                self.clear_cache()
                self.exp_time = now + self.lifetime
        result = super(TimedLRUCache, self).__call__(*args, **kwargs)
        if self.DEBUG:
            result += f" , ttl={self.ttl}"
        return result

    def clear_cache(self):
        self.cache = {}
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.current_size = 0


def lru_cache(func=None, *_, max_size=None, ttl=None):
    """
    additional decorator for calling `TimedLRUCache` with and without parameters
    """
    if func is None:
        return partial(lru_cache, max_size=max_size, ttl=ttl)
    kwargs = {}
    if max_size is not None:
        kwargs['max_size'] = max_size
    if ttl is not None:
        kwargs['ttl'] = ttl
    return TimedLRUCache(func=func, **kwargs)


def example_debug_ttl():
    """ Example with DEBUG output and TTL """
    LRUCache.DEBUG = True

    @lru_cache(max_size=5, ttl=4)
    def ex_func(n):
        print(f'Computing...{n}')
        time.sleep(1)
        return n

    print(f'\nFunction: ex_func')
    print(ex_func(1))
    print(ex_func(2))
    print(ex_func(3))
    print(ex_func(1))
    print(ex_func(3))
    print(ex_func(4))


def example_fibonacci():
    """ Example with fibonacci function """
    LRUCache.DEBUG = False

    def fibonacci(n):
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fibonacci(n - 1) + fibonacci(n - 2)

    @lru_cache()
    def fibonacci_cache(n):
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fibonacci_cache(n - 1) + fibonacci_cache(n - 2)

    print()
    start_time = timeit.default_timer()
    fibonacci(38)
    print(f'Duration of `fibonacci(38)`: {timeit.default_timer() - start_time} s')

    start_time = timeit.default_timer()
    fibonacci_cache(138)
    print(f'Duration of `fibonacci_cache(138)`: {timeit.default_timer() - start_time} s')


if __name__ == '__main__':
    example_debug_ttl()
    example_fibonacci()
