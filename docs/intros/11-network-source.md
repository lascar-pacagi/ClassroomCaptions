## From Apple networking to the application protocol

This subsystem spans six layers. Keeping them distinct prevents ambiguous
statements such as “the QR connects to the app”:

| Layer | Concrete mechanism | What it contributes |
| --- | --- | --- |
| Link/network | Wi-Fi and IPv4 | packets between classroom devices |
| Transport | TCP | ordered reliable byte stream |
| Apple API | Network.framework | listener and connection state machines |
| Application framing | minimal HTTP/1.1 | requests, routes, headers, bodies |
| Streaming protocol | Server-Sent Events | long-lived Mac-to-browser updates |
| Pairing presentation | URL encoded as QR | transfers a bearer capability |

The QR does not open a special Apple channel. The Camera app decodes text,
recognizes an `http://` URL, and asks the browser to perform an ordinary HTTP
request to the Mac's private IPv4 address.

## Network.framework in detail

### `NWParameters`

`NWParameters.tcp` asks Network.framework for a reliable byte-stream transport.
The framework chooses and configures BSD sockets internally, monitors path
changes, and reports asynchronous state transitions.

`requiredInterfaceType = .wifi` rejects paths that are not classified as Wi-Fi.
`includePeerToPeer = true` permits Apple peer-to-peer-capable paths when the
system and entitlement context allow them. It does not guarantee Bluetooth
transport and it is not a replacement for both devices sharing a reachable
network. `allowLocalEndpointReuse` permits rebinding after a quick restart
instead of waiting for old TCP state to expire.

### `NWListener`

Creating `NWListener(using:on:)` binds the local port but does not synchronously
wait for readiness. `start(queue:)` schedules all listener callbacks on the
chosen serial queue. Relevant states are `setup`, optionally `waiting`, then
`ready`; terminal outcomes are `failed` or `cancelled`. These are asynchronous
listener states, not HTTP request states.

At `.ready`, the kernel is accepting connections. The application then chooses
an address to advertise. A listener may be ready even when no useful Wi-Fi IPv4
address exists; binding and address presentation are separate problems.

`newConnectionHandler` receives one `NWConnection` per accepted TCP connection.
The server caps these objects before starting them to bound memory and file
descriptors.

### `NWConnection`

An accepted connection has its own state machine. `start(queue:)` schedules
callbacks, `receive(minimumIncompleteLength:maximumLength:)` supplies arbitrary
byte chunks, and `send` queues bytes for transport.

TCP preserves byte order but not application message boundaries. One receive
may contain half a header, several headers, or a header plus part of a body.
That is why `receiveRequest` appends bytes and searches for HTTP delimiters
rather than assuming one callback equals one request.

The completion arguments matter:

- `content` contains bytes delivered in this callback;
- `isComplete` means the peer ended its sending side;
- `error` means transport failure;
- a nil/empty callback without completion is not a complete HTTP request.

## Address selection and Bonjour

The listener advertises `_classcaptions._tcp` through DNS Service Discovery.
Bonjour combines multicast DNS name discovery with service records. The current
browser flow does not resolve that service; it embeds a numeric IPv4 address in
the QR. Advertisement remains useful for diagnostics and a future native app.

`getifaddrs` returns a linked list of interfaces. The code accepts only entries
that are up, non-loopback, and `AF_INET`, asks `getnameinfo` for numeric text,
prefers `en0`, and retains a fallback. This is pragmatic rather than perfect:
modern Macs, VPNs, USB adapters, and hotspot configurations can assign other
names. Network.framework knows the selected path, but converting that path into
the exact browser-reachable local address still requires care.

Private IPv4 addressing does not imply reachability. Classroom Wi-Fi may enable
client isolation, firewalls may reject inbound traffic, or VPN routing may
divert packets. A personal hotspot is often more predictable.

## The implemented HTTP subset

This is not a general HTTP server. It accepts one request per ordinary
connection and supports only known generated clients.

### Framing algorithm

The receiver appends at most 2,048 bytes per callback into an accumulated
buffer. It rejects more than 8 KiB total. Once it finds the four bytes
`CR LF CR LF`, it knows the header terminator. It parses `Content-Length`,
rejects bodies above 2 KiB, and waits until:

```text
received byte count >= header end + Content-Length
```

Only then does routing begin. Ordinary responses contain `Connection: close`,
so keep-alive request pipelining and chunked transfer encoding are intentionally
outside the grammar.

### Request parsing and routing

The first line is split into method, request target, and HTTP version.
`URLComponents` parses path and query. Header names become lowercase because
HTTP field names are case-insensitive.

Authentication is performed before revealing protected route behavior. Wrong
credentials receive the same 404 used for unknown routes. The viewer capability
authorizes only `/` and `/events`. The student capability authorizes the form
and ticket endpoint, while a ticket authorizes one source's question POSTs.

## Server-Sent Events as a byte protocol

SSE is UTF-8 text over one HTTP response that remains open:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream; charset=utf-8
Connection: keep-alive

retry: 1000

event: captions
data: {"finalized":["..."],"provisional":"...","revision":42}

: heartbeat

```

Each event ends with an empty line. Multiple `data:` lines would be joined by
the browser with newline characters. A line beginning with `:` is a comment;
the JavaScript receives no application event, but traffic keeps intermediate
state active. `retry: 1000` asks `EventSource` to reconnect after one second.

The server sends the latest snapshot immediately after stream establishment.
Otherwise a newly opened page would remain blank until the next spoken token.
The monotonic revision lets clients reason about freshness even though the
current page simply renders each received snapshot.

## Capabilities, tickets, and threat boundaries

Viewer and student URLs contain independent 256-bit random bearer tokens.
Possession is authorization; there is no account identity. Equal-length token
comparison XORs all bytes to avoid a first-difference timing signal.

A student page exchanges its long-lived page capability for an in-memory
ticket bound to the observed remote endpoint. Tickets expire and carry their
own submission history. Per-ticket, per-source, global, and absolute limits
address different abuse cases:

- one browser submitting too quickly;
- many tickets from one source;
- many sources flooding one class;
- unbounded dictionaries or professor queue growth.

These controls are availability defenses, not strong identity. NAT can merge
students into one source, while address changes can invalidate a legitimate
ticket.

### Operational limits at a glance

Every hard limit lives in one auditable place (`CaptionSharingSecurity` and the
app model). Knowing them ahead of class avoids surprises mid-lecture:

| Limit | Value | What happens at the limit |
| --- | --- | --- |
| Concurrent TCP connections | 64 | further connections are cancelled at accept |
| Time to complete a request | 10 s | the connection is cancelled (slowloris guard) |
| Live caption streams | 1 | a newer authenticated viewer pre-empts the old stream |
| Live student tickets | 256 total, 4 per source, 4-hour lifetime | `503 classroom_full` / `429 ticket_limit` |
| Question gap per ticket | 10 s | `429` |
| Questions per source | 8 per 5 min | `429` |
| Questions globally | 30 per min | `429` |
| Accepted questions | 100 per sliding hour | `429` until the window clears |
| Pending questions held by the app | 500 | memory bound only; unreachable below a multi-hour unmoderated backlog |
| Request size / body size | 8 KiB / 2 KiB | `431` / `413` |

Three of these are deliberate recoveries rather than caps. A connection that
never completes a request cannot hold one of the 64 slots beyond the timeout,
because authentication only happens after a full request is parsed. The single
caption stream goes to the most recent holder of the viewer token, so the
professor reclaims a stuck or hijacked stream by simply reopening the page.
And the accepted-question limit is a sliding window, so an active class
recovers automatically instead of losing questions for the rest of the
session.

Plain HTTP provides no confidentiality or integrity against a hostile network.
The intended deployment is trusted classroom Wi-Fi or a personal hotspot.

## How a QR symbol is built

The application delegates encoding to Core Image:

```swift
let filter = CIFilter.qrCodeGenerator()
filter.message = Data(url.absoluteString.utf8)
filter.correctionLevel = "M"
```

Understanding the result still requires following the QR encoder.

### 1. Payload bytes and mode

The message is the UTF-8 byte sequence of the capability URL. Because lowercase
letters and URL punctuation do not fit QR alphanumeric mode efficiently, an
encoder normally selects byte mode. The bitstream begins with the four-bit byte
mode indicator `0100`, followed by a character-count field whose width depends
on QR version, then eight bits per payload byte.

### 2. Version and capacity

QR versions run from 1 to 40. Version `v` has:

```text
module width = 21 + 4 * (v - 1)
```

The encoder selects the smallest version whose data-codeword capacity can hold
mode, count, payload, terminator, and byte alignment at error-correction level
M. A longer IP address, route, or token can therefore increase module density.

### 3. Terminator, alignment, and pad codewords

Up to four zero bits terminate the logical message. Zero bits then align to the
next byte boundary. Remaining data capacity is filled by alternating codewords
`0xEC` and `0x11`. These bytes are specified padding, not part of the URL.

### 4. Reed-Solomon correction over `GF(256)`

Data codewords are divided into blocks according to version and correction
level. Each byte is treated as an element of the finite field `GF(2^8)`.
Addition is XOR. Multiplication uses polynomial arithmetic modulo the QR
primitive polynomial:

```text
x^8 + x^4 + x^3 + x^2 + 1
```

For a block requiring `r` parity codewords, the data polynomial is multiplied
by `x^r` and divided by a degree-`r` generator polynomial. The remainder is the
parity sequence. A scanner uses the resulting syndromes to locate and correct
codeword errors.

“Level M corrects about 15%” is only a rule of thumb. Correctability depends on
which codewords are damaged and on interleaving, not simply on the percentage
of black/white modules obscured.

### 5. Interleaving

QR interleaves the first codeword from each data block, then the second from
each, and so on; parity blocks are interleaved similarly. Spatial damage then
affects several blocks moderately instead of destroying one contiguous block.

### 6. Reserved patterns

Before payload placement, the grid reserves:

- three 7x7 finder patterns plus white separators;
- horizontal and vertical alternating timing patterns;
- alignment patterns for versions above 1;
- format-information areas;
- version-information areas for versions 7 and above;
- one fixed dark module.

These patterns let a camera locate, rotate, scale, sample, and characterize the
symbol before decoding data.

### 7. Zigzag data placement

Interleaved bits are placed from the lower-right in vertical pairs of columns.
The direction alternates upward and downward. Placement skips every reserved
module and skips the vertical timing column. Remaining unused capacity receives
specified remainder bits.

### 8. Mask selection

Large uniform regions and finder-like accidental patterns are difficult for
cameras. QR defines eight masks. A mask condition flips only data/error
correction modules; fixed patterns remain unchanged.

Each candidate receives penalties for:

1. long runs of equal color;
2. 2x2 same-color blocks;
3. finder-like `1:1:3:1:1` patterns with surrounding light modules;
4. dark-module proportion far from 50%.

The lowest-penalty mask is retained.

### 9. Format and version information

Format bits encode the correction level and mask number, protected by a BCH
code and XOR mask. They are written twice near finder patterns. Versions 7 and
above also write BCH-protected version bits in two locations.

### 10. Rasterization and quiet zone

Core Image returns a logical one-pixel-per-module image. The app applies an
integer scale and disables interpolation so every module remains a sharp
rectangle. A clear light quiet zone of four modules around the symbol is
essential for finder detection.

The QR is only a visual transport for the URL. It does not encrypt that URL,
authenticate the scanner, or remain valid after the server rotates its token.

## End-to-end pairing sequence

@fig-network-request-flow shows the complete transport sequence. The
camera transfers URL text. The browser then creates ordinary TCP/HTTP
connections; `EventSource` owns the persistent caption stream, while the
student route exchanges its page capability for a source-bound ticket before
submitting questions.

The complete server source below implements every step after QR decoding. The
QR rendering helper itself appears in the dashboard chapter because it belongs
to presentation, but its exact code is quoted above and included in full there.
