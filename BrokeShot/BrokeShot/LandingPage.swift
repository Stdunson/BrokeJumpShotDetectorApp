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
    
    @Query(sort: [SortDescriptor(\jumpshot.shot.date, order: .reverse)])
        var jumpshots: [jumpshot]
    
    var body: some View {
        NavigationStack{
            Text("Broke Jumpshot Detector")
                .font(.largeTitle)
                .bold()
                .padding(.vertical, 16)
                .multilineTextAlignment(.center)
            
            if !jumpshots.isEmpty{
                ScrollView{
                    VStack(spacing: 8) {
                        ForEach(jumpshots){ item in
                            NavigationLink(destination: ResultsView(shot: item.shot, pastData: item)){
                                Text(item.shot.date.formatted(date: .abbreviated, time: .complete))
                                    .tint(Color.primary)
                                    .padding(12)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .background(Color.gray.opacity(0.05))
                                    .cornerRadius(8)
                            }
                        }
                    }
                    .padding(.horizontal, 16)
                }
                
                NavigationLink(destination: UploadView()){
                    Text("New Jumpshot")
                        .font(.title)
                        .tint(Color.primary)
                        .padding(12)
                        .bold()
                        .frame(maxWidth: .infinity)
                        .background(Color.orange.opacity(0.75))
                        .cornerRadius(12)
                }
                .padding(16)
                .tint(.orange)
                
            }else{
                NavigationLink(destination: UploadView()){
                    Text("Get Started")
                        .font(.title)
                        .tint(Color.primary)
                        .padding(12)
                        .bold()
                        .frame(maxWidth: .infinity)
                        .background(Color.orange.opacity(0.75))
                        .cornerRadius(12)
                }
                .padding(16)
                .tint(.orange)
            }
            
            
        }
        .navigationBarBackButtonHidden(true)
    }
}

#Preview {
    LandingPage()
}
