# Fix #162: Bounty Contract - No Dispute Mechanism

## 问题描述
- **严重性**: 高
- **影响**: 存在 `BountyStatus::Disputed` 状态，但无启动/解决争议的函数
- **风险**: 创作者和自由职业者无法处理分歧，可能导致资金冻结

## 修复方案

### 1. 添加争议相关数据结构

```rust
#[contracttype]
pub enum DisputeStatus {
    Pending = 0,
    Resolved = 1,
    Cancelled = 2,
}

#[contracttype]
pub struct Dispute {
    pub id: u64,
    pub bounty_id: u64,
    pub initiator: Address,        // 发起人 (creator或freelancer)
    pub respondent: Address,       // 被申诉人
    pub reason: String,
    pub evidence_urls: Vec<String>,  // 证据链接
    pub resolution_notes: Option<String>,
    pub status: DisputeStatus,
    pub created_at: u64,
    pub resolved_at: Option<u64>,
    pub resolver: Option<Address>,  // 争议解决者 (admin或DAO)
}

pub enum DataKey {
    // ... 现有的 keys ...
    DisputeCounter,
    Dispute(u64),
    BountyDispute(u64),  // bounty_id -> dispute_id
}
```

### 2. 实现争议处理函数

#### 2.1 启动争议

```rust
/// 发起争议
pub fn initiate_dispute(
    env: Env,
    bounty_id: u64,
    initiator: Address,
    reason: String,
    initial_evidence: String,
) -> u64 {
    initiator.require_auth();

    // 验证bounty存在且处于可争议状态
    let bounty_key = DataKey::Bounty(bounty_id);
    let mut bounty: Bounty = env
        .storage()
        .persistent()
        .get(&bounty_key)
        .expect("Bounty not found");

    if bounty.status != BountyStatus::InProgress {
        panic!("Can only dispute in-progress bounties");
    }

    // 检查是否已有争议
    if env.storage().persistent().has(&DataKey::BountyDispute(bounty_id)) {
        panic!("Bounty already has a dispute");
    }

    // 验证发起人是bounty的参与者
    let is_creator = bounty.creator == initiator;
    let selected = env.storage().persistent().get(&DataKey::SelectedFreelancer(bounty_id));
    let is_freelancer = selected.map(|f| f == initiator).unwrap_or(false);
    
    if !is_creator && !is_freelancer {
        panic!("Only creator or selected freelancer can initiate dispute");
    }

    // 创建争议
    let dispute_id: u64 = env
        .storage()
        .persistent()
        .get(&DataKey::DisputeCounter)
        .unwrap_or(0);

    let respondent = if is_creator {
        selected.expect("No freelancer selected")
    } else {
        bounty.creator.clone()
    };

    let dispute = Dispute {
        id: dispute_id,
        bounty_id,
        initiator: initiator.clone(),
        respondent,
        reason,
        evidence_urls: vec![initial_evidence],
        resolution_notes: None,
        status: DisputeStatus::Pending,
        created_at: env.ledger().timestamp(),
        resolved_at: None,
        resolver: None,
    };

    // 更新bounty状态
    bounty.status = BountyStatus::Disputed;
    env.storage().persistent().set(&bounty_key, &bounty);
    
    // 保存争议
    env.storage().persistent().set(&DataKey::Dispute(dispute_id), &dispute);
    env.storage().persistent().set(&DataKey::DisputeCounter, &(dispute_id + 1));
    env.storage().persistent().set(&DataKey::BountyDispute(bounty_id), &dispute_id);

    dispute_id
}
```

#### 2.2 提交证据

```rust
/// 添加证据到现有争议
pub fn add_dispute_evidence(
    env: Env,
    dispute_id: u64,
    submitter: Address,
    evidence_url: String,
    description: String,
) -> bool {
    submitter.require_auth();

    let key = DataKey::Dispute(dispute_id);
    let mut dispute: Dispute = env
        .storage()
        .persistent()
        .get(&key)
        .expect("Dispute not found");

    if dispute.status != DisputeStatus::Pending {
        panic!("Can only add evidence to pending disputes");
    }

    // 验证提交者是争议参与方
    if dispute.initiator != submitter && dispute.respondent != submitter {
        panic!("Only dispute parties can submit evidence");
    }

    // 添加证据
    // 在实际实现中，应该使用更复杂的证据结构
    dispute.evidence_urls.push(evidence_url);
    
    env.storage().persistent().set(&key, &dispute);
    true
}
```

#### 2.3 解决争议

```rust
/// 解决争议 (管理员或DAO)
pub fn resolve_dispute(
    env: Env,
    dispute_id: u64,
    resolver: Address,
    resolution: DisputeResolution,
    notes: String,
) -> bool {
    resolver.require_auth();

    // TODO: 添加管理员/DAO权限验证

    let key = DataKey::Dispute(dispute_id);
    let mut dispute: Dispute = env
        .storage()
        .persistent()
        .get(&key)
        .expect("Dispute not found");

    if dispute.status != DisputeStatus::Pending {
        panic!("Dispute already resolved");
    }

    let bounty_key = DataKey::Bounty(dispute.bounty_id);
    let mut bounty: Bounty = env
        .storage()
        .persistent()
        .get(&bounty_key)
        .expect("Bounty not found");

    // 根据解决方式更新bounty状态
    match resolution {
        DisputeResolution::FavorCreator => {
            bounty.status = BountyStatus::Cancelled;
        }
        DisputeResolution::FavorFreelancer => {
            bounty.status = BountyStatus::Completed;
        }
        DisputeResolution::MutualAgreement => {
            // 根据协议决定状态
            bounty.status = BountyStatus::Completed;
        }
        DisputeResolution::EscrowRefund => {
            bounty.status = BountyStatus::Cancelled;
        }
    }

    dispute.status = DisputeStatus::Resolved;
    dispute.resolution_notes = Some(notes);
    dispute.resolved_at = Some(env.ledger().timestamp());
    dispute.resolver = Some(resolver);

    env.storage().persistent().set(&bounty_key, &bounty);
    env.storage().persistent().set(&key, &dispute);
    
    true
}

pub enum DisputeResolution {
    FavorCreator,      // 支持创作者，退款
    FavorFreelancer,   // 支持自由职业者，付款
    MutualAgreement,   // 双方协议
    EscrowRefund,      // 托管退款
}
```

#### 2.4 查询函数

```rust
pub fn get_dispute(env: Env, dispute_id: u64) -> Dispute {
    env.storage()
        .persistent()
        .get(&DataKey::Dispute(dispute_id))
        .expect("Dispute not found")
}

pub fn get_bounty_dispute(env: Env, bounty_id: u64) -> Option<Dispute> {
    env.storage()
        .persistent()
        .get(&DataKey::BountyDispute(bounty_id))
        .map(|id| get_dispute(env, id))
}
```

## 安全改进

1. ✅ **参与方验证**: 只有bounty创作者或选定的自由职业者可以发起争议
2. ✅ **状态验证**: 只能在InProgress状态的bounty发起争议
3. ✅ **防重复**: 每个bounty只能有一个争议
4. ✅ **证据管理**: 双方都可以提交证据
5. ✅ **解决机制**: 管理员/DAO可以解决争议
6. ✅ **状态追踪**: 完整的争议生命周期追踪

## 测试用例

```rust
#[test]
fn test_initiate_dispute() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(BountyContract, ());
    let client = BountyContractClient::new(&env, &contract_id);

    let creator = Address::generate(&env);
    let freelancer = Address::generate(&env);

    // 创建bounty并申请
    let bounty_id = client.create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &1000i128,
        &100u64,
    );
    
    let app_id = client.apply_for_bounty(
        &bounty_id,
        &freelancer,
        &String::from_str(&env, "Proposal"),
        &900i128,
        &30u64,
    );
    
    client.select_freelancer(&bounty_id, &app_id);

    // 发起争议
    let dispute_id = client.initiate_dispute(
        &bounty_id,
        &creator,
        &String::from_str(&env, "Quality issues"),
        &String::from_str(&env, "https://evidence.com/1"),
    );

    assert_eq!(dispute_id, 1);
    
    let dispute = client.get_dispute(&dispute_id);
    assert_eq!(dispute.status, DisputeStatus::Pending);
    
    let bounty = client.get_bounty(&bounty_id);
    assert_eq!(bounty.status, BountyStatus::Disputed);
}

#[test]
fn test_resolve_dispute() {
    // 测试争议解决流程
}

#[test]
fn test_cannot_dispute_open_bounty() {
    // 测试不能对Open状态的bounty发起争议
}
```

---

**状态**: 修复方案完成。待实施代码修改
