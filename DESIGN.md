# Design

## Architecture

The service is implemented as a REST API using Django and Django REST Framework. PostgreSQL is used as the primary datastore.

All business logic related to wallet balances, purchases, and reward claiming is implemented on the backend using a service layer. The client only submits requests and never controls balances, inventory, or item prices.

```
Client
    │
    ▼
Django REST API
    │
Service Layer
    │
PostgreSQL
```

---

## Datastore Choice

PostgreSQL was selected because it provides:

- ACID transactions
- Row-level locking
- Reliable crash recovery
- Strong consistency

These features are required to safely process wallet operations while preventing duplicate processing and race conditions during concurrent requests.

---

## Database Design

The application consists of the following main models.

### Player

Stores player information and a unique `player_id`.

### Wallet

Stores the current wallet balance for a player.

Each player owns exactly one wallet through a One-to-One relationship.

### Transaction

Stores every successful wallet operation.

Transaction types include:

- CREDIT
- DEBIT
- REWARD

Each transaction records:

- amount
- reason
- status
- timestamp
- related idempotency record

This provides a complete audit history of wallet operations.

### ShopItems

Stores all purchasable items.

The server owns item prices and validates every purchase against the stored price.

### InventoryItem

Stores the items owned by each wallet.

A unique constraint on `(wallet, shop_item)` ensures that the same inventory item is stored once while its quantity is updated.

### Reward

Defines available rewards.

Rewards may grant either:

- Currency
- Inventory items

### RewardClaim

Records claimed rewards.

A unique constraint on `(wallet, reward)` guarantees that each reward can only be claimed once per wallet.

### IdempotencyKey

Stores processed requests.

Each record contains:

- idempotency key
- request hash
- response status
- response body
- creation timestamp
- expiry timestamp

This enables safe retries without executing the same operation multiple times.

---

## API Contract

The service exposes the following endpoints.

| Method | Endpoint |
|---------|----------|
| GET | `/v1/wallets/{playerId}/` |
| POST | `/v1/wallets/{playerId}/credit/` |
| POST | `/v1/wallets/{playerId}/purchase/` |
| POST | `/v1/rewards/{rewardId}/claim/` |

Currency values are stored using Django's `DecimalField` to provide accurate monetary calculations.

---

## Idempotency Strategy

All write operations require an `Idempotency-Key` header.

Supported operations:

- Wallet Credit
- Purchase Item
- Claim Reward

Each request generates a hash based on the request payload.

Processing flow:

1. Generate the request hash.
2. Search for the idempotency key.
3. If the key does not exist:
   - Execute the operation.
   - Store the response.
4. If the same key is reused with the same payload:
   - Return the stored response.
5. If the same key is reused with a different payload:
   - Reject the request with an idempotency conflict.

Idempotency records are retained for 24 hours to support client retries.

---

## Atomicity and Concurrency

All wallet-modifying operations execute inside `transaction.atomic()`.

Before modifying a wallet, the wallet row is locked using Django's `select_for_update()`.

For a purchase, the transaction performs the following steps:

1. Lock the wallet.
2. Validate the request.
3. Verify sufficient balance.
4. Deduct the wallet balance.
5. Update the inventory.
6. Create a transaction record.
7. Store the idempotency record.
8. Commit the transaction.

If any step fails, PostgreSQL rolls back the entire transaction automatically.

This guarantees that purchases are applied as an all-or-nothing operation.

---

## Reward Processing

Reward claiming follows the same transactional approach.

The service:

1. Locks the wallet.
2. Checks idempotency.
3. Verifies the reward has not already been claimed.
4. Applies either:
   - Currency reward
   - Inventory reward
5. Records the reward claim.
6. Creates a transaction.
7. Stores the idempotency response.

The unique constraint on `(wallet, reward)` prevents duplicate reward claims.

---

## Durability

The service relies on PostgreSQL's durability guarantees.

If the application terminates before a transaction commits (for example using `kill -9`), PostgreSQL automatically rolls back the incomplete transaction.

If the transaction has already committed, all changes remain durable after restart.

This guarantees that wallet updates are never partially applied.

---

## Testing

The project includes integration tests for the most critical scenarios.

### Idempotency Test

Verifies that duplicate requests using the same idempotency key:

- execute only once
- return the previously stored response
- do not create duplicate transactions

### Concurrency Test

Uses `TransactionTestCase` together with concurrent requests to verify that:

- only one purchase succeeds when two requests compete for the same wallet balance
- the wallet cannot be overspent
- only one inventory item is granted
- only one transaction is recorded

---

## System Constraints

- Wallet balances cannot become negative.
- Item prices are validated by the server.
- Each reward can only be claimed once per wallet.
- Every write operation requires an `Idempotency-Key`.
- Duplicate requests are processed exactly once.
- All wallet updates are executed inside database transactions.
- PostgreSQL is the single source of truth for balances, inventory, and transaction history.