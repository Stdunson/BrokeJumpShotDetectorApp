//
//  ResultsView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI
import SwiftData
import Combine

struct ResultsView: View {
    
    @Environment(\.modelContext) private var modelContext
    
    var shot: shotData
    
    var pastData: jumpshot?
    
    let loadingMessages = ["Analyzing", "Analyzing.", "Analyzing..", "Analyzing..."]
    
    @State var myScore: Int = -1
    
    @State private var loadingMessageIndex: Int = 0
    
    @State var errorMess: String = "ERROR: JumpShot Evaluation Failed"
    
    @StateObject private var vm = ShotAnalysisViewModel()
    
    var body: some View {
        NavigationStack{
            if myScore == -1 {
                Text(loadingMessages[loadingMessageIndex % loadingMessages.count])
                    .font(.largeTitle)
                    .bold()
                    .padding(.horizontal)
                    .padding(.top, 24)
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
                    .onReceive(Timer.publish(every: 1.0, on: .main, in: .common).autoconnect()) { _ in
                        loadingMessageIndex += 1
                    }
            }else if myScore == -2{
                Text("ERROR: " + errorMess)
                    .font(.largeTitle)
                    .bold()
                    .padding(.horizontal)
                    .padding(.top, 24)
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
            }else{
                ScrollView{
                    Text("Your Jumpshot is...")
                        .font(.largeTitle)
                        .bold()
                        .padding(.horizontal)
                        .padding(.top, 24)
                        .multilineTextAlignment(.center)
                    Text(determineShotMessage(score: myScore, type: 1))
                        .font(.largeTitle)
                        .bold()
                        .padding(.horizontal)
                        .multilineTextAlignment(.center)
                    
                    if let frame = vm.firstFrame {
                        Image(uiImage: frame)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .padding()
                    } else {
                        VStack{
                            Text("Image Unavailable")
                            Image(systemName: "basketball")
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(maxWidth: .infinity, maxHeight: .infinity)
                                .padding()
                        }
                    }
                    
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Shot Pocket: " + determineShotMessage(score: myScore, type: 2))
                            .bold()
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.gray.opacity(0.05))
                            .cornerRadius(8)
                        Text("Set Point: " + determineShotMessage(score: myScore, type: 3))
                            .bold()
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.gray.opacity(0.05))
                            .cornerRadius(8)
                        Text("Follow Through: " + determineShotMessage(score: myScore, type: 4))
                            .bold()
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.gray.opacity(0.05))
                            .cornerRadius(8)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 16)
                    
                    Text(determineShotMessage(score: myScore, type: 5))
                        .bold()
                        .padding()
                        .multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                }
                
                }
            NavigationLink(destination: LandingPage()){
                Text("Main Menu")
                    .tint(Color.primary)
                    .padding(12)
                    .bold()
                    .frame(maxWidth: .infinity)
                    .background(Color.orange.opacity(0.75))
                    .cornerRadius(12)
                    .padding(16)
            }
            .tint(.orange)
                
        }
        .onAppear {
            if pastData == nil{
                vm.analyze(videoURL: shot.imageURL)
            }else if let prevScoredResult = pastData{
                myScore = prevScoredResult.score
                vm.extractFrame(from: shot.imageURL)
            }
        }
        .onChange(of: vm.result) { oldValue, newValue in
            if let result = newValue {
                myScore = result.score
                let newShot = jumpshot(shot: shot, score: myScore)
                modelContext.insert(newShot)
            }
        }
        .onChange(of: vm.errorMessage) { oldValue, newValue in
            myScore = -2
            if let message = newValue {
                errorMess = message
            }
            
        }
        .navigationBarBackButtonHidden(true)
    }
}

#Preview {
    ResultsView(shot: shotData(date: Date(), imageURL: URL(string: "https://example.com/image.png")!), pastData: nil)
}
