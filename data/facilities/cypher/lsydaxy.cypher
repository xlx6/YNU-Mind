// 1. 创建学院主节点（关联东陆校区）并返回学院与校区关系
MATCH (dl:Campus {campus_id: "DL"})
CREATE (hac:College {
  name: "历史与档案学院",
  established: 2015,
  address: "东陆校区映秋院（203-213室）、文津楼、北学楼6楼",
  phone: "院长办公室 0871-65033280, 党委书记办公室 0871-65031162",
  website: "http://www.ha.ynu.edu.cn/index.htm"
})
CREATE (hac)-[:BELONGS_TO]->(dl);

// 2. 创建办公区节点并与学院建立关系
MATCH (hac:College {name: "历史与档案学院"})
WITH hac
UNWIND [
  {name: "映秋院主办公区", rooms: "203-213室", function: "行政办公"},
  {name: "文津楼", rooms: "中国经济史研究室", function: "科研"},
  {name: "北学楼6楼", rooms: "西南环境史研究所", function: "科研"}
] AS location
CREATE (hac)-[:HAS_LOCATION]->(:OfficeBuilding {
  name: location.name,
  rooms: location.rooms,
  function: location.function
});

// 3. 创建教学科研机构并与学院建立关系
MATCH (hac:College {name: "历史与档案学院"})
WITH hac
UNWIND [
  {name: "历史系", room: "映秋院212室", type: "教学系部"},
  {name: "档案与信息管理系", room: "映秋院213室", type: "教学系部"},
  {name: "中国经济史研究室", type: "科研平台", director: "李某某"},
  {name: "西南环境史研究所", type: "科研平台", director: "王某某"},
  {name: "地方史研究室", type: "科研平台", director: "张某某"}
] AS unit
CREATE (hac)-[:HAS_DEPARTMENT]->(:Department {
  name: unit.name,
  room: unit.room,
  type: unit.type,
  director: unit.director
});

// 4. 创建学科体系并与学院建立关系
MATCH (hac:College {name: "历史与档案学院"})
WITH hac
UNWIND [
  {name: "中国史", level: "国家级重点学科", type: "博士点", ranking: "全国前10%"},
  {name: "世界史", level: "省级重点学科", type: "硕士点"},
  {name: "档案学", level: "国家一流本科专业", type: "本科"},
  {name: "信息资源管理", level: "国家一流本科专业", type: "本科"}
] AS program
CREATE (hac)-[:HAS_PROGRAM]->(:AcademicProgram {
  name: program.name,
  level: program.level,
  type: program.type,
  ranking: program.ranking
});

// 5. 创建特色项目并与学院建立关系
CREATE (hac)-[:HAS_PROJECT]->(:SpecialProgram {
  name: "历史学拔尖试点班",
  type: "人才培养",
  partner: "复旦大学",
  model: "1+2+1联合培养"
});

// 6. 创建学术平台并与学院建立关系
MATCH (hac:College {name: "历史与档案学院"})
WITH hac
UNWIND [
  {name: "教育部虚拟教研室", type: "国家级", field: "数字人文"},
  {name: "云南省数字人文重点实验室", type: "省级", field: "文化遗产数字化"}
] AS platform
CREATE (hac)-[:HAS_PLATFORM]->(:ResearchPlatform {
  name: platform.name,
  type: platform.type,
  researchField: platform.field
});