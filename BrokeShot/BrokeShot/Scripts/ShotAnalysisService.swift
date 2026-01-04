//
//  ShotAnalysisService.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 12/21/25.
//

import Foundation

class ShotAnalysisService{
    
    static let shared = ShotAnalysisService()
    
    private init(){}
    
    func analyzeVideo(videoURL: URL, completion: @escaping (Result<ShotAnalysisResponse, Error>) -> Void){
        
        let boundary = UUID().uuidString
        let url = URL(string: "http://loaclhost:8000/analyze")! // Replace localhost with your LAN IP for local network
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"shot.mp4\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: video/mp4\r\n\r\n".data(using: .utf8)!)
        
        do{
            let videoData = Data(try Data(contentsOf: videoURL))
            body.append(videoData)
        }catch{
            completion(.failure(error))
            return
        }
        
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error{
                completion(.failure(error))
                return
            }
            
            guard let data = data else{
                completion(.failure(NSError()))
                return
            }
            
            Task { @MainActor in
                do {
                    let decoded = try JSONDecoder().decode(ShotAnalysisResponse.self, from: data)
                    completion(.success(decoded))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
}

