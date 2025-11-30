//
//  UploadView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI
import PhotosUI

let uploadGuidelines: String =
"""
1. Make sure nobody is near the shooter in the video
2. Video should start from the catch and end at the landing
3. Closer videos with good lighting are preferred
"""

struct UploadView: View {
    @State private var selectedVideo: PhotosPickerItem?
    @State var url: URL?
    
    var body: some View {
        VStack{
            Text("Upload Your Jumpshot")
                .font(.largeTitle)
                .bold()
                .padding()
                .multilineTextAlignment(.center)
            
            //Replace this HStack with selectedImagePicker
            //Based on this video: https://youtu.be/C01gnypNugY?si=fTrnUg05kpwHuBEP
            HStack{
                PhotosPicker(selection: $selectedVideo, matching: .videos){
                    Image(systemName: "photo.badge.plus")
                        .resizable()
                        .foregroundStyle(Color.primary)
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 75, height: 50)
                }
                
                PhotosPicker(selection: $selectedVideo, matching: .videos){
                    Image(systemName: "camera")
                        .resizable()
                        .foregroundStyle(Color.primary)
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 75, height: 50)
                }
            }
            .padding()
            
            NavigationLink(destination: ResultsView()){
                Text("Submit")
                    .font(.title)
                    .foregroundStyle(Color.primary)
                    .padding(7)
                    .bold()
                    .overlay(
                        RoundedRectangle(cornerRadius: 15)
                    )
                
            }
            
            Text("Upload Guidelines for Best Results:")
                .bold()
                .font(.title2)
                .padding()
            
            Text(uploadGuidelines)
                .padding(.horizontal)
                .padding(.bottom)
            
        }
    }
}

#Preview {
    UploadView()
}
