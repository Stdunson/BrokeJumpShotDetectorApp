//
//  ContentView.swift
//  BrokeShot
//
//  Created by Shavaughn Dunson on 11/28/25.
//

import SwiftUI
import SwiftData

/*
 NAVIGATION FLOW(Option 1):
 - Start at landing page
 Landing Page:
 - If user has past jumpshots, there will be a list of them in chronological order of upload
 - Clicking on any jumpshot navigates to results view
 - "Get Started" button goes to uploadview page, changes to continue if past jumpshot
 Upload View
 - Shows guidelines to upload videos
 - Options to upload from files, upload from
 - Allows cropping
 - "Submit" button navigates to results view + does API call
 Results View
- Takes jumpshot data structure as input
- Shows jumpshot analysis
- Saves jumpshot data to device
- "Main Menu" button navigates to Landing Page
 */

struct ContentView: View {
    var body: some View {
        TabView{
            
        }
    }

}

#Preview {
    ContentView()
}
