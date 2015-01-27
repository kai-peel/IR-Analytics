#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import wx

class IrHunterApp(wx.App):

    def OnInit(self):
        self.SetAppName("Ir Hunter")
        self.init_frame();
        return True
    
    def init_frame(self):
        #if wx.Platform == "__WXMAC__":
            #self.SetMacHelpMenuTitleName("Help")
            #self.SetMacExitMenuItemId()
        self.frame = MainFrame()
        self.SetTopWindow(self.frame)
        #self.frame.SetSize(wx.Size(800, 600))
        self.frame.Show()
        return True

class MainFrame(wx.Frame):
    """Main Frame"""
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title="Ir Hunter")
        self.createMenuBar()
        # create ToolBar
        self.createToolBar()

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label1 = wx.StaticText(panel, wx.ID_ANY, "Test Text")
        label2 = wx.StaticText(panel, wx.ID_ANY, "Hello text2")
        sizer.Add(label1, 0, wx.EXPAND)
        sizer.Add(label2)
        panel.SetSizer(sizer)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(panel, 0, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

    def createMenuBar(self):
        """Create main menu bar"""
        # Menu
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT, text = "&Exit")
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        newMenu = fileMenu.Append(wx.ID_ANY, text = "&New")
        preferencesMenu = fileMenu.Append(wx.ID_PREFERENCES, text = "&Preferences")
        menuBar.Append(fileMenu, "&File")

        helpMenu = wx.Menu()
        helpItem = helpMenu.Append(wx.ID_HELP, "Test &Help")
        aboutItem = helpMenu.Append(wx.ID_ABOUT, text="&About Ir Hunter")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

    def createToolBar(self):
        tb = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER|wx.TB_FLAT)

        tsize = (24, 24)
        new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize)
        tb.SetToolBitmapSize(tsize)
        tb.AddLabelTool(10, "New", new_bmp, shortHelp="New", longHelp="New Ir codes")
        tb.AddLabelTool(20, "Open", open_bmp, shortHelp="Open")
        tb.AddSeparator()
        tb.AddLabelTool(30, "Save", save_bmp, shortHelp="Save")
        tb.Realize()

    def OnExit(self, event):
        self.Close(True)

if __name__ == "__main__":
    app = IrHunterApp(False)
    app.MainLoop()
