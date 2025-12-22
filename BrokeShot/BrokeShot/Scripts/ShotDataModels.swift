//
//  ShotDataModels.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 12/21/25.
//

struct ShotAnalysisResponse: Decodable, Equatable {
    let score: Int
    let is_broke: Bool
    let max_score: Int
    let message: String
    let timestamp: String
    let phases: ShotPhases
}

struct ShotPhases: Decodable, Equatable {
    let shot_pocket: ShotPhase
    let set_point: ShotPhase
    let follow_through: ShotPhase
}

struct ShotPhase: Decodable, Equatable {
    let prediction: Int?
    let confidence: Double
    let phase: String?
    let phase_confidence: Double?
}

