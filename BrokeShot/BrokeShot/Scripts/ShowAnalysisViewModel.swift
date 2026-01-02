//
//  ShowAnalysisViewModel.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 12/21/25.
//

import SwiftUI
import Combine
import UIKit

@MainActor
class ShotAnalysisViewModel: ObservableObject{
    @Published var result: ShotAnalysisResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var firstFrame: UIImage?

    func extractFrame(from videoURL: URL) {
        Task {
            self.firstFrame = await VideoFrameExtractor.extractMiddleFrame(from: videoURL)
        }
    }

    func analyze(videoURL: URL) {
        isLoading = true
        errorMessage = nil

        extractFrame(from: videoURL)

        ShotAnalysisService.shared.analyzeVideo(videoURL: videoURL) { result in
            DispatchQueue.main.async {
                self.isLoading = false
                switch result {
                case .success(let response):
                    self.result = response
                case .failure(let error):
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }
}
