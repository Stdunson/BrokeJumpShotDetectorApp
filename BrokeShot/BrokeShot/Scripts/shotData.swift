//
//  shotData.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 12/9/25.
//
import Foundation
import SwiftUI
import SwiftData

//The backend will return a score, which represents which parts of the shot are broke, from 0-9.
//good pocket = 2, set point = 3, follow through == 4
struct shotData: Codable {
    let date: Date
    let imageURL: URL
    let score: Int
}

//class for swiftdata
@Model
class jumpshot: Identifiable{
    var shot: shotData
    var id: UUID
    
    init(shot: shotData) {
        self.shot = shot
        id = UUID()
    }
}

func determineShotMessage(shot: shotData, type: Int) -> String{
    //Type is 1 if overall brokeness, 2 if shot pocket, 3 if set point, 4 if follow through, 5 if message
    switch type{
    case 1:
        if(shot.score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 2:
        if(shot.score == 2 || shot.score == 5 || shot.score == 6 || shot.score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 3:
        if(shot.score == 3 || shot.score == 5 || shot.score == 7  || shot.score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 4:
        if(shot.score == 4 || shot.score == 6 || shot.score == 7  || shot.score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 5:
        switch shot.score{ //After make sure, put recommended improvements
        case 0:
            return "Your shot is about as broke as a shot can be 😭 the video uploaded may not be the best. Try another video or restarting your shot anew."
        case 2:
            return "You have a good base to your shot but it all falls apart once you start bringing the ball up. Make sure ..."
        case 3:
            return "You have a good set point, but the base and follow through aren't there. Make sure ..."
        case 4:
            return "You end the shot off well, but the base is a bit weak, and the shot pocket is off. Make sure ..."
        case 5:
            return "Everything is good up until the release. Make sure ..."
        case 6:
            return "Everything is good except that set point, and sometimes that's all it takes. Make sure ..."
        case 7:
            return "Your shot would be pure if you just follow through a little better. Make sure ..."
        case 9:
            return "Your shot is about as pure as it gets. Focus on getting reps in and you'll be golden."
        default:
            return "N/A"
        }
        
    default:
        return ""
    }
}
