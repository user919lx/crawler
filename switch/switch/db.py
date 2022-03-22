import pymysql
import struct
import zlib


class MySQLStorage:
    def __init__(self, mysql_config):
        self.mysql_config = mysql_config

    def __trans_value(self, value):
        return f"'{value}'" if type(value) == str else value

    def __mysql_compress(self, value) -> bytes:
        if value is None:
            return None
        if value == "":
            return b""
        size = struct.pack("I", len(value))
        data = zlib.compress(value.encode("utf8"))
        return size + data

    @staticmethod
    def uncompress(value, return_str=False):
        if not value or len(value) < 4:
            return value
        rv = zlib.decompress(value[4:])
        if return_str:
            rv = rv.decode()
        return rv

    def __transfrom_item_to_values(self, item_dict, compress_keys, escape_cols, upsert):
        values = []
        for col_name, value in item_dict.items():
            if col_name in compress_keys:
                value = self.__mysql_compress(value)
            if col_name in escape_cols:
                value = self.db.escape(value)
            values.append(value)
        values = tuple(values)
        if upsert:
            values = values * 2
        return values

    def fetchall(self, table, filter_clause=""):
        sql = f"SELECT * from {table}"
        if filter_clause:
            sql = f"{sql} where 1=1 and {filter_clause}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def record_iter(self, table, filter_clause="", batch_size=10000):
        sql = f"SELECT * from {table}"
        if filter_clause:
            sql = sql + f" where 1=1 and {filter_clause}"
        self.cursor.execute(sql)
        len_records = batch_size
        while len_records > 0:
            records = self.cursor.fetchmany(batch_size)
            len_records = len(records)
            yield records

    def save(self, table, item, compress_keys=[], escape_cols=[], upsert=True):
        keys_str = ", ".join(item.keys())
        placeholder = ",".join(["%s"] * len(item.keys()))
        sql = f"insert into {table} ({keys_str}) values ({placeholder})"
        if upsert:
            update_placeholder = ",".join([f"{k}=%s" for k in item.keys()])
            update_str = f"ON DUPLICATE KEY UPDATE {update_placeholder}"
            sql = f"{sql} {update_str}"
        values = self.__transfrom_item_to_values(item, compress_keys, escape_cols, upsert)
        self.cursor.execute(sql, values)
        self.db.commit()

    def save_many(self, table, item_list, compress_keys=[]):
        item_dict = item_list[0]
        keys_str = ", ".join(item_dict.keys())
        placeholder = ",".join(["%s"] * len(item_dict.keys()))
        sql = f"insert into {table} ({keys_str}) values ({placeholder})"
        values_list = []
        for item in item_list:
            values = self.__transfrom_item_to_values(item, compress_keys, upsert=False)
            values_list.append(values)
        self.cursor.executemany(sql, values_list)
        self.db.commit()

    def open(self):
        self.db = pymysql.connect(**self.mysql_config)
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def close(self):
        self.db.close()
