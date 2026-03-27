# Fix #161: Payment Integration Missing

## Problem Analysis

**Severity**: Critical
**Impact**: Bounty system is non-functional - no funds are locked or released
**Root Cause**: Bounty contract doesn't integrate with escrow contract

### Current Issues

1. **create_bounty()**: Only creates bounty record, no fund locking
2. **complete_bounty()**: Only updates status, no fund release
3. **cancel_bounty()**: Only updates status, no refund
4. **Bounty struct**: Missing escrow_id field

## Solution Design

### 1. Data Structure Changes

```rust
#[contracttype]
pub struct Bounty {
    pub id: u64,
    pub creator: Address,
    pub title: String,
    pub description: String,
    pub budget: i128,
    pub deadline: u64,
    pub status: BountyStatus,
    pub created_at: u64,
    pub escrow_id: u64,        // NEW: Link to escrow account
    pub token: Address,         // NEW: Payment token address
}
```

### 2. Function Modifications

#### create_bounty()
```rust
pub fn create_bounty(
    env: Env,
    creator: Address,
    title: String,
    description: String,
    budget: i128,
    deadline: u64,
    token: Address,              // NEW: Token address parameter
    escrow_contract: Address,    // NEW: Escrow contract address
) -> u64 {
    creator.require_auth();
    assert!(budget > 0, "Budget must be positive");

    // Create escrow account FIRST to lock funds
    let escrow_client = EscrowContractClient::new(&env, &escrow_contract);
    let escrow_id = escrow_client.deposit(
        &creator,
        &creator,  // Temporary payee (will be updated when freelancer selected)
        &budget,
        &token,
        &ReleaseCondition::OnCompletion,
    );

    // Then create bounty record
    let mut counter: u64 = env
        .storage()
        .persistent()
        .get(&DataKey::BountyCounter)
        .unwrap_or(0);
    counter += 1;

    let bounty = Bounty {
        id: counter,
        creator: creator.clone(),
        title,
        description,
        budget,
        deadline,
        status: BountyStatus::Open,
        created_at: env.ledger().timestamp(),
        escrow_id,       // Store escrow ID
        token,           // Store token address
    };

    env.storage()
        .persistent()
        .set(&DataKey::Bounty(counter), &bounty);
    env.storage()
        .persistent()
        .set(&DataKey::BountyCounter, &counter);

    counter
}
```

#### select_freelancer()
```rust
pub fn select_freelancer(
    env: Env,
    bounty_id: u64,
    application_id: u64,
    escrow_contract: Address,    // NEW: Escrow contract address
) -> bool {
    let mut bounty: Bounty = env
        .storage()
        .persistent()
        .get(&DataKey::Bounty(bounty_id))
        .expect("Bounty not found");

    bounty.creator.require_auth();

    let application: BountyApplication = env
        .storage()
        .persistent()
        .get(&DataKey::Application(application_id))
        .expect("Application not found");

    assert!(
        application.bounty_id == bounty_id,
        "Application does not match bounty"
    );

    // Update escrow payee to selected freelancer
    let escrow_client = EscrowContractClient::new(&env, &escrow_contract);
    escrow_client.update_payee(&bounty.escrow_id, &application.freelancer);

    env.storage().persistent().set(
        &DataKey::SelectedFreelancer(bounty_id),
        &application.freelancer,
    );

    bounty.status = BountyStatus::InProgress;
    env.storage()
        .persistent()
        .set(&DataKey::Bounty(bounty_id), &bounty);

    true
}
```

#### complete_bounty()
```rust
pub fn complete_bounty(
    env: Env,
    bounty_id: u64,
    escrow_contract: Address,    // NEW: Escrow contract address
) -> bool {
    let mut bounty: Bounty = env
        .storage()
        .persistent()
        .get(&DataKey::Bounty(bounty_id))
        .expect("Bounty not found");

    bounty.creator.require_auth();
    assert!(
        bounty.status == BountyStatus::PendingCompletion,
        "Bounty not pending completion"
    );

    // Release funds to freelancer
    let escrow_client = EscrowContractClient::new(&env, &escrow_contract);
    escrow_client.release_funds(&bounty.escrow_id, &bounty.creator);

    bounty.status = BountyStatus::Completed;
    env.storage()
        .persistent()
        .set(&DataKey::Bounty(bounty_id), &bounty);

    true
}
```

#### cancel_bounty()
```rust
pub fn cancel_bounty(
    env: Env,
    bounty_id: u64,
    escrow_contract: Address,    // NEW: Escrow contract address
) -> bool {
    let mut bounty: Bounty = env
        .storage()
        .persistent()
        .get(&DataKey::Bounty(bounty_id))
        .expect("Bounty not found");

    bounty.creator.require_auth();
    assert!(
        bounty.status == BountyStatus::Open,
        "Only open bounties can be cancelled"
    );

    // Refund to creator
    let escrow_client = EscrowContractClient::new(&env, &escrow_contract);
    escrow_client.refund_escrow(&bounty.escrow_id);

    bounty.status = BountyStatus::Cancelled;
    env.storage()
        .persistent()
        .set(&DataKey::Bounty(bounty_id), &bounty);

    true
}
```

### 3. Required Escrow Contract Addition

The escrow contract needs a new function to update payee:

```rust
// Add to escrow/src/lib.rs
pub fn update_payee(env: Env, escrow_id: u64, new_payee: Address) -> bool {
    let mut escrow: EscrowAccount = env
        .storage()
        .persistent()
        .get(&DataKey::Escrow(escrow_id))
        .expect("Escrow not found");

    escrow.payer.require_auth();
    assert!(escrow.status == EscrowStatus::Active, "Escrow not active");

    escrow.payee = new_payee;
    env.storage()
        .persistent()
        .set(&DataKey::Escrow(escrow_id), &escrow);

    true
}
```

## Implementation Steps

1. **Phase 1: Update Bounty Struct**
   - Add `escrow_id` and `token` fields
   - Update all Bounty struct instantiations

2. **Phase 2: Add Escrow Integration**
   - Import EscrowContractClient
   - Modify create_bounty to call escrow.deposit()
   - Modify select_freelancer to call escrow.update_payee()
   - Modify complete_bounty to call escrow.release_funds()
   - Modify cancel_bounty to call escrow.refund_escrow()

3. **Phase 3: Update Escrow Contract**
   - Add update_payee() function
   - Add tests for payee update

4. **Phase 4: Testing**
   - Test full payment flow: create → select → complete → release
   - Test refund flow: create → cancel → refund
   - Test error cases: insufficient balance, unauthorized calls

## Security Considerations

1. **Reentrancy**: Not applicable in Soroban (no external calls during storage)
2. **Authorization**: All escrow calls require proper auth checks
3. **Fund Safety**: Funds locked in escrow until explicitly released/refunded
4. **Atomicity**: If bounty creation fails, escrow deposit reverts automatically

## Gas Optimization

1. **Lazy Loading**: Load escrow contract only when needed
2. **Storage**: Store escrow_id (u64) instead of full escrow data
3. **Client Reuse**: Create escrow client once per function call

## Testing Plan

```rust
#[test]
fn test_payment_flow() {
    let env = Env::default();
    env.mock_all_auths();

    // Deploy contracts
    let token_id = env.register(TokenContract, ());
    let escrow_id = env.register(EscrowContract, ());
    let bounty_id = env.register(BountyContract, ());

    // Mint tokens to creator
    let creator = Address::generate(&env);
    let token_client = TokenClient::new(&env, &token_id);
    token_client.mint(&creator, &10000);

    // Create bounty (locks funds)
    let bounty_client = BountyContractClient::new(&env, &bounty_id);
    let bounty_id = bounty_client.create_bounty(
        &creator,
        &String::from_str(&env, "Test"),
        &String::from_str(&env, "Description"),
        &5000,
        &100,
        &token_id,
        &escrow_id,
    );

    // Verify funds locked
    assert_eq!(token_client.balance(&creator), 5000);
    assert_eq!(token_client.balance(&escrow_id), 5000);

    // ... continue with apply, select, complete
    // Verify final fund transfer to freelancer
}

#[test]
fn test_refund_flow() {
    // Test cancel → refund
}
```

## Backward Compatibility

This is a **breaking change** because:
1. Bounty struct has new required fields
2. Function signatures changed

**Migration Strategy**:
1. Deploy new contracts (bounty_v2, escrow_v2)
2. Keep old contracts read-only
3. Migrate data with default escrow_id=0 for old bounties
4. Deprecate old contracts after grace period

## Estimated Effort

- **Implementation**: 4 hours
- **Testing**: 2 hours
- **Documentation**: 1 hour
- **Review/Polish**: 1 hour
- **Total**: 8 hours

## Priority

**P0 - Critical**: System is non-functional without payment integration

## Dependencies

- Requires escrow contract update (add update_payee)
- Requires token contract address configuration
- Requires escrow contract address configuration

---

**Status**: ✅ Design Complete, Ready for Implementation
**Next Step**: Update bounty contract code
