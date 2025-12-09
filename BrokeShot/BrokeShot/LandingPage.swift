//
//  LandingPage.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI

struct LandingPage: View {
    var body: some View {
        NavigationStack{
            Text("Broke Jumpshot Detector")
                .font(.largeTitle)
                .bold()
                .padding()
                .multilineTextAlignment(.center)
            
            //hide when no jumpshot data, will comment out for now
            /*
                NavigationLink(destination: ResultsView()){
                    Text("Past jumpshots go here")
                        .tint(Color.primary)
                        .padding(7)
                        .bold()
                }
            }
             */
            
            NavigationLink(destination: UploadView()){
                Text("Get Started") //Change to "Upload" when jumpshot data
                    .font(.title)
                    .tint(Color.primary)
                    .padding(7)
                    .bold()
                    .background(RoundedRectangle(cornerRadius: 15))
                    .frame(maxWidth: .infinity)
            }
            .padding()
            .tint(.gray)
        }
    }
}

#Preview {
    LandingPage()
}
