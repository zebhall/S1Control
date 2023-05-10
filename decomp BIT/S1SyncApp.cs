// Decompiled with JetBrains decompiler
// Type: S1Sync.S1SyncApp
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using BrukerCommunication;
using BrukerFileSystemTreeView;
using FlickerFreeListView;
using Microsoft.VisualBasic.FileIO;
using ReportGenerator.Engine;
using ReportGenerator.WpfGui;
using S1Sync.Properties;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Text;
using System.Windows.Forms;

namespace S1Sync
{
  public class S1SyncApp : Form
  {
    private const int CP_NOCLOSE_BUTTON = 512;
    private bool bPopulatingList;
    private SortOrder sortOder = SortOrder.Ascending;
    private TreeNode m_SeletedNode;
    private string m_LastDownloadPath = Settings.Default.LastDownloadedFolder;
    private FolderBrowserDialog folderDialog = new FolderBrowserDialog();
    public string m_TreeViewSelectedPath = "";
    private bool bAcceptEdit;
    private string sActualText = "";
    private bool bCancelDelete;
    private ListViewItem m_LastHoverNode;
    private FileAction m_FileAction;
    private ArrayList m_FileList = new ArrayList();
    private FileSource m_FileSource;
    private IContainer components;
    private ToolTip toolTip;
    private ImageList imageList;
    private ToolStrip toolStrip;
    private ImageList listViewImageList;
    private ImageList treeViewImageList;
    private ToolStripButton folderUpToolStripButton;
    private ToolStripButton uploadToolStripButton;
    private ToolStripButton downloadToolStripButton;
    private ImageList batteryImageList;
    private ToolStripStatusLabel lblMessage;
    private SaveFileDialog saveFileDialog;
    private OpenFileDialog openFileDialog;
    private ContextMenuStrip menuEdit;
    private ToolStripMenuItem menuDelete;
    private ToolStripMenuItem menuRename;
    private ToolStripMenuItem menuDownload;
    private ToolStripMenuItem menuNewFolder;
    private ToolStripMenuItem menuCut;
    private ToolStripMenuItem menuCopy;
    private ToolStripMenuItem menuPaste;
    private ToolStripSeparator toolStripSeparator2;
    private ToolStripSeparator toolStripSeparator3;
    private ToolStripMenuItem menuUpload;
    private ToolStripMenuItem menuView;
    private ToolStripSeparator toolStripSeparator9;
    private ToolStripSeparator lineCopyFullPathText;
    private ToolStripMenuItem menuCopyFullPathText;
    private ImageList imageListFileSystem;
    private ContextMenuStrip menuFileSystem;
    private ToolStripMenuItem menuFsProperties;
    private ToolStripMenuItem menuFsEexplore;
    private ToolStripMenuItem menuFsOpen;
    private ToolStripMenuItem menuFsEdit;
    private ToolStripMenuItem menuFsDelete;
    private ToolStripMenuItem menuFsCopy;
    private ToolStripMenuItem menuFsPaste;
    private ToolStripSeparator toolStripSeparator4;
    private ToolStripSeparator toolStripSeparator6;
    private ToolStripSeparator toolStripSeparator7;
    private ToolStripMenuItem menuLaunchExplorer;
    private ToolStripMenuItem menuFsCut;
    private ToolStripMenuItem menuFsRename;
    private ToolStripSeparator toolStripSeparator8;
    private ComboBox cmbFolderPath;
    private Splitter splitter1;
    private TreeView treeView;
    private Splitter splitter2;
    private FlickerFreeListView.FlickerFreeListView listView;
    private ColumnHeader colName;
    private ColumnHeader colSize;
    private ColumnHeader colType;
    private ColumnHeader colDateModified;
    private TextBox txtMenu;
    private BackgroundWorker threadFileSystem;
    private ToolStripButton refreshToolStripButton;
    private FileSystemTreeView treeViewFileSystem;

    public S1SyncApp(string strDeviceName)
    {
      this.InitializeComponent();
      WindowsThemeWrapper.SetWindowTheme(this.treeView.Handle, "explorer");
      WindowsThemeWrapper.SetWindowTheme(this.listView.Handle, "explorer");
      this.treeView.TreeViewNodeSorter = (IComparer) new NodeSorter();
      this.listView.ListViewItemSorter = (IComparer) new ListViewItemComparer(0, SortOrder.Ascending);
      if (strDeviceName.Length > 0)
        this.LoadRootNode(strDeviceName);
      else
        this.LoadRootNode("Unknown");
    }

    private void S1Sync_Load(object sender, EventArgs e)
    {
      this.listView.Items.Clear();
      this.UpdateListViewColumnHeader(0);
      this.treeView.ExpandAll();
      this.listView.FullRowSelect = true;
      this.threadFileSystem.RunWorkerAsync();
      if (Options.m_LoginType == LoginType.Normal)
        return;
      this.listView.LabelEdit = true;
    }

    protected override CreateParams CreateParams
    {
      get
      {
        CreateParams createParams = base.CreateParams;
        createParams.ClassStyle |= 512;
        return createParams;
      }
    }

    public void LogMessage(string strFunction, MessageType intStatus, string strMessage)
    {
    }

    public void ConnectPort()
    {
      if (BrukerCommWrapper.CommManager.IsOpen())
        return;
      BrukerCommWrapper.CommManager.Open();
    }

    private string FormatFileSize(long lSize)
    {
      NumberFormatInfo provider = new NumberFormatInfo();
      return (lSize >= 1024L ? (lSize / 1024L).ToString("n", (IFormatProvider) provider).Replace(".00", "") : (lSize != 0L ? "1" : "0")) + " KB";
    }

    private string FormatFileDate(long longDate)
    {
      try
      {
        DateTime dateTime = DateTimeOffset.FromFileTime(longDate).DateTime;
        return dateTime.ToShortDateString().ToString() + " " + dateTime.ToShortTimeString().ToString();
      }
      catch (Exception ex)
      {
        return DateTime.Now.ToShortDateString().ToString() + " " + DateTime.Now.ToShortTimeString().ToString();
      }
    }

    private string FormatFileDate(DateTime dtDate)
    {
      try
      {
        return dtDate.ToShortDateString().ToString() + " " + dtDate.ToShortTimeString().ToString();
      }
      catch (Exception ex)
      {
        DateTime now = DateTime.Now;
        string str1 = now.ToShortDateString().ToString();
        now = DateTime.Now;
        string str2 = now.ToShortTimeString().ToString();
        return str1 + " " + str2;
      }
    }

    private bool IsFileViewable(string strFileName)
    {
      bool flag = true;
      if (strFileName.ToLower().Equals("\\windows") || strFileName.ToLower().Equals("\\bruker\\bruker"))
        flag = false;
      return flag;
    }

    private void PopulateListView(string sourceDir)
    {
      this.bPopulatingList = true;
      BrukerCommWrapper.DataSyncEvent.Reset();
      this.listView.Items.Clear();
      if (!sourceDir.EndsWith("\\"))
        sourceDir += "\\";
      int num = 5;
      string str1 = "";
      while (--num > 0)
      {
        str1 = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 500);
        if (str1.Length > 5)
          break;
      }
      if (str1.Length > 5)
      {
        string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "GetFileList " + sourceDir + "*.*", 5, CommunicationManager.TimeoutType.CharCount, 1000);
        byte[] numArray = (byte[]) null;
        if (comm.StartsWith("!FW") && comm.Length == 5)
        {
          while (BrukerCommWrapper.WaitForEvent(CommunicationManager.TimeoutType.CharCount, 300, 500))
          {
            byte[] byteArray = BrukerCommWrapper.CommManager.ReadBytesAvailable(300);
            if (byteArray.Length == 300)
            {
              BRKR_WIN32_FIND_DATAA fileData = BrukerCommWrapper.ByteArrayToFileData(byteArray);
              long longDate = (long) fileData.fData.ftLastWriteTime;
              if (longDate < 0L)
                longDate = 0L;
              if ((fileData.fData.dwFileAttributes & 16U) > 0U)
              {
                if (this.IsFileViewable(sourceDir + fileData.cFileName))
                {
                  string str2 = this.FormatFileDate(longDate);
                  ListViewItem listViewItem = new ListViewItem(new string[4]
                  {
                    fileData.cFileName,
                    "",
                    "File Folder",
                    str2
                  }, -1);
                  this.InsertFolderIcon();
                  this.GetFileIconIndex("folder");
                  listViewItem.ImageKey = "folder";
                  listViewItem.Tag = (object) (sourceDir + fileData.cFileName);
                  listViewItem.SubItems[0].Tag = (object) ("0" + fileData.cFileName);
                  listViewItem.SubItems[1].Tag = (object) "0";
                  listViewItem.SubItems[2].Tag = (object) "0File Folder";
                  listViewItem.SubItems[3].Tag = (object) ("0" + str2);
                  this.listView.Items.Add(listViewItem);
                  this.AddTreeViewNode(this.treeView.SelectedNode, fileData.cFileName, listViewItem.Tag.ToString());
                }
              }
              else if (this.IsFileViewable(sourceDir + fileData.cFileName))
              {
                int startIndex = fileData.cFileName.LastIndexOf('.');
                string str3 = "";
                if (startIndex != -1)
                  str3 = fileData.cFileName.Substring(startIndex).ToLower();
                string str4 = FileAssociation.FileTypeFromExtension(str3);
                ListViewItem listViewItem = new ListViewItem(new string[4]
                {
                  fileData.cFileName,
                  this.FormatFileSize((long) fileData.fData.nFileSizeLow),
                  str4,
                  this.FormatFileDate(longDate)
                }, -1);
                this.InsertFileIcon(str3);
                int fileIconIndex = this.GetFileIconIndex(str3);
                listViewItem.ImageIndex = fileIconIndex;
                listViewItem.Tag = (object) (sourceDir + fileData.cFileName);
                listViewItem.SubItems[0].Tag = (object) ("1" + fileData.cFileName);
                listViewItem.SubItems[1].Tag = (object) ("1" + this.FormatFileSize((long) fileData.fData.nFileSizeLow));
                listViewItem.SubItems[2].Tag = (object) ("1" + str4);
                listViewItem.SubItems[3].Tag = (object) ("1" + this.FormatFileDate(longDate));
                this.listView.Items.Add(listViewItem);
              }
              Application.DoEvents();
              if (!BrukerCommWrapper.CommManager.IsOpen())
                break;
            }
            else
              break;
          }
        }
        numArray = BrukerCommWrapper.CommManager.ReadBytesAvailable();
        BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 3, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
        BrukerCommWrapper.DataSyncEvent.Set();
      }
      this.bPopulatingList = false;
    }

    private void RefreshExplorer()
    {
      if (this.treeView.SelectedNode == null)
        this.treeView.SelectedNode = this.treeView.Nodes[0];
      this.treeView.SelectedNode.Nodes.Clear();
      if (this.bPopulatingList || this.treeView.SelectedNode.Tag == null || !BrukerCommWrapper.CommManager.IsOpen())
        return;
      string str1 = this.treeView.SelectedNode.Tag.ToString();
      if (str1 == null)
        return;
      string[] strArray = str1.Split('\\');
      string str2 = "";
      foreach (string str3 in strArray)
      {
        if (str3.Length > 0)
          str2 = str2 + "\\" + str3;
      }
      if (str2.Length == 0)
        str2 = "\\";
      this.cmbFolderPath.Text = str2;
      this.sortOder = this.listView.Sorting;
      BrukerCommWrapper.DataSyncEvent.Reset();
      string sourceDir;
      if (this.treeView.SelectedNode.Parent == null && this.treeView.SelectedNode.Tag.ToString().Equals("\\"))
      {
        this.listView.Sorting = this.sortOder;
        sourceDir = "\\";
      }
      else
        sourceDir = this.treeView.SelectedNode.Tag.ToString();
      this.UpdateListViewColumnHeader(0);
      this.PopulateListView(sourceDir);
      this.m_SeletedNode = this.treeView.SelectedNode;
      if (this.listView.Items.Count == 0 || this.listView.SelectedItems.Count == 0)
        this.downloadToolStripButton.Enabled = false;
      else
        this.downloadToolStripButton.Enabled = true;
      if (str2.StartsWith("\\BRUKER"))
      {
        if (str2.StartsWith("\\BRUKER\\BRUKER"))
          this.uploadToolStripButton.Enabled = false;
        else
          this.uploadToolStripButton.Enabled = true;
      }
      else
        this.uploadToolStripButton.Enabled = false;
      BrukerCommWrapper.DataSyncEvent.Set();
    }

    private void treeView_DoubleClick(object sender, EventArgs e)
    {
      if (this.bPopulatingList || BrukerCommWrapper.CommManager.CommunicationType == CommunicationManager.CommType.DirectHardwareAccess || this.treeView.Nodes[0].Text.Equals("Disconnected"))
        return;
      this.m_SeletedNode = this.treeView.SelectedNode;
      this.treeView.SelectedNode.Nodes.Add(".");
      this.treeView.SelectedNode.Collapse();
      this.treeView.SelectedNode.Expand();
    }

    private int GetFileIconIndex(string ext)
    {
      int fileIconIndex = 0;
      try
      {
        fileIconIndex = !this.listViewImageList.Images.ContainsKey(ext) ? this.listViewImageList.Images.IndexOfKey("unknown") : this.listViewImageList.Images.IndexOfKey(ext);
      }
      catch (Exception ex)
      {
      }
      return fileIconIndex;
    }

    private int InsertFolderIcon()
    {
      int num = 0;
      try
      {
        if (!this.listViewImageList.Images.ContainsKey("folder"))
        {
          try
          {
            this.listViewImageList.Images.Add("folder", FileAssociation.GetFolderIcon(FileAssociation.IconSize.Small, FileAssociation.FolderType.Closed));
          }
          catch
          {
          }
        }
      }
      catch (Exception ex)
      {
      }
      return num;
    }

    private int InsertFileIcon(string ext)
    {
      int num = 0;
      try
      {
        if (!this.listViewImageList.Images.ContainsKey(ext))
        {
          try
          {
            Icon icon = FileAssociation.IconFromExtension(ext, FileAssociation.IconSize.Small);
            this.listViewImageList.Images.Add(ext, icon);
          }
          catch
          {
          }
        }
      }
      catch (Exception ex)
      {
      }
      return num;
    }

    private TreeNode AddTreeViewNode(TreeNode parentNode, string text, string tag)
    {
      int num = 2;
      if (!this.treeViewImageList.Images.ContainsKey("folder"))
        this.treeViewImageList.Images.Add("folder", FileAssociation.GetFolderIcon(FileAssociation.IconSize.Small, FileAssociation.FolderType.Open));
      if (this.treeViewImageList.Images.ContainsKey("folder"))
        num = this.treeViewImageList.Images.IndexOfKey("folder");
      TreeNode node = new TreeNode(text, num, num);
      node.Tag = (object) tag;
      parentNode.Nodes.Add(node);
      return node;
    }

    private void listView_DoubleClick(object sender, EventArgs e)
    {
      if (this.bPopulatingList || BrukerCommWrapper.CommManager.CommunicationType == CommunicationManager.CommType.DirectHardwareAccess || this.treeView.Nodes[0].Text.Equals("Disconnected"))
        return;
      if (this.listView.SelectedItems[0].ImageKey != "folder")
      {
        this.menuView_Click(sender, e);
      }
      else
      {
        BrukerCommWrapper.DataSyncEvent.Reset();
        string[] strArray = this.listView.SelectedItems[0].Tag.ToString().Split('\\');
        string str1 = "";
        foreach (string str2 in strArray)
        {
          if (str2.Length > 0)
            str1 = str1 + "\\" + str2;
        }
        if (str1.Length == 0)
          str1 = "\\";
        this.cmbFolderPath.Text = str1;
        bool flag = false;
        for (int index = 0; index < this.m_SeletedNode.Nodes.Count; ++index)
        {
          if (this.m_SeletedNode.Nodes[index].Text == this.listView.SelectedItems[0].Text)
          {
            this.treeView.SelectedNode = this.m_SeletedNode.Nodes[index];
            flag = true;
            break;
          }
        }
        if (flag)
        {
          this.treeView.SelectedNode.Nodes.Clear();
          this.treeView.SelectedNode.Nodes.Add(".");
          this.treeView.SelectedNode.Collapse();
          this.treeView.SelectedNode.Expand();
        }
        if (this.listView.Items.Count == 0 || this.listView.SelectedItems.Count == 0)
          this.downloadToolStripButton.Enabled = false;
        else
          this.downloadToolStripButton.Enabled = true;
        if (str1.StartsWith("\\BRUKER"))
        {
          if (str1.StartsWith("\\BRUKER\\BRUKER"))
            this.uploadToolStripButton.Enabled = false;
          else
            this.uploadToolStripButton.Enabled = true;
        }
        else
          this.uploadToolStripButton.Enabled = false;
        BrukerCommWrapper.DataSyncEvent.Set();
      }
    }

    private void listView_ItemSelectionChanged(
      object sender,
      ListViewItemSelectionChangedEventArgs e)
    {
      if (this.listView.Columns.Count == 2)
        return;
      if (this.listView.Items.Count == 0 || this.listView.SelectedItems.Count == 0)
        this.downloadToolStripButton.Enabled = false;
      else
        this.downloadToolStripButton.Enabled = true;
    }

    public void GetXrayOpsVersion()
    {
    }

    private void UpdateListViewColumnHeader(int iType)
    {
      this.colName.Text = "Name";
      this.colName.Width = 200;
      this.colSize.Text = "Size";
      this.colSize.Width = 75;
      this.colType.Text = "Type";
      this.colType.Width = 75;
      this.colDateModified.Text = "Date Modified";
      this.colDateModified.Width = 150;
      this.listView.Columns.Clear();
      this.listView.Columns.AddRange(new ColumnHeader[4]
      {
        this.colName,
        this.colSize,
        this.colType,
        this.colDateModified
      });
      this.listView.Sorting = this.sortOder;
      this.listView.GridLines = false;
      this.listView.ShowGroups = false;
      this.folderUpToolStripButton.Enabled = true;
    }

    private void AddListViewItem(string nodeText, string subText) => this.listView.Items.Add(new ListViewItem(nodeText)
    {
      SubItems = {
        subText
      }
    });

    private void AddListViewItem(ListViewGroup group, string nodeText, string subText) => this.listView.Items.Add(new ListViewItem(nodeText, group)
    {
      SubItems = {
        subText
      }
    });

    private string FindColumnType(int columnNo)
    {
      string columnType = "String";
      if (this.listView.Columns[columnNo].Text == "Date Modified")
        columnType = "DateTime";
      else if (this.listView.Columns[columnNo].Text == "Size")
        columnType = "Long";
      return columnType;
    }

    private void listView_ColumnClick(object sender, ColumnClickEventArgs e)
    {
      this.listView.ListViewItemSorter = (IComparer) new ListViewItemComparer(e.Column, this.listView.Sorting, this.FindColumnType(e.Column));
      this.listView.Sort();
      if (this.listView.Sorting == SortOrder.Ascending)
        this.listView.Sorting = SortOrder.Descending;
      else
        this.listView.Sorting = SortOrder.Ascending;
    }

    private void downloadToolStripButton_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList)
        return;
      BrukerCommWrapper.DataSyncEvent.Reset();
      if (this.listView.Items.Count == 0)
      {
        int num = (int) MessageBox.Show((IWin32Window) this, "No files selected for download.", "Download", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
        BrukerCommWrapper.DataSyncEvent.Set();
      }
      else if (this.listView.SelectedItems.Count == 0)
      {
        int num = (int) MessageBox.Show((IWin32Window) this, "No files selected for download.", "Download", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
        BrukerCommWrapper.DataSyncEvent.Set();
      }
      else
      {
        string[] source = new string[this.listView.SelectedItems.Count];
        int num1 = 0;
        foreach (ListViewItem selectedItem in this.listView.SelectedItems)
        {
          if (!selectedItem.Tag.ToString().ToLower().EndsWith("password.csv") || Options.m_LoginType > LoginType.Normal)
            source[num1++] = selectedItem.Tag.ToString();
        }
        if (num1 == 0)
          return;
        if (this.m_LastDownloadPath.Length == 0)
          this.m_LastDownloadPath = Environment.GetFolderPath(Environment.SpecialFolder.Personal);
        this.folderDialog.SelectedPath = this.m_LastDownloadPath;
        this.folderDialog.ShowNewFolderButton = true;
        if (this.folderDialog.ShowDialog() == DialogResult.OK)
        {
          this.m_LastDownloadPath = this.folderDialog.SelectedPath;
          string selectedPath = this.folderDialog.SelectedPath;
          this.m_TreeViewSelectedPath = this.m_SeletedNode == null ? "" : this.m_SeletedNode.Tag.ToString();
          int num2 = (int) new Download(this.m_TreeViewSelectedPath, source, selectedPath, true).ShowDialog();
          Settings.Default.LastDownloadedFolder = this.m_LastDownloadPath;
          Settings.Default.Save();
        }
        BrukerCommWrapper.DataSyncEvent.Set();
      }
    }

    private void uploadToolStripButton_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList || this.m_SeletedNode == null)
        return;
      BrukerCommWrapper.DataSyncEvent.Reset();
      string dest = this.m_SeletedNode.Tag.ToString();
      if (dest.Length == 0)
      {
        int num = (int) MessageBox.Show((IWin32Window) this, "Please select the destination folder", "Upload", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
      }
      else
      {
        FileAndFolderDialog fileAndFolderDialog = new FileAndFolderDialog();
        DialogResult dialogResult = DialogResult.Cancel;
        if (fileAndFolderDialog.ShowDialog() == DialogResult.OK)
          dialogResult = new Upload(fileAndFolderDialog.FileNames, dest, 0, true, true).ShowDialog();
        BrukerCommWrapper.DataSyncEvent.Set();
        if (dialogResult != DialogResult.OK)
          return;
        this.refreshToolStripButton_Click(sender, e);
      }
    }

    private void refreshToolStripButton_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList)
        return;
      this.ConnectPort();
      if (this.treeView.SelectedNode == null)
        this.treeView.SelectedNode = this.treeView.Nodes[0];
      if (this.m_SeletedNode != null)
        this.treeView.SelectedNode = this.m_SeletedNode;
      this.treeView_DoubleClick(sender, e);
      this.treeView.Focus();
    }

    private void folderUpToolStripButton_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList || this.m_SeletedNode == null || this.m_SeletedNode.Parent == null || this.m_SeletedNode.Parent.Tag.ToString() == "Hardware")
        return;
      this.treeView.SelectedNode = this.m_SeletedNode.Parent;
      this.treeView_DoubleClick(sender, e);
      this.treeView.Focus();
    }

    private void renameToolStripMenuItem_Click(object sender, EventArgs e)
    {
      this.sActualText = this.listView.SelectedItems[0].Text;
      this.listView.SelectedItems[0].BeginEdit();
    }

    private void menuEdit_Opening(object sender, CancelEventArgs e)
    {
      bool flag1 = false;
      this.menuDelete.Enabled = false;
      this.menuRename.Enabled = false;
      this.menuNewFolder.Enabled = false;
      this.menuDownload.Enabled = false;
      this.menuCut.Enabled = false;
      this.menuCopy.Enabled = false;
      this.menuPaste.Enabled = false;
      this.menuUpload.Enabled = false;
      this.menuView.Enabled = false;
      this.menuCopyFullPathText.Enabled = false;
      if (this.bPopulatingList)
        return;
      if (this.listView.SelectedItems.Count >= 1)
      {
        this.menuDownload.Enabled = true;
        this.menuCut.Enabled = true;
        this.menuCopy.Enabled = true;
        this.menuDelete.Enabled = true;
        this.menuView.Enabled = true;
        if (this.listView.SelectedItems.Count == 1)
        {
          this.menuRename.Enabled = true;
          if (this.listView.SelectedItems[0].ImageKey != "folder")
          {
            string upper = this.listView.SelectedItems[0].Tag.ToString().ToUpper();
            if (upper.EndsWith("DLL") || upper.EndsWith("EXE") || upper.EndsWith("TTF") || upper.EndsWith("BIN"))
              this.menuView.Enabled = false;
            if (upper.EndsWith("PASSWORD.CSV"))
            {
              this.menuView.Enabled = false;
              this.menuCopy.Enabled = false;
              this.menuDownload.Enabled = false;
              this.menuUpload.Enabled = false;
              flag1 = true;
            }
            this.menuCopyFullPathText.Text = "Copy File Path";
          }
          else
            this.menuCopyFullPathText.Text = "Copy Folder Path";
          this.menuCopyFullPathText.Enabled = true;
        }
      }
      if (this.treeView.Nodes.Count > 0 && this.treeView.Nodes[0].Text != "Disconnected" && this.treeView.SelectedNode.Tag.ToString().Length > 0)
      {
        this.menuNewFolder.Enabled = true;
        if (this.m_SeletedNode.Tag.ToString().StartsWith("\\BRUKER"))
        {
          if (this.m_SeletedNode.Tag.ToString().StartsWith("\\BRUKER\\BRUKER") | flag1)
            this.menuUpload.Enabled = false;
          else
            this.menuUpload.Enabled = true;
        }
        if ((this.m_FileAction == FileAction.Copy || this.m_FileAction == FileAction.Cut) && this.m_SeletedNode.Parent != null)
          this.menuPaste.Enabled = true;
      }
      this.menuCopyFullPathText.Visible = Options.m_LoginType != LoginType.Normal && !flag1;
      this.lineCopyFullPathText.Visible = Options.m_LoginType != LoginType.Normal && !flag1;
      bool flag2 = Options.m_LoginType != 0;
      this.menuCut.Visible = flag2 && !flag1;
      this.menuDelete.Visible = flag2 && !flag1;
      this.menuRename.Visible = flag2 && !flag1;
    }

    private void deleteToolStripMenuItem_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList)
        return;
      this.bCancelDelete = false;
      if (DialogResult.Yes != MessageBox.Show((IWin32Window) this, "Do you want to delete the file(s) permanently?", "Confirm File Delete", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation))
        return;
      this.bPopulatingList = true;
      ArrayList arrayList = new ArrayList();
      for (int index = 0; index < this.listView.SelectedItems.Count; ++index)
        arrayList.Add(this.listView.SelectedItems[index].Tag);
      foreach (object obj in arrayList)
      {
        int num = 5;
        string str1 = obj.ToString();
        this.lblMessage.Text = "Deleting " + str1;
        string str2 = "DeleteFile ";
        BRKR_WIN32_FIND_DATA_EXT fileStatus = BrukerCommWrapper.GetFileStatus(str1);
        if ((fileStatus.dwFileAttributes & 16U) > 0U)
          str2 = "DeleteFolder ";
        do
          ;
        while (--num > 0 && BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000).Length <= 5);
        string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, str2 + str1, 4, CommunicationManager.TimeoutType.CharCount, 5000);
        StringBuilder stringBuilder = new StringBuilder();
        if (comm.StartsWith("!FW") && comm.Length == 4)
        {
          this.FindListItemByTag(str1)?.Remove();
          if ((fileStatus.dwFileAttributes & 16U) > 0U)
            this.FindByTag(str1)?.Remove();
        }
        BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 3, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
        Application.DoEvents();
        if (this.bCancelDelete)
          break;
      }
      this.lblMessage.Text = "";
      this.listView_Click(sender, e);
      this.bPopulatingList = false;
    }

    private void treeView_BeforeExpand(object sender, TreeViewCancelEventArgs e) => this.RefreshExplorer();

    private void treeView_AfterCollapse(object sender, TreeViewEventArgs e)
    {
    }

    private void ResetRootNode(string needle)
    {
      this.treeView.Nodes[0].Text = needle;
      this.treeView.Nodes[0].Tag = (object) "\\";
      this.treeView.Nodes[0].Nodes.Clear();
      this.treeView.Nodes[0].Collapse();
    }

    private void LoadRootNode(string needle)
    {
      this.treeView.Nodes[0].Text = needle;
      this.treeView.Nodes[0].Tag = (object) "\\";
      this.treeView.Nodes[0].Nodes.Clear();
      this.treeView.Nodes[0].Nodes.Add(".");
      this.m_SeletedNode = this.treeView.Nodes[0];
      this.m_SeletedNode.Collapse();
      this.m_SeletedNode.Expand();
    }

    private TreeNode GetNode(string path, string tag) => new TreeNode()
    {
      Text = path,
      Tag = (object) tag,
      ImageIndex = 0
    };

    private void listView_KeyDown(object sender, KeyEventArgs e)
    {
      switch (e.KeyCode)
      {
        case Keys.Return:
          this.listView_DoubleClick(sender, (EventArgs) e);
          break;
        case Keys.Escape:
          this.bCancelDelete = true;
          this.m_FileAction = FileAction.None;
          this.m_FileSource = FileSource.None;
          this.m_FileList.Clear();
          break;
        case Keys.Delete:
          if (Options.m_LoginType == LoginType.Normal)
            break;
          this.deleteToolStripMenuItem_Click(sender, (EventArgs) e);
          break;
        case Keys.F2:
          if (Options.m_LoginType == LoginType.Normal || this.listView.SelectedItems.Count <= 0)
            break;
          this.listView.LabelEdit = true;
          this.sActualText = this.listView.SelectedItems[0].Text;
          this.listView.SelectedItems[0].BeginEdit();
          break;
      }
    }

    private bool IsFileOrFolderExits(string file)
    {
      BRKR_WIN32_FIND_DATA_EXT fileStatus = BrukerCommWrapper.GetFileStatus(file);
      return fileStatus.dwFileAttributes != 0U || fileStatus.nFileSizeHigh != 0U || fileStatus.nFileSizeLow != 0U;
    }

    private bool ExecuteRenameFile(string source, string dest)
    {
      if (source == dest)
        return false;
      string str1 = this.listView.SelectedItems[0].Tag.ToString();
      string fileName = str1.Replace(source, dest);
      BRKR_WIN32_FIND_DATA_EXT fileStatus1 = BrukerCommWrapper.GetFileStatus(fileName);
      if (fileStatus1.dwFileAttributes != 0U || fileStatus1.nFileSizeHigh != 0U || fileStatus1.nFileSizeLow != 0U)
      {
        int num = (int) MessageBox.Show((IWin32Window) this, "Cannot rename " + fileName + ". A file with the name you specified already exists. Specify a different name.", "Rename File", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
        return false;
      }
      BRKR_WIN32_FIND_DATA_EXT fileStatus2 = BrukerCommWrapper.GetFileStatus(str1);
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
      string str2 = (fileStatus2.dwFileAttributes & 16U) <= 0U ? BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "RenameFile " + str1 + ";" + fileName, 4, CommunicationManager.TimeoutType.CharCount, 30000) : BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "RenameFolder " + str1 + ";" + fileName, 4, CommunicationManager.TimeoutType.CharCount, 30000);
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
      int num1 = str2.StartsWith("!FW") ? 1 : 0;
      if (num1 == 0)
        return num1 != 0;
      this.listView.SelectedItems[0].Tag = (object) fileName;
      if ((fileStatus2.dwFileAttributes & 16U) <= 0U)
        return num1 != 0;
      TreeNode byTag = this.FindByTag(str1);
      if (byTag == null)
        return num1 != 0;
      byTag.Tag = (object) fileName;
      return num1 != 0;
    }

    private string BuildCmdString(string sCmd)
    {
      string str1 = "";
      string str2 = sCmd;
      char[] chArray = new char[1]{ '\\' };
      foreach (string str3 in str2.Split(chArray))
      {
        if (str3.Length > 0)
          str1 = str1 + "\\" + str3;
      }
      if (str1.Length == 0)
        str1 = "\\";
      return str1;
    }

    private ListViewItem FindListItemByTag(string sTag)
    {
      ListViewItem listItemByTag1 = (ListViewItem) null;
      foreach (ListViewItem listItemByTag2 in this.listView.Items)
      {
        if (listItemByTag2.Tag.ToString().ToLower() == sTag.ToLower())
          return listItemByTag2;
      }
      return listItemByTag1;
    }

    private TreeNode FindByTag(string sTag)
    {
      TreeNode byTag = (TreeNode) null;
      foreach (TreeNode node in this.treeView.Nodes)
      {
        if (node.Tag.ToString().ToLower() == sTag.ToLower())
          return node;
        byTag = this.FindRecursiveTag(node, sTag);
        if (byTag != null)
          break;
      }
      return byTag;
    }

    private TreeNode FindRecursiveTag(TreeNode treeNode, string sTag)
    {
      TreeNode recursiveTag = (TreeNode) null;
      foreach (TreeNode node in treeNode.Nodes)
      {
        if (node.Tag.ToString().ToLower() == sTag.ToLower())
          return node;
        recursiveTag = this.FindRecursiveTag(node, sTag);
        if (recursiveTag != null)
          break;
      }
      return recursiveTag;
    }

    private void UnsetAllSelectedItems()
    {
      foreach (ListViewItem selectedItem in this.listView.SelectedItems)
        selectedItem.Selected = false;
    }

    private bool FindNodeAndExecute(string sCmd)
    {
      bool nodeAndExecute = false;
      if (this.treeView.Nodes[0].Text.Equals("Disconnected"))
        return nodeAndExecute;
      TreeNode byTag = this.FindByTag(this.BuildCmdString(sCmd));
      if (byTag != null)
      {
        this.treeView.SelectedNode = byTag;
        this.treeView_DoubleClick((object) null, (EventArgs) null);
        this.treeView.Focus();
        nodeAndExecute = true;
      }
      else
      {
        int listViewItem = this.FindListViewItem(sCmd);
        if (listViewItem >= 0)
        {
          this.UnsetAllSelectedItems();
          this.listView.Items[listViewItem].Selected = true;
          this.listView_DoubleClick((object) null, (EventArgs) null);
          this.listView.Focus();
          nodeAndExecute = true;
        }
      }
      return nodeAndExecute;
    }

    private int FindListViewItem(string sTag)
    {
      for (int index = 0; index < this.listView.Items.Count; ++index)
      {
        if (this.listView.Items[index].Tag.ToString().ToLower() == sTag.ToLower())
          return index;
      }
      return -1;
    }

    private void cmbFolderPath_KeyDown(object sender, KeyEventArgs e)
    {
      if (e.KeyValue != 13 || !this.FindNodeAndExecute(this.cmbFolderPath.Text) || this.cmbFolderPath.Items.IndexOf((object) this.cmbFolderPath.Text) != -1)
        return;
      this.cmbFolderPath.Items.Add((object) this.cmbFolderPath.Text);
    }

    private void cmbFolderPath_SelectedIndexChanged(object sender, EventArgs e)
    {
      if (!this.FindNodeAndExecute(this.cmbFolderPath.Text) || this.cmbFolderPath.Items.IndexOf((object) this.cmbFolderPath.Text) != -1)
        return;
      this.cmbFolderPath.Items.Add((object) this.cmbFolderPath.Text);
    }

    private void downloadToolStripMenuItem_Click(object sender, EventArgs e) => this.downloadToolStripButton_Click(sender, e);

    private void listView_DragOver(object sender, DragEventArgs e)
    {
      if (e.Data.GetDataPresent(typeof (List<TreeNode>)))
      {
        Point client = this.listView.PointToClient(new Point(e.X, e.Y));
        ListViewItem itemAt = this.listView.GetItemAt(client.X, client.Y);
        if (this.m_LastHoverNode == null)
        {
          foreach (ListViewItem selectedItem in this.listView.SelectedItems)
            selectedItem.Selected = false;
        }
        if (this.m_LastHoverNode != null && this.m_LastHoverNode != itemAt)
          this.m_LastHoverNode.Selected = false;
        if (itemAt == null || itemAt.ImageKey != "folder")
        {
          e.Effect = DragDropEffects.None;
        }
        else
        {
          List<TreeNode> data = (List<TreeNode>) e.Data.GetData(typeof (List<TreeNode>));
          itemAt.Selected = true;
          this.listView.Focus();
          this.m_LastHoverNode = itemAt;
          e.Effect = DragDropEffects.Copy;
        }
      }
      else
        e.Effect = DragDropEffects.None;
    }

    private void listView_DragDrop(object sender, DragEventArgs e)
    {
      if (this.bPopulatingList || !BrukerCommWrapper.CommManager.IsOpen())
        return;
      if (e.Data.GetDataPresent(typeof (List<TreeNode>)))
      {
        Point client = this.listView.PointToClient(new Point(e.X, e.Y));
        ListViewItem itemAt = this.listView.GetItemAt(client.X, client.Y);
        List<TreeNode> data = (List<TreeNode>) e.Data.GetData(typeof (List<TreeNode>));
        string[] sources = new string[data.Count];
        for (int index = 0; index < data.Count; ++index)
          sources[index] = data[index].Tag.ToString();
        string dest = itemAt.Tag.ToString();
        if (e.Effect == DragDropEffects.Copy)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num = (int) new Upload(sources, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        else if (e.Effect == DragDropEffects.Move)
        {
          if (Options.m_LoginType == LoginType.Normal)
          {
            int num = (int) MessageBox.Show("You don't have the permissions to move the files.", "S1 Sync", MessageBoxButtons.OK);
            this.m_LastHoverNode = (ListViewItem) null;
            return;
          }
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num1 = (int) new Upload(sources, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        if (e.Effect == DragDropEffects.Copy || e.Effect == DragDropEffects.Move)
        {
          this.treeView_DoubleClick((object) null, (EventArgs) null);
          foreach (ListViewItem listViewItem in this.listView.Items)
          {
            foreach (string str1 in sources)
            {
              string str2 = str1.Substring(str1.LastIndexOf("\\"));
              if (dest + str2 == listViewItem.Tag.ToString())
              {
                listViewItem.Selected = true;
                listViewItem.EnsureVisible();
                break;
              }
            }
          }
        }
        this.m_LastHoverNode = (ListViewItem) null;
      }
      e.Data.SetData((object) null);
      e.Effect = DragDropEffects.None;
      this.Invalidate(new Region(this.ClientRectangle));
    }

    private bool IsDroppable(
      string sTag,
      ListView.SelectedListViewItemCollection itemCollection)
    {
      foreach (ListViewItem listViewItem in itemCollection)
      {
        if (listViewItem.Tag.ToString().ToLower() == "\\bruker\\system\\password.csv" && Options.m_LoginType == LoginType.Normal || listViewItem.Tag.ToString().ToLower() == sTag.ToLower())
          return false;
      }
      return true;
    }

    private void treeView_DragDrop(object sender, DragEventArgs e)
    {
      if (this.bPopulatingList || !BrukerCommWrapper.CommManager.IsOpen())
        return;
      if (this.IsFileSystemObject(e))
      {
        Array data = (Array) e.Data.GetData(DataFormats.FileDrop);
        string[] sources = new string[data.Length];
        int num1 = 0;
        foreach (object obj in data)
          sources[num1++] = obj.ToString();
        if (e.Effect == DragDropEffects.Copy)
        {
          string dest = this.treeView.SelectedNode.Tag.ToString();
          if (dest == "\\" || this.treeView.SelectedNode.Parent == null)
            return;
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num2 = (int) new Upload(sources, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
          this.treeView_DoubleClick((object) null, (EventArgs) null);
          foreach (ListViewItem listViewItem in this.listView.Items)
          {
            foreach (string str1 in sources)
            {
              string str2 = str1.Substring(str1.LastIndexOf("\\"));
              if (dest + str2 == listViewItem.Tag.ToString())
              {
                listViewItem.Selected = true;
                listViewItem.EnsureVisible();
                break;
              }
            }
          }
        }
      }
      else if (e.Data.GetDataPresent(typeof (ListView.SelectedListViewItemCollection)))
      {
        TreeNode nodeAt = this.treeView.GetNodeAt(this.treeView.PointToClient(new Point(e.X, e.Y)));
        this.treeView.SelectedNode = nodeAt;
        ListView.SelectedListViewItemCollection data = (ListView.SelectedListViewItemCollection) e.Data.GetData(typeof (ListView.SelectedListViewItemCollection));
        string[] items = new string[data.Count];
        for (int index = 0; index < data.Count; ++index)
          items[index] = data[index].Tag.ToString();
        string dest = nodeAt.Tag.ToString();
        if (e.Effect == DragDropEffects.Copy)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num = (int) new Copy(dest, items).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        else if (e.Effect == DragDropEffects.Move)
        {
          if (Options.m_LoginType == LoginType.Normal)
          {
            int num = (int) MessageBox.Show("You don't have the permissions to move the files.", "S1 Sync", MessageBoxButtons.OK);
            return;
          }
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num3 = (int) new S1Sync.Move(dest, items).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        if (e.Effect == DragDropEffects.Copy || e.Effect == DragDropEffects.Move)
        {
          this.treeView_DoubleClick((object) null, (EventArgs) null);
          foreach (ListViewItem listViewItem in this.listView.Items)
          {
            foreach (string str3 in items)
            {
              string str4 = str3.Substring(str3.LastIndexOf("\\"));
              if (dest + str4 == listViewItem.Tag.ToString())
              {
                listViewItem.Selected = true;
                listViewItem.EnsureVisible();
                break;
              }
            }
          }
        }
      }
      else if (e.Data.GetDataPresent(typeof (List<TreeNode>)))
      {
        TreeNode nodeAt = this.treeView.GetNodeAt(this.treeView.PointToClient(new Point(e.X, e.Y)));
        this.treeView.SelectedNode = nodeAt;
        List<TreeNode> data = (List<TreeNode>) e.Data.GetData(typeof (List<TreeNode>));
        string[] sources = new string[data.Count];
        for (int index = 0; index < data.Count; ++index)
          sources[index] = data[index].Tag.ToString();
        nodeAt.Tag.ToString();
        string dest = "";
        if (e.Effect == DragDropEffects.Copy)
        {
          dest = this.treeView.SelectedNode.Tag.ToString();
          if (dest == "\\" || this.treeView.SelectedNode.Parent == null)
            return;
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num = (int) new Upload(sources, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        else if (e.Effect == DragDropEffects.Move)
        {
          dest = this.treeView.SelectedNode.Tag.ToString();
          if (dest == "\\" || this.treeView.SelectedNode.Parent == null)
            return;
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num = (int) new Upload(sources, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        if (e.Effect == DragDropEffects.Copy || e.Effect == DragDropEffects.Move)
        {
          this.treeView_DoubleClick((object) null, (EventArgs) null);
          foreach (ListViewItem listViewItem in this.listView.Items)
          {
            foreach (string str5 in sources)
            {
              string str6 = str5.Substring(str5.LastIndexOf("\\"));
              if (dest + str6 == listViewItem.Tag.ToString())
              {
                listViewItem.Selected = true;
                listViewItem.EnsureVisible();
                break;
              }
            }
          }
        }
        this.m_LastHoverNode = (ListViewItem) null;
      }
      e.Effect = DragDropEffects.None;
      this.Invalidate(new Region(this.ClientRectangle));
    }

    private bool IsFileSystemObject(DragEventArgs e)
    {
      bool flag = false;
      foreach (string format in e.Data.GetFormats())
      {
        if (format == "Shell IDList Array")
        {
          flag = true;
          break;
        }
      }
      return flag;
    }

    private void treeView_DragOver(object sender, DragEventArgs e)
    {
      if (this.IsFileSystemObject(e))
      {
        TreeNode nodeAt = this.treeView.GetNodeAt(this.treeView.PointToClient(new Point(e.X, e.Y)));
        if (nodeAt == null || nodeAt.Parent == null)
        {
          e.Effect = DragDropEffects.None;
        }
        else
        {
          this.treeView.SelectedNode = nodeAt;
          this.treeView.Focus();
          e.Effect = DragDropEffects.Copy;
        }
      }
      else if (e.Data.GetDataPresent(typeof (ListView.SelectedListViewItemCollection)))
      {
        TreeNode nodeAt = this.treeView.GetNodeAt(this.treeView.PointToClient(new Point(e.X, e.Y)));
        if (nodeAt == null || nodeAt.Parent == null)
        {
          e.Effect = DragDropEffects.None;
        }
        else
        {
          ListView.SelectedListViewItemCollection data = (ListView.SelectedListViewItemCollection) e.Data.GetData(typeof (ListView.SelectedListViewItemCollection));
          this.treeView.SelectedNode = nodeAt;
          this.treeView.Focus();
          if (!this.IsDroppable(nodeAt.Tag.ToString(), data))
            e.Effect = DragDropEffects.None;
          else if ((e.KeyState & 8) == 8 && (e.AllowedEffect & DragDropEffects.Copy) == DragDropEffects.Copy)
            e.Effect = DragDropEffects.Copy;
          else if ((e.KeyState & 4) == 4 && (e.AllowedEffect & DragDropEffects.Move) == DragDropEffects.Move)
            e.Effect = DragDropEffects.Move;
          else if ((e.AllowedEffect & DragDropEffects.Move) == DragDropEffects.Move)
            e.Effect = DragDropEffects.Move;
          else
            e.Effect = DragDropEffects.None;
        }
      }
      else if (e.Data.GetDataPresent(typeof (List<TreeNode>)))
      {
        TreeNode nodeAt = this.treeView.GetNodeAt(this.treeView.PointToClient(new Point(e.X, e.Y)));
        if (nodeAt == null || nodeAt.Parent == null)
        {
          e.Effect = DragDropEffects.None;
        }
        else
        {
          List<TreeNode> data = (List<TreeNode>) e.Data.GetData(typeof (List<TreeNode>));
          this.treeView.SelectedNode = nodeAt;
          this.treeView.Focus();
          e.Effect = DragDropEffects.Copy;
        }
      }
      else
        e.Effect = DragDropEffects.None;
    }

    private string GetNewFolderName()
    {
      string str = "New Folder";
      ulong num1 = 0;
      foreach (ListViewItem listViewItem in this.listView.Items)
      {
        string text = listViewItem.Text;
        if (text.ToLower().StartsWith("new folder"))
        {
          if (text.Length > "new folder".Length)
          {
            ulong num2 = (ulong) Convert.ToDouble(text.Substring("new folder".Length));
            num1 = num2 > num1 ? num2 : num1;
          }
          else
            num1 = 1UL;
        }
      }
      return num1 < 1UL ? str : str + " " + (num1 + 1UL).ToString();
    }

    private void newFolderToolStripMenuItem_Click(object sender, EventArgs e)
    {
      string newFolderName = this.GetNewFolderName();
      DateTime now = DateTime.Now;
      ListViewItem listViewItem = new ListViewItem(new string[4]
      {
        newFolderName,
        "",
        "File Folder",
        this.FormatFileDate(now)
      }, -1);
      this.InsertFolderIcon();
      this.GetFileIconIndex("folder");
      listViewItem.ImageKey = "folder";
      string str = this.m_SeletedNode.Tag.ToString();
      string tag = str.Length <= 1 ? str + newFolderName : str + "\\" + newFolderName;
      listViewItem.Tag = (object) tag;
      listViewItem.SubItems[0].Tag = (object) ("0" + newFolderName);
      listViewItem.SubItems[1].Tag = (object) "0";
      listViewItem.SubItems[2].Tag = (object) "0File Folder";
      listViewItem.SubItems[3].Tag = (object) ("0" + this.FormatFileDate(now));
      this.UnsetAllSelectedItems();
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "CreateFolder " + tag, 4, CommunicationManager.TimeoutType.CharCount, 30000);
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
      if (!comm.StartsWith("!FW"))
        return;
      this.AddTreeViewNode(this.m_SeletedNode, newFolderName, tag);
      this.listView.Items.Add(listViewItem);
      listViewItem.Selected = true;
      listViewItem.Focused = true;
      this.listView.LabelEdit = true;
      this.listView.SelectedItems[0].BeginEdit();
    }

    private void listView_ItemDrag(object sender, ItemDragEventArgs e)
    {
      if (this.listView.SelectedItems.Count <= 0 || e.Button != MouseButtons.Left)
        return;
      int num = (int) this.DoDragDrop((object) this.listView.SelectedItems, DragDropEffects.All);
    }

    private void txtMenu_Enter(object sender, EventArgs e) => this.sActualText = this.txtMenu.Text;

    private void S1SyncApp_FormClosed(object sender, FormClosedEventArgs e)
    {
      Point location = this.Location;
      Size size = this.Size;
      Settings.Default.WindowLocation = location;
      Settings.Default.WindowSize = size;
      Settings.Default.Save();
      if (BrukerCommWrapper.CommManager.IsOpen())
        BrukerCommWrapper.CommManager.ClosePort();
      ((S1SyncMain) this.MdiParent).menuDisconnect.Checked = false;
      ((S1SyncMain) this.MdiParent).menuConnect.Checked = false;
    }

    private void menuCut_Click(object sender, EventArgs e)
    {
      this.m_FileAction = FileAction.Cut;
      this.m_FileSource = FileSource.ListView;
      this.m_FileList.Clear();
      for (int index = 0; index < this.listView.SelectedItems.Count; ++index)
        this.m_FileList.Add(this.listView.SelectedItems[index].Tag);
    }

    private void menuCopy_Click(object sender, EventArgs e)
    {
      this.m_FileAction = FileAction.Copy;
      this.m_FileSource = FileSource.ListView;
      this.m_FileList.Clear();
      for (int index = 0; index < this.listView.SelectedItems.Count; ++index)
        this.m_FileList.Add(this.listView.SelectedItems[index].Tag);
    }

    private void menuPaste_Click(object sender, EventArgs e)
    {
      if (this.m_FileSource == FileSource.ListView)
      {
        string dest = this.m_SeletedNode.Tag.ToString();
        string[] array = (string[]) this.m_FileList.ToArray(typeof (string));
        if (this.m_FileAction == FileAction.Copy)
        {
          int num1 = (int) new Copy(dest, array).ShowDialog();
        }
        else if (this.m_FileAction == FileAction.Cut)
        {
          int num2 = (int) new S1Sync.Move(dest, array).ShowDialog();
        }
        if (this.m_FileAction != FileAction.Copy && this.m_FileAction != FileAction.Cut)
          return;
        this.treeView_DoubleClick((object) null, (EventArgs) null);
        foreach (ListViewItem listViewItem in this.listView.Items)
        {
          foreach (string file in this.m_FileList)
          {
            string str = file.Substring(file.LastIndexOf("\\"));
            if (dest + str == listViewItem.Tag.ToString())
            {
              listViewItem.Selected = true;
              listViewItem.EnsureVisible();
              break;
            }
          }
        }
      }
      else
      {
        if (this.m_FileSource != FileSource.TreeView)
          return;
        string dest = this.m_SeletedNode.Tag.ToString();
        string[] array = (string[]) this.m_FileList.ToArray(typeof (string));
        if (this.m_FileAction == FileAction.Copy)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num = (int) new Upload(array, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        else if (this.m_FileAction == FileAction.Cut)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          int num = (int) new Upload(array, dest, 0, true, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        if (this.m_FileAction != FileAction.Copy && this.m_FileAction != FileAction.Cut)
          return;
        this.treeView_DoubleClick((object) null, (EventArgs) null);
        foreach (ListViewItem listViewItem in this.listView.Items)
        {
          foreach (string file in this.m_FileList)
          {
            string str = file.Substring(file.LastIndexOf("\\"));
            if (dest + str == listViewItem.Tag.ToString())
            {
              listViewItem.Selected = true;
              listViewItem.EnsureVisible();
              break;
            }
          }
        }
      }
    }

    private void menuUpload_Click(object sender, EventArgs e) => this.uploadToolStripButton_Click(sender, e);

    private void listView_Click(object sender, EventArgs e)
    {
      if (this.listView.Items.Count == 0 || this.listView.SelectedItems.Count == 0)
        this.downloadToolStripButton.Enabled = false;
      else
        this.downloadToolStripButton.Enabled = true;
      if (this.m_SeletedNode.Tag.ToString().StartsWith("\\BRUKER"))
      {
        if (this.m_SeletedNode.Tag.ToString().StartsWith("\\BRUKER\\BRUKER"))
          this.uploadToolStripButton.Enabled = false;
        else
          this.uploadToolStripButton.Enabled = true;
      }
      else
        this.uploadToolStripButton.Enabled = false;
    }

    private void LaunchApp(Form formToLaunch)
    {
      foreach (Form mdiChild in this.MdiParent.MdiChildren)
      {
        if (mdiChild.Name == formToLaunch.Name)
        {
          mdiChild.Close();
          break;
        }
      }
      formToLaunch.MdiParent = this.MdiParent;
      formToLaunch.Show();
    }

    private void menuView_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList)
        return;
      if (this.listView.Items.Count == 0)
      {
        int num1 = (int) MessageBox.Show((IWin32Window) this, "No files available to view.", "View", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
      }
      else if (this.listView.SelectedItems.Count == 0)
      {
        int num2 = (int) MessageBox.Show((IWin32Window) this, "No files selected to view.", "View", MessageBoxButtons.OK, MessageBoxIcon.Asterisk);
      }
      else
      {
        string upper = this.listView.SelectedItems[0].Tag.ToString().ToUpper();
        if (upper.EndsWith("EXE") || upper.EndsWith("DLL") || upper.EndsWith("TTF") || upper.EndsWith("BIN") || Options.m_LoginType == LoginType.Normal && upper.EndsWith("\\PASSWORD.CSV"))
          return;
        string[] source = new string[this.listView.SelectedItems.Count];
        this.listView.SelectedItems[0].Tag.ToString();
        for (int index = 0; index < this.listView.SelectedItems.Count; ++index)
          source[index] = this.listView.SelectedItems[index].Tag.ToString();
        BrukerCommWrapper.DataSyncEvent.Reset();
        string tempPath = Path.GetTempPath();
        this.m_TreeViewSelectedPath = "";
        Download download = new Download(this.m_TreeViewSelectedPath, source, tempPath, true);
        int num3 = (int) download.ShowDialog();
        BrukerCommWrapper.DataSyncEvent.Set();
        try
        {
          string remoteFileName = this.listView.SelectedItems[0].Tag.ToString();
          string str1 = remoteFileName.Substring(remoteFileName.LastIndexOf('\\') + 1);
          string str2 = remoteFileName.Substring(0, remoteFileName.LastIndexOf('\\') + 1);
          if (Options.m_LoginType != LoginType.Normal && str2.ToLower() == "\\bruker\\autoid\\" && str1.EndsWith(".xml") && str1.ToLower() != "settings.xml")
            this.LaunchApp((Form) new AutoIdEditor(download.m_LastFileDownloaded, remoteFileName));
          else if (Options.m_LoginType != LoginType.Normal && str2.ToLower() == "\\bruker\\system\\" && (str1.ToLower().EndsWith("lib.csv") || str1.ToLower().Equals("trampresidual.csv")))
            this.LaunchApp((Form) new GradeLibraryEditor(this, download.m_LastFileDownloaded, remoteFileName));
          else if (Options.m_LoginType != LoginType.Normal && remoteFileName.ToLower().EndsWith("\\limits.csv"))
            this.LaunchApp((Form) new LimitsEditor(this, download.m_LastFileDownloaded, remoteFileName));
          else if (remoteFileName.ToLower() == "\\bruker\\instrumentdef.idf")
            this.LaunchApp((Form) new InstrumentDefinition());
          else if (Options.m_LoginType != LoginType.Normal && str1.EndsWith(".uap"))
            this.LaunchApp((Form) new UserAppPreferencesEditor(download.m_LastFileDownloaded, remoteFileName));
          else if (str1.ToLower().EndsWith(".pdz"))
          {
            List<string> stringList = new List<string>();
            foreach (string dowloadedLocalFile in download.m_DowloadedLocalFileList)
            {
              if (dowloadedLocalFile.ToLower().EndsWith(".pdz"))
                stringList.Add(dowloadedLocalFile);
            }
            if (Options.m_LoginType == LoginType.Production || Options.m_LoginType == LoginType.Supervisor)
            {
              this.LaunchApp((Form) new SpectrumViewer(stringList));
            }
            else
            {
              string path1 = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "Bruker", "Bruker_Instrument_Tools");
              ReportBuilder.StateFileName = Path.Combine(path1, "state.xml");
              ReportBuilder.ShowReportingPreviewWindow(new ReportingContext((Image) Resources.CompanyLogo1, "en-US", Path.Combine(path1, "ReportGeneratorTemplates")), (IEnumerable<string>) stringList);
            }
          }
          else
          {
            if (str1.EndsWith(".dll") || str1.EndsWith(".exe") || str1.EndsWith(".TTF"))
              return;
            Process.Start(download.m_LastFileDownloaded);
          }
        }
        catch (Exception ex)
        {
          int num4 = (int) MessageBox.Show((IWin32Window) this, ex.Message, "S1 Sync", MessageBoxButtons.OK, MessageBoxIcon.Hand);
        }
      }
    }

    private void menuCopyFullPathText_Click(object sender, EventArgs e)
    {
      Clipboard.Clear();
      Clipboard.SetText(this.listView.SelectedItems[0].Tag.ToString());
    }

    private void menuBrukerInstaller_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList)
        return;
      if (!BrukerCommWrapper.CommManager.IsOpen())
      {
        this.LogMessage("Bruker Installer", MessageType.ERROR, "Server unavailable. Connect the server first.");
      }
      else
      {
        BrukerCommWrapper.DataSyncEvent.Reset();
        int num = (int) new BrukerInstaller().ShowDialog();
        BrukerCommWrapper.DataSyncEvent.Set();
      }
    }

    private void treeViewFileSystem_ItemDrag(object sender, ItemDragEventArgs e)
    {
      if (this.treeViewFileSystem.SelectedNodes.Count <= 0 || e.Button != MouseButtons.Left)
        return;
      int num = (int) this.DoDragDrop((object) this.treeViewFileSystem.SelectedNodes, DragDropEffects.All);
    }

    private void treeViewFileSystem_DragDrop(object sender, DragEventArgs e)
    {
      if (this.bPopulatingList || !BrukerCommWrapper.CommManager.IsOpen())
        return;
      if (e.Data.GetDataPresent(typeof (ListView.SelectedListViewItemCollection)))
      {
        TreeNode nodeAt = this.treeViewFileSystem.GetNodeAt(this.treeViewFileSystem.PointToClient(new Point(e.X, e.Y)));
        this.treeViewFileSystem.SelectedNode = nodeAt;
        ListView.SelectedListViewItemCollection data = (ListView.SelectedListViewItemCollection) e.Data.GetData(typeof (ListView.SelectedListViewItemCollection));
        string[] source = new string[data.Count];
        for (int index = 0; index < data.Count; ++index)
          source[index] = data[index].Tag.ToString();
        nodeAt.Tag.ToString();
        if (e.Effect == DragDropEffects.Copy)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          string dest = this.treeViewFileSystem.SelectedNode.Tag.ToString();
          this.m_TreeViewSelectedPath = this.m_SeletedNode == null ? "" : this.m_SeletedNode.Tag.ToString();
          int num = (int) new Download(this.m_TreeViewSelectedPath, source, dest, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        else if (e.Effect == DragDropEffects.Move)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          string dest = this.treeViewFileSystem.SelectedNode.Tag.ToString();
          this.m_TreeViewSelectedPath = this.m_SeletedNode == null ? "" : this.m_SeletedNode.Tag.ToString();
          int num = (int) new Download(this.m_TreeViewSelectedPath, source, dest, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        if ((e.Effect == DragDropEffects.Copy || e.Effect == DragDropEffects.Move) && this.treeViewFileSystem.SelectedNode.IsExpanded)
        {
          this.treeViewFileSystem.SelectedNode.Collapse();
          this.treeViewFileSystem.SelectedNode.Expand();
        }
      }
      e.Effect = DragDropEffects.None;
      this.Invalidate(new Region(this.ClientRectangle));
    }

    private void treeViewFileSystem_DragOver(object sender, DragEventArgs e)
    {
      if (!e.Data.GetDataPresent(typeof (ListView.SelectedListViewItemCollection)))
      {
        e.Effect = DragDropEffects.None;
      }
      else
      {
        TreeNode nodeAt = this.treeViewFileSystem.GetNodeAt(this.treeViewFileSystem.PointToClient(new Point(e.X, e.Y)));
        if (nodeAt == null || nodeAt.Tag.ToString() == "$$$mycomputer")
        {
          e.Effect = DragDropEffects.None;
        }
        else
        {
          ListView.SelectedListViewItemCollection data = (ListView.SelectedListViewItemCollection) e.Data.GetData(typeof (ListView.SelectedListViewItemCollection));
          this.treeViewFileSystem.SelectedNode = nodeAt;
          this.treeViewFileSystem.Focus();
          if (!this.IsDroppable(nodeAt.Tag.ToString(), data))
            e.Effect = DragDropEffects.None;
          else
            e.Effect = DragDropEffects.Copy;
        }
      }
    }

    private string GetSelectFileSystemFiles()
    {
      string str = "";
      foreach (TreeNode selectedNode in this.treeViewFileSystem.SelectedNodes)
        str = str + "\"" + selectedNode.Tag.ToString() + "\"";
      return "\"" + str + "\"";
    }

    private void menuFsProperties_Click(object sender, EventArgs e) => FileOperations.ExecuteShell(this.GetSelectFileSystemFiles(), FileOperations.FileOperationType.Properties);

    private void menuFsEexplore_Click(object sender, EventArgs e) => FileOperations.ExecuteShell(this.GetSelectFileSystemFiles(), FileOperations.FileOperationType.Explore);

    private void menuFsEdit_Click(object sender, EventArgs e) => FileOperations.ExecuteShell(this.GetSelectFileSystemFiles(), FileOperations.FileOperationType.Edit);

    private void menuFsOpen_Click(object sender, EventArgs e) => FileOperations.ExecuteShell(this.GetSelectFileSystemFiles(), FileOperations.FileOperationType.Open);

    private void menuFsDelete_Click(object sender, EventArgs e)
    {
      if (MessageBox.Show((IWin32Window) this, "Do you want to delete the selected file(s)?", "Delete Files", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.No)
        return;
      TreeNode treeNode = (TreeNode) null;
      foreach (TreeNode selectedNode in this.treeViewFileSystem.SelectedNodes)
      {
        try
        {
          if (Directory.Exists(selectedNode.Tag.ToString()))
            FileSystem.DeleteDirectory(selectedNode.Tag.ToString(), UIOption.OnlyErrorDialogs, RecycleOption.SendToRecycleBin, UICancelOption.DoNothing);
          else
            FileSystem.DeleteFile(selectedNode.Tag.ToString(), UIOption.OnlyErrorDialogs, RecycleOption.SendToRecycleBin, UICancelOption.DoNothing);
          if (!Directory.Exists(selectedNode.Tag.ToString()))
          {
            if (!File.Exists(selectedNode.Tag.ToString()))
            {
              treeNode = selectedNode.NextNode;
              selectedNode.Remove();
            }
          }
        }
        catch (IOException ex)
        {
          int num = (int) MessageBox.Show(ex.Message);
          break;
        }
      }
      if (treeNode == null)
        return;
      this.treeViewFileSystem.SelectedNode = treeNode;
      this.treeViewFileSystem.Focus();
    }

    private bool IsValidDrive(string strDrive)
    {
      foreach (DriveInfo drive in DriveInfo.GetDrives())
      {
        if (drive.IsReady && drive.Name == strDrive)
          return true;
      }
      return false;
    }

    private void menuFileSystem_Opening(object sender, CancelEventArgs e)
    {
      this.menuFsCut.Enabled = false;
      this.menuFsCopy.Enabled = false;
      this.menuFsPaste.Enabled = false;
      this.menuFsDelete.Enabled = false;
      this.menuFsRename.Enabled = false;
      this.menuFsOpen.Enabled = false;
      this.menuFsEdit.Enabled = false;
      this.menuFsEexplore.Enabled = false;
      this.menuFsProperties.Enabled = false;
      if (this.treeViewFileSystem.SelectedNodes.Count == 0)
        return;
      if (this.treeViewFileSystem.SelectedNodes[0].Tag.ToString() == "$$$mycomputer")
      {
        this.menuFsProperties.Enabled = true;
      }
      else
      {
        if (this.m_FileSource == FileSource.ListView && (this.m_FileAction == FileAction.Copy || this.m_FileAction == FileAction.Cut))
          this.menuFsPaste.Enabled = true;
        if (this.IsValidDrive(this.treeViewFileSystem.SelectedNodes[0].Tag.ToString()))
        {
          this.menuFsOpen.Enabled = true;
          this.menuFsEexplore.Enabled = true;
          this.menuFsProperties.Enabled = true;
        }
        else
        {
          this.menuFsCut.Enabled = true;
          this.menuFsCopy.Enabled = true;
          this.menuFsDelete.Enabled = true;
          this.menuFsRename.Enabled = true;
          this.menuFsOpen.Enabled = true;
          if (File.Exists(this.treeViewFileSystem.SelectedNodes[0].Tag.ToString()))
            this.menuFsEdit.Enabled = true;
          this.menuFsEexplore.Enabled = true;
          this.menuFsProperties.Enabled = true;
        }
      }
    }

    private void menuLaunchExplorer_Click(object sender, EventArgs e) => Process.Start("explorer.exe");

    private void menuFsCopy_Click(object sender, EventArgs e)
    {
      this.m_FileAction = FileAction.Copy;
      this.m_FileSource = FileSource.TreeView;
      this.m_FileList.Clear();
      for (int index = 0; index < this.treeViewFileSystem.SelectedNodes.Count; ++index)
        this.m_FileList.Add(this.treeViewFileSystem.SelectedNodes[index].Tag);
    }

    private void menuFsRename_Click(object sender, EventArgs e)
    {
      if (this.treeViewFileSystem.SelectedNode.IsEditing)
        return;
      this.sActualText = this.treeViewFileSystem.SelectedNode.Text;
      this.treeViewFileSystem.SelectedNode.BeginEdit();
    }

    private void menuFsCut_Click(object sender, EventArgs e)
    {
      this.m_FileAction = FileAction.Cut;
      this.m_FileSource = FileSource.TreeView;
      this.m_FileList.Clear();
      for (int index = 0; index < this.treeViewFileSystem.SelectedNodes.Count; ++index)
        this.m_FileList.Add(this.treeViewFileSystem.SelectedNodes[index].Tag);
    }

    private void treeViewFileSystem_AfterLabelEdit(object sender, NodeLabelEditEventArgs e)
    {
      if (e.Label == null)
      {
        e.CancelEdit = true;
      }
      else
      {
        string str = e.Node.Tag.ToString();
        string path = e.Node.Tag.ToString().Substring(0, e.Node.Tag.ToString().LastIndexOf("\\") + 1) + e.Label;
        if (!(this.sActualText != e.Label))
          return;
        if (Directory.Exists(this.sActualText))
        {
          if (Directory.Exists(path))
          {
            int num = (int) MessageBox.Show("Directory already exists.", "File Rename", MessageBoxButtons.OK);
            return;
          }
          FileSystem.RenameDirectory(str, e.Label);
        }
        else
        {
          if (File.Exists(path))
          {
            int num = (int) MessageBox.Show("File already exists.", "File Rename", MessageBoxButtons.OK);
            return;
          }
          FileSystem.RenameFile(str, e.Label);
        }
        e.Node.Tag = (object) path;
      }
    }

    private void menuFsPaste_Click(object sender, EventArgs e)
    {
      if (this.bPopulatingList || !BrukerCommWrapper.CommManager.IsOpen())
        return;
      if (this.m_FileSource == FileSource.ListView)
      {
        this.treeViewFileSystem.SelectedNode.Tag.ToString();
        string[] array = (string[]) this.m_FileList.ToArray(typeof (string));
        if (this.m_FileAction == FileAction.Copy)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          string dest = this.treeViewFileSystem.SelectedNode.Tag.ToString();
          this.m_TreeViewSelectedPath = this.m_SeletedNode == null ? "" : this.m_SeletedNode.Tag.ToString();
          int num = (int) new Download(this.m_TreeViewSelectedPath, array, dest, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        else if (this.m_FileAction == FileAction.Cut)
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          string dest = this.treeViewFileSystem.SelectedNode.Tag.ToString();
          this.m_TreeViewSelectedPath = this.m_SeletedNode == null ? "" : this.m_SeletedNode.Tag.ToString();
          int num = (int) new Download(this.m_TreeViewSelectedPath, array, dest, true).ShowDialog();
          BrukerCommWrapper.DataSyncEvent.Set();
        }
        if ((this.m_FileAction == FileAction.Copy || this.m_FileAction == FileAction.Cut) && this.treeViewFileSystem.SelectedNode.IsExpanded)
        {
          this.treeViewFileSystem.SelectedNode.Collapse();
          this.treeViewFileSystem.SelectedNode.Expand();
        }
        this.Invalidate(new Region(this.ClientRectangle));
      }
      else
      {
        int fileSource = (int) this.m_FileSource;
      }
    }

    private void listView_BeforeLabelEdit(object sender, LabelEditEventArgs e) => this.sActualText = this.listView.SelectedItems[0].Text;

    private void listView_AfterLabelEdit(object sender, LabelEditEventArgs e)
    {
      if (e.Label != null && e.Label.ToLower() != this.sActualText.ToLower())
      {
        this.bAcceptEdit = this.ExecuteRenameFile(this.sActualText, e.Label);
        if (!this.bAcceptEdit)
          e.CancelEdit = true;
      }
      if (Options.m_LoginType != LoginType.Normal)
        return;
      this.listView.LabelEdit = false;
    }

    private void listView_SelectedIndexChanged(object sender, EventArgs e)
    {
      if (this.listView.Items.Count == 0 || this.listView.SelectedItems.Count == 0)
        this.downloadToolStripButton.Enabled = false;
      else
        this.downloadToolStripButton.Enabled = true;
      if (this.m_SeletedNode.Tag.ToString().StartsWith("\\BRUKER"))
      {
        if (this.m_SeletedNode.Tag.ToString().StartsWith("\\BRUKER\\BRUKER"))
          this.uploadToolStripButton.Enabled = false;
        else
          this.uploadToolStripButton.Enabled = true;
      }
      else
        this.uploadToolStripButton.Enabled = false;
    }

    public void ListView_LabelEdit(bool bValue) => this.listView.LabelEdit = bValue;

    private void threadFileSystem_DoWork(object sender, DoWorkEventArgs e) => this.Invoke((Delegate) (() =>
    {
      this.treeViewFileSystem.Load();
      this.treeViewFileSystem.Nodes[0].Expand();
    }));

    private void S1SyncApp_Shown(object sender, EventArgs e)
    {
      if (Settings.Default.WindowSize.Height == 0)
      {
        this.WindowState = FormWindowState.Normal;
      }
      else
      {
        this.Location = Settings.Default.WindowLocation;
        this.Size = Settings.Default.WindowSize;
      }
    }

    protected override void Dispose(bool disposing)
    {
      if (disposing && this.components != null)
        this.components.Dispose();
      base.Dispose(disposing);
    }

    private void InitializeComponent()
    {
      this.components = (IContainer) new System.ComponentModel.Container();
      ComponentResourceManager componentResourceManager = new ComponentResourceManager(typeof (S1SyncApp));
      TreeNode treeNode = new TreeNode("Disconnected", 0, 0);
      this.imageList = new ImageList(this.components);
      this.toolStrip = new ToolStrip();
      this.refreshToolStripButton = new ToolStripButton();
      this.folderUpToolStripButton = new ToolStripButton();
      this.downloadToolStripButton = new ToolStripButton();
      this.uploadToolStripButton = new ToolStripButton();
      this.treeViewImageList = new ImageList(this.components);
      this.menuEdit = new ContextMenuStrip(this.components);
      this.menuView = new ToolStripMenuItem();
      this.toolStripSeparator9 = new ToolStripSeparator();
      this.menuCut = new ToolStripMenuItem();
      this.menuCopy = new ToolStripMenuItem();
      this.menuPaste = new ToolStripMenuItem();
      this.toolStripSeparator2 = new ToolStripSeparator();
      this.menuDelete = new ToolStripMenuItem();
      this.menuRename = new ToolStripMenuItem();
      this.menuNewFolder = new ToolStripMenuItem();
      this.toolStripSeparator3 = new ToolStripSeparator();
      this.menuDownload = new ToolStripMenuItem();
      this.menuUpload = new ToolStripMenuItem();
      this.lineCopyFullPathText = new ToolStripSeparator();
      this.menuCopyFullPathText = new ToolStripMenuItem();
      this.listViewImageList = new ImageList(this.components);
      this.menuFileSystem = new ContextMenuStrip(this.components);
      this.menuFsOpen = new ToolStripMenuItem();
      this.menuFsEdit = new ToolStripMenuItem();
      this.menuFsEexplore = new ToolStripMenuItem();
      this.toolStripSeparator4 = new ToolStripSeparator();
      this.menuFsCut = new ToolStripMenuItem();
      this.menuFsCopy = new ToolStripMenuItem();
      this.menuFsPaste = new ToolStripMenuItem();
      this.toolStripSeparator8 = new ToolStripSeparator();
      this.menuFsDelete = new ToolStripMenuItem();
      this.menuFsRename = new ToolStripMenuItem();
      this.toolStripSeparator6 = new ToolStripSeparator();
      this.menuFsProperties = new ToolStripMenuItem();
      this.toolStripSeparator7 = new ToolStripSeparator();
      this.menuLaunchExplorer = new ToolStripMenuItem();
      this.imageListFileSystem = new ImageList(this.components);
      this.toolTip = new ToolTip(this.components);
      this.batteryImageList = new ImageList(this.components);
      this.lblMessage = new ToolStripStatusLabel();
      this.saveFileDialog = new SaveFileDialog();
      this.openFileDialog = new OpenFileDialog();
      this.cmbFolderPath = new ComboBox();
      this.splitter1 = new Splitter();
      this.treeView = new TreeView();
      this.splitter2 = new Splitter();
      this.txtMenu = new TextBox();
      this.threadFileSystem = new BackgroundWorker();
      this.listView = new FlickerFreeListView.FlickerFreeListView();
      this.colName = new ColumnHeader();
      this.colSize = new ColumnHeader();
      this.colType = new ColumnHeader();
      this.colDateModified = new ColumnHeader();
      this.treeViewFileSystem = new FileSystemTreeView();
      this.toolStrip.SuspendLayout();
      this.menuEdit.SuspendLayout();
      this.menuFileSystem.SuspendLayout();
      this.SuspendLayout();
      this.imageList.ImageStream = (ImageListStreamer) componentResourceManager.GetObject("imageList.ImageStream");
      this.imageList.TransparentColor = Color.Transparent;
      this.imageList.Images.SetKeyName(0, "delete.ico");
      this.imageList.Images.SetKeyName(1, "success.ico");
      this.imageList.Images.SetKeyName(2, "info.ico");
      this.toolStrip.Items.AddRange(new ToolStripItem[4]
      {
        (ToolStripItem) this.refreshToolStripButton,
        (ToolStripItem) this.folderUpToolStripButton,
        (ToolStripItem) this.downloadToolStripButton,
        (ToolStripItem) this.uploadToolStripButton
      });
      this.toolStrip.Location = new Point(0, 0);
      this.toolStrip.Name = "toolStrip";
      this.toolStrip.Size = new Size(958, 25);
      this.toolStrip.TabIndex = 1;
      this.toolStrip.Text = "ToolStrip";
      this.refreshToolStripButton.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.refreshToolStripButton.Image = (Image) Resources.refresh;
      this.refreshToolStripButton.ImageTransparentColor = Color.Magenta;
      this.refreshToolStripButton.Name = "refreshToolStripButton";
      this.refreshToolStripButton.Size = new Size(75, 22);
      this.refreshToolStripButton.Text = "&Refresh";
      this.refreshToolStripButton.Click += new EventHandler(this.refreshToolStripButton_Click);
      this.folderUpToolStripButton.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.folderUpToolStripButton.Image = (Image) Resources.FolderUp;
      this.folderUpToolStripButton.ImageTransparentColor = Color.Magenta;
      this.folderUpToolStripButton.Name = "folderUpToolStripButton";
      this.folderUpToolStripButton.Size = new Size(88, 22);
      this.folderUpToolStripButton.Text = "Fo&lder Up";
      this.folderUpToolStripButton.ToolTipText = "Folder Up";
      this.folderUpToolStripButton.Click += new EventHandler(this.folderUpToolStripButton_Click);
      this.downloadToolStripButton.Enabled = false;
      this.downloadToolStripButton.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.downloadToolStripButton.Image = (Image) Resources.FillDownHS;
      this.downloadToolStripButton.ImageTransparentColor = Color.Magenta;
      this.downloadToolStripButton.Name = "downloadToolStripButton";
      this.downloadToolStripButton.Size = new Size(89, 22);
      this.downloadToolStripButton.Text = "&Download";
      this.downloadToolStripButton.ToolTipText = "Download";
      this.downloadToolStripButton.Click += new EventHandler(this.downloadToolStripButton_Click);
      this.uploadToolStripButton.Enabled = false;
      this.uploadToolStripButton.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.uploadToolStripButton.Image = (Image) Resources.FillUpHS;
      this.uploadToolStripButton.ImageTransparentColor = Color.Magenta;
      this.uploadToolStripButton.Name = "uploadToolStripButton";
      this.uploadToolStripButton.Size = new Size(73, 22);
      this.uploadToolStripButton.Text = "&Upload";
      this.uploadToolStripButton.ToolTipText = "Upload";
      this.uploadToolStripButton.Click += new EventHandler(this.uploadToolStripButton_Click);
      this.treeViewImageList.ImageStream = (ImageListStreamer) componentResourceManager.GetObject("treeViewImageList.ImageStream");
      this.treeViewImageList.TransparentColor = Color.Transparent;
      this.treeViewImageList.Images.SetKeyName(0, "pda.ico");
      this.treeViewImageList.Images.SetKeyName(1, "motherboard-icon.png");
      this.treeViewImageList.Images.SetKeyName(2, "folder-yellow-icon2.png");
      this.menuEdit.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.menuEdit.Items.AddRange(new ToolStripItem[14]
      {
        (ToolStripItem) this.menuView,
        (ToolStripItem) this.toolStripSeparator9,
        (ToolStripItem) this.menuCut,
        (ToolStripItem) this.menuCopy,
        (ToolStripItem) this.menuPaste,
        (ToolStripItem) this.toolStripSeparator2,
        (ToolStripItem) this.menuDelete,
        (ToolStripItem) this.menuRename,
        (ToolStripItem) this.menuNewFolder,
        (ToolStripItem) this.toolStripSeparator3,
        (ToolStripItem) this.menuDownload,
        (ToolStripItem) this.menuUpload,
        (ToolStripItem) this.lineCopyFullPathText,
        (ToolStripItem) this.menuCopyFullPathText
      });
      this.menuEdit.Name = "menuEdit";
      this.menuEdit.Size = new Size(163, 248);
      this.menuEdit.Opening += new CancelEventHandler(this.menuEdit_Opening);
      this.menuView.Name = "menuView";
      this.menuView.Size = new Size(162, 22);
      this.menuView.Text = "&View";
      this.menuView.Click += new EventHandler(this.menuView_Click);
      this.toolStripSeparator9.Name = "toolStripSeparator9";
      this.toolStripSeparator9.Size = new Size(159, 6);
      this.menuCut.Image = (Image) Resources.CutHS;
      this.menuCut.Name = "menuCut";
      this.menuCut.Size = new Size(162, 22);
      this.menuCut.Text = "Cut";
      this.menuCut.Click += new EventHandler(this.menuCut_Click);
      this.menuCopy.Image = (Image) Resources.CopyHS;
      this.menuCopy.Name = "menuCopy";
      this.menuCopy.Size = new Size(162, 22);
      this.menuCopy.Text = "Copy";
      this.menuCopy.Click += new EventHandler(this.menuCopy_Click);
      this.menuPaste.Image = (Image) Resources.PasteHS;
      this.menuPaste.Name = "menuPaste";
      this.menuPaste.Size = new Size(162, 22);
      this.menuPaste.Text = "Paste";
      this.menuPaste.Click += new EventHandler(this.menuPaste_Click);
      this.toolStripSeparator2.Name = "toolStripSeparator2";
      this.toolStripSeparator2.Size = new Size(159, 6);
      this.menuDelete.Image = (Image) Resources.DeleteHS;
      this.menuDelete.Name = "menuDelete";
      this.menuDelete.Size = new Size(162, 22);
      this.menuDelete.Text = "Delete";
      this.menuDelete.Click += new EventHandler(this.deleteToolStripMenuItem_Click);
      this.menuRename.Image = (Image) Resources.Rename;
      this.menuRename.Name = "menuRename";
      this.menuRename.Size = new Size(162, 22);
      this.menuRename.Text = "Rename";
      this.menuRename.Click += new EventHandler(this.renameToolStripMenuItem_Click);
      this.menuNewFolder.Image = (Image) Resources.Newfolder;
      this.menuNewFolder.Name = "menuNewFolder";
      this.menuNewFolder.Size = new Size(162, 22);
      this.menuNewFolder.Text = "New Folder";
      this.menuNewFolder.Click += new EventHandler(this.newFolderToolStripMenuItem_Click);
      this.toolStripSeparator3.Name = "toolStripSeparator3";
      this.toolStripSeparator3.Size = new Size(159, 6);
      this.menuDownload.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.menuDownload.Image = (Image) Resources.FillDownHS;
      this.menuDownload.Name = "menuDownload";
      this.menuDownload.Size = new Size(162, 22);
      this.menuDownload.Text = "Download";
      this.menuDownload.Click += new EventHandler(this.downloadToolStripMenuItem_Click);
      this.menuUpload.Image = (Image) Resources.FillUpHS;
      this.menuUpload.Name = "menuUpload";
      this.menuUpload.Size = new Size(162, 22);
      this.menuUpload.Text = "Upload";
      this.menuUpload.Click += new EventHandler(this.menuUpload_Click);
      this.lineCopyFullPathText.Name = "lineCopyFullPathText";
      this.lineCopyFullPathText.Size = new Size(159, 6);
      this.menuCopyFullPathText.Name = "menuCopyFullPathText";
      this.menuCopyFullPathText.Size = new Size(162, 22);
      this.menuCopyFullPathText.Text = "Copy Full Path";
      this.menuCopyFullPathText.Click += new EventHandler(this.menuCopyFullPathText_Click);
      this.listViewImageList.ImageStream = (ImageListStreamer) componentResourceManager.GetObject("listViewImageList.ImageStream");
      this.listViewImageList.TransparentColor = Color.Transparent;
      this.listViewImageList.Images.SetKeyName(0, "unknown");
      this.menuFileSystem.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.menuFileSystem.Items.AddRange(new ToolStripItem[14]
      {
        (ToolStripItem) this.menuFsOpen,
        (ToolStripItem) this.menuFsEdit,
        (ToolStripItem) this.menuFsEexplore,
        (ToolStripItem) this.toolStripSeparator4,
        (ToolStripItem) this.menuFsCut,
        (ToolStripItem) this.menuFsCopy,
        (ToolStripItem) this.menuFsPaste,
        (ToolStripItem) this.toolStripSeparator8,
        (ToolStripItem) this.menuFsDelete,
        (ToolStripItem) this.menuFsRename,
        (ToolStripItem) this.toolStripSeparator6,
        (ToolStripItem) this.menuFsProperties,
        (ToolStripItem) this.toolStripSeparator7,
        (ToolStripItem) this.menuLaunchExplorer
      });
      this.menuFileSystem.Name = "menuFileSystem";
      this.menuFileSystem.Size = new Size(231, 248);
      this.menuFileSystem.Opening += new CancelEventHandler(this.menuFileSystem_Opening);
      this.menuFsOpen.Name = "menuFsOpen";
      this.menuFsOpen.Size = new Size(230, 22);
      this.menuFsOpen.Text = "Open";
      this.menuFsOpen.Click += new EventHandler(this.menuFsOpen_Click);
      this.menuFsEdit.Name = "menuFsEdit";
      this.menuFsEdit.Size = new Size(230, 22);
      this.menuFsEdit.Text = "Edit";
      this.menuFsEdit.Visible = false;
      this.menuFsEdit.Click += new EventHandler(this.menuFsEdit_Click);
      this.menuFsEexplore.Name = "menuFsEexplore";
      this.menuFsEexplore.Size = new Size(230, 22);
      this.menuFsEexplore.Text = "Explore";
      this.menuFsEexplore.Visible = false;
      this.menuFsEexplore.Click += new EventHandler(this.menuFsEexplore_Click);
      this.toolStripSeparator4.Name = "toolStripSeparator4";
      this.toolStripSeparator4.Size = new Size(227, 6);
      this.menuFsCut.Name = "menuFsCut";
      this.menuFsCut.Size = new Size(230, 22);
      this.menuFsCut.Text = "Cut";
      this.menuFsCut.Click += new EventHandler(this.menuFsCut_Click);
      this.menuFsCopy.Name = "menuFsCopy";
      this.menuFsCopy.Size = new Size(230, 22);
      this.menuFsCopy.Text = "Copy";
      this.menuFsCopy.Click += new EventHandler(this.menuFsCopy_Click);
      this.menuFsPaste.Name = "menuFsPaste";
      this.menuFsPaste.Size = new Size(230, 22);
      this.menuFsPaste.Text = "Paste";
      this.menuFsPaste.Click += new EventHandler(this.menuFsPaste_Click);
      this.toolStripSeparator8.Name = "toolStripSeparator8";
      this.toolStripSeparator8.Size = new Size(227, 6);
      this.menuFsDelete.Name = "menuFsDelete";
      this.menuFsDelete.Size = new Size(230, 22);
      this.menuFsDelete.Text = "Delete";
      this.menuFsDelete.Click += new EventHandler(this.menuFsDelete_Click);
      this.menuFsRename.Name = "menuFsRename";
      this.menuFsRename.Size = new Size(230, 22);
      this.menuFsRename.Text = "Rename";
      this.menuFsRename.Click += new EventHandler(this.menuFsRename_Click);
      this.toolStripSeparator6.Name = "toolStripSeparator6";
      this.toolStripSeparator6.Size = new Size(227, 6);
      this.menuFsProperties.Name = "menuFsProperties";
      this.menuFsProperties.Size = new Size(230, 22);
      this.menuFsProperties.Text = "Properties";
      this.menuFsProperties.Click += new EventHandler(this.menuFsProperties_Click);
      this.toolStripSeparator7.Name = "toolStripSeparator7";
      this.toolStripSeparator7.Size = new Size(227, 6);
      this.menuLaunchExplorer.Name = "menuLaunchExplorer";
      this.menuLaunchExplorer.Size = new Size(230, 22);
      this.menuLaunchExplorer.Text = "Launch Windows Explorer";
      this.menuLaunchExplorer.Click += new EventHandler(this.menuLaunchExplorer_Click);
      this.imageListFileSystem.ImageStream = (ImageListStreamer) componentResourceManager.GetObject("imageListFileSystem.ImageStream");
      this.imageListFileSystem.TransparentColor = Color.Transparent;
      this.imageListFileSystem.Images.SetKeyName(0, "mycomputer");
      this.toolTip.IsBalloon = true;
      this.toolTip.OwnerDraw = true;
      this.toolTip.ShowAlways = true;
      this.toolTip.ToolTipIcon = ToolTipIcon.Info;
      this.toolTip.ToolTipTitle = "Battery Status";
      this.batteryImageList.ImageStream = (ImageListStreamer) componentResourceManager.GetObject("batteryImageList.ImageStream");
      this.batteryImageList.TransparentColor = Color.Transparent;
      this.batteryImageList.Images.SetKeyName(0, "no");
      this.batteryImageList.Images.SetKeyName(1, "green");
      this.batteryImageList.Images.SetKeyName(2, "red");
      this.batteryImageList.Images.SetKeyName(3, "yellow");
      this.batteryImageList.Images.SetKeyName(4, "power");
      this.lblMessage.AutoSize = false;
      this.lblMessage.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.lblMessage.Name = "lblMessage";
      this.lblMessage.Size = new Size(1054, 22);
      this.lblMessage.Spring = true;
      this.lblMessage.Text = "Disconnected";
      this.lblMessage.TextAlign = ContentAlignment.MiddleLeft;
      this.cmbFolderPath.AutoCompleteMode = AutoCompleteMode.Suggest;
      this.cmbFolderPath.AutoCompleteSource = AutoCompleteSource.ListItems;
      this.cmbFolderPath.Dock = DockStyle.Top;
      this.cmbFolderPath.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Bold, GraphicsUnit.Point, (byte) 0);
      this.cmbFolderPath.Location = new Point(0, 25);
      this.cmbFolderPath.Margin = new Padding(3, 4, 3, 4);
      this.cmbFolderPath.Name = "cmbFolderPath";
      this.cmbFolderPath.Size = new Size(958, 24);
      this.cmbFolderPath.Sorted = true;
      this.cmbFolderPath.TabIndex = 15;
      this.cmbFolderPath.SelectedIndexChanged += new EventHandler(this.cmbFolderPath_SelectedIndexChanged);
      this.cmbFolderPath.KeyDown += new KeyEventHandler(this.cmbFolderPath_KeyDown);
      this.splitter1.BackColor = SystemColors.ControlDark;
      this.splitter1.Dock = DockStyle.Bottom;
      this.splitter1.Location = new Point(0, 409);
      this.splitter1.Name = "splitter1";
      this.splitter1.Size = new Size(958, 5);
      this.splitter1.TabIndex = 17;
      this.splitter1.TabStop = false;
      this.treeView.AllowDrop = true;
      this.treeView.BorderStyle = BorderStyle.None;
      this.treeView.Dock = DockStyle.Left;
      this.treeView.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.treeView.FullRowSelect = true;
      this.treeView.HideSelection = false;
      this.treeView.ImageIndex = 0;
      this.treeView.ImageList = this.treeViewImageList;
      this.treeView.Location = new Point(0, 49);
      this.treeView.Margin = new Padding(3, 4, 3, 4);
      this.treeView.Name = "treeView";
      treeNode.ImageIndex = 0;
      treeNode.Name = "Node0";
      treeNode.NodeFont = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Bold, GraphicsUnit.Point, (byte) 0);
      treeNode.SelectedImageIndex = 0;
      treeNode.Tag = (object) "\\";
      treeNode.Text = "Disconnected";
      this.treeView.Nodes.AddRange(new TreeNode[1]
      {
        treeNode
      });
      this.treeView.SelectedImageIndex = 0;
      this.treeView.ShowNodeToolTips = true;
      this.treeView.Size = new Size(294, 360);
      this.treeView.TabIndex = 18;
      this.treeView.Tag = (object) "";
      this.treeView.AfterCollapse += new TreeViewEventHandler(this.treeView_AfterCollapse);
      this.treeView.BeforeExpand += new TreeViewCancelEventHandler(this.treeView_BeforeExpand);
      this.treeView.DoubleClick += new EventHandler(this.treeView_DoubleClick);
      this.treeView.DragDrop += new DragEventHandler(this.treeView_DragDrop);
      this.treeView.DragOver += new DragEventHandler(this.treeView_DragOver);
      this.splitter2.BackColor = SystemColors.ControlDark;
      this.splitter2.Location = new Point(294, 49);
      this.splitter2.Name = "splitter2";
      this.splitter2.Size = new Size(5, 360);
      this.splitter2.TabIndex = 19;
      this.splitter2.TabStop = false;
      this.txtMenu.BorderStyle = BorderStyle.FixedSingle;
      this.txtMenu.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.txtMenu.Location = new Point(357, 146);
      this.txtMenu.Margin = new Padding(3, 4, 3, 4);
      this.txtMenu.Name = "txtMenu";
      this.txtMenu.Size = new Size(220, 22);
      this.txtMenu.TabIndex = 21;
      this.txtMenu.Visible = false;
      this.threadFileSystem.DoWork += new DoWorkEventHandler(this.threadFileSystem_DoWork);
      this.listView.AllowColumnReorder = true;
      this.listView.AllowDrop = true;
      this.listView.BorderStyle = BorderStyle.None;
      this.listView.Columns.AddRange(new ColumnHeader[4]
      {
        this.colName,
        this.colSize,
        this.colType,
        this.colDateModified
      });
      this.listView.ContextMenuStrip = this.menuEdit;
      this.listView.Dock = DockStyle.Fill;
      this.listView.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.listView.FullRowSelect = true;
      this.listView.HideSelection = false;
      this.listView.Location = new Point(299, 49);
      this.listView.Margin = new Padding(3, 4, 3, 4);
      this.listView.Name = "listView";
      this.listView.ShowGroups = false;
      this.listView.ShowItemToolTips = true;
      this.listView.Size = new Size(659, 360);
      this.listView.SmallImageList = this.listViewImageList;
      this.listView.Sorting = SortOrder.Ascending;
      this.listView.StateImageList = this.listViewImageList;
      this.listView.TabIndex = 20;
      this.listView.UseCompatibleStateImageBehavior = false;
      this.listView.View = View.Details;
      this.listView.AfterLabelEdit += new LabelEditEventHandler(this.listView_AfterLabelEdit);
      this.listView.SelectedIndexChanged += new EventHandler(this.listView_SelectedIndexChanged);
      this.listView.DoubleClick += new EventHandler(this.listView_DoubleClick);
      this.listView.DragDrop += new DragEventHandler(this.listView_DragDrop);
      this.listView.ColumnClick += new ColumnClickEventHandler(this.listView_ColumnClick);
      this.listView.BeforeLabelEdit += new LabelEditEventHandler(this.listView_BeforeLabelEdit);
      this.listView.KeyDown += new KeyEventHandler(this.listView_KeyDown);
      this.listView.ItemDrag += new ItemDragEventHandler(this.listView_ItemDrag);
      this.listView.DragOver += new DragEventHandler(this.listView_DragOver);
      this.listView.Click += new EventHandler(this.listView_Click);
      this.colName.Text = "Name";
      this.colName.Width = 200;
      this.colSize.Text = "Size";
      this.colSize.TextAlign = HorizontalAlignment.Right;
      this.colSize.Width = 75;
      this.colType.Text = "Type";
      this.colType.Width = 75;
      this.colDateModified.Text = "Date Modified";
      this.colDateModified.Width = 150;
      this.treeViewFileSystem.AllowDrop = true;
      this.treeViewFileSystem.BorderStyle = BorderStyle.None;
      this.treeViewFileSystem.ContextMenuStrip = this.menuFileSystem;
      this.treeViewFileSystem.Dock = DockStyle.Bottom;
      this.treeViewFileSystem.FileFilter = "*.*";
      this.treeViewFileSystem.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.treeViewFileSystem.HideSelection = false;
      this.treeViewFileSystem.ImageIndex = 0;
      this.treeViewFileSystem.ImageList = this.imageListFileSystem;
      this.treeViewFileSystem.LabelEdit = true;
      this.treeViewFileSystem.Location = new Point(0, 414);
      this.treeViewFileSystem.Name = "treeViewFileSystem";
      this.treeViewFileSystem.SelectedImageIndex = 0;
      this.treeViewFileSystem.SelectedNodes = (List<TreeNode>) componentResourceManager.GetObject("treeViewFileSystem.SelectedNodes");
      this.treeViewFileSystem.Size = new Size(958, 248);
      this.treeViewFileSystem.StateImageList = this.imageListFileSystem;
      this.treeViewFileSystem.TabIndex = 16;
      this.treeViewFileSystem.AfterLabelEdit += new NodeLabelEditEventHandler(this.treeViewFileSystem_AfterLabelEdit);
      this.treeViewFileSystem.DragDrop += new DragEventHandler(this.treeViewFileSystem_DragDrop);
      this.treeViewFileSystem.ItemDrag += new ItemDragEventHandler(this.treeViewFileSystem_ItemDrag);
      this.treeViewFileSystem.DragOver += new DragEventHandler(this.treeViewFileSystem_DragOver);
      this.AutoScaleDimensions = new SizeF(8f, 16f);
      this.AutoScaleMode = AutoScaleMode.Font;
      this.ClientSize = new Size(958, 662);
      this.Controls.Add((Control) this.listView);
      this.Controls.Add((Control) this.splitter2);
      this.Controls.Add((Control) this.txtMenu);
      this.Controls.Add((Control) this.treeView);
      this.Controls.Add((Control) this.splitter1);
      this.Controls.Add((Control) this.treeViewFileSystem);
      this.Controls.Add((Control) this.cmbFolderPath);
      this.Controls.Add((Control) this.toolStrip);
      this.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.Icon = (Icon) componentResourceManager.GetObject("$this.Icon");
      this.Margin = new Padding(3, 4, 3, 4);
      this.Name = nameof (S1SyncApp);
      this.StartPosition = FormStartPosition.Manual;
      this.Text = "Bruker Instrument Explorer";
      this.Load += new EventHandler(this.S1Sync_Load);
      this.Shown += new EventHandler(this.S1SyncApp_Shown);
      this.FormClosed += new FormClosedEventHandler(this.S1SyncApp_FormClosed);
      this.toolStrip.ResumeLayout(false);
      this.toolStrip.PerformLayout();
      this.menuEdit.ResumeLayout(false);
      this.menuFileSystem.ResumeLayout(false);
      this.ResumeLayout(false);
      this.PerformLayout();
    }

    private delegate void UpdateLogMessageDelegate(
      string strCmd,
      MessageType type,
      string strValue);
  }
}
