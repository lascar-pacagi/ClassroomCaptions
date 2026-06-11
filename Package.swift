// swift-tools-version: 6.2

import PackageDescription

let package = Package(
    name: "ClassroomCaptions",
    platforms: [
        .macOS(.v15),
    ],
    products: [
        .executable(name: "ClassroomCaptions", targets: ["ClassroomCaptions"]),
        .executable(name: "VoxtralBenchmark", targets: ["VoxtralBenchmark"]),
        .library(name: "ClassroomCaptionsCore", targets: ["ClassroomCaptionsCore"]),
    ],
    targets: [
        .target(
            name: "CVoxtralEngine",
            path: "Sources/CVoxtralEngine",
            publicHeadersPath: "include",
            cSettings: [
                .define("USE_BLAS"),
                .define("USE_METAL"),
                .define("ACCELERATE_NEW_LAPACK"),
                .unsafeFlags(["-O3", "-march=native"]),
            ],
            linkerSettings: [
                .linkedFramework("Accelerate"),
                .linkedFramework("Metal"),
                .linkedFramework("MetalPerformanceShaders"),
                .linkedFramework("MetalPerformanceShadersGraph"),
                .linkedFramework("Foundation"),
            ]
        ),
        .target(name: "ClassroomCaptionsCore"),
        .executableTarget(
            name: "ClassroomCaptions",
            dependencies: ["ClassroomCaptionsCore", "CVoxtralEngine"],
            resources: [.copy("RenderAssets")]
        ),
        .executableTarget(
            name: "VoxtralBenchmark",
            dependencies: ["CVoxtralEngine"]
        ),
        .testTarget(
            name: "ClassroomCaptionsCoreTests",
            dependencies: [
                "ClassroomCaptionsCore",
                "ClassroomCaptions",
                "CVoxtralEngine",
            ]
        ),
    ]
)
