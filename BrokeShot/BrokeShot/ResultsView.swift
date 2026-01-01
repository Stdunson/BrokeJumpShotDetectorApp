//
//  ResultsView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI
import SwiftData

struct ResultsView: View {
    
    @Environment(\.modelContext) private var modelContext
    
    var shot: shotData
    
    var pastData: jumpshot?
    
    @State var myScore: Int = -1
    
    @StateObject private var vm = ShotAnalysisViewModel()
    
    var body: some View {
        NavigationStack{
            if myScore == -1 {
                Text("Loading...")
                    .font(.largeTitle)
                    .bold()
                    .padding(.horizontal)
                    .padding(.top)
                    .multilineTextAlignment(.center)
            }else{
                ScrollView{
                    Text("Your Jumpshot is...")
                        .font(.largeTitle)
                        .bold()
                        .padding(.horizontal)
                        .padding(.top)
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
                    
                    VStack(alignment: .leading) {
                        Text("Shot Pocket: " + determineShotMessage(score: myScore, type: 2))
                            .bold()
                            .padding(.horizontal)
                            .padding(.bottom)
                        Text("Set Point: " + determineShotMessage(score: myScore, type: 3))
                            .bold()
                            .padding(.horizontal)
                            .padding(.bottom)
                        Text("Follow Through: " + determineShotMessage(score: myScore, type: 4))
                            .bold()
                            .padding(.horizontal)
                            .padding(.bottom)
                    }
                    
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
                    .padding(15)
                    .bold()
                    .frame(maxWidth: .infinity)
                    .background(RoundedRectangle(cornerRadius: 15))
                    .padding()
            }
            .padding()
            .tint(.gray)
                
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
        .navigationBarBackButtonHidden(true)
    }
}

#Preview {
    ResultsView(shot: shotData(date: Date(), imageURL: URL(string: "https://example.com/image.png")!), pastData: nil)
}
