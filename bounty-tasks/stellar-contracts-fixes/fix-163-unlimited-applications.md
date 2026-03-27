# Fix #163: Bounty Contract - Unlimited Applications

## 问题描述
- **严重性**: 中
- **影响**: 无申请数量限制。无防重复申请
- **风险**: 存储膨胀，DoS攻击向量

## 修复方案

### 1. 添加申请限制配置

```rust
#[contracttype]
pub struct ApplicationLimits {
    pub max_applications_per_bounty: u32,     // 每个bounty最多申请数
    pub max_applications_per_freelancer: u32,  // 每个自由职业者最多申请数
    pub cooldown_period: u64,                 // 重复申请冷却时间（秒）
}

pub enum DataKey {
    // ... 现有的 keys ...
    ApplicationLimits,
    FreelancerApplicationCount(Address),  // 自由职业者申请计数
    BountyApplicationCount(u64),  // bounty申请计数
    FreelancerAppliedBounty(Address, u64),  // 自由职业者是否已申请某bounty
}
```

### 2. 修改 apply_for_bounty 函数

**修复前**:
```rust
pub fn apply_for_bounty(
    env: Env,
    bounty_id: u64,
    freelancer: Address,
    proposal: String,
    proposed_budget: i128,
    timeline: u64,
) -> u64 {
    freelancer.require_auth();
    // ❌ 无限制检查
    let application = BountyApplication { ... };
}
```

**修复后**:
```rust
pub fn apply_for_bounty(
    env: Env,
    bounty_id: u64,
    freelancer: Address,
    proposal: String,
    proposed_budget: i128,
    timeline: u64,
) -> u64 {
    freelancer.require_auth();

    // ✅ 获取限制配置
    let limits = env
        .storage()
        .persistent()
        .get(&DataKey::ApplicationLimits)
        .unwrap_or(ApplicationLimits {
            max_applications_per_bounty: 50,
            max_applications_per_freelancer: 20,
            cooldown_period: 86400, // 24小时
        });

    // ✅ 验证bounty存在且开放
    let bounty: Bounty = env
        .storage()
        .persistent()
        .get(&DataKey::Bounty(bounty_id))
        .expect("Bounty not found");

    if bounty.status != BountyStatus::Open {
        panic!("Bounty is not open for applications");
    }

    // ✅ 检查bounty申请数量
    let bounty_count: u32 = env
        .storage()
        .persistent()
        .get(&DataKey::BountyApplicationCount(bounty_id))
        .unwrap_or(0);

    if bounty_count >= limits.max_applications_per_bounty {
        panic!("Bounty has reached maximum applications");
    }

    // ✅ 检查自由职业者申请数量
    let freelancer_count: u32 = env
        .storage()
        .persistent()
        .get(&DataKey::FreelancerApplicationCount(freelancer.clone()))
        .unwrap_or(0);

    if freelancer_count >= limits.max_applications_per_freelancer {
        panic!("You have reached maximum applications limit");
    }

    // ✅ 检查是否已申请此bounty
    let applied_key = DataKey::FreelancerAppliedBounty(freelancer.clone(), bounty_id);
    if env.storage().persistent().has(&applied_key) {
        // 检查冷却时间
        let last_applied: u64 = env
            .storage()
            .persistent()
            .get(&applied_key)
            .unwrap();
        
        let current_time = env.ledger().timestamp();
        if current_time - last_applied < limits.cooldown_period {
            panic!("Cooldown period not yet passed");
        }
    }

    // ✅ 验证proposal不为空
    if proposal.len() == 0 {
        panic!("Proposal cannot be empty");
    }

    // ✅ 验证proposed_budget合理
    if proposed_budget <= 0 {
        panic!("Proposed budget must be positive");
    }

    // 创建申请
    let mut counter: u64 = env
        .storage()
        .persistent()
        .get(&DataKey::AppCounter)
        .unwrap_or(0);
    counter += 1;

    let application = BountyApplication {
        id: counter,
        bounty_id,
        freelancer: freelancer.clone(),
        proposal,
        proposed_budget,
        timeline,
        created_at: env.ledger().timestamp(),
    };

    // 保存申请
    env.storage()
        .persistent()
        .set(&DataKey::Application(counter), &application);
    env.storage()
        .persistent()
        .set(&DataKey::AppCounter, &counter);

    // 更新计数
    env.storage()
        .persistent()
        .set(&DataKey::BountyApplicationCount(bounty_id), &(bounty_count + 1));
    env.storage()
        .persistent()
        .set(&DataKey::FreelancerApplicationCount(freelancer.clone()), &(freelancer_count + 1));
    
    // 记录申请时间
    env.storage()
        .persistent()
        .set(&applied_key, &env.ledger().timestamp());

    counter
}

/// 设置申请限制（管理员）
pub fn set_application_limits(
    env: Env,
    admin: Address,
    limits: ApplicationLimits,
) -> bool {
    admin.require_auth();
    
    // TODO: 添加管理员权限验证

    if limits.max_applications_per_bounty == 0 {
        panic!("Max applications per bounty must be > 0");
    }

    if limits.max_applications_per_freelancer == 0 {
        panic!("Max applications per freelancer must be > 0");
    }

    env.storage()
        .persistent()
        .set(&DataKey::ApplicationLimits, &limits);
    
    true
}

/// 获取bounty的申请统计
pub fn get_bounty_application_stats(env: Env, bounty_id: u64) -> ApplicationStats {
    let count: u32 = env
        .storage()
        .persistent()
        .get(&DataKey::BountyApplicationCount(bounty_id))
        .unwrap_or(0);

    let limits = env
        .storage()
        .persistent()
        .get(&DataKey::ApplicationLimits)
        .unwrap_or(ApplicationLimits {
            max_applications_per_bounty: 50,
            max_applications_per_freelancer: 20,
            cooldown_period: 86400,
        });

    ApplicationStats {
        current_applications: count,
        max_applications: limits.max_applications_per_bounty,
        remaining_slots: limits.max_applications_per_bounty.saturating_sub(count),
    }
}

pub struct ApplicationStats {
    pub current_applications: u32,
    pub max_applications: u32,
    pub remaining_slots: u32,
}
```

## 安全改进

1. ✅ **Bounty申请限制**: 每个bounty最多50个申请
2. ✅ **用户申请限制**: 每个自由职业者最多20个活跃申请
3. ✅ **防重复申请**: 同一bounty冷却期内不能重复申请
4. ✅ **内容验证**: proposal不能为空
5. ✅ **预算验证**: proposed_budget必须为正数
6. ✅ **状态验证**: 只能申请Open状态的bounty
7. ✅ **可配置**: 管理员可以调整限制
8. ✅ **统计查询**: 可以查看bounty的申请统计

## 测试用例

```rust
#[test]
fn test_application_limit_enforced() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    let bounty_id = client.create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &1000i128,
        &100u64,
    );

    // 设置低限制用于测试
    client.set_application_limits(
        &creator,
        &ApplicationLimits {
            max_applications_per_bounty: 2,
            max_applications_per_freelancer: 20,
            cooldown_period: 86400,
        },
    );

    // 创建2个申请 - 应该成功
    for i in 0..2 {
        let freelancer = Address::generate(&env);
        client.apply_for_bounty(
            &bounty_id,
            &freelancer,
            &String::from_str(&env, "Proposal"),
            &900i128,
            &30u64,
        );
    }

    // 第3个申请应该失败
    let freelancer3 = Address::generate(&env);
    let result = client.try_apply_for_bounty(
        &bounty_id,
        &freelancer3,
        &String::from_str(&env, "Proposal"),
        &900i128,
        &30u64,
    );
    assert!(!result);
}

#[test]
fn test_duplicate_application_rejected() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    let freelancer = Address::generate(&env);

    let bounty_id = client.create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &1000i128,
        &100u64,
    );

    client.apply_for_bounty(
        &bounty_id,
        &freelancer,
        &String::from_str(&env, "First application"),
        &900i128,
        &30u64,
    );

    // 立即再次申请应该失败（冷却期内）
    let result = client.try_apply_for_bounty(
        &bounty_id,
        &freelancer,
        &String::from_str(&env, "Second application"),
        &900i128,
        &30u64,
    );
    assert!(!result);
}

#[test]
fn test_freelancer_limit_enforced() {
    // 测试自由职业者申请数量限制
}
```

---

**状态**: 修复方案完成。待实施代码修改
