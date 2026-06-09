## What each test layer proves

Pure domain tests prove deterministic state transitions and validation policy.
They run quickly and should cover edge cases densely.

Boundary tests cover:

- C ABI defaults, errors, and pinned revision;
- overlay geometry without creating a visible course session;
- WAV binary fields and archive output;
- local HTTP authentication, tickets, and rate limiting;
- parser tolerance for remote protocol shapes;
- process-memory measurement availability.

Tests do not prove model quality, real-time deadline behavior under every
machine load, classroom Wi-Fi reachability, or GPU numerical equivalence across
all inputs. Those remain benchmark/integration/manual-test responsibilities.

## Reading XCTest

`XCTAssertEqual`, `XCTAssertTrue`, and related functions record a failure while
allowing the test process to continue. `XCTUnwrap` converts an unexpected
optional absence into a test failure and returns the wrapped value.

An `async` test method runs in Swift concurrency. Tests that open a loopback
server use bounded waits and explicit teardown so a failure cannot leave a
listener affecting later tests.

## Tests as change constraints

When documentation identifies an invariant, the corresponding test should make
the invariant executable. Examples include:

- raw captions survive correction failure;
- final drain is accepted while stopping;
- question-shaped captions remain questions;
- wrong capability receives no protected resource;
- odd trailing PCM byte is ignored;
- overlay frame never escapes visible bounds.
