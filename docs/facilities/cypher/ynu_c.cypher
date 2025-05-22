// 1. 创建大学主节点
CREATE (ynu:University {
  university_id: "YNU",
  name: "云南大学",
  established_year: 1922,
  motto: "自尊 致知 正义 力行",
  spirit: "会泽百家，至公天下",
  colleges: 29,
  research_institutes: 8,
  affiliated_hospital: 1,
  affiliated_high_school: 1,
  undergraduates: 18000,
  postgraduates: 19000,
  international_students: 1000,
  total_faculty: 3500,
  doctoral_programs: 22,
  master_programs: 43,
  phone: "0871-65031141",
  email: "ynu@ynu.edu.cn",
  website: "https://www.ynu.edu.cn"
})
RETURN ynu;

// 2. 添加校区节点
MATCH (u:University {university_id: "YNU"})
WITH u, [
  {campus_id: "CG", name: "呈贡校区", address: "昆明市呈贡区大学城东外环南路", area_size: "4016亩"},
  {campus_id: "DL", name: "东陆校区", address: "昆明市五华区翠湖北路2号", area_size: "351亩"}
] AS campuses
UNWIND campuses AS campus
CREATE (c:Campus {
  campus_id: campus.campus_id,
  name: campus.name,
  address: campus.address,
  area_size: campus.area_size
})-[:BELONGS_TO]->(u);

// 3. 添加关键成就
MATCH (u:University {university_id: "YNU"})
WITH u, [
  "中国首批42所‘双一流’建设高校",
  "国家‘211工程’重点建设大学",
  "民族学、生态学学科全国前7%"
] AS achievements
UNWIND achievements AS achievement
CREATE (u)-[:HAS_ACHIEVEMENT]->(:Achievement {description: achievement});

// 4. 添加重点学科
MATCH (u:University {university_id: "YNU"})
WITH u, ["民族学", "生态学", "统计学", "生物与生物医药", "边疆问题和区域国别研究"] AS disciplines
UNWIND disciplines AS discipline
CREATE (u)-[:HAS_KEY_DISCIPLINE]->(:Discipline {name: discipline});

// 5. 添加排名信息
WITH [
  {name: "211工程", is_member: true},
  {name: "双一流", is_member: true},
  {name: "软科", rank: 70},
  {name: "USNews", rank: 822},
  {name: "校友会", rank: 90}
] AS rankings
UNWIND rankings AS ranking
CREATE (r:Ranking {
  name: ranking.name,
  is_member: COALESCE(ranking.is_member, false),
  rank: ranking.rank
});

// 关联大学与排名
MATCH (u:University {university_id: "YNU"}), (r:Ranking)
WHERE r.name IN ["211工程", "双一流", "软科", "USNews", "校友会"]
CREATE (u)-[:HAS_RANKING]->(r);

// 6. 添加历史里程碑
MATCH (u:University {university_id: "YNU"})
WITH u, [
  {year: 1922, event: "建校，初名私立东陆大学"},
  {year: 1934, event: "更名为省立云南大学"},
  {year: 1938, event: "改为国立云南大学"},
  {year: 1946, event: "被《不列颠百科全书》列为中国15所在世界最具影响的大学之一"},
  {year: 1978, event: "被国务院确定为全国88所重点大学之一"},
  {year: 1996, event: "首批列入国家‘211工程’重点建设大学"},
  {year: 2017, event: "入选国家首批42所‘双一流’建设高校"},
  {year: 2023, event: "习近平总书记致信祝贺云南大学建校100周年"}
] AS milestones
UNWIND milestones AS milestone
CREATE (u)-[:HAS_MILESTONE]->(:Milestone {year: milestone.year, event: milestone.event});

// 7. 添加教职工与领导层
MATCH (u:University {university_id: "YNU"})
CREATE (:Person:Faculty {name: "熊庆来", role: "著名数学家、教育家，曾任校长"})-[:WORKED_AT]->(u);

WITH [
  {name: "张亚平", position: "名誉校长"},
  {name: "周学斌", position: "党委书记"},
  {name: "马文会", position: "校长"},
  {name: "陈克清", position: "副校长"},
  {name: "廖炼忠", position: "副校长"},
  {name: "吴涧", position: "副校长"},
  {name: "段兴武", position: "副校长"},
  {name: "唐年胜", position: "副校长"},
  {name: "杨绍军", position: "副校长"}
] AS leaders
UNWIND leaders AS leader
CREATE (l:Person:Leader {
  name: leader.name,
  position: leader.position
});

// 关联领导层到大学
MATCH (u:University {university_id: "YNU"}), (l:Person:Leader)
CREATE (l)-[:SERVES_AS]->(u);

// 8. 添加学术资源
MATCH (u:University {university_id: "YNU"})
CREATE (lib:Library {
  collection: "445万册",
  equipment_value: "20亿元"
})
CREATE (u)-[:HAS_LIBRARY]->(lib);
