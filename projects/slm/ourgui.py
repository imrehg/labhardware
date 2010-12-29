import wx

def openFile(type="*"):
    ''' Simple application to present a file-selection dialog
    
    filepath = openFile(type="*")
    input parameter
    ----------------
    type: file extension to filter by default. E.g.: type="py" to select
          Python source files
        
    output parameter
    -----------------
    filepath: selected file name with complete path,
              or empty string if no file selected
    '''
    application = wx.PySimpleApp()
    dialog = wx.FileDialog(parent=None, message="Select file to open", 
            wildcard="*.%s"%(type), style=wx.OPEN)
    if dialog.ShowModal() == wx.ID_OK:
        return dialog.GetPath()
    else:
        print 'Nothing was selected.'
        return ""
