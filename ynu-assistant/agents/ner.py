from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import asyncio
import json
from pypinyin import lazy_pinyin, Style
import re


class NER:
    def __init__(self, llm, entities_path='./data/entities.txt'):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
你是一个实体识别助手，专门用于从文本中识别并提取不同类别的实体信息。以下是需要提取的实体类别：

1. **人名**（例如：李华、王刚等）
2. **教室名**（例如：格物楼2103，教学楼A105等）
3. **教学楼名**（例如：文汇楼302，天光楼等）
4. **组织机构名**（例如：信息学院，软件学院等）
5. **课程名**（例如：计算机网络，数据结构，算法设计与分析等）

请注意：
- **简写**的情况也需要识别。例如：
  - “信息学院” 可以简写为 “信院”。
  - “算法设计与分析” 可以简写为 “算法课”。
- 你需要根据这些规则处理并分类问题中的实体。

### 示例输入：
**问题**：信院的王静老师的算法课是在格物楼1栋1507上吗？

### 输出格式：
请按严格照以下 JSON 格式提供你的输出，不要返回多于信息，确保将每个实体分类清楚地提取出来：
```json
{{
    "person": ["王静"],
    "classroom": ["格物楼1栋1507"],
    "course": ["算法课"],
    "department": ["信院"]
}}```
若没有识别出实体，则返回"无需处理"。                                                       
当前问题：{question}""")

        self.chain = self.prompt | self.llm | self._parse_output
        self.load_entities()

    def _parse_output(self, response):
        return response.content.strip()
    
    def load_entities(self):
        with open('C:\\Users\\Burning\\Desktop\\YNU-Mind\\ynu-assistant\\agents\\data\\entities.txt', 'r', encoding='utf-8') as f:
            tmp = f.read().split('\n')
        self.entities = []
        for line in tmp:
            if line.strip():
                tmp2 = line.strip().split(',')
                self.entities.append((tmp2[0], tmp2[1]))
        with open('C:\\Users\\Burning\\Desktop\\YNU-Mind\\ynu-assistant\\agents\\data\\pinyin_entities.txt', 'r', encoding='utf-8') as f:
            tmp = f.read().split('\n')
        self.pinyin_entities = []
        for line in tmp:
            if line.strip():
                tmp2 = line.strip().split(',')
                self.pinyin_entities.append((tmp2[0], tmp2[1]))

    def edit_distance(self, s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[m][n]
    
    def get_min_pinyin_distance(self, py, _type):
        min_dist = int(1e9)
        min_v = {}
        for idx,(k, v) in enumerate(self.pinyin_entities):
            if v != _type:
                continue
            dist = self.edit_distance(py, k)
            if dist < min_dist:
                min_dist = dist
                min_v[dist] = []
                min_v[dist].append(self.entities[idx][0])
            elif dist == min_dist:
                min_v[dist].append(self.entities[idx][0])
        return min_v[min_dist]
    
    def get_classroom(self, classroom_name):
        tmp = []
        numbers = re.findall(r'\d{3,}', classroom_name)
        for k, v in self.entities or numbers[0] not in classroom_name:
            if v != 'Classroom':
                continue
            cnt = 0
            for c in classroom_name:
                if c in k:
                    cnt += 1
            tmp.append({k: cnt})
        tmp = sorted(tmp, key=lambda x: list(x.values())[0], reverse=True)
        return [next(iter(x.keys())) for x in tmp[:5]]
    
    def get_min_hz_distance(self, hz, _type):
        """
        input: hz: str, entity name in Chinese
               _type: str, entity type
        class variable: self.entities: list of tuples (entity name, entity type)
        return: 返回一个列表，列表中包含与输入实体最接近的实体（hz出现的的每个字符都要在实体中出现）
        """
        tmp = []
        for k, v in self.entities:
            if v != _type:
                continue
            cnt = 0
            for c in hz:
                if c in k:
                    cnt += 1
            tmp.append({k: cnt})
        tmp = sorted(tmp, key=lambda x: list(x.values())[0], reverse=True)
        return [next(iter(x.keys())) for x in tmp[:5]]
    
    def ner_update(self, ner_dic, question):
        reason = ''
        for person in ner_dic.get("person", []):
            if (person,'Person') not in self.entities:
                person_py = ''.join(lazy_pinyin(person, style=Style.NORMAL))
                new_persons = self.get_min_pinyin_distance(person_py, 'Person')
                if new_persons:
                    reason += '候选教师实体: ' + ', '.join(new_persons) + '\n'
                    question = question.replace(person, new_persons[0])
        for classroom in ner_dic.get("classroom", []):
            if (classroom,'Classroom') not in self.entities:
                classroom_py = ''.join(lazy_pinyin(classroom, style=Style.NORMAL))
                new_classrooms = self.get_min_pinyin_distance(classroom_py, 'Classroom')
                if new_classrooms:
                    reason += '候选教室实体: ' + ', '.join(new_classrooms) + '\n'
                    question = question.replace(classroom, new_classrooms[0])
        for course in ner_dic.get("course", []):
            if (course,'Course') not in self.entities:
                new_course = self.get_min_hz_distance(course,'Course')
                if new_course:
                    reason +='候选课程实体: ' + ', '.join(new_course) + '\n'
                    question = question.replace(course, new_course[0])
        for department in ner_dic.get("department", []):
            if (department,'College') not in self.entities:
                new_department = self.get_min_hz_distance(department,'College')
                if new_department:
                    reason += '候选学院实体: ' + ', '.join(new_department) + '\n'
                    question = question.replace(department, new_department[0])
        return question, reason

    async def process(self, question: str) -> str:
        ner_string =  await self.chain.ainvoke({"question": question})
        if '无需处理' in ner_string:
            return question, '无实体'
        if "```json" in ner_string:
            ner_string = ner_string.split("```json")[1].split("```")[0].strip()
        ner_dic = json.loads(ner_string)

        return self.ner_update(ner_dic, question)

    


async def main():
    llm = ChatOpenAI(
        model="glm-4-air-250414",
        openai_api_key="",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        temperature=0
        )
    agent = NER(llm)
    question = "信院的王金老师的算法课是在格物楼1507上吗？"
    output = await agent.process(question)
    print(output)
        

if __name__ == "__main__":
    asyncio.run(main())

