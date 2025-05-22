// 1. 创建软件学院主节点并关联校区
MATCH (campus:Campus {campus_id: "CG"})
CREATE (college:College {
  name: "软件学院",
  established: "2002年",
  description: "云南大学国家示范性软件学院，国家示范性软件学院之一，培养国际化、工程型人才。",
  website: "https://www.ynu.edu.cn",
  research_centers: ["教育部跨境网络空间安全工程中心", "云南省软件工程重点实验室", "云南省云计算工程研究中心", "云南省高校数据科学与智能计算重点实验室", "昆明市数据科学与智能计算重点实验室"]
})-[:BELONGS_TO]->(campus)
RETURN college;

// 2. 添加学院领导团队
MATCH (college:College {name: "软件学院"})
WITH college, [
  {position: "院长", name: "杨云"},
  {position: "党委副书记", name: "许佳"},
  {position: "副院长", name: "谢诚"},
  {position: "副院长", name: "蔡莉"},
  {position: "副院长", name: "刘金卓"}
] AS leaders
UNWIND leaders AS leader
CREATE (p:Person:Leader {
  name: leader.name,
  position: leader.position
})-[:HOLDS_POSITION]->(college);

// 3. 创建学院各系
MATCH (college:College {name: "软件学院"})
WITH college, [
  {name: "软件工程系", phone: "0871-65931551", office: "软件学院楼A座1105室"},
  {name: "网络工程系", phone: "0871-65931551", office: "软件学院楼A座1103室"},
  {name: "信息安全系", phone: "0871-65931551", office: "软件学院楼A座1102室"},
  {name: "数字媒体技术系", phone: "0871-65931551", office: "软件学院楼A座1103室"}
] AS departments
UNWIND departments AS dept
CREATE (college)-[:HAS_DEPARTMENT]->(:Department {
  name: dept.name,
  phone: dept.phone,
  office: dept.office
});

// 4. 创建实验中心
MATCH (college:College {name: "软件学院"})
WITH college
CREATE (college)-[:HAS_LAB]->(:Lab {
  name: "软件工程省级实验教学示范中心",
  office: "软件学院A座1205室",
  phone: "0871-65931534"
});

// 5. 创建学院机关
MATCH (college:College {name: "软件学院"})
WITH college, [
  {name: "教务办公室", phone: "0871-65931540", office: "软件学院楼A座1309室"},
  {name: "党政办公室", phone: "0871-65931551", office: "软件学院楼A座1305室"},
  {name: "研究生办公室", phone: "0871-65931540", office: "软件学院楼A座1309室"},
  {name: "学工办公室", phone: "0871-65931551", office: "软件学院楼A座1107室"}
] AS offices
UNWIND offices AS office
CREATE (college)-[:HAS_OFFICE]->(:Office {
  name: office.name,
  phone: office.phone,
  office: office.office
});

// 6. 创建本科专业
MATCH (college:College {name: "软件学院"})
WITH college, [
  {name: "软件工程", level: "国家和省级卓越工程师培养计划"},
  {name: "数字媒体技术", level: "国家和省级卓越工程师培养计划"},
  {name: "网络空间安全", level: "国家级特色及卓越工程师培养计划"},
  {name: "人工智能", level: "2021年新增"}
] AS programs
UNWIND programs AS program
CREATE (college)-[:HAS_PROGRAM]->(:AcademicProgram {
  name: program.name,
  level: program.level,
  type: "本科"
});

// 7. 创建研究生专业
MATCH (college:College {name: "软件学院"})
WITH college, [
  {name: "软件工程", type: "学术型硕士"},
  {name: "网络空间安全", type: "学术型硕士"},
  {name: "软件工程", type: "专业硕士"}
] AS graduate_programs
UNWIND graduate_programs AS program
CREATE (college)-[:HAS_PROGRAM]->(:AcademicProgram {
  name: program.name,
  type: program.type
});

// 8. 创建科研基地
MATCH (college:College {name: "软件学院"})
WITH college, [
  "国家软件人才国际培训基地（昆明）",
  "国家Linux技术培训与推广中心",
  "中国信息安全产品测评认证中心云南测评中心",
  "国家软件人才培养改革创新实验区"
] AS centers
UNWIND centers AS center
CREATE (college)-[:HAS_RESEARCH_CENTER]->(:ResearchCenter {name: center});

// 9. 创建合作企业
MATCH (college:College {name: "软件学院"})
WITH college, [
  "IBM", "Intel", "华为", "甲骨文"
] AS partners
UNWIND partners AS partner
CREATE (college)-[:COLLABORATES_WITH]->(:Company {name: partner});

// 10. 创建发展目标
MATCH (college:College {name: "软件学院"})
WITH college, [
  "培养国际化、工程型人才",
  "推进协同育人、科研育人、实践育人和文化育人",
  "深化CDIO工程教育模式",
  "推行产学研一体化人才培养模式"
] AS goals
UNWIND goals AS goal
CREATE (college)-[:HAS_GOAL]->(:Goal {description: goal});
