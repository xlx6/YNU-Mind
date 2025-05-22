// 0. 获取呈贡校区节点
MATCH (campus:Campus {campus_id: "CG"})

// 1. 创建学院主节点并关联校区
CREATE (college:College {
  name: "信息学院",
  established: "1998年4月（2015年12月合并云南省电子计算中心）",
  philosophy: "以人为本、教书育人，求是务实、博学创新",
  website: "http://www.ise.ynu.edu.cn/"
})-[:BELONGS_TO]->(campus)
RETURN college;

// 2. 添加领导团队
MATCH (college:College {name: "信息学院"})
WITH college, [
  {position: "党委书记", name: "赵征鹏", role: "全面负责党委工作"},
  {position: "党委副书记", name: "谭明川", role: "负责学生工作"},
  {position: "院长", name: "张学杰", role: "全面负责行政工作"},
  {position: "副院长", name: "岳昆", role: "科研、学科建设"},
  {position: "副院长", name: "普园媛", role: "本科生教学、教学实验室管理"},
  {position: "副院长", name: "聂仁灿", role: "双一流项目建设、资产管理、外事及安全稳定"},
  {position: "副院长", name: "王津", role: "研究生培养及学位点建设"}
] AS leaders
UNWIND leaders AS leader
CREATE (p:Person:Leader {
  name: leader.name,
  position: leader.position,
  responsibility: leader.role
})-[:HOLDS_POSITION]->(college);

// 3. 构建教学科研体系
MATCH (college:College {name: "信息学院"})
WITH college, [
  "计算机科学与工程系", "通信工程系", "信息与电子工程系", "物联网工程系",
  "智能科学与技术系", "实验中心", "公共计算机教学部", "高性能计算中心"
] AS departments
UNWIND departments AS dept
CREATE (college)-[:HAS_DEPARTMENT]->(:Department {name: dept});

// 科研平台
MATCH (college:College {name: "信息学院"})
WITH college, [
  {name: "云南省发改委工程实验室", level: "省级"},
  {name: "5个云南省高校重点实验室", level: "省级"},
  {name: "2个昆明市重点实验室", level: "市级"}
] AS platforms
UNWIND platforms AS p
CREATE (college)-[:HAS_PLATFORM]->(:Platform {name: p.name, level: p.level});

// 4. 专业设置
MATCH (college:College {name: "信息学院"})
WITH college, [
  {name: "计算机科学与技术", level: "国家级特色专业+国家级一流本科专业"},
  {name: "通信工程", level: "国家级一流本科专业"},
  {name: "电子信息工程"},
  {name: "物联网工程"},
  {name: "智能科学与技术"}
] AS programs
UNWIND programs AS program
CREATE (college)-[:HAS_PROGRAM]->(:AcademicProgram {
  name: program.name,
  level: COALESCE(program.level, "未标明"),
  type: "本科"
});

// 研究生培养
MATCH (college:College {name: "信息学院"})
WITH college, ["信息与通信工程", "计算机科学与技术"] AS phd_programs
UNWIND phd_programs AS phd
CREATE (college)-[:HAS_PROGRAM]->(:AcademicProgram {name: phd, type: "博士点"});

MATCH (college:College {name: "信息学院"})
WITH college, ["计算机科学与技术", "信息与通信工程", "生物医学工程", "控制科学与工程"] AS master_programs
UNWIND master_programs AS master
CREATE (college)-[:HAS_PROGRAM]->(:AcademicProgram {name: master, type: "硕士点"});

// 5. 科研成果
MATCH (college:College {name: "信息学院"})
CREATE (research:ResearchAchievement {
  projects_total: 200,
  nsfc_projects: 60,
  funding: 6800,
  awards: ["教育部自然科学奖", "吴文俊人工智能奖等10余项"],
  papers: 600,
  patents: 60,
  monographs: 30
})
CREATE (college)-[:HAS_ACHIEVEMENT]->(research);

// 6. 合作交流
MATCH (college:College {name: "信息学院"})
WITH college, ["华为", "腾讯", "中兴等共建联合实验室"] AS partners
UNWIND partners AS partner
CREATE (college)-[:COLLABORATES_WITH]->(:Collaboration {name: partner, type: "校企合作"});

MATCH (college:College {name: "信息学院"})
CREATE (defense:Collaboration {
  name: "国防人才培养",
  details: "培养500余名武警国防生",
  type: "国防建设"
})
CREATE (college)-[:COOPERATES_WITH]->(defense);

// 7. 发展目标
MATCH (college:College {name: "信息学院"})
WITH college, [
  "西部一流的信息技术人才培养基地",
  "产学研融合高地",
  "边疆信息技术转化桥头堡"
] AS goals
UNWIND goals AS goal
CREATE (college)-[:HAS_GOAL]->(:Goal {description: goal});
