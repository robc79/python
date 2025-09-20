#! /usr/bin/env python


import datetime
import pickle
import sqlite3
import threading


class Cache:
    """ A simple caching class that works with an in-memory or file based
    cache. """

    _lock = threading.Lock()

    def __init__(self, filename=None):
        """ Construct a new in-memory or file based cache."""
        if filename is None:
            self._connection = sqlite3.connect(":memory:")
        else:
            self._connection = sqlite3.connect(filename)
        self._create_schema()


    def _create_schema(self):
        table_name = "Cache"
        cursor = self._connection.cursor()
        result = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' and name = ?",
            (table_name,))
        cache_exists = result.fetchone() is not None
        if cache_exists:
            return    
        sql = """
            CREATE TABLE 'Cache' (
            'Key' TEXT NOT NULL UNIQUE,
            'Item' BLOB NOT NULL,
            'CreatedOn' TEXT NOT NULL,
            'TimeToLive' TEXT NOT NULL,
            PRIMARY KEY('Key'))
        """
        cursor.execute(sql)
        cursor.close()


    def update(self, key, item, ttl=60):
        """ Add or update an item in the cache using the supplied key. Optional
        ttl specifies how many seconds the item will live in the cache for. """
        sql = "SELECT Key FROM 'Cache' WHERE Key = ?"
        cursor = self._connection.cursor()
        result = cursor.execute(sql, (key,))
        row = result.fetchone()
        with self.__class__._lock:
            if row is not None:
                self._remove_item(key, cursor)
            sql = "INSERT INTO 'Cache' values(?, ?, datetime(), ?)"
            pickled_item = pickle.dumps(item)
            cursor.execute(sql, (key, pickled_item, ttl))
            self._connection.commit()
        cursor.close()


    def _remove_item(self, key, cursor):
        sql = "DELETE FROM 'Cache' WHERE Key = ?"
        cursor.execute(sql, (key,))
        cursor.connection.commit()


    def get(self, key):
        """ Get an item from the cache using the specified key. """
        sql = "SELECT Item, CreatedOn, TimeToLive FROM 'Cache' WHERE Key = ?"
        cursor = self._connection.cursor()
        result = cursor.execute(sql, (key,))
        row = result.fetchone()
        if row is None:
            return
        item = pickle.loads(row[0])
        if self._item_has_expired(row[1], row[2]):
            with self.__class__._lock:
                self._remove_item(key, cursor)
            item = None
        cursor.close()
        return item


    def _item_has_expired(self, created, ttl):
        expiry_date = datetime.datetime.fromisoformat(created) + datetime.timedelta(seconds=int(ttl))
        now = datetime.datetime.now()
        return expiry_date <= now


    def remove(self, key):
        """ Remove an item from the cache using the specified key. """
        cursor = self._connection.cursor()
        with self.__class__._lock:
            self._remove_item(key, cursor)
        cursor.close()


    def purge(self, all=False):
        """ Remove expired items from the cache, or all items if flag is set. """
        cursor = self._connection.cursor()
        with self.__class__._lock:
            if all:
                sql = "DELETE FROM 'Cache'"
                cursor.execute(sql)
                self._connection.commit()
            else:
                sql = "SELECT Key, CreatedOn, TimeToLive from 'Cache'"
                for row in cursor.execute(sql):
                    if self._item_has_expired(row[1], row[2]):
                        with self.__class__._lock:
                            self._remove_item(row[0], cursor)
        cursor.close()


    def close(self):
        """ Close the underlying connection used by the cache. """
        self._connection.close()
