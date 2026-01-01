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
4. Shooter's full body should be in frame
"""

struct UploadView: View {

    @State private var selectedImage: URL?
    
    var body: some View {
        NavigationStack{
            Text("Upload Your Jumpshot")
                .font(.largeTitle)
                .bold()
                .padding()
                .multilineTextAlignment(.center)
            
            //add image which has the video on it, grayscreen as default
            SelectionImagePicker(selectedImage: $selectedImage){
                Text("Pick your video")
                    .opacity(0.5)
            }
            
            Text("Upload Guidelines for Best Results:")
                .bold()
                .font(.title2)
                .padding()
            
            Text(uploadGuidelines)
                .padding(.horizontal)
                .padding(.bottom)
            
            //this navlink should only be active if a video has been submitted
            if let im = selectedImage{
                let newData = shotData(date: Date(), imageURL: im)
                
                NavigationLink(destination: ResultsView(shot: newData, pastData: nil)){
                    Text("Submit")
                        .font(.title)
                        .tint(Color.primary)
                        .padding(7)
                        .bold()
                        .background(RoundedRectangle(cornerRadius: 15))
                }
                .padding()
                .tint(.gray)
            }
            
        }
    }
}

#Preview {
    UploadView()
}
