//
//  ResultsView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI

struct ResultsView: View {
    var body: some View {
        Text("Your Jumpshot is...")
            .font(.largeTitle)
            .bold()
            .padding(.horizontal)
            .padding(.top)
            .multilineTextAlignment(.center)
        Text("BROKE 🧱")
            .font(.largeTitle)
            .bold()
            .padding(.horizontal)
            .padding(.bottom)
            .multilineTextAlignment(.center)
        
        Image(systemName: "basketball") //will show video of the jumper
            .resizable()
            .aspectRatio(contentMode: .fit)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .padding(.horizontal)
        
        VStack(alignment: .leading) {
            Text("Set Point: BROKE 🧱")
                .bold()
                .padding(.horizontal)
                .padding(.bottom)
            Text("Shot Pocket: BROKE 🧱")
                .bold()
                .padding(.horizontal)
                .padding(.bottom)
            Text("Follow Through: BROKE 🧱")
                .bold()
                .padding(.horizontal)
                .padding(.bottom)
        }
        
        NavigationLink(destination: LandingPage()){
            Text("Main Menu")
                .foregroundStyle(Color.primary)
                .padding(15)
                .bold()
                .frame(maxWidth: .infinity)
                .overlay(
                    RoundedRectangle(cornerRadius: 15)
                )
                .padding()
            
        }
    }
}

#Preview {
    ResultsView()
}
