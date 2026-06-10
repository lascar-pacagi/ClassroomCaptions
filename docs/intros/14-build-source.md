## Package graph

`Package.swift` declares:

- `ClassroomCaptionsCore`, platform-independent domain logic;
- `CVoxtralEngine`, C/Objective-C headers and implementation;
- `ClassroomCaptions`, the macOS executable;
- `VoxtralBenchmark`, the command-line executable;
- the XCTest target.

Framework linker settings are part of the implementation contract: AppKit and
SwiftUI serve UI; AVFoundation/AudioToolbox/CoreAudio serve capture; Network
serves local TCP; Metal/MPS/Accelerate serve inference.

## Bundle construction

A macOS `.app` is a directory hierarchy:

```text
ClassroomCaptions.app/
  Contents/
    MacOS/ClassroomCaptions
    Info.plist
    Resources/
```

The packaging script builds release code, creates this hierarchy, copies the
executable/property list, and ad-hoc code-signs the bundle with
`codesign --force --deep --sign -` (an ad-hoc signature carries no developer
identity; it is the minimum signing Apple-silicon macOS requires to run an
executable). Model weights are
not copied into the bundle because they are tens of gigabytes and have an
independent download/update lifecycle.

## Reproducible model acquisition

The download script selects the expected repository/revision and files. Model
layout is an ABI: changing filenames, tensor names, tokenizer data, or component
directories can break the C loader even when the checkpoint architecture is
nominally compatible.

## Documentation build

The book build first regenerates source chapters and verifies byte-for-byte
coverage, then asks Quarto (the publishing system that builds this book) to
render HTML and Typst/PDF (Typst is the typesetting engine used for the PDF
output). Generated chapters are
artifacts; human explanations live in generator metadata, introductions, and
figures so rebuilding does not erase them.
