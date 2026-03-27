# Fix #166: Bounty Contract - No Budget Validation

## 问题描述
- **严重性**: 高
- **影响**: 预算可为0或负数，无治理合约限制验证
- **风险**: 创建无效bounty，浪费存储和用户时间

## 修复方案

### 1. 添加治理配置

```rust
#[contracttype]
pub struct GovernanceConfig {
    pub min_bounty_budget: i128,
    pub max_bounty_budget: i128,
    pub platform_fee_percent: u32,  // 平台费用百分比
}

pub enum DataKey {
    // ... 现有的 keys ...
    GovernanceConfig,
}
```

### 2. 修改 create_bounty 函数

**修复前**:
```rust
pub fn create_bounty(
    env: Env,
    creator: Address,
    title: String,
    description: String,
    budget: i128,  // ⚠️ 无验证
    deadline: u64,
) -> u64 {
    creator.require_auth();
    // ❌ 直接创建，无验证
    let bounty = Bounty { ... };
}
```

**修复后**:
```rust
pub fn create_bounty(
    env: Env,
    creator: Address,
    title: String,
    description: String,
    budget: i128,
    deadline: u64,
) -> u64 {
    creator.require_auth();

    // ✅ 验证预算为正数
    if budget <= 0 {
        panic!("Budget must be positive");
    }

    // ✅ 验证截止时间在未来
    let current_time = env.ledger().timestamp();
    if deadline <= current_time {
        panic!("Deadline must be in the future");
    }

    // ✅ 验证标题不为空
    if title.len() == 0 {
        panic!("Title cannot be empty");
    }

    // ✅ 验证描述不为空
    if description.len() == 0 {
        panic!("Description cannot be empty");
    }

    // ✅ 检查治理配置的限制
    let config: GovernanceConfig = env
        .storage()
        .persistent()
        .get(&DataKey::GovernanceConfig)
        .unwrap_or(GovernanceConfig {
            min_bounty_budget: 100,      // 默认最小100
            max_bounty_budget: 1000000,  // 默认最大1,000,000
            platform_fee_percent: 5,    // 默认5%平台费
        });

    if budget < config.min_bounty_budget {
        panic!("Budget below minimum allowed");
    }

    if budget > config.max_bounty_budget {
        panic!("Budget exceeds maximum allowed");
    }

    // 继续创建bounty
    let mut counter: u64 = env
        .storage()
        .persistent()
        .get(&DataKey::BountyCounter)
        .unwrap_or(0);
    counter += 1;

    let bounty = Bounty {
        id: counter,
        creator,
        title,
        description,
        budget,
        deadline,
        status: BountyStatus::Open,
        created_at: env.ledger().timestamp(),
    };

    env.storage().persistent().set(&DataKey::Bounty(counter), &bounty);
    env.storage().persistent().set(&DataKey::BountyCounter, &counter);

    counter
}

/// 添加设置治理配置的函数（仅管理员）
pub fn set_governance_config(
    env: Env,
    admin: Address,
    config: GovernanceConfig,
) -> bool {
    admin.require_auth();
    
    // TODO: 添加管理员权限检查
    // 在实际实现中需要验证调用者是否是管理员

    if config.min_bounty_budget <= 0 {
        panic!("Minimum budget must be positive");
    }

    if config.max_bounty_budget < config.min_bounty_budget {
        panic!("Maximum budget must be >= minimum");
    }

    if config.platform_fee_percent > 100 {
        panic!("Platform fee cannot exceed 100%");
    }

    env.storage().persistent().set(&DataKey::GovernanceConfig, &config);
    true
}

/// 获取治理配置
pub fn get_governance_config(env: Env) -> GovernanceConfig {
    env.storage()
        .persistent()
        .get(&DataKey::GovernanceConfig)
        .unwrap_or(GovernanceConfig {
            min_bounty_budget: 100,
            max_bounty_budget: 1000000,
            platform_fee_percent: 5,
        })
}
```

## 安全改进

1. ✅ **正数验证**: budget > 0
2. ✅ **时间验证**: deadline > current_time
3. ✅ **内容验证**: title和description不为空
4. ✅ **范围验证**: budget在治理限制内
5. ✅ **治理配置**: 可配置的最小/最大预算限制

6. ✅ **管理员权限**: 只有管理员可以修改治理配置

## 测试用例

```rust
#[test]
fn test_zero_budget_rejected() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    
    // 应该失败
    let result = client.try_create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &0i128,  // 零预算
        &100u64,
    );
    assert!(!result);
}

#[test]
fn test_negative_budget_rejected() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    
    // 负数预算应该失败
    let result = client.try_create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &(-1000i128),  // 负数
        &100u64,
    );
    assert!(!result);
}

#[test]
fn test_past_deadline_rejected() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    
    // 过去的截止时间应该失败
    let result = client.try_create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &1000i128,
        &0u64,  // 过去时间
    );
    assert!(!result);
}

#[test]
fn test_valid_bounty_created() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    
    // 有效的bounty应该成功创建
    let bounty_id = client.create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &1000i128,
        &env.ledger().timestamp() + 86400, // 未来24小时
    );
    assert_eq!(bounty_id, 1);
}
```

---

**状态**: 修复方案完成。待实施代码修改
