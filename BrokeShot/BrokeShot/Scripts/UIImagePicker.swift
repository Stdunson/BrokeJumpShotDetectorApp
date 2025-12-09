//
//  UIImagePicker.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 12/5/25.
//

import SwiftUI

enum ImageSourceType: String, Identifiable{
    var id: String  { self.rawValue }
    
    case camera
    case photoLibrary
}

struct UIImagePicker: UIViewControllerRepresentable {
    
    @Environment(\.dismiss) private var dismiss
    
    let imageSourceType: ImageSourceType
    @Binding var selectedImage: UIImage?
    
    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self, selectedImage: $selectedImage)
    }
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let imagePicker = UIImagePickerController()
        imagePicker.delegate = context.coordinator
        imagePicker.allowsEditing = true
        
        switch imageSourceType {
        case .camera:
            imagePicker.sourceType = .camera
            imagePicker.cameraCaptureMode = .video
        case .photoLibrary:
            imagePicker.mediaTypes = ["public.movie"]
            imagePicker.sourceType = .photoLibrary
        }

        
        return imagePicker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {
        
    }
    
    typealias UIViewControllerType = UIImagePickerController
    
    class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate{
        
        let parent: UIImagePicker
        @Binding var selectedImage: UIImage?
        
        init(parent: UIImagePicker, selectedImage: Binding<UIImage?> = .constant(nil)){
            self.parent = parent
            self._selectedImage = selectedImage
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let uiImage = info[.editedImage] as? UIImage {
                self.selectedImage = uiImage
            } else if let uiImage = info[.originalImage] as? UIImage {
                self.selectedImage = uiImage
            }
            parent.dismiss()
        }
        
    }
    
}
