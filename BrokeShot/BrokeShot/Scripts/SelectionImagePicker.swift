//
//  SelectionImagePicker.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 12/5/25.
//

import SwiftUI

struct SelectionImagePicker<Label: View>: View {
    
    @Binding var selectedImage: UIImage?
    @ViewBuilder var label: () -> Label
    
    @State private var isConfirmationDialoguePresented: Bool = false
    @State private var selectedImageSourceType: ImageSourceType?
    
    var body: some View {
        Button {
            isConfirmationDialoguePresented.toggle()
        } label: {
            label()
        }
        .buttonStyle(.plain)
        .confirmationDialog("Choose an image", isPresented: $isConfirmationDialoguePresented) {
            Button("Camera") {
                selectedImageSourceType = .camera
            }
            Button("Library") {
                selectedImageSourceType = .photoLibrary
            }
            Button("Cancel", role: .cancel) {}
        }
        .sheet(item: $selectedImageSourceType) { sourceType in
            UIImagePicker(imageSourceType: sourceType, selectedImage: $selectedImage)
                .ignoresSafeArea()
        }
    }
}
