import pymysql
from neo4j import GraphDatabase
from pymysql.cursors import DictCursor
from configuration.config import MYSQL_CONFIG, NEO4J_CONFIG

driver=GraphDatabase.driver(**NEO4J_CONFIG)

class MysqlReader:
    def __init__(self):
        self.connection = pymysql.connect(**MYSQL_CONFIG)
        self.cursor = self.connection.cursor(DictCursor)
    def read(self,sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    def close(self):
        self.cursor.close()
        self.connection.close()

class Neo4jWriter:
    def __init__(self):
        self.driver=GraphDatabase.driver(**NEO4J_CONFIG)
    def write_nodes(self,label,properties:list[dict]):
        cypher = f"""
                UNWIND $batch AS item
                MERGE (:{label} {{id:item.id,name:item.name}})"""
        driver.execute_query(cypher, batch=properties)
    def write_relations(self,type,start_label,end_label,relations:list[dict]):
        cypher = f"""
                UNWIND $batch AS item
                MATCH(start:{start_label}{{id:item.start_id}}),(end:{end_label}{{id:item.end_id}})
                MERGE (start)-[:{type}]->(end)"""
        driver.execute_query(cypher, batch=relations)


# 写入neo4j的工具类
if __name__ == '__main__':
    reader=MysqlReader()

    sql="""
    select id,name
    from
    base_category1"""
    # [{'id': 1, 'name': '图书、音像、电子书刊'}, {'id': 2, 'name': '手机'}]
    category1=reader.read(sql)
    print(category1)

    sql="""
        select id,name
        from
        base_category2"""
        # [{'id': 1, 'name': '图书、音像、电子书刊'}, {'id': 2, 'name': '手机'}]
    category2=reader.read(sql)
    print(category2)

    writer=Neo4jWriter()
    writer.write_nodes('category1',category1)
    writer.write_nodes('category2',category2)

    # cypher="""
    #     UNWIND $category1 AS item
    #     MERGE (:Category1 {id:item.id,name:item.name})"""
    # driver.execute_query(cypher,category1=category1)
    #
    #

    # cypher="""
    #         UNWIND $category2 AS item
    #         MERGE (:Category2 {id:item.id,name:item.name})"""
    # driver.execute_query(cypher,category2=category2)
    #
    sql="""
    select id as start_id,
        category1_id as end_id
        from
        base_category2"""
    relations=reader.read(sql)
    print(relations)
    writer.write_relations('Belong','category2','category1',relations=relations)

    # cypher="""
    # UNWIND $relations AS item
    # MATCH(start:Category2{id:item.start_id}),(end:Category1{id:item.end_id})
    # MERGE (start)-[:Belong]->(end)
    # """
    # driver.execute_query(cypher,relations=relations)

