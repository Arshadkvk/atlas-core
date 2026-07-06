
# Design

## Architecture

The service is implemented as a REST API using Django and Django REST Framework. PostgreSQL is used as the primary datastore. All business logic related to wallet balance, purchases, and rewards is handled by the backend. The client only sends requests and never controls balances, inventory, or prices.

```
Client
    │
    ▼
Django REST API
    │
Business Logic
    │
PostgreSQL
```

---

## Datastore Choice

PostgreSQL was selected because it provides ACID transactions, row-level locking, and reliable crash recovery. These features are required to guarantee that wallet operations are processed safely without losing or duplicating data during concurrent requests or unexpected server failures.

---

## Database Design

The application uses the following main tables:

**Player**

* Stores the player's current wallet balance.

**InventoryItem**

* Stores items owned by each player.

**RewardClaim**

* Stores rewards claimed by players.
* A unique constraint on `(player_id, reward_id)` ensures a reward can only be claimed once.

**Ledger**

* Stores every successful wallet transaction (credit, purchase, reward).
* Used for auditing and reconciliation.
* The wallet balance is stored as a mutable column on the Player table for fast reads, while the ledger provides an immutable history of all balance changes.

**IdempotencyRequest**

* Stores processed idempotency keys, request hash, response status, and response body.
* Prevents duplicate processing of the same request.

---

## API Contract

The service exposes the following endpoints:

* `POST /v1/wallets/{playerId}/credit`
* `POST /v1/wallets/{playerId}/purchase`
* `POST /v1/rewards/{rewardId}/claim`
* `GET /v1/wallets/{playerId}`

Currency values are stored as positive integers (smallest unit, no decimal values).

| Operation                | Success | Failure                           |
| ------------------------ | ------- | --------------------------------- |
| Credit                   | 200 OK  | 400 Bad Request                   |
| Purchase                 | 200 OK  | 409 Conflict (insufficient funds) |
| Reward Claim             | 200 OK  | 409 Conflict (already claimed)    |
| Invalid Request          | -       | 400 Bad Request                   |
| Idempotency Key Conflict | -       | 409 Conflict                      |

---

## Non-Duplicate Strategy

Every write operation requires an `Idempotency-Key` header.

The idempotency record stores:

* Player ID
* Endpoint
* Idempotency key
* Request body hash
* Response status
* Response body

The idempotency key is scoped to `(player_id, endpoint, idempotency_key)`.

Request handling:

* If the key does not exist, the request is processed and the response is stored.
* If the same key is received with the same request body, the stored response is returned without executing the operation again.
* If the same key is reused with a different request body, the request is rejected with `409 Conflict`.

To prevent duplicate processing during concurrent requests, the idempotency record is created inside the transaction with a unique constraint. This ensures only one request can process a given idempotency key.

Idempotency records are retained for 24 hours to support client retries.

---

## Atomicity & Concurrency

Purchase operations are executed inside a single database transaction.

The transaction performs the following steps:

1. Lock the player's wallet using `SELECT FOR UPDATE`.
2. Validate the available balance.
3. Deduct the purchase amount.
4. Add the purchased item to the inventory.
5. Create a ledger record.
6. Commit the transaction.

If any step fails, the transaction is rolled back and no changes are saved.

The service uses PostgreSQL's default `READ COMMITTED` isolation level together with row-level locking. This ensures that only one transaction can modify the same wallet at a time, preventing double spending while keeping transaction overhead low.

Reward claiming follows the same transactional approach. The unique constraint on `(player_id, reward_id)` guarantees that the reward can only be granted once.

---

## Durability

The service relies on PostgreSQL's transaction guarantees.

If the application is terminated before a transaction commits (for example, using `kill -9`), PostgreSQL rolls back the incomplete transaction automatically.

If the transaction has already committed, all changes remain durable after restart. This guarantees that purchases are always applied as an all-or-nothing operation.

---

## Limits

* Currency values must be positive integers.
* Wallet balances cannot become negative.
* Reward claims are limited to one claim per player.
* All write operations require an `Idempotency-Key`.
* The service is designed as a single backend service using one PostgreSQL database.
