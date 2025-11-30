//
//  LandingPage.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI

struct LandingPage: View {
    var body: some View {
        VStack{
            Text("Broke Jumpshot Detector")
                .font(.largeTitle)
                .bold()
                .padding()
                .multilineTextAlignment(.center)
            
            //hide when no jumpshot data
            List{
                NavigationLink(destination: ResultsView()){
                    Text("Past jumpshots go here")
                        .padding()
                        .multilineTextAlignment(.center)
                        .foregroundStyle(Color.primary)
                }
            }
            
            NavigationLink(destination: UploadView()){
                Text("Get Started")
                    .foregroundStyle(Color.primary)
                    .padding(15)
                    .bold()
                    .frame(maxWidth: .infinity)
                    .overlay(
                        RoundedRectangle(cornerRadius: 15)
                    )
                
            }
            .padding()
        }
    }
}

#Preview {
    LandingPage()
}
