# -*- coding: utf-8 -*-
# @Time : 2025/4/16 19:41
# @Author : lx
# @File : kg_qa.py

import os
import json
from typing import List, Dict, Generator
from neo4j import GraphDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI


class KGQA:
    def __init__(self, llm, config_path: str = None):
        """
        初始化知识图谱问答系统
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if config_path is None:
            config_path = os.path.join(current_dir, "config", "neo4j_config.json")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.driver = GraphDatabase.driver(
            self.config["uri"],
            auth=(self.config["user"], self.config["password"]),
            max_connection_lifetime=1000
        )

        self.model = llm
        neo_prompt = """你是一个 Neo4j 图数据库查询助手，负责将用户的自然语言问题转换为 Cypher 查询语句。不要对输出做出解释！
**图谱特征说明**(Label)-[Relationship]-(Label)
- 核心路径：`(College)<-[:BELONGS_TO]-(Person)<-[:TAUGHT_BY]-(CourseSession)-[:OFFERED_AS]->(Course)`
- 建筑层级：`(Classroom)-[:BELONGS_TO]->(Building)-[:LOCATED_IN]->(Campus)`
- 教学班必连：`(CourseSession)-[:HAS_MEETING]->(Meeting)-[:AT_CLASSROOM]->(Classroom)`
- 教师和论文: `(Person)-[:HAS_PAPER]->(Paper)`
- 教师档案双模式：直接属性`profile` 或 通过 `[:HAS_PROFILE]` 关联节点
【关系方向规则】
- 教师属于学院：(Person)-[:BELONGS_TO]->(College)
- 教学班由教师授课：(CourseSession)-[:TAUGHT_BY]->(Person)
- 教学班开设课程：(CourseSession)-[:OFFERED_AS]->(Course)
- 教学班在教室上课：(Meeting)-[:AT_CLASSROOM]->(Classroom)
- 教室属于教学楼：(Classroom)-[:BELONGS_TO]->(Building)
- 教学楼位于校区：(Building)-[:LOCATED_IN]->(Campus)
- 教学班包含上课时间：(CourseSession)-[:HAS_MEETING]->(Meeting)

主要实体及属性：
- Campus：area_size, campus_id, name, address
- Person / Faculty：name, position, email
- Course: courseId, courseName
- Meeting：start_time, end_time, weekday, weekRange
- CourseSession: hours(学时), credits, campus, section(课序号), department(开课单位), courseCategory, enrollment(教学班人数)
- College：name, website, motto, established_year, research_fields
- Paper / Book / Patent / Project：title, date (Book 还有Publisher)
**示例**
- 介绍一下闵文文老师？
MATCH (p:Person{{name:'闵文文'}})\nOPTIONAL MATCH (p)-[:HAS_PROFILE]->(prof:Profile)\nreturn p, prof
- 金钊老师在哪个学院？
    MATCH (p:Person {{name: '金钊'}})-[:BELONGS_TO]->(c:College)\nRETURN c.name AS college_name
- 数学分析（2）是谁教的？
    MATCH (cs:CourseSession)-[:TAUGHT_BY]->(p:Person)\nWHERE cs.courseName = '数学分析（2）'\nRETURN p
- 格物楼2栋2403的容量有多大？
    MATCH (classroom:Classroom {{name: '格物楼2栋2403'}})\nRETURN classroom
- 数学分析习作（2）的学分是多少？
    MATCH (cs:CourseSession{{courseName: '数学分析习作（2）'}})\nRETURN cs
**生成规则**
1. 尽量返回整个节点+关系而非单个属性\
2. 特别注意：(Person)<-[:TAUGHT_BY]-(CourseSession)
2. 优先级策略：
   - 先匹配主实体（教师/课程），再扩展关联路径
   - 涉及可选属性时优先使用`OPTIONAL MATCH`而非`WHERE exists()`
   - 多条件查询使用`AND`连接而非多个`MATCH`子句
"""
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", neo_prompt),  # ← 可填入你的详细说明
            ("human", "{question}")
        ])

        # 调用并查看各阶段输出

        self.chain = (
                {"question": RunnablePassthrough()}
                | self.prompt_template
                | self.model
                | RunnableLambda(self._execute_cypher)
        )


    def _extract_cypher(self, text: str) -> str:
        """
        提取 Cypher 查询语句
        """
        try:
            if "```cypher" in text:
                return text.split("```cypher")[1].split("```")[0].strip()
            return text.strip()
        except Exception:
            raise ValueError("无法解析模型返回的 Cypher 查询语句")


    def _execute_cypher(self, response):
        """
        执行 Cypher 查询
        """
        try:
            content = getattr(response, "content", "").strip()
            cypher = self._extract_cypher(content)
            # print("[Raw Cypher]:", cypher)  # 调试输出
            # print('#####################################################')
            print("[Generated Cypher]:", cypher)  # 调试输出
            if not cypher.lower().startswith("match") and "return" not in cypher.lower():
                raise ValueError(f"无效的 Cypher 查询语句：{cypher}")
            with self.driver.session() as session:
                result = session.run(cypher)
                # print(result)
                return {'result':[record.data() for record in result], 'cypher': cypher}
        except Exception as e:
            return [{"error": f"查询执行失败: {str(e)}"}]


    def neo4j_query(self, question: str) -> Dict:
        result = self.chain.invoke(question)
        return {'question': question, 'content': result['result'], 'cypher': result['cypher']}


    def close(self):
        """关闭连接"""
        self.driver.close()


# 示例用法
if __name__ == "__main__":
    llm = ChatOpenAI(
        model="qwen-max",
        openai_api_key="",
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    kg_qa = KGQA(llm=llm)

    # print("== 普通查询 ==")
    result = kg_qa.neo4j_query("王津老师教授的课程有哪些？")
    print(result)

    kg_qa.close()
