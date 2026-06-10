# Plan: 技能后攻击 CD 统一到 UnitDefinition 配置

## 改动清单

### 1. UnitDefinition.cs — 新增字段
- `[SerializeField] private float postSkillAttackCd = -1f;`
- Tooltip: "技能结束后攻击 CD（秒），-1 = 使用 AtkInterval"
- 属性: `public float PostSkillAttackCd => postSkillAttackCd;`

### 2. UnitDefinitionEditor.cs — Inspector
- Landing「时序 / Timing」区域加 `Prop("postSkillAttackCd")`

### 3. LandingActionBase.cs — 统一 CD
- `StartAttackCooldown()` 改读 `unit.Definition.PostSkillAttackCd`（-1 时回退 AtkInterval）
- `Finish()` 内加 `StartAttackCooldown()` 调用

### 4. 删除 10 个子类的重复 StartAttackCooldown() 调用
- ChargeStunAction.cs
- RapidVolleyAction.cs
- MultiFireballAction.cs
- AreaStunAction.cs
- KnockupStunAction.cs
- InvincibleSlashAction.cs
- MineRushAction.cs
- TwoBounceAction.cs
- BarrelRollAction.cs
- TauntMarkerAction.cs

## 默认值策略
- `postSkillAttackCd = -1`：-1 表示"未配置，使用 AtkInterval"
- 旧 .asset 无需迁移，行为不变

## Validation
- build-local: 编译通过即可
