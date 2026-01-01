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
}

//class for swiftdata
@Model
class jumpshot: Identifiable{
    var shot: shotData
    var id: UUID
    var score: Int
    
    init(shot: shotData, score: Int) {
        self.shot = shot
        id = UUID()
        self.score = score
    }
}

func determineShotMessage(score: Int, type: Int) -> String{
    //Type is 1 if overall brokeness, 2 if shot pocket, 3 if set point, 4 if follow through, 5 if message
    switch type{
    case 1:
        if(score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 2:
        if(score == 2 || score == 5 || score == 6 || score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 3:
        if(score == 3 || score == 5 || score == 7  || score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 4:
        if(score == 4 || score == 6 || score == 7  || score == 9){
            return "PURE 💦"
        }else{
            return "BROKE 🧱"
        }
    case 5:
        switch score{ //After make sure, put recommended improvements
        case 0:
            return "Your shot is about as broke as a shot can be 😭 the video uploaded may not be the best. Try another video or restarting your shot anew."
        case 2:
            return "You have a good base to your shot but it all falls apart once you start bringing the ball up. To improve your set point, make sure that he ball is at the center of your body or slightly towards the dominant hand, your wrist is loaded, your shooting hand is under the ball, and the ball is slightly in front of your head. To improve your follow through, make sure your guide hand comes off of the ball before your release, you’re keeping that shooting elbow straight, and your shooting hand flicks towards the basket."
        case 3:
            return "You have a good set point, but the base and follow through aren't there. To improve your shot pocket, make sure you’re keeping the ball close to your body, your wrist is loaded, and the ball is at the center of your body or slightly towards the dominant hand. To improve your follow through, make sure your guide hand comes off of the ball before your release, you’re keeping that shooting elbow straight, and your shooting hand flicks towards the basket."
        case 4:
            return "You end the shot off well, but the base is a bit weak, and the set point is off. To improve your shot pocket, make sure you’re keeping the ball close to your body, your wrist is loaded, and the ball is at the center of your body or slightly towards the dominant hand. To improve your set point, make sure that he ball is at the center of your body or slightly towards the dominant hand, your wrist is loaded, your shooting hand is under the ball, and the ball is slightly in front of your head."
        case 5:
            return "Everything is good up until the release. Make sure your guide hand comes off of the ball before your release, you’re keeping that shooting elbow straight, and your shooting hand flicks towards the basket."
        case 6:
            return "Everything is good except that set point, and sometimes that's all it takes. Make sure that he ball is at the center of your body or slightly towards the dominant hand, your wrist is loaded, your shooting hand is under the ball, and the ball is slightly in front of your head."
        case 7:
            return "Your shot looks good for the most part, but when the base is off, everything is off. Make sure you’re keeping the ball close to your body, your wrist is loaded, and the ball is at the center of your body or slightly towards the dominant hand."
        case 9:
            return "Your shot is about as pure as it gets. Focus on getting reps in and you'll be golden."
        default:
            return "N/A"
        }
        
    default:
        return ""
    }
}
