```javascript
import fs from 'fs';
import path from 'path';

export default function createFactsModule(dataDir) {
  const factsPath = path.join(dataDir, 'facts.json');
  let facts = [];

  // 读取初始数据
  if (fs.existsSync(factsPath)) {
    facts = JSON.parse(fs.readFileSync(factsPath, 'utf8'));
  }

  // 写入一条事实
  function addFact({ s, p, o, prov }) {
    if (!prov) return null;
    const fact = { s, p, o, prov, hits: 1, disputed: false };
    facts.push(fact);
    saveFacts();
    return fact;
  }

  // 按 (s,p,o) 去重合并，重复的只增加 hits
  function mergeFacts(items) {
    items.forEach(item => {
      const existing = facts.find(f => f.s === item.s && f.p === item.p && f.o === item.o);
      if (existing) {
        existing.hits++;
        existing.disputed = true;
      } else {
        facts.push({ ...item, hits: 1, disputed: false });
      }
    });
    saveFacts();
  }

  // 查询
  function queryFacts({ p, s, limit }) {
    return facts
      .filter(f => (!p || f.p === p) && (!s || f.s === s))
      .sort((a, b) => b.hits - a.hits)
      .slice(0, limit);
  }

  // 用正则从 episode 文本里抽取事实，返回数组
  function ruleFacts(episodes) {
    const facts = [];
    episodes.forEach(episode => {
      const matches = episode.match(/(\w+)\.(\w+)\(([^)]+)\)/g);
      if (matches) {
        matches.forEach(match => {
          const [_, s, p, o] = match.match(/(\w+)\.(\w+)\(([^)]+)\)/);
          facts.push({ s, p, o, prov: episode });
        });
      }
    });
    return facts;
  }

  // 获取所有事实
  function allFacts() {
    return facts;
  }

  // 保存事实到文件
  function saveFacts() {
    fs.writeFileSync(factsPath, JSON.stringify(facts, null, 2));
  }

  return {
    addFact,
    mergeFacts,
    queryFacts,
    ruleFacts,
    allFacts,
  };
}
```