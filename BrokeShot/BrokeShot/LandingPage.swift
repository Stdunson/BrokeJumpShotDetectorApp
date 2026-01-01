//
//  LandingPage.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI
import SwiftData

struct LandingPage: View {
    
    @Environment(\.modelContext) private var modelContext
    
    @Query var jumpshots: [jumpshot]
    
    var body: some View {
        NavigationStack{
            Text("Broke Jumpshot Detector")
                .font(.largeTitle)
                .bold()
                .padding()
                .multilineTextAlignment(.center)
            
            if !jumpshots.isEmpty{
                ScrollView{
                    VStack{
                        ForEach(jumpshots){ item in
                            NavigationLink(destination: ResultsView(shot: item.shot, pastData: item)){
                                Text(item.shot.date.formatted(date: .abbreviated, time: .complete))
                                    .tint(Color.primary)
                                    .padding(7)
                                    .bold()
                            }
                        }
                    }
                }
            }
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
        .navigationBarBackButtonHidden(true)
    }
}

#Preview {
    LandingPage()
}
