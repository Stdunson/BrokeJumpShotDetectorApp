//
//  VideoFrameExtractor.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 01/01/26.
//

import AVFoundation
import UIKit

class VideoFrameExtractor {
    static func extractFirstFrame(from videoURL: URL) async -> UIImage? {
        let asset = AVAsset(url: videoURL)
        let imageGenerator = AVAssetImageGenerator(asset: asset)
        imageGenerator.appliesPreferredTrackTransform = true
        
        do {
            let cgImage = try imageGenerator.copyCGImage(at: .zero, actualTime: nil)
            return UIImage(cgImage: cgImage)
        } catch {
            print("Error extracting frame: \(error)")
            return nil
        }
    }
}
