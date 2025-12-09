//
//  ResultsView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI

struct ResultsView: View {
    
    let shot: shotData
    
    var body: some View {
        NavigationStack{
            Text("Your Jumpshot is...")
                .font(.largeTitle)
                .bold()
                .padding(.horizontal)
                .padding(.top)
                .multilineTextAlignment(.center)
            Text(determineShotMessage(shot: shot, type: 1))
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
                Text("Shot Pocket: " + determineShotMessage(shot: shot, type: 2))
                    .bold()
                    .padding(.horizontal)
                    .padding(.bottom)
                Text("Set Point: " + determineShotMessage(shot: shot, type: 3))
                    .bold()
                    .padding(.horizontal)
                    .padding(.bottom)
                Text("Follow Through: " + determineShotMessage(shot: shot, type: 4))
                    .bold()
                    .padding(.horizontal)
                    .padding(.bottom)
            }
            
            Text(determineShotMessage(shot: shot, type: 5))
                .bold()
                .padding()
                .multilineTextAlignment(.center)
            
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
    }
}

#Preview {
    ResultsView(shot: shotData(date: Date(), imageURL: URL(string: "https://example.com/image.png")!, score: 9))
}
