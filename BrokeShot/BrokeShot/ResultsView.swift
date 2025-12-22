//
//  ResultsView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI

struct ResultsView: View {
    
    var shot: shotData
    
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
                
                Image(systemName: "basketball") //will show video of the jumper
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .padding()
                
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
            vm.analyze(videoURL: shot.imageURL)
        }
        .onChange(of: vm.result) { oldValue, newValue in
            if let result = newValue {
                myScore = result.score
            }
        }
    }
}

#Preview {
    ResultsView(shot: shotData(date: Date(), imageURL: URL(string: "https://example.com/image.png")!))
}
