// 1. 创建学院节点并关联校区
MATCH (dlCampus:Campus {campus_id: "DL"})  // 东陆校区
CREATE (liberalCollege:College {
  name: "云南大学文学院",
  address: "云南省昆明市五华区翠湖北路2号",
  website: "http://www.wxy.ynu.edu.cn"
})
CREATE (liberalCollege)-[:BELONGS_TO]->(dlCampus);

// 2. 创建组织机构
CREATE (partyCommittee:OrganizationUnit {
  name: "文学院党委",
  type: "党委"
})-[:PART_OF]->(liberalCollege),
(disciplineCommittee:OrganizationUnit {
  name: "文学院纪委",
  type: "纪委"
})-[:PART_OF]->(liberalCollege),
(adminCommittee:OrganizationUnit {
  name: "文学院行政机构",
  type: "行政"
})-[:PART_OF]->(liberalCollege);

// 3. 创建领导节点体系
WITH liberalCollege, partyCommittee, disciplineCommittee, adminCommittee
UNWIND [
  // 党委系统
  {name: "赵永忠", positions: ["党委书记", "党委委员"], unit: partyCommittee},
  {name: "何丹娜", positions: ["党委副书记", "纪委书记", "党委委员", "纪委委员"], unit: partyCommittee},
  {name: "舒凌鸿", positions: ["党委委员"], unit: partyCommittee},
  {name: "黄瑞琪", positions: ["党委委员"], unit: partyCommittee},
  
  // 行政系统
  {name: "孙兴义", positions: ["主持工作副院长", "纪委委员"], unit: adminCommittee},
  {name: "张多", positions: ["副院长"], unit: adminCommittee},
  {name: "卢云燕", positions: ["纪委委员"], unit: adminCommittee}
] AS leader
CREATE (p:Person {
  name: leader.name,
  positions: leader.positions
})
// 建立多重关系
FOREACH (pos IN leader.positions | 
  CREATE (p)-[:HAS_POSITION {role: pos}]->(liberalCollege)
)
CREATE (p)-[:BELONGS_TO]->(leader.unit);

// 4. 特殊角色关系
// 纪委隶属党委
MATCH (dc:OrganizationUnit {name:"文学院纪委"})
MATCH (pc:OrganizationUnit {name:"文学院党委"})
CREATE (dc)-[:UNDER]->(pc);