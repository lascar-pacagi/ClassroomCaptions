## The coordinator as a set of transactions

`ClassroomAppModel` is large because it expresses end-to-end workflows, not
because every subsystem implementation belongs in it. A useful reading method
is to identify the transaction and its rollback/cleanup path.

### Start transaction

1. Reject duplicate starts and reset transient diagnostics.
2. Snapshot settings that must remain stable for the session.
3. Prepare the optional archive and Gemma warm-up independently.
4. Start the selected Voxtral backend (priming the decoder with silence) and
   wait for its `connected` event.
5. Only after `connected`, create the value-type `ClassroomSession`, request
   permission, and open the selected microphone.
6. Mark the session `listening`.

The session is deliberately *not* created up front: it is constructed at the
moment the microphone opens, after Voxtral reports `connected`. The model does
not open the microphone while Voxtral is still loading, because audio callbacks
have no replay buffer at that point, so doing so would exchange a slightly faster
button response for lost first words.

### Stop transaction

Stop has a stronger ordering requirement:

1. close the atomic capture gate;
2. cancel periodic commit and silence-flush work;
3. stop hardware callbacks;
4. flush/finish Voxtral and drain final text;
5. accept final captions while phase is `stopping`;
6. wait a bounded time for corrections;
7. rewrite/finalize archive files;
8. return the domain session to `idle`;
9. clear runtime-only references and refresh presentation.

Each step removes one producer before destroying its consumer. This is the
same lifetime discipline used for C callback contexts and GPU command queues.

## Observation and actor isolation

`@Observable` instruments property access so SwiftUI can invalidate only views
that read changed properties. It does not create synchronization. The
`@MainActor` annotation is the synchronization rule: observable properties are
read and written on the main executor.

When a callback arrives from a dispatch queue, a URLSession delegate (the
object Foundation's HTTP client calls back with results), or the server
queue, the callback creates a `Task { @MainActor in ... }` or otherwise hops to
the main actor. The copied event/question/snapshot crosses the boundary; the
originating service object remains with its own owner.

## Tasks and cancellation

Stored `Task` references represent ongoing workflows such as event observation,
periodic commits, model start, correction work, and stop. Cancellation is
cooperative: calling `cancel()` sets a flag and causes cancellation-aware
suspension points to throw, but ordinary synchronous code must still test
cancellation or finish quickly.

A stale task is dangerous even when memory-safe. For example, an old startup
task could report failure after a newer session begins. Session identifiers and
current-task checks prevent such temporal races from mutating the wrong
aggregate.

## Derived presentation state

The overlay and browser do not own the transcript. They receive derived
snapshots built from:

- finalized `displayText`;
- current provisional text;
- selected/pending question state;
- overlay visibility and clear-boundary policy;
- optional diagnostics.

Rebuilding a snapshot after mutation is intentionally cheap. It avoids sharing
the mutable `ClassroomSession` with AppKit or Network.framework.
