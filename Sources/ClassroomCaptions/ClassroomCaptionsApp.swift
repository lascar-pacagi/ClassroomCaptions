import SwiftUI

@main
struct ClassroomCaptionsApp: App {
    @State private var model = ClassroomAppModel()

    var body: some Scene {
        WindowGroup {
            DashboardView(model: model)
                .frame(minWidth: 820, minHeight: 560)
        }
        .defaultSize(width: 980, height: 680)

        MenuBarExtra("Classroom Captions", systemImage: model.isListening ? "captions.bubble.fill" : "captions.bubble") {
            Button(model.isListening ? "Stop Session" : "Start Session") {
                model.toggleSession()
            }

            Button(model.isOverlayVisible ? "Hide Overlay" : "Show Overlay") {
                model.toggleOverlay()
            }

            Divider()

            Button("Quit") {
                model.shutdown()
                NSApplication.shared.terminate(nil)
            }
        }
    }
}
