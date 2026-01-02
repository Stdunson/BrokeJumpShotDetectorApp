//
//  VideoFrameExtractor.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 01/01/26.
//

import AVFoundation
import UIKit

class VideoFrameExtractor {
    
    /// Extract a frame at a specific time
    static func extractFrame(from videoURL: URL, at time: CMTime) async -> UIImage? {
        let asset = AVAsset(url: videoURL)
        let imageGenerator = AVAssetImageGenerator(asset: asset)
        imageGenerator.appliesPreferredTrackTransform = true
        
        do {
            let (cgImage, _) = try await imageGenerator.image(at: time)
            return UIImage(cgImage: cgImage)
        } catch {
            print("Error extracting frame: \(error)")
            return nil
        }
    }
    
    static func extractFirstFrame(from videoURL: URL) async -> UIImage? {
        return await extractFrame(from: videoURL, at: .zero)
    }
    
    static func extractMiddleFrame(from videoURL: URL) async -> UIImage? {
        let asset = AVAsset(url: videoURL)
        do {
            let duration = try await asset.load(.duration)
            let middleTime = CMTime(seconds: duration.seconds / 2, preferredTimescale: duration.timescale)
            return await extractFrame(from: videoURL, at: middleTime)
        } catch {
            print("Error loading duration: \(error)")
            return nil
        }
    }
    
    static func extractLastFrame(from videoURL: URL) async -> UIImage? {
        let asset = AVAsset(url: videoURL)
        do {
            let duration = try await asset.load(.duration)
            let lastTime = CMTime(seconds: max(0, duration.seconds - 0.1), preferredTimescale: duration.timescale)
            return await extractFrame(from: videoURL, at: lastTime)
        } catch {
            print("Error loading duration: \(error)")
            return nil
        }
    }
    
    //0 is start, 1 is end
    static func extractFrame(from videoURL: URL, at ratio: Double) async -> UIImage? {
        let asset = AVAsset(url: videoURL)
        do {
            let duration = try await asset.load(.duration)
            let timeAtRatio = CMTime(seconds: duration.seconds * ratio, preferredTimescale: duration.timescale)
            return await extractFrame(from: videoURL, at: timeAtRatio)
        } catch {
            print("Error loading duration: \(error)")
            return nil
        }
    }
}
