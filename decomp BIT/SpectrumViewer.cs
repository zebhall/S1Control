// Decompiled with JetBrains decompiler
// Type: S1Sync.SpectrumViewer
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using BrukerAXS.Handheld.SpectrumFileNS;
using BrukerCommunication;
using ReportGenerator.Engine;
using ReportGenerator.WpfGui;
using S1Sync.Common;
using S1Sync.Properties;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Printing;
using System.IO;
using System.Linq;
using System.Linq.Expressions;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace S1Sync
{
  public class SpectrumViewer : Form
  {
    private bool m_bDoRefresh;
    private ThreadSafeList<MultiSpectrumData> m_MultiSpectrumDataList = new ThreadSafeList<MultiSpectrumData>();
    private MultiSpectrumData m_MSDOverlaySpectra;
    private SpectrumInFile m_SIFOverlaySpectrumInFile;
    private SpectrumFile m_SFOverlaySpectrumFile;
    private bool m_bNewOverlayFile = true;
    private bool m_bNewOverlayPhase = true;
    private int m_SpectrumCount;
    private ArrayList m_SpectrumNormalizeFactor;
    private int m_LargeSpect;
    private bool m_bNormalize;
    private int m_iPreviousPanelWith = -1;
    private float m_fPreviousCursorLeft = -1f;
    private List<Element> m_ActiveElements = new List<Element>();
    private SpectrumFile m_SpectrumFile;
    private List<AlphaLines> m_AlphaLines = new List<AlphaLines>()
    {
      AlphaLines.KLine
    };
    private Random randomGen = new Random();
    private XrayOpsEngine m_XrayOpsEngine = new XrayOpsEngine(BrukerCommWrapper.CommManager, BrukerCommWrapper.DataSyncEvent);
    private float m_fVerticalMutiplier = 1f;
    private PointF m_ptPeakPoint = new PointF(0.0f, 0.0f);
    private int m_iTickCount;
    private int m_iStartX;
    private int m_iEndX;
    private AreaSelectorControl m_AreaSelector = new AreaSelectorControl();
    private CursorControl m_CursorControl = new CursorControl();
    private Stack m_ZoomHistoryStack = new Stack();
    private bool m_bLiveSpectrumMode;
    private bool m_bInstrumentInitiatedAssay;
    private static List<Form> m_ActiveForms = new List<Form>();
    private int m_iSpectraIndex;
    private bool m_bShowLineNames = true;
    private bool m_bMoveGraphHorizontally;
    private bool m_bScaleGraphVertically;
    private int m_iHorizontalPos;
    private float m_fHorizontalValue;
    private bool m_bCursorNonZero;
    private int m_iCursorInitialPos;
    private float m_fCursorValue;
    private int m_iVerticalPos;
    private float m_fVerticalValue;
    private int m_RemID;
    private int m_iPacketCount = -1;
    public int m_YaxisHeight = 1200;
    public float m_fVisbleXStartStep;
    public float m_fVisibleXWidth = 2048f;
    public float m_fVisbleXSteps = 16f;
    public float m_fVisbleYSteps = 10f;
    public PdzViewerOptions2 m_PdzViewerOptions2;
    public PdzViewerXraySettings m_PdzViewerXraySettings = new PdzViewerXraySettings();
    public List<SpectrumFileEntry> m_FileNameList = new List<SpectrumFileEntry>();
    public string m_CurrentSpectrumFileName = "";
    public string m_PreviousSpectrumFileName = "";
    public List<SpectrumResultRow> m_ResultsTable = new List<SpectrumResultRow>();
    public int m_StdMultiplier = 1;
    public List<Image> m_Images = new List<Image>();
    public bool m_bShowResolutionAtCursor;
    private CommunicationManager m_LiveCommManager;
    private int m_LiveDataPortNo = 55203;
    private List<byte> m_StartMask = new List<byte>()
    {
      (byte) 3,
      (byte) 2,
      (byte) 0,
      (byte) 0
    };
    private List<byte> m_EndMask = new List<byte>()
    {
      (byte) 6,
      (byte) 42,
      byte.MaxValue,
      byte.MaxValue
    };
    private InstrumentDefinition idfDocForm;
    private CInstrumentDef m_IDF;
    private IlluminationSelector IllumSelect;
    public string cmdline;
    private Mutex LiveSpectraMutex = new Mutex();
    private bool m_bNoDataToDrawError;
    public int BtoBCounter;
    public int MaxAssayTime = 300;
    public bool BtoBPause;
    private byte[] dataArray;
    private int BufReadStage;
    private int dataSize;
    private SpectrumLiveData liveCommand;
    private Rectangle dragBoxFromMouseDown;
    public int oneOnly = -1;
    private int panelGraph_DragX;
    private int panelGraph_DragY;
    private SpectrumViewerROI ROIForm;
    private int m_ROIRightClickIndex = -1;
    private bool m_bDataFromLiveSpectrum;
    private IContainer components;
    private DoubleBufferPanel panelSpectrum;
    private OpenFileDialog openFileDialog;
    private DoubleBufferPanel panelAxisY;
    private DoubleBufferPanel panelAxisX;
    public DoubleBufferPanel panelGraph;
    private ContextMenuStrip contextMenu;
    private ToolStripMenuItem menuReset;
    private ToolStripMenuItem menuUnZoom;
    private BackgroundWorker backgroundWorker;
    private FolderBrowserDialog folderBrowserDialog;
    private ToolStripSeparator toolStripSeparator2;
    private ToolStripMenuItem menuNormalize;
    private ToolStripSeparator toolStripSeparator8;
    private ToolStripMenuItem menuAddLabel;
    private ToolStripMenuItem enableOverlayToolStripMenuItem;
    private ToolStripSeparator toolStripSeparator11;
    private ToolStripMenuItem menuRenameROI;
    private ToolStripMenuItem menuDeleteROI;
    private ToolStripMenuItem menuChangeROIBounds;
    private SaveFileDialog saveFileDialog;
    private PrintDialog printDialog;
    private PrintDocument printDocument;
    private ToolStripDropDownButton menuOptions;
    private ToolStripMenuItem menuFileSelector;
    private ToolStripSeparator toolStripSeparator4;
    private ToolStripMenuItem menuSaveAsPdz;
    private ToolStripSeparator toolStripSeparator5;
    private ToolStripMenuItem menuAtomicTable;
    private ToolStripMenuItem menuCursorInfo;
    private ToolStripMenuItem menuSpectrumInfo;
    private ToolStripMenuItem menuResults;
    private ToolStripMenuItem menuImages;
    private ToolStripMenuItem menuShowReportGenerator;
    private ToolStripMenuItem menuResolutionFWHM;
    private ToolStripMenuItem menuResolutionCursor;
    private ToolStripSeparator toolStripSeparator1;
    private ToolStripMenuItem menuSettings;
    private ToolStripMenuItem menuXraySettings;
    private ToolStripMenuItem menuPrint;
    private ToolStripSeparator toolStripSeparator3;
    private ToolStripMenuItem menuLiveSpectrum;
    private ToolStripSeparator lineLiveSpectrum;
    private ToolStripMenuItem menuExit;
    private ToolStripDropDownButton menuEdit;
    private ToolStripMenuItem menuCopy;
    private ToolStripSeparator toolStripSeparator6;
    private ToolStripLabel lblSpectrumList;
    public ToolStripFontComboBox cmbSpectrumFiles;
    private ToolStripSeparator toolStripSeparator7;
    private ToolStripDropDownButton windowsMenu;
    private ToolStripMenuItem menuCascade;
    private ToolStripMenuItem menuCloseAll;
    private ToolStripButton picLiveSpectrum;
    private ToolStrip toolStrip;
    private ToolStripSeparator toolStripSeparator9;
    private ToolStripButton PerChartBtn;
    private ToolStripButton CurInfoBtn;
    private ToolStripMenuItem menuSetIllumination;
    private ToolStripMenuItem SpectrumReviewMenuItem;
    private ToolStripSeparator toolStripSeparator10;
    private ToolStripMenuItem selectOverlaySpectrumToolStripMenuItem;
    private ToolStripMenuItem overlaySpectraToolStripMenuItem;
    private ToolStripMenuItem menuShowBackground;
    private ToolStripMenuItem menuShowOneSpectrum;
    private ToolStripMenuItem menuRegionOfInterest;

    private void OnDispose(bool disposing) => this.DisConnectLiveManager();

    public SpectrumViewer()
    {
      this.InitializeComponent();
      this.panelGraph.AllowDrop = true;
      this.panelGraph.DragEnter += new DragEventHandler(this.panelGraph_DragEnter);
      this.panelGraph.DragDrop += new DragEventHandler(this.panelGraph_DragDrop);
      this.m_PdzViewerOptions2 = new PdzViewerOptions2(this);
      this.InitCommon();
      this.ConnectLiveCommManager();
      if (!this.backgroundWorker.IsBusy && this.m_LiveCommManager != null && this.m_LiveCommManager.IsOpen())
        this.backgroundWorker.RunWorkerAsync();
      this.components.Add((IComponent) new SpectrumViewer.Disposer(new Action<bool>(this.OnDispose)));
    }

    public SpectrumFile GetSpectrumFile() => this.m_SpectrumFile;

    private void panelGraph_DragEnter(object sender, DragEventArgs e)
    {
      if (e.Data.GetDataPresent(DataFormats.FileDrop))
        e.Effect = DragDropEffects.Copy;
      else if (e.Data.GetDataPresent("System.Windows.Forms.ToolStripItem", false))
        e.Effect = DragDropEffects.Move;
      else
        e.Effect = DragDropEffects.None;
    }

    private void panelGraph_DragDrop(object sendser, DragEventArgs e)
    {
      char ch = '\u001E';
      foreach (string str in (string[]) e.Data.GetData(DataFormats.FileDrop))
      {
        SpectrumFileEntry spectrumFileEntry = new SpectrumFileEntry();
        spectrumFileEntry.FileName = str;
        spectrumFileEntry.ShowSpectra = true;
        spectrumFileEntry.Color = this.getNextColor();
        spectrumFileEntry.spectrumFile = (SpectrumFile) null;
        this.m_FileNameList.Add(spectrumFileEntry);
        // ISSUE: variable of a compiler-generated type
        Settings settings = Settings.Default;
        settings.SpectrumViewerFileList = settings.SpectrumViewerFileList + spectrumFileEntry.FileName + ch.ToString();
        Console.WriteLine(str);
      }
      this.LoadPdzFiles();
    }

    public SpectrumViewer(List<string> localFileNames)
    {
      this.InitializeComponent();
      this.panelGraph.AllowDrop = true;
      this.panelGraph.DragEnter += new DragEventHandler(this.panelGraph_DragEnter);
      this.panelGraph.DragDrop += new DragEventHandler(this.panelGraph_DragDrop);
      this.InitCommon();
      this.m_PdzViewerOptions2 = new PdzViewerOptions2(this);
      foreach (string localFileName in localFileNames)
        this.m_FileNameList.Add(new SpectrumFileEntry()
        {
          FileName = localFileName,
          ShowSpectra = true,
          Color = this.getNextColor(),
          spectrumFile = (SpectrumFile) null
        });
      this.m_CurrentSpectrumFileName = localFileNames[0];
      this.ConnectLiveCommManager();
      if (!this.backgroundWorker.IsBusy && this.m_LiveCommManager != null && this.m_LiveCommManager.IsOpen())
        this.backgroundWorker.RunWorkerAsync();
      this.components.Add((IComponent) new SpectrumViewer.Disposer(new Action<bool>(this.OnDispose)));
    }

    public bool SpectrumColor(out Color color)
    {
      bool flag = false;
      color = Color.Black;
      if (this.cmbSpectrumFiles.Items.Count > 0 && this.cmbSpectrumFiles.SelectedItem is ComboBoxItem selectedItem)
      {
        color = selectedItem.ForeColor;
        flag = true;
      }
      return flag;
    }

    public Color getNextColor()
    {
      int count = this.m_PdzViewerOptions2.ListOfSpectrumColors.Count;
      if (count <= 0)
        return Color.Black;
      int[] numArray = new int[count];
      for (int index = 0; index < count; ++index)
        numArray[index] = 0;
      for (int index1 = 0; index1 < this.m_FileNameList.Count; ++index1)
      {
        int index2 = this.colorIndex(this.m_FileNameList[index1].Color);
        if (index2 >= 0)
          ++numArray[index2];
      }
      int maxValue = int.MaxValue;
      int index3 = 0;
      for (int index4 = 0; index4 < this.m_PdzViewerOptions2.ListOfSpectrumColors.Count; ++index4)
      {
        if (numArray[index4] < maxValue)
        {
          maxValue = numArray[index4];
          index3 = index4;
        }
      }
      return this.m_PdzViewerOptions2.ListOfSpectrumColors[index3];
    }

    private void InitCommon()
    {
      this.panelSpectrum.Location = new Point(0, 27);
      this.panelGraph.MouseWheel += new MouseEventHandler(this.panelGraph_MouseWheel);
      this.enableOverlayToolStripMenuItem.Checked = Settings.Default.OverlaySpectraEnable;
      this.menuShowBackground.Checked = Settings.Default.ShowBackground;
      this.menuShowOneSpectrum.Checked = Settings.Default.ShowOneSpectrum;
      if (!BrukerCommWrapper.CommManager.IsOpen())
        return;
      this.idfDocForm = new InstrumentDefinition();
      this.idfDocForm.InstrumentDefinition_Load((object) null, (EventArgs) null);
      this.m_IDF = (CInstrumentDef) this.idfDocForm.propertyGrid.SelectedObject;
      this.m_RemID = BrukerCommWrapper.ReadRemID();
    }

    private void panelAxisY_Paint(object sender, PaintEventArgs e)
    {
      Pen pen = new Pen(Color.Black, 3f);
      e.Graphics.DrawLine(pen, new Point(this.panelAxisY.Width, this.panelAxisY.Top), new Point(this.panelAxisY.Width, this.panelAxisY.Bottom - this.panelAxisX.Height));
      Font font = new Font("Verdana", 8f, FontStyle.Bold);
      SolidBrush solidBrush = new SolidBrush(Color.Black);
      float single = Convert.ToSingle(this.panelAxisY.Height - this.panelAxisX.Height);
      float num = single / this.m_fVisbleYSteps;
      for (int index = 0; index <= (int) this.m_fVisbleYSteps; ++index)
      {
        string s = ((float) ((double) Convert.ToSingle(index) / (double) this.m_fVisbleYSteps * ((double) Convert.ToSingle(this.m_YaxisHeight) / (double) this.m_fVerticalMutiplier))).ToString("F1");
        if (index == (int) this.m_fVisbleYSteps)
          e.Graphics.DrawString(s, font, (Brush) solidBrush, 0.0f, single - (float) index * num);
        else
          e.Graphics.DrawString(s, font, (Brush) solidBrush, 0.0f, (float) ((double) single - (double) index * (double) num - 5.0));
        e.Graphics.DrawLine(pen, new PointF(Convert.ToSingle(this.panelAxisY.Width) - 5f, single - (float) index * num), new PointF(Convert.ToSingle(this.panelAxisY.Width), single - (float) index * num));
      }
      e.Graphics.DrawString(" Ch:", font, (Brush) solidBrush, (float) (this.panelAxisY.Width - 30), (float) (this.panelAxisY.Height - 50));
      e.Graphics.DrawString("keV:", font, (Brush) solidBrush, (float) (this.panelAxisY.Width - 30), (float) (this.panelAxisY.Height - 35));
    }

    private void panelAxisX_Paint(object sender, PaintEventArgs e)
    {
      int iSpectraIndex = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        iSpectraIndex = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      Pen pen1 = new Pen(Color.Black, 2f);
      e.Graphics.DrawLine(pen1, new Point(0, 0), new Point(this.panelAxisX.Width, 0));
      Font font1 = new Font("Verdana", 8f, FontStyle.Bold);
      SolidBrush solidBrush = new SolidBrush(Color.Black);
      float num1 = (float) this.panelGraph.Width / this.m_fVisbleXSteps;
      float num2 = this.m_fVisibleXWidth / this.m_fVisbleXSteps;
      Pen pen2 = new Pen(Color.Black, 3f);
      float num3 = 20f;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() > 0)
        num3 = (float) this.m_SpectrumFile.SpectrumFileInfo[iSpectraIndex].EVPerChannel;
      for (int index = 0; index <= (int) this.m_fVisbleXSteps; ++index)
      {
        float num4 = (float) index * num2 + this.m_fVisbleXStartStep;
        double num5 = (double) num4 * (double) num3;
        string s1 = num4.ToString("F1");
        if (index == 0)
          e.Graphics.DrawString(s1, font1, (Brush) solidBrush, (float) ((double) index * (double) num1 - 2.0), (float) (this.panelAxisX.Height - 50));
        else if (index == (int) this.m_fVisbleXSteps)
          e.Graphics.DrawString(s1, font1, (Brush) solidBrush, (float) ((double) index * (double) num1 - 35.0), (float) (this.panelAxisX.Height - 50));
        else
          e.Graphics.DrawString(s1, font1, (Brush) solidBrush, (float) ((double) index * (double) num1 - 20.0), (float) (this.panelAxisX.Height - 50));
        string s2 = ((float) (num5 / 1000.0)).ToString("F3");
        if (index == 0)
          e.Graphics.DrawString(s2, font1, (Brush) solidBrush, (float) ((double) index * (double) num1 - 2.0), (float) (this.panelAxisX.Height - 35));
        else if (index == (int) this.m_fVisbleXSteps)
          e.Graphics.DrawString(s2, font1, (Brush) solidBrush, (float) ((double) index * (double) num1 - 35.0), (float) (this.panelAxisX.Height - 35));
        else
          e.Graphics.DrawString(s2, font1, (Brush) solidBrush, (float) ((double) index * (double) num1 - 20.0), (float) (this.panelAxisX.Height - 35));
        e.Graphics.DrawLine(pen2, new PointF((float) index * num1, 0.0f), new PointF((float) index * num1, 5f));
      }
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() > 0)
      {
        double resolution = (double) this.FindResolution(this.m_SpectrumFile.SpectrumFileInfo[iSpectraIndex].SpectrumData);
      }
      int num6 = 0;
      int num7 = 0;
      float num8 = 1f;
      if (this.m_SpectrumFile != null)
      {
        SpectrumInfo spectrumInfo = new SpectrumInfo(this.m_SpectrumFile, iSpectraIndex);
        num6 = spectrumInfo.RawCounts;
        num7 = spectrumInfo.ValidCounts;
        double liveTime = (double) spectrumInfo.LiveTime;
        int countsPerSecond = spectrumInfo.CountsPerSecond;
        num8 = spectrumInfo.ActiveTime;
      }
      float num9 = 0.0f;
      float num10 = 0.0f;
      float num11 = 0.0f;
      if ((double) num8 != 0.0)
      {
        num9 = (float) num6 / num8;
        num10 = (float) num7 / num8;
      }
      if (num6 != 0)
        num11 = (float) (100 * (num6 - num7)) / (float) num6;
      string str1 = "";
      string str2;
      if (!this.m_bLiveSpectrumMode)
      {
        str2 = "InputCounts/Sec = " + num9.ToString("F2") + " \t OutputCounts/Sec = " + num10.ToString("F2") + " \t Dead Time% = " + num11.ToString("F2");
      }
      else
      {
        if (str1.Length != 0)
          str1 += " \t ";
        if (this.BtoBCounter > 0)
          str1 = str1 + "BtoB Remaining = " + this.BtoBCounter.ToString() + " \t ";
        str2 = this.IllumSelect == null || this.IllumSelect.AppIllumCheck.Checked || this.m_bInstrumentInitiatedAssay ? str1 + "Time Elapsed = " + (this.m_iPacketCount >= 0 ? this.m_iPacketCount.ToString() : "0") : str1 + "Time Remaining = " + (this.IllumSelect.iAssayTime - this.m_iPacketCount).ToString("F2");
      }
      Font font2 = new Font("Verdana", 9f, FontStyle.Bold);
      int width = 1000;
      SizeF sizeF1 = new SizeF();
      SizeF sizeF2 = e.Graphics.MeasureString(str2, font2, width);
      Color color = Color.Red;
      if (this.cmbSpectrumFiles.Items.Count > 0 && this.cmbSpectrumFiles.SelectedItem is ComboBoxItem selectedItem)
        color = selectedItem.ForeColor;
      e.Graphics.DrawRectangle(new Pen(color, 1f), (float) (((double) this.panelAxisX.Width - (double) sizeF2.Width) / 2.0), (float) this.panelAxisX.Height - sizeF2.Height, sizeF2.Width, sizeF2.Height);
      e.Graphics.DrawString(str2, font2, Brushes.Black, new PointF((float) (((double) this.panelAxisX.Width - (double) sizeF2.Width) / 2.0), (float) this.panelAxisX.Height - sizeF2.Height));
    }

    private void panelGraph_Paint(object sender, PaintEventArgs e)
    {
      if (this.ROIForm != null)
      {
        SolidBrush solidBrush1 = new SolidBrush(Color.Beige);
        SolidBrush solidBrush2 = new SolidBrush(Color.Black);
        Font font = new Font("Verdana", 8f);
        StringFormat format = new StringFormat(StringFormatFlags.FitBlackBox);
        format.LineAlignment = StringAlignment.Near;
        format.Alignment = StringAlignment.Center;
        int num = this.ROIForm.NumRegions();
        for (int index = 0; index < num; ++index)
        {
          SpectrumViewerROI.ROIBounds bounds = this.ROIForm.GetBounds(index);
          float x = this.KeVToPanelPos(bounds.start);
          float width = this.KeVToPanelPos(bounds.end) - x;
          if ((double) width > 0.0)
          {
            e.Graphics.FillRectangle((Brush) solidBrush1, x, 0.0f, width, (float) this.panelGraph.Height);
            RectangleF layoutRectangle = new RectangleF(x, 0.0f, width, 30f);
            e.Graphics.DrawString(this.ROIForm.GetName(index), font, (Brush) solidBrush2, layoutRectangle, format);
          }
        }
      }
      if (Settings.Default.ShowGridLines)
      {
        Pen pen = new Pen(Color.LightGray, 0.1f);
        float height = (float) this.panelGraph.Height;
        float width = (float) this.panelGraph.Width;
        float num1 = width / this.m_fVisbleXSteps;
        for (int index = 1; index <= (int) this.m_fVisbleXSteps; ++index)
        {
          float num2 = (float) index * num1;
          e.Graphics.DrawLine(pen, num2, 0.0f, num2, height);
        }
        float num3 = height / this.m_fVisbleYSteps;
        for (int index = 1; index <= (int) this.m_fVisbleYSteps; ++index)
        {
          float num4 = height - (float) index * num3;
          e.Graphics.DrawLine(pen, 0.0f, num4, width, num4);
        }
      }
      if (!this.m_bDoRefresh)
        return;
      bool bBackground = false;
      PointF[] m_ActiveSpecPoints = (PointF[]) null;
      int iSpectraCounter = 0;
      int num5 = Settings.Default.OverlaySpectraEnable ? 1 : 0;
      string overlaySpectraFile = Settings.Default.OverlaySpectraFile;
      if (this.m_MultiSpectrumDataList.Count<MultiSpectrumData>() == 0)
        return;
      foreach (MultiSpectrumData multiSpectrumData in this.m_MultiSpectrumDataList)
      {
        if (this.oneOnly != -1)
        {
          bool flag = true;
          if (Settings.Default.OverlaySpectraEnable && iSpectraCounter == this.m_MultiSpectrumDataList.Count<MultiSpectrumData>() - 1)
            flag = false;
          if (this.oneOnly == iSpectraCounter)
            flag = false;
          if (this.m_bLiveSpectrumMode)
            flag = false;
          if (flag)
          {
            ++iSpectraCounter;
            continue;
          }
        }
        Color randomColor = Color.Red;
        if (multiSpectrumData != null)
          randomColor = multiSpectrumData.DisplayColor;
        if (Settings.Default.OverlaySpectraEnable && Settings.Default.OverlaySpectraFile != null && iSpectraCounter == this.m_MultiSpectrumDataList.Count<MultiSpectrumData>() - 1)
        {
          randomColor = Color.Black;
          bBackground = true;
        }
        if (Settings.Default.ShowBackground)
          this.DrawSpectra(iSpectraCounter, multiSpectrumData.SpectraIndex, (int[]) multiSpectrumData.BackgroundData, ref m_ActiveSpecPoints, ref e, Color.Black, true);
        this.DrawSpectra(iSpectraCounter, multiSpectrumData.SpectraIndex, (int[]) multiSpectrumData.SpectrumData, ref m_ActiveSpecPoints, ref e, randomColor, bBackground);
        ++iSpectraCounter;
      }
      if (!this.ShowIntensityLines(this.m_ActiveElements))
        return;
      foreach (Element activeElement in this.m_ActiveElements)
      {
        Color color = Color.Blue;
        if (activeElement != null)
          color = activeElement.BackColor;
        Pen pen = new Pen(color, 1f);
        float num6 = 20f;
        int index = this.m_iSpectraIndex;
        if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
          index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
        if (this.m_SpectrumFile != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() > 0)
        {
          num6 = (float) this.m_SpectrumFile.SpectrumFileInfo[index].EVPerChannel;
          if ((double) num6 < 0.001)
            num6 = 20f;
        }
        bool flag = false;
        float num7 = 0.0f;
        foreach (LineIntensity lineIntensity in activeElement.m_LineIntensity)
        {
          if (this.DrawThisLine(lineIntensity) && (double) lineIntensity.m_fIntensity > 0.0)
          {
            float num8 = (float) ((double) this.panelGraph.Width / (double) this.m_fVisibleXWidth * ((double) (lineIntensity.m_fLine * 1000f / num6) - (double) this.m_fVisbleXStartStep));
            float num9;
            if (!flag)
            {
              num7 = this.FindMidDataPointY(m_ActiveSpecPoints, num8) * (lineIntensity.m_fIntensity / 100f);
              num9 = num7;
              flag = true;
            }
            else
              num9 = (float) this.panelGraph.Height - ((float) this.panelGraph.Height - num7) * (lineIntensity.m_fIntensity / 100f);
            e.Graphics.DrawLine(pen, new PointF(num8, num9), new PointF(num8, (float) this.panelGraph.Height));
            string strText = activeElement.Name;
            if (this.m_bShowLineNames)
              strText = strText + " " + lineIntensity.m_LineName;
            this.DrawLineLabel(e.Graphics, pen, strText, num8, num9);
          }
        }
      }
    }

    private void DrawSpectra(
      int iSpectraCounter,
      int spectraIndex,
      int[] spectraData,
      ref PointF[] m_ActiveSpecPoints,
      ref PaintEventArgs e,
      Color randomColor,
      bool bBackground)
    {
      PointF[] pointFArray1 = new PointF[((IEnumerable<int>) spectraData).Count<int>()];
      int num1 = 0;
      int num2 = 0;
      foreach (int num3 in spectraData)
        num2 = num3 > num2 ? num3 : num2;
      bool flag = false;
      float num4 = 1f;
      if (this.m_SpectrumNormalizeFactor != null && this.m_SpectrumNormalizeFactor.Count > iSpectraCounter)
        num4 = Convert.ToSingle(this.m_SpectrumNormalizeFactor[iSpectraCounter]);
      if (this.m_bNormalize && (double) num4 > 1.0 && iSpectraCounter != this.m_LargeSpect)
        flag = true;
      int num5 = 0;
      foreach (int num6 in spectraData)
      {
        float num7 = this.m_fVisbleXStartStep + this.m_fVisibleXWidth;
        if (num1 >= (int) this.m_fVisbleXStartStep && num1 <= (int) num7)
        {
          float num8 = (float) this.panelGraph.Width / this.m_fVisibleXWidth * ((float) num1 - this.m_fVisbleXStartStep);
          float num9 = (float) this.panelGraph.Height - (float) ((double) this.panelGraph.Height / (double) this.m_YaxisHeight * (double) this.m_fVerticalMutiplier * (flag ? (double) num6 * (double) num4 : (double) num6));
          float x = (double) num8 < 0.0 ? 0.0f : num8;
          float y = (double) num9 < 0.0 ? 0.0f : num9;
          pointFArray1[num5++] = new PointF(x, y);
        }
        ++num1;
      }
      if (num5 <= 1)
        return;
      int length = num5 - 1;
      PointF[] pointFArray2 = new PointF[length];
      int num10 = 0;
      foreach (PointF pointF in pointFArray1)
      {
        pointFArray2[num10++] = pointF;
        if (num10 >= length)
          break;
      }
      float width = 1.5f;
      if (this.cmbSpectrumFiles.Items.Count > 0 && this.cmbSpectrumFiles.SelectedIndex == iSpectraCounter)
      {
        if (this.cmbSpectrumFiles.Items.Count > 1)
          width = this.m_bDataFromLiveSpectrum ? 1f : 2f;
        m_ActiveSpecPoints = pointFArray2;
      }
      if (bBackground)
        width = 1.5f;
      Pen pen = new Pen(randomColor, width);
      pen.DashStyle = (DashStyle) spectraIndex;
      if (bBackground)
        pen.DashStyle = DashStyle.Solid;
      if (pointFArray2[0].Y.CompareTo(float.NaN) == 0)
        this.m_bNoDataToDrawError = true;
      else if (((IEnumerable<PointF>) pointFArray2).Count<PointF>() == 1)
        e.Graphics.DrawEllipse(pen, pointFArray2[0].X, pointFArray2[0].Y, 2f, 2f);
      else
        e.Graphics.DrawLines(pen, pointFArray2);
      if ((double) this.m_ptPeakPoint.Y <= 0.0)
        return;
      float num11 = (float) this.panelGraph.Width / this.m_fVisibleXWidth * (this.m_ptPeakPoint.X - this.m_fVisbleXStartStep);
      float num12 = (float) this.panelGraph.Height - (float) this.panelGraph.Height / (float) this.m_YaxisHeight * this.m_fVerticalMutiplier * this.m_ptPeakPoint.Y;
      float num13 = (double) num11 < 0.0 ? 0.0f : num11;
      float num14 = (double) num12 < 0.0 ? 0.0f : num12;
    }

    private void DrawLineLabel(
      Graphics graphics,
      Pen pen,
      string strText,
      float xPos,
      float yPos)
    {
      Font font = new Font("Verdana", 8f, FontStyle.Bold);
      int width = 1000;
      SizeF sizeF1 = new SizeF();
      SizeF sizeF2 = graphics.MeasureString(strText, font, width);
      yPos = Math.Max(sizeF2.Height, yPos);
      graphics.DrawRectangle(pen, xPos - sizeF2.Width / 2f, yPos - sizeF2.Height, sizeF2.Width, sizeF2.Height);
      graphics.DrawString(strText, font, Brushes.Black, new PointF(xPos - sizeF2.Width / 2f, yPos - sizeF2.Height));
    }

    private float FindMidDataPointY(PointF[] points, float x)
    {
      float midDataPointY = 0.0f;
      if (points == null)
        return midDataPointY;
      int num = ((IEnumerable<PointF>) points).Count<PointF>();
      for (int index = 1; index <= num; ++index)
      {
        PointF point1 = points[index - 1];
        if ((double) point1.X == (double) x)
        {
          midDataPointY = point1.Y;
          break;
        }
        if ((double) point1.X > (double) x)
        {
          if (index < 2)
          {
            midDataPointY = point1.Y;
            break;
          }
          PointF point2 = points[index - 2];
          PointF pointF = point1;
          midDataPointY = point2.Y + (float) (((double) pointF.Y - (double) point2.Y) / ((double) pointF.X - (double) point2.X) * ((double) x - (double) point2.X));
          break;
        }
      }
      return midDataPointY;
    }

    private PointF FindNearestPointWithX(PointF[] points, float x)
    {
      PointF nearestPointWithX = new PointF(0.0f, 0.0f);
      if (((IEnumerable<PointF>) points).Count<PointF>() > 1)
      {
        float num = -1f;
        foreach (PointF point in points)
        {
          if ((double) num != -1.0 && (double) Math.Abs(point.X - x) > (double) num)
            return point;
          num = Math.Abs(point.X - x);
        }
      }
      return nearestPointWithX;
    }

    private bool DrawThisLine(LineIntensity lineIntensity)
    {
      foreach (AlphaLines alphaLine in this.m_AlphaLines)
      {
        switch (alphaLine)
        {
          case AlphaLines.KLine:
            if (lineIntensity.m_LineName.StartsWith("K"))
              return true;
            continue;
          case AlphaLines.LLine:
            if (lineIntensity.m_LineName.StartsWith("L"))
              return true;
            continue;
          case AlphaLines.MLine:
            if (lineIntensity.m_LineName.StartsWith("M"))
              return true;
            continue;
          default:
            continue;
        }
      }
      return false;
    }

    private bool ShowIntensityLines(List<Element> elements)
    {
      if (elements.Count == 0)
        return false;
      foreach (Element element in elements)
      {
        foreach (LineIntensity lineIntensity in element.m_LineIntensity)
        {
          if ((double) lineIntensity.m_fIntensity > 0.0)
            return true;
        }
      }
      return false;
    }

    private bool ShowIntensityLines(Element element)
    {
      if (element == null)
        return false;
      foreach (LineIntensity lineIntensity in element.m_LineIntensity)
      {
        if ((double) lineIntensity.m_fIntensity > 0.0)
          return true;
      }
      return false;
    }

    public void PaintWithElement(List<Element> elements, bool bShowLineNames)
    {
      this.m_ActiveElements = elements;
      this.m_bShowLineNames = bShowLineNames;
      this.m_bDoRefresh = true;
      this.panelGraph.Refresh();
    }

    public void LineButtonFired(List<AlphaLines> lines, bool bShowLineNames)
    {
      this.m_AlphaLines.Clear();
      this.m_AlphaLines = lines;
      this.m_bShowLineNames = bShowLineNames;
      if (this.m_MultiSpectrumDataList.Count <= 0 || this.m_bLiveSpectrumMode)
        return;
      this.m_bDoRefresh = true;
      this.panelGraph.Refresh();
    }

    private Color CreateRandomColor() => Color.FromArgb(this.randomGen.Next(0, 200), this.randomGen.Next(0, 200), this.randomGen.Next(0, 200));

    private void panelAxisY_Resize(object sender, EventArgs e) => this.DrawCoordinates();

    private void panelGraph_Resize(object sender, EventArgs e)
    {
      this.m_CursorControl.Height = this.panelGraph.Height + 4;
      this.m_AreaSelector.Height = this.panelGraph.Height + 4;
      this.DrawCoordinates();
      this.UpdateCursorPosition();
    }

    private void UpdateCursorPosition()
    {
      if ((double) this.m_fPreviousCursorLeft == -1.0)
        this.m_fPreviousCursorLeft = (float) this.m_CursorControl.Left;
      if (this.m_iPreviousPanelWith != -1)
      {
        this.m_fPreviousCursorLeft = (float) this.panelGraph.Width * (this.m_fPreviousCursorLeft / (float) this.m_iPreviousPanelWith);
        this.m_CursorControl.Left = (int) this.m_fPreviousCursorLeft;
      }
      this.m_iPreviousPanelWith = this.panelGraph.Width;
    }

    private void panelAxisX_Resize(object sender, EventArgs e) => this.DrawCoordinates();

    private void DrawCoordinates() => this.RefreshGraph();

    private int colorIndex(Color color)
    {
      for (int index = 0; index < this.m_PdzViewerOptions2.ListOfSpectrumColors.Count; ++index)
      {
        if (this.m_PdzViewerOptions2.ListOfSpectrumColors[index] == color)
          return index;
      }
      return -1;
    }

    public void UpdateSpectrumInformation()
    {
      try
      {
        SpectrumInfo spectrumInfo;
        if (!this.m_bDataFromLiveSpectrum)
        {
          if (this.m_CurrentSpectrumFileName.Length == 0)
          {
            spectrumInfo = new SpectrumInfo((SpectrumFile) null, this.m_iSpectraIndex);
          }
          else
          {
            this.m_PreviousSpectrumFileName = this.m_CurrentSpectrumFileName;
            this.m_SpectrumFile = new SpectrumFile();
            this.m_SpectrumFile.LoadFromFile(this.m_CurrentSpectrumFileName, (string) null, 45);
            spectrumInfo = new SpectrumInfo(this.m_SpectrumFile, this.m_iSpectraIndex);
          }
        }
        else
          spectrumInfo = new SpectrumInfo(this.m_SpectrumFile, 0);
        foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
        {
          if (activeForm is SpectrumViewerInformation)
          {
            ((SpectrumViewerInformation) activeForm).SpectrumInformation.SelectedObject = (object) spectrumInfo;
            break;
          }
        }
      }
      catch (Exception ex)
      {
      }
    }

    public void LoadPdzFiles()
    {
      this.m_bDoRefresh = false;
      this.m_MultiSpectrumDataList = new ThreadSafeList<MultiSpectrumData>();
      this.m_ptPeakPoint = new PointF(0.0f, 0.0f);
      this.m_bNormalize = false;
      this.m_SpectrumCount = this.m_FileNameList.Count;
      if (this.cmbSpectrumFiles.Items != null && this.cmbSpectrumFiles.Items.Count > 0)
        this.cmbSpectrumFiles.Items.Clear();
      new SpectrumFileEntry().FileName = "";
      int num1 = 0;
      int num2 = 0;
      foreach (SpectrumFileEntry spectrumFileEntry1 in this.m_FileNameList.ToList<SpectrumFileEntry>())
      {
        SpectrumFileEntry spFile = spectrumFileEntry1;
        SpectrumFileEntry spectrumFileEntry2;
        if (spFile.spectrumFile == null)
        {
          spectrumFileEntry2 = this.m_FileNameList.Find((Predicate<SpectrumFileEntry>) (x => x.FileName == spFile.FileName));
          try
          {
            SpectrumFile spectrumFile = new SpectrumFile();
            if (spectrumFile.LoadFromFile(spFile.FileName, (string) null, 0))
              spectrumFileEntry2.spectrumFile = spectrumFile;
          }
          catch (Exception ex)
          {
          }
          if (spectrumFileEntry2.spectrumFile == null)
          {
            this.m_FileNameList?.Remove(spectrumFileEntry2);
            string text = "File " + spectrumFileEntry2.FileName + " is not a valid PDZ file, it has been removed from the list of files to open.\n";
            this.m_SpectrumCount = this.m_FileNameList.Count;
            if (this.BtoBCounter <= 0)
            {
              int num3 = (int) MessageBox.Show(text);
            }
          }
        }
        else
          spectrumFileEntry2 = spFile;
        Color color = spFile.Color;
        if (spectrumFileEntry2.spectrumFile != null)
        {
          int realStart = this.spectrumStartBin(spectrumFileEntry2.spectrumFile.SerialString);
          int num4 = 0;
          foreach (SpectrumInFile spectrum in spectrumFileEntry2.spectrumFile)
          {
            this.m_MultiSpectrumDataList.Add(new MultiSpectrumData()
            {
              SpectrumData = (object) spectrum.SpectrumData,
              BackgroundData = (object) this.computeBackground(spectrum.SpectrumData, realStart),
              FileIndex = num1,
              SpectraIndex = num4,
              DisplayColor = color
            });
            this.DetermineSpectraPeak(spectrum);
            ComboBoxItem comboBoxItem = spectrumFileEntry2.spectrumFile.NumSpectra <= 1 ? new ComboBoxItem(Path.GetFileName(spectrumFileEntry2.FileName), (object) num1.ToString(), color) : new ComboBoxItem(Path.GetFileName(spectrumFileEntry2.FileName) + ":" + (num4 + 1).ToString(), (object) num2.ToString(), color);
            this.cmbSpectrumFiles.Items.Add((object) comboBoxItem);
            using (Graphics graphics = Graphics.FromImage((Image) new Bitmap(1, 1)))
            {
              SizeF sizeF = graphics.MeasureString(comboBoxItem.ToString(), this.cmbSpectrumFiles.Font);
              if ((double) this.cmbSpectrumFiles.DropDownWidth < (double) sizeF.Width)
                this.cmbSpectrumFiles.DropDownWidth = (int) sizeF.Width;
            }
            ++num4;
          }
          ++num1;
          num2 = num1 + num4;
        }
        if (this.m_SpectrumCount == 0)
          break;
      }
      this.m_bDoRefresh = true;
      this.RefreshOverlaySpectra(false);
      this.DrawCoordinates();
      this.m_CurrentSpectrumFileName = "";
      if (this.m_SpectrumCount <= 0)
        return;
      this.m_CurrentSpectrumFileName = this.m_FileNameList[this.m_FileNameList.Count<SpectrumFileEntry>() - 1].FileName;
      this.cmbSpectrumFiles.SelectedIndex = this.cmbSpectrumFiles.Items.Count - 1;
      this.m_PreviousSpectrumFileName = this.m_CurrentSpectrumFileName;
      this.m_SpectrumFile = new SpectrumFile();
      this.m_SpectrumFile.LoadFromFile(this.m_CurrentSpectrumFileName, (string) null, 0);
      SpectrumInfo spectrumInfo = new SpectrumInfo(this.m_SpectrumFile, this.m_iSpectraIndex);
      foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
      {
        if (activeForm is SpectrumViewerInformation)
        {
          ((SpectrumViewerInformation) activeForm).SpectrumInformation.SelectedObject = (object) spectrumInfo;
          break;
        }
      }
    }

    public List<SpectrumViewerROI.ROIStats> GetROIStats(ref float startKeV, ref float endKeV)
    {
      double num = this.KeVPerChannel();
      int startChannel = (int) Math.Round((double) startKeV / num, 1);
      int endChannel = (int) Math.Round((double) endKeV / num - 0.10000000149011612, 1);
      if (startChannel < 0)
        startChannel = 0;
      if (endChannel > 2047)
        endChannel = 2047;
      startKeV = (float) Math.Round((double) startChannel * num, 3);
      endKeV = (float) Math.Round((double) (endChannel + 1) * num, 3);
      return this.getROIStats(startChannel, endChannel);
    }

    public void ROIInfoChanged() => this.panelGraph.Invalidate();

    private void PdzViewer_Load(object sender, EventArgs e)
    {
      this.cmbSpectrumFiles.Items.Clear();
      this.m_YaxisHeight = Convert.ToInt32(Settings.Default.VerticalAxisHeight);
      this.m_fVisbleYSteps = Convert.ToSingle(Settings.Default.VerticalAxisTotalPoints);
      this.m_fVisibleXWidth = Convert.ToSingle(Settings.Default.HorizontalAxisTotalPoints);
      this.m_fVisbleXSteps = Convert.ToSingle(Settings.Default.HorizontalAxisWidth);
      this.CreateLineControl();
      this.WindowState = FormWindowState.Maximized;
      this.menuReset_Click(sender, e);
      this.RefreshOverlaySpectra(false);
    }

    private int spectrumStartBin(string serialNumber)
    {
      int num = 29;
      if (serialNumber != null && serialNumber.Length >= 4)
      {
        switch (serialNumber[3])
        {
          case 'F':
          case 'N':
            num = 34;
            break;
          case 'G':
            num = 29;
            break;
          default:
            num = 29;
            break;
        }
      }
      return num;
    }

    private void ZoomGraphHorizontallyUp(bool bUp)
    {
      double num1 = (double) this.m_fVisbleXStartStep + (double) this.m_fVisibleXWidth;
      float channel = this.PanelPosToChannel(this.m_CursorControl.Left);
      float num2 = channel - this.m_fVisbleXStartStep;
      float num3 = (float) num1 - channel;
      float num4 = (float) (5.0 * (double) num2 / ((double) num2 + (double) num3));
      float num5 = (float) (5.0 * (double) num3 / ((double) num2 + (double) num3));
      float num6 = this.m_fVisbleXStartStep + (bUp ? -1f * num4 : num4);
      float num7 = (float) (num1 + (bUp ? (double) num5 : -1.0 * (double) num5));
      float num8 = (double) num6 > 2048.0 ? 2048f : num6;
      float num9 = (double) num7 > 2048.0 ? 2048f : num7;
      float num10 = (double) num8 < 0.0 ? 0.0f : num8;
      float num11 = (double) num9 < 0.0 ? 0.0f : num9;
      if ((double) num11 <= (double) num10 || (double) num10 == (double) num11)
        return;
      this.SaveXAxisInfo();
      this.m_fVisbleXStartStep = num10;
      this.m_fVisibleXWidth = num11 - num10;
      this.RefreshGraph();
      this.UpdateCursorInformation();
      this.UpdateCursorPosition();
    }

    private void SaveXAxisInfo() => this.m_ZoomHistoryStack.Push((object) new SpectrumViewer.XAxisInfo(this.m_fVisbleXStartStep, this.m_fVisibleXWidth, this.m_CursorControl.Left));

    private bool RestoreXAxisInfo()
    {
      int num = this.m_ZoomHistoryStack.Count > 0 ? 1 : 0;
      if (num == 0)
        return num != 0;
      SpectrumViewer.XAxisInfo xaxisInfo = (SpectrumViewer.XAxisInfo) this.m_ZoomHistoryStack.Pop();
      this.m_fVisbleXStartStep = xaxisInfo.start;
      this.m_fVisibleXWidth = xaxisInfo.width;
      this.m_CursorControl.Left = xaxisInfo.cursor;
      return num != 0;
    }

    private void ZoomGraphVerticallyUp(bool bUp)
    {
      double verticalMutiplier1 = (double) this.m_fVerticalMutiplier;
      this.m_fVerticalMutiplier += bUp ? 1f : -1f;
      if ((double) this.m_fVerticalMutiplier < 1.0)
        this.m_fVerticalMutiplier = 1f;
      double verticalMutiplier2 = (double) this.m_fVerticalMutiplier;
      if ((double) Math.Abs((float) (verticalMutiplier1 - verticalMutiplier2)) <= 0.10000000149011612)
        return;
      this.RefreshGraph();
    }

    private void PanGraphLeft(bool bLeft)
    {
      double num1 = (double) this.m_fVisbleXStartStep + (double) this.m_fVisibleXWidth;
      float num2 = this.m_fVisbleXStartStep + (bLeft ? 1f : -1f);
      double num3 = bLeft ? 1.0 : -1.0;
      float num4 = (float) (num1 + num3);
      if ((double) num4 <= (double) num2 || (double) num2 == (double) num4 || (double) num2 < 0.0 || (double) num4 > 2048.0)
        return;
      this.SaveXAxisInfo();
      this.m_fVisbleXStartStep = num2;
      this.m_fVisibleXWidth = num4 - num2;
      this.RefreshGraph();
      this.UpdateCursorInformation();
      this.UpdateCursorPosition();
    }

    private bool GraphHasFocus() => this.panelGraph.Focused || this.panelAxisX.Focused || this.panelAxisY.Focused;

    protected override bool ProcessCmdKey(ref Message msg, Keys keyData)
    {
      if (!this.GraphHasFocus())
        return base.ProcessCmdKey(ref msg, keyData);
      bool flag = false;
      switch (keyData)
      {
        case Keys.Escape:
          if (this.m_AreaSelector.Visible)
            this.m_AreaSelector.Visible = false;
          flag = true;
          break;
        case Keys.Prior:
          this.ZoomGraphVerticallyUp(true);
          flag = true;
          break;
        case Keys.Next:
          this.ZoomGraphVerticallyUp(false);
          flag = true;
          break;
        case Keys.Left:
        case Keys.Down:
          if (this.m_CursorControl.Left > 0)
          {
            --this.m_CursorControl.Left;
            this.UpdateCursorInformation();
            this.m_fPreviousCursorLeft = (float) this.m_CursorControl.Left;
          }
          flag = true;
          break;
        case Keys.Up:
        case Keys.Right:
          if (this.m_CursorControl.Left < this.panelGraph.Width)
          {
            ++this.m_CursorControl.Left;
            this.UpdateCursorInformation();
            this.m_fPreviousCursorLeft = (float) this.m_CursorControl.Left;
          }
          flag = true;
          break;
        case Keys.Left | Keys.Shift:
        case Keys.Down | Keys.Shift:
          this.PanGraphLeft(true);
          flag = true;
          break;
        case Keys.Up | Keys.Shift:
        case Keys.Right | Keys.Shift:
          this.PanGraphLeft(false);
          flag = true;
          break;
        case Keys.Left | Keys.Control:
        case Keys.Down | Keys.Control:
          this.ZoomGraphHorizontallyUp(true);
          flag = true;
          break;
        case Keys.Up | Keys.Control:
        case Keys.Right | Keys.Control:
          this.ZoomGraphHorizontallyUp(false);
          flag = true;
          break;
        case Keys.C | Keys.Control:
          this.ExportSpectrumToClipboard();
          flag = true;
          break;
        default:
          base.ProcessCmdKey(ref msg, keyData);
          break;
      }
      return flag;
    }

    private void CreateLineControl()
    {
      this.m_AreaSelector.Height = this.panelGraph.Height + 4;
      this.panelGraph.Controls.Add((Control) this.m_AreaSelector);
      this.m_CursorControl.Size = new Size(1, this.panelGraph.Height + 4);
      this.m_CursorControl.Left = 0;
      this.m_CursorControl.Top = -2;
      this.m_CursorControl.BackColor = Settings.Default.CursorLineColor;
      this.panelGraph.Controls.Add((Control) this.m_CursorControl);
      this.m_AreaSelector.Visible = false;
      this.m_CursorControl.Visible = true;
    }

    private void panelGraph_MouseDown(object sender, MouseEventArgs e)
    {
      this.panelGraph.Focus();
      if (e.Button == MouseButtons.Left)
      {
        this.m_iTickCount = Environment.TickCount;
        this.m_iStartX = e.X;
        this.m_iCursorInitialPos = this.m_CursorControl.Left;
        if (this.m_iStartX < 0)
          this.m_iStartX = 0;
        this.m_AreaSelector.Left = this.m_iStartX;
        this.m_AreaSelector.Top = -2;
        this.m_AreaSelector.Visible = true;
        this.m_AreaSelector.Height = this.panelGraph.Height + 4;
      }
      else
      {
        if (e.Button != MouseButtons.Right)
          return;
        bool flag = false;
        if (this.ROIForm != null)
        {
          this.m_ROIRightClickIndex = this.ROIForm.GetIndexFromKeV(this.PanelPosToKeV(e.X));
          flag = this.m_ROIRightClickIndex >= 0;
        }
        this.menuRenameROI.Enabled = flag;
        this.menuDeleteROI.Enabled = flag;
        this.menuChangeROIBounds.Enabled = flag;
      }
    }

    private void panelGraph_MouseMove(object sender, MouseEventArgs e)
    {
      if (!this.m_AreaSelector.Visible)
        return;
      int num = e.X - this.m_iStartX;
      this.m_AreaSelector.Left = num >= 0 ? this.m_iStartX : e.X;
      this.m_AreaSelector.Width = Math.Abs(num);
    }

    private void panelGraph_MouseUp(object sender, MouseEventArgs e)
    {
      if (e.Button != MouseButtons.Left || !this.m_AreaSelector.Visible)
        return;
      this.m_AreaSelector.Visible = false;
      if (Environment.TickCount - this.m_iTickCount < 200)
        return;
      this.m_iEndX = e.X;
      if (this.m_iEndX < 0)
        this.m_iEndX = 0;
      if (this.m_iStartX == this.m_iEndX)
        return;
      if (this.m_iEndX < this.m_iStartX)
      {
        int iEndX = this.m_iEndX;
        this.m_iEndX = this.m_iStartX;
        this.m_iStartX = iEndX;
      }
      float channel1 = this.PanelPosToChannel(this.m_iStartX);
      float channel2 = this.PanelPosToChannel(this.m_iEndX);
      if ((Control.ModifierKeys & Keys.Shift) == Keys.Shift)
        this.RegionOfInterest(channel1, channel2);
      else
        this.ZoomRegion(channel1, channel2);
    }

    private float PanelPosToChannel(int X) => (float) X * this.m_fVisibleXWidth / (float) this.panelGraph.Width + this.m_fVisbleXStartStep;

    private float PanelPosToKeV(int X) => this.PanelPosToChannel(X) * (float) this.KeVPerChannel();

    private float ChannelToPanelPos(float channel) => (float) (((double) channel - (double) this.m_fVisbleXStartStep) * ((double) this.panelGraph.Width / (double) this.m_fVisibleXWidth));

    private float KeVToPanelPos(float keV) => this.ChannelToPanelPos(keV / (float) this.KeVPerChannel());

    private void RegionOfInterest(float start, float end)
    {
      int startChannel = (int) Math.Round((double) start, 1);
      int endChannel = (int) Math.Round((double) end - 0.10000000149011612, 1);
      if (startChannel < 0)
        startChannel = 0;
      if (endChannel > 2047)
        endChannel = 2047;
      double num1 = this.KeVPerChannel();
      float num2 = (float) Math.Round((double) startChannel * num1, 3);
      float num3 = (float) Math.Round((double) (endChannel + 1) * num1, 3);
      List<SpectrumViewerROI.ROIStats> roiStats = this.getROIStats(startChannel, endChannel);
      if (this.ROIForm == null)
      {
        this.ROIForm = new SpectrumViewerROI(this);
        this.ROIForm.FormClosed += new FormClosedEventHandler(this.ROIFormClosed);
      }
      this.ROIForm.AddROI(num2, num3, roiStats, this.getDefaultROIName(num2, num3));
      this.ShowForm((Form) this.ROIForm);
    }

    private List<SpectrumViewerROI.ROIStats> getROIStats(int startChannel, int endChannel)
    {
      List<SpectrumViewerROI.ROIStats> roiStats1 = new List<SpectrumViewerROI.ROIStats>();
      foreach (MultiSpectrumData multiSpectrumData in this.m_MultiSpectrumDataList)
      {
        long grossCount = 0;
        long noiseCount = 0;
        for (int index = startChannel; index <= endChannel; ++index)
        {
          grossCount += (long) ((int[]) multiSpectrumData.SpectrumData)[index];
          noiseCount += (long) ((int[]) multiSpectrumData.BackgroundData)[index];
        }
        long netCount = grossCount - noiseCount;
        if (netCount < 0L)
        {
          noiseCount = grossCount;
          netCount = 0L;
        }
        SpectrumViewerROI.ROIStats roiStats2 = new SpectrumViewerROI.ROIStats(this.m_FileNameList[multiSpectrumData.FileIndex].FileName, multiSpectrumData.DisplayColor, grossCount, netCount, noiseCount);
        roiStats1.Add(roiStats2);
      }
      return roiStats1;
    }

    private void ROIFormClosed(object sender, FormClosedEventArgs e)
    {
      this.RemoveForm((Form) this.ROIForm);
      this.ROIForm = (SpectrumViewerROI) null;
      this.panelGraph.Invalidate();
    }

    private double KeVPerChannel()
    {
      double num = 20.0;
      int index = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null)
      {
        if (index >= ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>())
          index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
        num = this.m_SpectrumFile.SpectrumFileInfo[index].EVPerChannel;
      }
      return num / 1000.0;
    }

    private string getDefaultROIName(float fStartKeV, float fEndKev)
    {
      string defaultRoiName = "";
      float num = 0.0f;
      if (this.ShowIntensityLines(this.m_ActiveElements))
      {
        foreach (Element activeElement in this.m_ActiveElements)
        {
          foreach (LineIntensity lineIntensity in activeElement.m_LineIntensity)
          {
            if ((double) lineIntensity.m_fLine >= (double) fStartKeV && (double) lineIntensity.m_fLine <= (double) fEndKev && (double) lineIntensity.m_fIntensity > (double) num)
            {
              defaultRoiName = activeElement.Name;
              if (this.m_bShowLineNames)
                defaultRoiName = defaultRoiName + " " + lineIntensity.m_LineName;
              num = lineIntensity.m_fIntensity;
            }
          }
        }
      }
      return defaultRoiName;
    }

    private void ZoomRegion(float start, float end)
    {
      this.m_CursorControl.Left = this.m_iCursorInitialPos;
      this.SaveXAxisInfo();
      this.SaveCursor();
      this.m_fVisbleXStartStep = start;
      this.m_fVisibleXWidth = end - start;
      this.RestoreCursor();
      this.RefreshGraph();
      this.UpdateCursorInformation();
    }

    private void panelGraph_MouseWheel(object sender, MouseEventArgs e)
    {
      double verticalMutiplier1 = (double) this.m_fVerticalMutiplier;
      this.m_fVerticalMutiplier += e.Delta > 0 ? 1f : -1f;
      if ((double) this.m_fVerticalMutiplier < 1.0)
        this.m_fVerticalMutiplier = 1f;
      double verticalMutiplier2 = (double) this.m_fVerticalMutiplier;
      if ((double) Math.Abs((float) (verticalMutiplier1 - verticalMutiplier2)) <= 0.10000000149011612)
        return;
      this.RefreshGraph();
    }

    private void menuReset_Click(object sender, EventArgs e)
    {
      this.m_bNormalize = false;
      this.m_fVerticalMutiplier = 1f;
      this.m_fVisbleXStartStep = 0.0f;
      this.m_fVisibleXWidth = 2048f;
      this.m_CursorControl.Left = 0;
      this.RefreshGraph();
      this.UpdateCursorInformation();
    }

    private void menuUnZoom_Click(object sender, EventArgs e)
    {
      if (!this.RestoreXAxisInfo())
        return;
      this.RefreshGraph();
      this.UpdateCursorInformation();
    }

    private void contextMenu_Opening(object sender, CancelEventArgs e)
    {
      this.menuUnZoom.Enabled = this.m_ZoomHistoryStack.Count > 0;
      this.menuNormalize.Enabled = this.m_MultiSpectrumDataList.Count >= 2;
    }

    private void PdzViewer_FormClosing(object sender, FormClosingEventArgs e)
    {
      for (int index = 0; index < SpectrumViewer.m_ActiveForms.Count<Form>(); ++index)
        SpectrumViewer.m_ActiveForms[index].Close();
      if (!this.backgroundWorker.IsBusy)
        return;
      this.backgroundWorker.CancelAsync();
    }

    private void ShowForm(Form formToShow)
    {
      Form form = (Form) null;
      foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
      {
        if (activeForm.Name == formToShow.Name)
        {
          form = activeForm;
          break;
        }
      }
      if (form == null)
      {
        form = formToShow;
        form.Owner = (Form) this;
        SpectrumViewer.m_ActiveForms.Add(formToShow);
      }
      form.Show();
      form.Activate();
    }

    public void RemoveForm(Form formToRemove)
    {
      foreach (Control activeForm in SpectrumViewer.m_ActiveForms)
      {
        if (activeForm.Name == formToRemove.Name)
        {
          SpectrumViewer.m_ActiveForms.Remove(formToRemove);
          break;
        }
      }
    }

    private void ReloadFileListCombo()
    {
      int selectedIndex = this.cmbSpectrumFiles.SelectedIndex;
      this.cmbSpectrumFiles.Items.Clear();
      int num1 = 0;
      int num2 = 0;
      foreach (SpectrumFileEntry fileName in this.m_FileNameList)
      {
        SpectrumFileEntry spFile = fileName;
        int num3 = 0;
        SpectrumFileEntry spectrumFileEntry;
        if (spFile.spectrumFile == null)
        {
          spectrumFileEntry = this.m_FileNameList.Find((Predicate<SpectrumFileEntry>) (x => x.FileName == spFile.FileName)) with
          {
            spectrumFile = new SpectrumFile()
          };
          spectrumFileEntry.spectrumFile.LoadFromFile(spectrumFileEntry.FileName, (string) null, 0);
        }
        else
          spectrumFileEntry = spFile;
        Color color = spectrumFileEntry.Color;
        foreach (SpectrumInFile spectrumInFile in spectrumFileEntry.spectrumFile)
        {
          if (spectrumFileEntry.spectrumFile.NumSpectra > 1)
            this.cmbSpectrumFiles.Items.Add((object) new ComboBoxItem(Path.GetFileName(spectrumFileEntry.FileName) + ":" + (num3 + 1).ToString(), (object) num2.ToString(), color));
          else
            this.cmbSpectrumFiles.Items.Add((object) new ComboBoxItem(Path.GetFileName(spectrumFileEntry.FileName), (object) num1.ToString(), color));
          ++num3;
        }
        ++num1;
        num2 = num1 + num3;
      }
      if (this.cmbSpectrumFiles.Items.Count <= selectedIndex)
        return;
      this.cmbSpectrumFiles.SelectedIndex = selectedIndex;
    }

    public void UpdateGraph()
    {
      this.m_YaxisHeight = Convert.ToInt32(Settings.Default.VerticalAxisHeight);
      this.m_fVisbleYSteps = Convert.ToSingle(Settings.Default.VerticalAxisTotalPoints);
      this.m_fVisbleYSteps = (double) this.m_fVisbleYSteps <= 0.0 ? 1f : this.m_fVisbleYSteps;
      this.m_fVisibleXWidth = Convert.ToSingle(Settings.Default.HorizontalAxisTotalPoints);
      this.m_fVisbleXSteps = Convert.ToSingle(Settings.Default.HorizontalAxisWidth);
      this.m_fVisbleXSteps = (double) this.m_fVisbleXSteps <= 0.0 ? 1f : this.m_fVisbleXSteps;
      this.m_CursorControl.BackColor = Settings.Default.CursorLineColor;
      this.RefreshGraph();
      this.ReloadFileListCombo();
    }

    private void RefreshGraph()
    {
      if (this.panelAxisX.InvokeRequired)
      {
        this.Invoke((Delegate) (() => this.RefreshGraph()));
      }
      else
      {
        this.m_bDoRefresh = true;
        this.panelAxisX.Refresh();
        this.panelAxisY.Refresh();
        this.panelGraph.Refresh();
      }
    }

    public void UpdateCursorInformation()
    {
      if (this.m_SpectrumFile == null || this.m_SpectrumFile.SpectrumFileInfo == null || ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() < 1)
        return;
      float channel = this.PanelPosToChannel(this.m_CursorControl.Left);
      int index = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      if (index < 0)
        index = 0;
      float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index].EVPerChannel;
      PdzCursorCustomObjectType customObjectType = new PdzCursorCustomObjectType();
      customObjectType.Channel = (int) channel;
      if (customObjectType.Channel > 2047)
        customObjectType.Channel = 2047;
      if (customObjectType.Channel < 0)
        customObjectType.Channel = 0;
      customObjectType.Count = this.m_SpectrumFile.SpectrumFileInfo[index].SpectrumData[customObjectType.Channel];
      customObjectType.EnergyIneV = (float) customObjectType.Channel * evPerChannel;
      List<CursorLineData> source1 = new List<CursorLineData>();
      foreach (AtomicElement atomicElement in PeriodicTableInfo.ElementsWithIntensity())
      {
        if (atomicElement != null)
        {
          foreach (LineIntensity lineIntensity in atomicElement.m_LineIntensity)
          {
            if ((double) lineIntensity.m_fIntensity > 0.0)
            {
              float num1 = lineIntensity.m_fLine * 1000f;
              float num2 = Math.Abs(num1 - customObjectType.EnergyIneV);
              if ((double) num2 <= 200.0)
                source1.Add(new CursorLineData()
                {
                  ElementDisplayName = atomicElement.Name + "-" + lineIntensity.m_LineName,
                  ElementLineName = lineIntensity.m_LineName.Substring(0, 1),
                  EnergyInKev = num1,
                  EnergyInKevDelta = num2
                });
            }
          }
        }
      }
      IOrderedQueryable<CursorLineData> source2 = source1.AsQueryable<CursorLineData>().OrderBy<CursorLineData, float>((Expression<Func<CursorLineData, float>>) (c => c.EnergyInKevDelta));
      Expression<Func<CursorLineData, string>> keySelector = (Expression<Func<CursorLineData, string>>) (n => n.ElementLineName);
      foreach (CursorLineData cursorLineData in (IEnumerable<CursorLineData>) source2.OrderBy<CursorLineData, string>(keySelector))
        customObjectType.Properties.Add(new PdzCursorCustomProperty()
        {
          Name = cursorLineData.ElementDisplayName,
          Type = typeof (int),
          Desc = cursorLineData.EnergyInKev.ToString(),
          DefaultValue = (object) (int) cursorLineData.EnergyInKev
        });
      foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
      {
        if (activeForm is SpectrumViewerCursorInfo)
        {
          ((SpectrumViewerCursorInfo) activeForm).CursorInformatoinGrid.SelectedObject = (object) customObjectType;
          break;
        }
      }
      this.RefreshResolutionDialog();
    }

    private void panelGraph_Click(object sender, EventArgs e)
    {
      this.m_CursorControl.Left = this.panelGraph.PointToClient(Cursor.Position).X;
      this.m_CursorControl.Height = this.panelGraph.Height + 4;
      this.UpdateCursorInformation();
      this.m_fPreviousCursorLeft = (float) this.m_CursorControl.Left;
    }

    private void SpectrumViewer_Resize(object sender, EventArgs e)
    {
      this.m_CursorControl.Height = this.panelGraph.Height + 4;
      this.m_AreaSelector.Height = this.panelGraph.Height + 4;
    }

    private void menuFileSelector_Click(object sender, EventArgs e)
    {
      if (this.m_bDataFromLiveSpectrum)
      {
        int num = (int) MessageBox.Show((IWin32Window) this, "Save the live data first.", "Save Live Data", MessageBoxButtons.OK, MessageBoxIcon.Hand);
      }
      else
        this.ShowForm((Form) new SpectrumViewerFileSelector(this));
    }

    private void menuAtomicTable_Click(object sender, EventArgs e) => this.ShowForm((Form) new SpectrumViewerPeriodicTable(this));

    private void menuCursorInfo_Click(object sender, EventArgs e) => this.ShowForm((Form) new SpectrumViewerCursorInfo(this));

    private void menuSpectrumInfo_Click(object sender, EventArgs e) => this.ShowForm((Form) new SpectrumViewerInformation(this));

    private void menuSettings_Click(object sender, EventArgs e)
    {
      Settings.Default.VerticalAxisHeight = (float) this.m_YaxisHeight;
      Settings.Default.VerticalAxisTotalPoints = this.m_fVisbleYSteps;
      Settings.Default.HorizontalAxisWidth = this.m_fVisbleXSteps;
      Settings.Default.HorizontalAxisTotalPoints = this.m_fVisibleXWidth;
      Settings.Default.CursorLineColor = this.m_CursorControl.BackColor;
      this.ShowForm((Form) this.m_PdzViewerOptions2);
    }

    private void menuNormalize_Click(object sender, EventArgs e)
    {
      this.m_SpectrumNormalizeFactor = new ArrayList(this.m_SpectrumCount);
      if (!(this.m_bNormalize = this.CalculateNormalizationRatio()))
        return;
      this.m_bDoRefresh = true;
      this.panelGraph.Refresh();
    }

    private bool IsCurveIncreasing(int[] spectraData, int iChannel)
    {
      bool flag = false;
      int num = spectraData[iChannel];
      for (int index = iChannel + 1; index < ((IEnumerable<int>) spectraData).Count<int>(); ++index)
      {
        if (num != spectraData[index])
        {
          flag = num < spectraData[index];
          break;
        }
      }
      return flag;
    }

    private bool CalculateNormalizationRatio()
    {
      if (this.m_MultiSpectrumDataList.Count == 0)
        return false;
      int channel = (int) this.PanelPosToChannel(this.m_CursorControl.Left);
      if (channel < 1)
      {
        int num = (int) MessageBox.Show("Place the cursor on a peak before normalizing.");
        return false;
      }
      this.m_LargeSpect = 0;
      int num1 = 0;
      int num2 = 0;
      foreach (MultiSpectrumData multiSpectrumData in this.m_MultiSpectrumDataList)
      {
        int[] spectrumData = (int[]) multiSpectrumData.SpectrumData;
        if (num1 < spectrumData[channel])
        {
          num1 = spectrumData[channel];
          this.m_LargeSpect = num2;
        }
        ++num2;
      }
      int num3 = 0;
      foreach (MultiSpectrumData multiSpectrumData in this.m_MultiSpectrumDataList)
      {
        if (num3++ == this.m_LargeSpect)
        {
          this.m_SpectrumNormalizeFactor.Add((object) 1f);
        }
        else
        {
          int[] spectrumData = (int[]) multiSpectrumData.SpectrumData;
          int index1;
          if (spectrumData[channel - 1] <= spectrumData[channel] && spectrumData[channel + 1] <= spectrumData[channel])
            index1 = channel;
          else if (this.IsCurveIncreasing(spectrumData, channel))
          {
            int num4 = 0;
            int num5 = spectrumData[channel];
            bool flag1 = false;
            int index2;
            for (index2 = channel + 1; index2 < ((IEnumerable<int>) spectrumData).Count<int>(); ++index2)
            {
              bool flag2;
              if (num5 > spectrumData[index2])
              {
                flag2 = true;
              }
              else
              {
                num5 = spectrumData[index2];
                flag1 = true;
                flag2 = false;
              }
              if (flag2 & flag1)
                break;
            }
            index1 = num4 = index2 - 1;
          }
          else
          {
            int num6 = spectrumData[channel];
            int num7 = 0;
            bool flag3 = false;
            int index3;
            for (index3 = channel - 1; index3 > 0; --index3)
            {
              bool flag4;
              if (num6 < spectrumData[index3])
              {
                num6 = spectrumData[index3];
                flag3 = true;
                flag4 = false;
              }
              else
                flag4 = true;
              if (flag3 & flag4)
                break;
            }
            index1 = num7 = index3 + 1;
          }
          float num8 = (float) ((int[]) this.m_MultiSpectrumDataList[this.m_LargeSpect].SpectrumData)[index1];
          float num9 = (float) spectrumData[index1];
          this.m_SpectrumNormalizeFactor.Add((object) (((double) num8 == 0.0 ? 1f : num8) / ((double) num9 == 0.0 ? 1f : num9)));
        }
      }
      return true;
    }

    private float[] ApplySlidingAverage(int[] spectraData)
    {
      float[] numArray = new float[((IEnumerable<int>) spectraData).Count<int>()];
      numArray[0] = (float) spectraData[0];
      numArray[1] = (float) spectraData[1];
      int num1 = ((IEnumerable<int>) spectraData).Count<int>();
      for (int index1 = 2; index1 < num1 - 2; ++index1)
      {
        int num2 = 0;
        for (int index2 = -2; index2 <= 2; ++index2)
          num2 += spectraData[index1 + index2];
        numArray[index1] = (float) (num2 / 5);
      }
      numArray[num1 - 2] = (float) spectraData[num1 - 2];
      numArray[num1 - 1] = (float) spectraData[num1 - 1];
      return numArray;
    }

    private int FindZeroStobeChannel(int[] spectraData)
    {
      int index1 = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index1 = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      int zeroStobeChannel = (int) this.m_SpectrumFile.SpectrumFileInfo[index1].EVPerChannel;
      int num = 0;
      for (int index2 = 15; index2 < 25; ++index2)
      {
        if (num < spectraData[index2])
        {
          num = spectraData[index2];
          zeroStobeChannel = index2;
        }
      }
      return zeroStobeChannel;
    }

    private float FindFWHM(int[] spectraData)
    {
      int index1 = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index1 = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      int zeroStobeChannel = this.FindZeroStobeChannel(spectraData);
      float num1 = (float) spectraData[zeroStobeChannel] / 2f;
      float num2 = 0.0f;
      float num3 = 0.0f;
      for (int index2 = zeroStobeChannel - 1; index2 > 0; --index2)
      {
        if ((double) num1 > (double) spectraData[index2])
        {
          num2 = (float) index2 + (num1 - (float) spectraData[index2]) / (float) (spectraData[index2 + 1] - spectraData[index2]);
          break;
        }
      }
      for (int index3 = zeroStobeChannel + 1; index3 < ((IEnumerable<int>) spectraData).Count<int>(); ++index3)
      {
        if ((double) num1 > (double) spectraData[index3])
        {
          num3 = (float) index3 + (num1 - (float) spectraData[index3 + 1]) / (float) (spectraData[index3] - spectraData[index3 + 1]);
          break;
        }
      }
      float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index1].EVPerChannel;
      return (num3 - num2) * evPerChannel;
    }

    private float FindResolution(int[] spectraData)
    {
      double fwhm = (double) this.FindFWHM(spectraData);
      float x = 119f;
      return (float) Math.Sqrt(Math.Pow(fwhm, 2.0) + Math.Pow((double) x, 2.0));
    }

    public void UpdateXraySettings()
    {
      XrayOpsEngine xrayOpsEngine = this.m_XrayOpsEngine;
    }

    private void menuXraySettings_Click(object sender, EventArgs e)
    {
      this.RefreshXrayOpsData();
      this.ShowForm((Form) new SpectrumViewerXraySettings(this));
    }

    public void RefreshXrayOpsData()
    {
      if (this.m_XrayOpsEngine == null)
        return;
      this.m_XrayOpsEngine.ReadEprom();
      Thread.Sleep(25);
      this.m_XrayOpsEngine.UpdateActuals(true);
      this.m_PdzViewerXraySettings.ActualHighVoltageInKV = this.m_XrayOpsEngine.ActualVoltage;
      this.m_PdzViewerXraySettings.AnodeCurrentInMilliAmp = this.m_XrayOpsEngine.ActualCurrent;
      this.m_PdzViewerXraySettings.Temperature = this.m_XrayOpsEngine.ActualTemp;
      this.m_PdzViewerXraySettings.Filter = (int) this.m_XrayOpsEngine.ActiveFlt;
      this.m_PdzViewerXraySettings.AnodeDiode = (float) this.m_XrayOpsEngine.Anode;
      this.m_PdzViewerXraySettings.CathodeDiode = (float) this.m_XrayOpsEngine.Cathode;
      this.m_PdzViewerXraySettings.InputVoltage = this.m_XrayOpsEngine.ActualINVolt;
      this.m_PdzViewerXraySettings.InputCurrent = (float) this.m_XrayOpsEngine.ActualInputCurrent;
      this.m_PdzViewerXraySettings.PulseLength = (float) this.m_XrayOpsEngine.ActPulseLength;
      this.m_PdzViewerXraySettings.FilterError = (float) this.m_XrayOpsEngine.FltError;
      this.m_PdzViewerXraySettings.Flux = (float) this.m_XrayOpsEngine.ActualFlux;
      this.m_PdzViewerXraySettings.IrLed = (float) this.m_XrayOpsEngine.IRLED;
      this.m_PdzViewerXraySettings.Vacuum = (float) this.m_XrayOpsEngine.ReadVacuum();
      this.m_PdzViewerXraySettings.ActualHvgDac = (float) this.m_XrayOpsEngine.ActualDACVolt;
      this.m_PdzViewerXraySettings.HvgCurrentInMilliAmp = (float) this.m_XrayOpsEngine.ActualINCur;
      this.m_PdzViewerXraySettings.ActualFgDac = (float) this.m_XrayOpsEngine.ActualDACCur;
      this.m_PdzViewerXraySettings.FgCurrentInMilliAmp = (float) this.m_XrayOpsEngine.FilamentCur;
    }

    private void SpectrumViewer_Shown(object sender, EventArgs e)
    {
      this.cmbSpectrumFiles.Focus();
      if (this.m_FileNameList.Count > 0)
      {
        this.LoadPdzFiles();
        this.m_SpectrumFile = new SpectrumFile();
        this.m_PreviousSpectrumFileName = this.m_CurrentSpectrumFileName;
        this.m_SpectrumFile.LoadFromFile(this.m_CurrentSpectrumFileName, (string) null, 0);
        SpectrumInfo spectrumInfo = new SpectrumInfo(this.m_SpectrumFile, this.m_iSpectraIndex);
        foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
        {
          if (activeForm is SpectrumViewerInformation)
          {
            ((SpectrumViewerInformation) activeForm).SpectrumInformation.SelectedObject = (object) spectrumInfo;
            break;
          }
        }
        this.RefreshGraph();
      }
      if (!Settings.Default.ShowSpectrumViewerHelp)
        return;
      SpectrumViewerHelp spectrumViewerHelp = new SpectrumViewerHelp();
      if (spectrumViewerHelp.ShowDialog() == DialogResult.OK)
      {
        Settings.Default.ShowSpectrumViewerHelp = !spectrumViewerHelp.chkDontShow.Checked;
        Settings.Default.Save();
      }
      spectrumViewerHelp.Dispose();
    }

    private void menuOptions_DropDownOpening(object sender, EventArgs e)
    {
      bool flag1 = Options.m_LoginType == LoginType.Production;
      bool flag2 = Options.m_LoginType != 0;
      bool flag3 = BrukerCommWrapper.CommManager.IsOpen();
      bool flag4 = true;
      if (this.m_IDF != null & flag3)
      {
        string safetyConfiguration = this.m_IDF.SafetyConfiguration;
        if (this.m_IDF.Safety != null)
        {
          int num = ((IEnumerable<CSafetyConfiguration>) this.m_IDF.Safety.SafetyConfigurations).Count<CSafetyConfiguration>();
          for (int index = 0; index < num; ++index)
          {
            if (this.m_IDF.Safety.SafetyConfigurations[index].ID.CompareTo(safetyConfiguration) == 0)
            {
              flag4 = this.m_IDF.Safety.SafetyConfigurations[index].AllowTimedAssay == "Yes";
              if (!flag4 && this.m_IDF.Safety.SafetyConfigurations[index].TimedAssayAllowedWithBTS.ToLower() == "yes" && this.m_RemID == 2)
                flag4 = true;
              this.MaxAssayTime = Convert.ToInt32(this.m_IDF.Safety.SafetyConfigurations[index].MaxAssayLength);
            }
          }
        }
      }
      else
        flag4 = false;
      if (!this.m_bDataFromLiveSpectrum)
        this.menuSaveAsPdz.Enabled = this.m_CurrentSpectrumFileName.Length > 0;
      this.menuResolutionFWHM.Visible = flag1;
      this.menuResolutionCursor.Visible = flag1;
      this.menuLiveSpectrum.Enabled = flag2 & flag3 & flag4;
      bool flag5;
      this.menuSetIllumination.Enabled = flag5 = flag2 & flag3 & flag4;
      this.lineLiveSpectrum.Enabled = flag1 & flag3;
    }

    private void menuSaveAsPdz_Click(object sender, EventArgs e)
    {
      if (this.m_bDataFromLiveSpectrum)
      {
        this.saveFileDialog.DefaultExt = "pdz";
        this.saveFileDialog.Filter = "PDZ Files (*.pdz)|*.pdz";
        if (this.saveFileDialog.ShowDialog() != DialogResult.OK)
          return;
        string fileName = this.saveFileDialog.FileName;
        this.m_bDataFromLiveSpectrum = false;
      }
      else
      {
        if (this.folderBrowserDialog.ShowDialog() != DialogResult.OK)
          return;
        bool flag1 = false;
        bool flag2 = false;
        foreach (SpectrumFileEntry fileName1 in this.m_FileNameList)
        {
          string fileName2 = Path.GetFileName(fileName1.FileName);
          string str = this.folderBrowserDialog.SelectedPath + "\\" + fileName2;
          if (File.Exists(str))
          {
            if (!flag1)
              flag2 = MessageBox.Show((IWin32Window) this, string.Format("File ({0}) already exists. Do you want to overwrite?", (object) fileName2), this.Text, MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.OK;
            if (flag2)
              File.Delete(str);
            else
              continue;
          }
          File.Copy(fileName1.FileName, str);
        }
      }
    }

    public void cmbSpectrumFiles_SelectedIndexChanged(object sender, EventArgs e)
    {
      if (this.m_bDataFromLiveSpectrum)
      {
        int num1 = (int) MessageBox.Show((IWin32Window) this, "Save the live data first.", "Save Live Data", MessageBoxButtons.OK, MessageBoxIcon.Hand);
      }
      else
      {
        if (this.m_FileNameList.Count == 0)
          return;
        this.m_bDataFromLiveSpectrum = false;
        this.m_CurrentSpectrumFileName = this.m_FileNameList[this.m_MultiSpectrumDataList[this.cmbSpectrumFiles.SelectedIndex].FileIndex].FileName;
        if (Settings.Default.ShowOneSpectrum)
          this.oneOnly = this.cmbSpectrumFiles.SelectedIndex;
        this.m_SpectrumFile = new SpectrumFile();
        this.m_PreviousSpectrumFileName = this.m_CurrentSpectrumFileName;
        this.m_SpectrumFile.LoadFromFile(this.m_CurrentSpectrumFileName, (string) null, 45);
        this.m_ResultsTable.Clear();
        this.m_ResultsTable = this.m_SpectrumFile.SpectrumResults;
        this.m_StdMultiplier = this.m_SpectrumFile.StdMultiplier;
        this.m_Images.Clear();
        this.m_Images = this.m_SpectrumFile.SpectrumImages;
        this.m_iSpectraIndex = 0;
        string str = this.cmbSpectrumFiles.SelectedItem.ToString();
        if (str.Contains(":"))
        {
          int num2 = str.LastIndexOf(':');
          this.m_iSpectraIndex = Convert.ToInt32(str.Substring(num2 + 1));
          --this.m_iSpectraIndex;
        }
        SpectrumInfo spectrumInfo = new SpectrumInfo(this.m_SpectrumFile, this.m_iSpectraIndex);
        foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
        {
          if (activeForm is SpectrumViewerInformation)
            ((SpectrumViewerInformation) activeForm).SpectrumInformation.SelectedObject = (object) spectrumInfo;
          if (activeForm is SpectrumViewerResults)
            ((SpectrumViewerResults) activeForm).LoadResultsTable();
          if (activeForm is SpectrumViewerFWHM)
            ((SpectrumViewerFWHM) activeForm).LoadData();
          if (activeForm is SpectrumViewerImageGallery)
          {
            ((SpectrumViewerImageGallery) activeForm).SpectrumViewerImageGallery_Load((object) null, (EventArgs) null);
            ((SpectrumViewerImageGallery) activeForm).ImageRefresh();
          }
        }
        this.RefreshGraph();
        this.UpdateCursorInformation();
      }
    }

    private void lblSpectrumList_Click(object sender, EventArgs e) => this.cmbSpectrumFiles.Focus();

    private void menuExit_Click(object sender, EventArgs e) => this.Close();

    private void menuResults_Click(object sender, EventArgs e) => this.ShowForm((Form) new SpectrumViewerResults(this));

    private bool ExportSpectrumToClipboard()
    {
      bool clipboard = false;
      try
      {
        int width = this.panelSpectrum.Size.Width;
        int height = this.panelSpectrum.Size.Height;
        Bitmap bitmap = new Bitmap(width, height);
        this.panelSpectrum.DrawToBitmap(bitmap, new Rectangle(0, 0, width, height));
        Clipboard.SetImage((Image) bitmap);
        clipboard = true;
      }
      catch (Exception ex)
      {
      }
      return clipboard;
    }

    private void menuCopy_Click(object sender, EventArgs e) => this.ExportSpectrumToClipboard();

    private void menuImages_Click(object sender, EventArgs e) => this.ShowForm((Form) new SpectrumViewerImageGallery(this));

    private void menuAddLabel_Click(object sender, EventArgs e)
    {
      this.panelGraph.Controls.Add((Control) new LabelControl((Control) this.panelGraph, this));
      this.panelGraph.Controls[this.panelGraph.Controls.Count - 1].BringToFront();
    }

    private void menuPrint_Click(object sender, EventArgs e)
    {
      this.printDialog.Document = this.printDocument;
      if (this.printDialog.ShowDialog() != DialogResult.OK)
        return;
      try
      {
        this.printDocument.PrinterSettings = this.printDialog.PrinterSettings;
        this.printDocument.DefaultPageSettings.Margins = new Margins(0, 0, 0, 0);
        this.printDocument.OriginAtMargins = false;
        this.printDocument.Print();
      }
      catch (Exception ex)
      {
        int num = (int) MessageBox.Show((IWin32Window) this, ex.Message.ToString(), "Print Error", MessageBoxButtons.OK, MessageBoxIcon.Hand);
      }
    }

    private void printDocument_PrintPage(object sender, PrintPageEventArgs e)
    {
      int width = this.panelSpectrum.Size.Width;
      int height = this.panelSpectrum.Size.Height;
      Bitmap bitmap = new Bitmap(width, height);
      this.panelSpectrum.DrawToBitmap(bitmap, new Rectangle(0, 0, width, height));
      double num = 5000.0 / (double) sbyte.MaxValue;
      if (this.printDocument.DefaultPageSettings.Landscape)
        e.Graphics.DrawImage((Image) bitmap, 0.0f, 0.0f, (float) (27.0 * num), (float) (18.0 * num));
      else
        e.Graphics.DrawImage((Image) bitmap, 0.0f, 0.0f, (float) (19.0 * num), (float) (10.0 * num));
    }

    private void SaveCursor()
    {
      this.m_bCursorNonZero = this.m_CursorControl.Left != 0;
      if (!this.m_bCursorNonZero)
        return;
      this.m_fCursorValue = (float) this.m_CursorControl.Left * this.m_fVisibleXWidth / (float) this.panelAxisX.Width + this.m_fVisbleXStartStep;
    }

    private void RestoreCursor()
    {
      if (this.m_bCursorNonZero)
        this.m_CursorControl.Left = (int) Math.Round(((double) this.m_fCursorValue - (double) this.m_fVisbleXStartStep) * ((double) this.panelAxisX.Width / (double) this.m_fVisibleXWidth));
      else
        this.m_CursorControl.Left = 0;
    }

    private void panelAxisX_MouseDown(object sender, MouseEventArgs e)
    {
      if (e.Button != MouseButtons.Left)
        return;
      this.m_iHorizontalPos = e.X;
      this.m_fHorizontalValue = (float) e.X * this.m_fVisibleXWidth / (float) this.panelAxisX.Width + this.m_fVisbleXStartStep;
      this.SaveCursor();
      this.m_bMoveGraphHorizontally = true;
    }

    private void panelAxisX_MouseMove(object sender, MouseEventArgs e)
    {
      if (!this.m_bMoveGraphHorizontally || e.Button != MouseButtons.Left || e.X == this.m_iHorizontalPos)
        return;
      this.m_iHorizontalPos = e.X;
      float num1 = this.m_fHorizontalValue - (float) e.X * this.m_fVisibleXWidth / (float) this.panelAxisX.Width;
      if ((double) num1 < 0.0)
        num1 = 0.0f;
      float num2 = 2048f - this.m_fVisibleXWidth;
      if ((double) num1 > (double) num2)
        num1 = num2;
      if ((double) num1 == (double) this.m_fVisbleXStartStep)
        return;
      this.m_fVisbleXStartStep = num1;
      this.RestoreCursor();
      this.panelAxisX.Refresh();
      this.panelGraph.Refresh();
    }

    private void panelAxisX_MouseUp(object sender, MouseEventArgs e)
    {
      if (e.Button != MouseButtons.Left)
        return;
      this.m_bMoveGraphHorizontally = false;
    }

    private void panelAxisY_MouseDown(object sender, MouseEventArgs e)
    {
      if (e.Button != MouseButtons.Left)
        return;
      this.m_iVerticalPos = e.Y;
      int num = this.panelAxisY.Bottom - this.panelAxisX.Height;
      this.m_fVerticalValue = (float) ((num - e.Y) * this.m_YaxisHeight) / ((float) (num - this.panelAxisY.Top) * this.m_fVerticalMutiplier);
      this.m_bScaleGraphVertically = true;
    }

    private void panelAxisY_MouseMove(object sender, MouseEventArgs e)
    {
      if (!this.m_bScaleGraphVertically || e.Button != MouseButtons.Left || e.Y == this.m_iVerticalPos)
        return;
      int num = this.panelAxisY.Bottom - this.panelAxisX.Height;
      if (e.Y >= num)
        return;
      this.m_iVerticalPos = e.Y;
      this.m_fVerticalMutiplier = (float) ((num - e.Y) * this.m_YaxisHeight) / ((float) (num - this.panelAxisY.Top) * this.m_fVerticalValue);
      this.panelAxisY.Refresh();
      this.panelGraph.Refresh();
    }

    private void panelAxisY_MouseUp(object sender, MouseEventArgs e)
    {
      if (e.Button != MouseButtons.Left)
        return;
      this.m_bScaleGraphVertically = false;
    }

    private void menuCloseAll_Click(object sender, EventArgs e)
    {
      for (int index = SpectrumViewer.m_ActiveForms.Count - 1; index >= 0; --index)
        SpectrumViewer.m_ActiveForms[index].Close();
    }

    private void menuCascade_Click(object sender, EventArgs e)
    {
      int x = this.Location.X;
      int y = this.Location.Y;
      foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
      {
        x += 50;
        y += 50;
        Point point = new Point(x, y);
        activeForm.Location = point;
      }
    }

    private void menuShowReportGenerator_Click(object sender, EventArgs e)
    {
      List<string> fileNames = new List<string>();
      foreach (SpectrumFileEntry fileName in this.m_FileNameList)
        fileNames.Add(fileName.FileName);
      string path1 = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "Bruker", "Bruker_Instrument_Tools");
      ReportBuilder.StateFileName = Path.Combine(path1, "state.xml");
      ReportBuilder.ShowReportingPreviewWindow(new ReportingContext((Image) Resources.CompanyLogo1, "en-US", Path.Combine(path1, "ReportGeneratorTemplates")), (IEnumerable<string>) fileNames);
    }

    private void menuResolutionFWHM_Click(object sender, EventArgs e)
    {
      this.m_bShowResolutionAtCursor = false;
      this.ShowForm((Form) new SpectrumViewerFWHM(this));
    }

    private float FindResolutionWithElement(int[] spectraData, ResolutionElements elementName)
    {
      float resolutionWithElement = 0.0f;
      int maxKalpha = this.GetMaxKalpha(elementName);
      int peakChannel = this.FindPeakChannel(spectraData, maxKalpha);
      if (peakChannel > 1 && peakChannel < ((IEnumerable<int>) spectraData).Count<int>() - 2)
      {
        Point[] source = new Point[5];
        int index1 = 0;
        for (int index2 = peakChannel - 2; index2 <= peakChannel + 2; ++index2)
        {
          source[index1].X = index2;
          source[index1++].Y = spectraData[index2];
        }
        double num1 = 0.0;
        double num2 = 0.0;
        double num3 = 0.0;
        double num4 = 0.0;
        double num5 = 0.0;
        double num6 = 0.0;
        double num7 = 0.0;
        foreach (Point point in source)
        {
          num1 += (double) point.Y * Math.Pow((double) point.X, 2.0);
          num2 += (double) (point.X * point.Y);
          num3 += (double) point.Y;
          num7 += Math.Pow((double) point.X, 4.0);
          num6 += Math.Pow((double) point.X, 3.0);
          num5 += Math.Pow((double) point.X, 2.0);
          num4 += (double) point.X;
        }
        double num8 = (double) ((IEnumerable<Point>) source).Count<Point>();
        double num9 = ((num3 * num7 - num1 * num5) * (num5 * num7 - num6 * num6) + (num1 * num6 - num2 * num7) * (num4 * num7 - num5 * num6)) / ((num5 * num6 - num4 * num7) * (num4 * num7 - num5 * num6) + (num8 * num7 - num5 * num5) * (num5 * num7 - num6 * num6));
        double num10 = (num2 * num7 - num1 * num6 - num9 * (num4 * num7 - num5 * num6)) / (num5 * num7 - num6 * num6);
        double num11 = (num1 - num10 * num6 - num9 * num5) / num7;
        float x = (float) (-1.0 * num10 / (2.0 * num11));
        float num12 = (float) (num11 * (double) x * (double) x + num10 * (double) x + num9);
        PointF halfMaxPoint = new PointF(x, num12 / 2f);
        Point[] nearPoints = this.GetNearPoints(spectraData, halfMaxPoint);
        float num13 = (float) nearPoints[0].X + (float) (nearPoints[1].Y - nearPoints[0].Y) / ((float) (nearPoints[1].X - nearPoints[0].X) * halfMaxPoint.Y);
        resolutionWithElement = Math.Abs((float) nearPoints[3].X - (float) (nearPoints[2].Y - nearPoints[3].Y) / ((float) (nearPoints[3].X - nearPoints[2].X) * halfMaxPoint.Y) - num13);
      }
      return resolutionWithElement;
    }

    private Point[] GetNearPoints(int[] spectraData, PointF halfMaxPoint)
    {
      Point[] nearPoints = new Point[4];
      int x = (int) halfMaxPoint.X;
      for (int index = x; index > 1 && x - index <= 100; --index)
      {
        if (index > 0 && index < 2047 && (double) halfMaxPoint.Y > (double) spectraData[index])
        {
          nearPoints[0].X = index;
          nearPoints[0].Y = spectraData[index];
          nearPoints[1].X = index + 1;
          nearPoints[1].Y = spectraData[index + 1];
          break;
        }
      }
      for (int index = x; index < ((IEnumerable<int>) spectraData).Count<int>() - 1 && index - x <= 100; ++index)
      {
        if (index > 0 && index < 2047 && (double) halfMaxPoint.Y > (double) spectraData[index])
        {
          nearPoints[2].X = index;
          nearPoints[2].Y = spectraData[index];
          nearPoints[3].X = index - 1;
          nearPoints[3].Y = spectraData[index - 1];
          break;
        }
      }
      return nearPoints;
    }

    private int GetMaxKalpha(ResolutionElements elementName)
    {
      int maxKalpha = 0;
      int num = 0;
      int index = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index].EVPerChannel;
      foreach (string str in Settings.Default.AtomicCsv)
      {
        if (num == elementName.ToInt())
        {
          char[] chArray = new char[3]{ '"', ',', '\n' };
          string[] strArray = str.Split(chArray);
          maxKalpha = (int) Math.Max(Convert.ToSingle(strArray[4]) * 1000f / evPerChannel, Convert.ToSingle(strArray[6]) * 1000f / evPerChannel);
          break;
        }
        ++num;
      }
      return maxKalpha;
    }

    private int FindPeakChannel(int[] spectraData, int iChannel)
    {
      iChannel = iChannel <= 0 ? 1 : iChannel;
      int peakChannel;
      if (spectraData[iChannel - 1] <= spectraData[iChannel] && spectraData[iChannel + 1] <= spectraData[iChannel])
        peakChannel = iChannel;
      else if (this.IsCurveIncreasing(spectraData, iChannel))
      {
        int num1 = 0;
        int num2 = spectraData[iChannel];
        bool flag1 = false;
        int index;
        for (index = iChannel + 1; index < ((IEnumerable<int>) spectraData).Count<int>(); ++index)
        {
          bool flag2;
          if (num2 > spectraData[index])
          {
            flag2 = true;
          }
          else
          {
            num2 = spectraData[index];
            flag1 = true;
            flag2 = false;
          }
          if (flag2 & flag1)
            break;
        }
        peakChannel = num1 = index - 1;
      }
      else
      {
        int num3 = spectraData[iChannel];
        int num4 = 0;
        bool flag3 = false;
        int index;
        for (index = iChannel - 1; index > 0; --index)
        {
          bool flag4;
          if (num3 < spectraData[index])
          {
            num3 = spectraData[index];
            flag3 = true;
            flag4 = false;
          }
          else
            flag4 = true;
          if (flag3 & flag4)
            break;
        }
        peakChannel = num4 = index + 1;
      }
      return peakChannel;
    }

    private int FindMnPeakChannel(int[] spectraData)
    {
      int mnPeakChannel = 2;
      int num1 = 0;
      int index1 = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index1 = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index1].EVPerChannel;
      int num2 = (int) (5000.0 / (double) evPerChannel);
      int num3 = (int) (7000.0 / (double) evPerChannel);
      for (int index2 = num2; index2 <= num3; ++index2)
      {
        if (spectraData[index2] > num1)
        {
          num1 = spectraData[index2];
          mnPeakChannel = index2;
        }
      }
      return mnPeakChannel;
    }

    public float FindResolutionWithElement(ResolutionElements resElement)
    {
      float resolutionWithElement = 0.0f;
      int index = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo[index] != null)
      {
        if (resElement == ResolutionElements.Mn)
        {
          resolutionWithElement = this.FindResolution(this.m_SpectrumFile.SpectrumFileInfo[index].SpectrumData);
        }
        else
        {
          float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index].EVPerChannel;
          resolutionWithElement = this.FindResolutionWithElement(this.m_SpectrumFile.SpectrumFileInfo[index].SpectrumData, resElement) * evPerChannel;
        }
      }
      return resolutionWithElement;
    }

    public float FindMnResolution(ResolutionMethod resMethod, bool bUseCursorPos)
    {
      float mnResolution = 0.0f;
      int index = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo[index] != null)
      {
        float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index].EVPerChannel;
        mnResolution = resMethod != ResolutionMethod.Parabola ? this.FindMnResolutionUsingGaussian(bUseCursorPos) * evPerChannel : this.FindMnResolutionUsingParabola(bUseCursorPos) * evPerChannel;
      }
      return mnResolution;
    }

    private float FindBackgroundCorrection()
    {
      float num1 = 0.0f;
      int index1 = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index1 = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      float evPerChannel = (float) this.m_SpectrumFile.SpectrumFileInfo[index1].EVPerChannel;
      int num2 = (int) (4500.0 / (double) evPerChannel);
      int num3 = (int) (5500.0 / (double) evPerChannel);
      for (int index2 = num2; index2 <= num3; ++index2)
        num1 += (float) this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData[index2];
      int num4 = (int) (8000.0 / (double) evPerChannel);
      int num5 = (int) (9000.0 / (double) evPerChannel);
      for (int index3 = num4; index3 <= num5; ++index3)
        num1 += (float) this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData[index3];
      return num1 / 102f;
    }

    private int FindPeakNearCursor()
    {
      int index = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      int channel = (int) this.PanelPosToChannel(this.m_CursorControl.Left);
      return this.FindPeakChannel(this.m_SpectrumFile.SpectrumFileInfo[index].SpectrumData, channel);
    }

    private float FindMnResolutionUsingGaussian(bool bUseCursorPos)
    {
      float resolutionUsingGaussian = 0.0f;
      int index1 = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index1 = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      int num1 = !bUseCursorPos ? this.FindMnPeakChannel(this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData) : this.FindPeakNearCursor();
      if (num1 > 1 && num1 < ((IEnumerable<int>) this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData).Count<int>() - 2)
      {
        Point[] pointArray = new Point[3];
        int index2 = 0;
        for (int index3 = num1 - 2; index3 <= num1 + 2; index3 += 2)
        {
          pointArray[index2].X = index3;
          pointArray[index2++].Y = this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData[index3];
        }
        float num2 = 0.0f;
        if (!bUseCursorPos)
          num2 = this.FindBackgroundCorrection();
        float num3 = (float) Math.Log((double) pointArray[0].Y - (double) num2);
        float num4 = (float) Math.Log((double) pointArray[1].Y - (double) num2);
        float num5 = (float) Math.Log((double) pointArray[2].Y - (double) num2);
        resolutionUsingGaussian = (float) (2.0 / Math.Sqrt(2.0 * (double) num4 - ((double) num3 + (double) num5)) * 2.0) * (float) Math.Sqrt(2.0 * Math.Log(2.0));
      }
      return resolutionUsingGaussian;
    }

    private float FindMnResolutionUsingParabola(bool bUseCursorPos)
    {
      float resolutionUsingParabola = 0.0f;
      int index1 = this.m_iSpectraIndex;
      if (this.m_SpectrumFile != null && this.m_SpectrumFile.SpectrumFileInfo != null && ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() <= this.m_iSpectraIndex)
        index1 = ((IEnumerable<SpectrumInFile>) this.m_SpectrumFile.SpectrumFileInfo).Count<SpectrumInFile>() - 1;
      int num1 = !bUseCursorPos ? this.FindMnPeakChannel(this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData) : this.FindPeakNearCursor();
      if (num1 > 1 && num1 < ((IEnumerable<int>) this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData).Count<int>() - 2)
      {
        Point[] source = new Point[5];
        int index2 = 0;
        for (int index3 = num1 - 2; index3 <= num1 + 2; ++index3)
        {
          source[index2].X = index3;
          source[index2++].Y = this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData[index3];
        }
        double num2 = 0.0;
        double num3 = 0.0;
        double num4 = 0.0;
        double num5 = 0.0;
        double num6 = 0.0;
        double num7 = 0.0;
        double num8 = 0.0;
        foreach (Point point in source)
        {
          num2 += (double) point.Y * Math.Pow((double) point.X, 2.0);
          num3 += (double) (point.X * point.Y);
          num4 += (double) point.Y;
          num8 += Math.Pow((double) point.X, 4.0);
          num7 += Math.Pow((double) point.X, 3.0);
          num6 += Math.Pow((double) point.X, 2.0);
          num5 += (double) point.X;
        }
        double num9 = (double) ((IEnumerable<Point>) source).Count<Point>();
        double num10 = ((num4 * num8 - num2 * num6) * (num6 * num8 - num7 * num7) + (num2 * num7 - num3 * num8) * (num5 * num8 - num6 * num7)) / ((num6 * num7 - num5 * num8) * (num5 * num8 - num6 * num7) + (num9 * num8 - num6 * num6) * (num6 * num8 - num7 * num7));
        double num11 = (num3 * num8 - num2 * num7 - num10 * (num5 * num8 - num6 * num7)) / (num6 * num8 - num7 * num7);
        double num12 = (num2 - num11 * num7 - num10 * num6) / num8;
        float x = (float) (-1.0 * num11 / (2.0 * num12));
        float num13 = (float) (num12 * (double) x * (double) x + num11 * (double) x + num10);
        if (!bUseCursorPos)
          num13 -= this.FindBackgroundCorrection();
        PointF halfMaxPoint = new PointF(x, num13 / 2f);
        Point[] nearPoints = this.GetNearPoints(this.m_SpectrumFile.SpectrumFileInfo[index1].SpectrumData, halfMaxPoint);
        float num14 = 0.0f;
        float num15 = 0.0f;
        if (nearPoints.Length >= 4)
        {
          num14 = (float) nearPoints[2].X + (halfMaxPoint.Y - (float) nearPoints[2].Y) / (float) (nearPoints[2].Y - nearPoints[3].Y) * (float) (nearPoints[2].X - nearPoints[3].X);
          num15 = (float) nearPoints[0].X + (halfMaxPoint.Y - (float) nearPoints[0].Y) / (float) (nearPoints[1].Y - nearPoints[0].Y) * (float) (nearPoints[1].X - nearPoints[0].X);
        }
        resolutionUsingParabola = Math.Abs(num15 - num14);
      }
      return resolutionUsingParabola;
    }

    public void RefreshResolutionDialog()
    {
      foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
      {
        if (activeForm is SpectrumViewerFWHM)
        {
          ((SpectrumViewerFWHM) activeForm).LoadData();
          break;
        }
      }
    }

    private void ConnectLiveCommManager()
    {
      this.DisConnectLiveManager();
      if (!BrukerCommWrapper.CommManager.IsOpen())
        return;
      this.m_LiveCommManager = (CommunicationManager) new TcpCommManager(((TcpCommManager) BrukerCommWrapper.CommManager).RemoteIpAddress, this.m_LiveDataPortNo);
      this.m_LiveCommManager.OpenPort();
    }

    private void DisConnectLiveManager()
    {
      if (this.m_LiveCommManager != null && this.m_LiveCommManager.IsOpen())
        this.m_LiveCommManager.ClosePort();
      this.m_LiveCommManager = (CommunicationManager) null;
    }

    private void EnableControls(bool bEnable)
    {
      if (this.panelSpectrum.InvokeRequired)
      {
        this.Invoke((Delegate) (() =>
        {
          if (!bEnable)
          {
            this.menuSaveAsPdz.Enabled = true;
            this.menuLiveSpectrum.Text = "Stop Live Spectrum";
          }
          else
            this.menuLiveSpectrum.Text = "Start Live Spectrum";
          this.cmbSpectrumFiles.Enabled = bEnable;
          this.menuFileSelector.Enabled = bEnable;
          this.menuResults.Enabled = bEnable;
          this.menuImages.Enabled = bEnable;
          this.menuShowReportGenerator.Enabled = bEnable;
          this.menuSettings.Enabled = bEnable;
          this.menuXraySettings.Enabled = bEnable;
          this.menuPrint.Enabled = bEnable;
        }));
      }
      else
      {
        if (!bEnable)
        {
          this.menuSaveAsPdz.Enabled = true;
          this.menuLiveSpectrum.Text = "Stop Live Spectrum";
        }
        else
          this.menuLiveSpectrum.Text = "Start Live Spectrum";
        this.cmbSpectrumFiles.Enabled = bEnable;
        this.menuFileSelector.Enabled = bEnable;
        this.menuResults.Enabled = bEnable;
        this.menuImages.Enabled = bEnable;
        this.menuShowReportGenerator.Enabled = bEnable;
        this.menuSettings.Enabled = bEnable;
        this.menuXraySettings.Enabled = bEnable;
        this.menuPrint.Enabled = bEnable;
      }
    }

    private void menuLiveSpectrum_Click(object sender, EventArgs e) => this.LiveSpectrum();

    private void LiveSpectrum()
    {
      this.m_bLiveSpectrumMode = !this.m_bLiveSpectrumMode;
      this.EnableControls(!this.m_bLiveSpectrumMode);
      if (this.m_bLiveSpectrumMode)
      {
        this.m_iSpectraIndex = 0;
        bool flag;
        if (this.IllumSelect != null)
        {
          this.BtoBCounter = this.IllumSelect.BackToBackCount;
          this.BtoBPause = this.IllumSelect.PauseBetween;
          this.cmdline = this.IllumSelect.cmdLine;
          flag = BrukerCommWrapper.StartTrigger(this.cmdline);
        }
        else
          flag = BrukerCommWrapper.StartTrigger("");
        if (!flag)
        {
          this.menuLiveSpectrum.Text = "Start Live Spectrum";
          this.m_bLiveSpectrumMode = false;
        }
        else
        {
          Thread.Sleep(1);
          if (this.backgroundWorker.IsBusy)
            return;
          this.backgroundWorker.RunWorkerAsync();
        }
      }
      else
      {
        BrukerCommWrapper.StopTrigger();
        this.BtoBCounter = 0;
      }
    }

    private void ProcessSpectrumData()
    {
      bool flag = true;
      while (flag && !this.backgroundWorker.CancellationPending)
      {
        if (this.m_LiveCommManager != null && this.m_LiveCommManager.IsOpen())
        {
          BrukerCommWrapper.DataSyncEvent.Reset();
          while (this.BufReadStage < 5 & flag)
          {
            this.m_LiveCommManager._writeMutex.WaitOne();
            switch (this.BufReadStage)
            {
              case 0:
                if (this.m_LiveCommManager.BufferAvailableSize > 3)
                {
                  if (Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == (byte) 3 && Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == (byte) 2 && Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == (byte) 0 && Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == (byte) 0)
                  {
                    ++this.BufReadStage;
                    break;
                  }
                  continue;
                }
                flag = false;
                break;
              case 1:
                if (this.m_LiveCommManager.BufferAvailableSize > 1)
                {
                  this.liveCommand = (SpectrumLiveData) ((uint) Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) + ((uint) Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) << 8));
                  ++this.BufReadStage;
                  break;
                }
                flag = false;
                break;
              case 2:
                if (this.m_LiveCommManager.BufferAvailableSize > 3)
                {
                  this.dataSize = (int) Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) + ((int) Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) << 8) + ((int) Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) << 16) + ((int) Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) << 24);
                  ++this.BufReadStage;
                  break;
                }
                flag = false;
                break;
              case 3:
                if (this.m_LiveCommManager.BufferAvailableSize >= this.dataSize)
                {
                  this.dataArray = new byte[this.dataSize];
                  for (int index = 0; index < this.dataSize; ++index)
                    this.dataArray[index] = Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue());
                  ++this.BufReadStage;
                  break;
                }
                flag = false;
                break;
              case 4:
                if (this.m_LiveCommManager.BufferAvailableSize > 3)
                {
                  if (Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == (byte) 6 && Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == (byte) 42 && Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == byte.MaxValue && Convert.ToByte(this.m_LiveCommManager._bufferQueue.Dequeue()) == byte.MaxValue)
                  {
                    ++this.BufReadStage;
                    break;
                  }
                  continue;
                }
                flag = false;
                break;
              default:
                this.BufReadStage = 0;
                break;
            }
            this.m_LiveCommManager._writeMutex.ReleaseMutex();
          }
          if (flag)
          {
            this.BufReadStage = 0;
            switch (this.liveCommand)
            {
              case SpectrumLiveData.COOKED_PLUS_DATA:
                if (!this.m_bLiveSpectrumMode)
                {
                  this.m_bLiveSpectrumMode = true;
                  this.m_bInstrumentInitiatedAssay = true;
                  this.EnableControls(false);
                }
                ++this.m_iPacketCount;
                S1CookedDataWithHeader cookedData = new S1CookedDataWithHeader();
                this.FillCookedData(ref cookedData, this.dataArray);
                this.ProcessAndUpdateSpectrum(cookedData);
                continue;
              case SpectrumLiveData.ASSAY_DONE:
                if (this.UpdateResultWithFileName(Encoding.Default.GetString(this.dataArray).Replace("\0", "")))
                  --this.BtoBCounter;
                this.m_iPacketCount = -1;
                this.m_bInstrumentInitiatedAssay = false;
                this.RefreshGraph();
                foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
                {
                  if (activeForm is SpectrumViewerFileSelector)
                    ((SpectrumViewerFileSelector) activeForm).RefreshFileList();
                }
                if (this.BtoBCounter > 0)
                {
                  if (this.BtoBPause)
                  {
                    int num1 = (int) MessageBox.Show("Pausing between assays.\nClick OK to start the next assay.");
                  }
                  else
                    Thread.Sleep(5000);
                  this.m_LiveCommManager._bufferQueue.Clear();
                  int num2 = 0;
                  while (!BrukerCommWrapper.StartTrigger(this.cmdline, num2 >= 4) && num2 < 5)
                  {
                    ++num2;
                    Thread.Sleep(500);
                    this.m_LiveCommManager._bufferQueue.Clear();
                    Thread.Sleep(500);
                    this.m_LiveCommManager._bufferQueue.Clear();
                  }
                  if (num2 >= 5)
                  {
                    int num3 = (int) MessageBox.Show("Can't start the next assay.\nBack-to-Back processing terminated.");
                    this.BtoBCounter = 0;
                    this.m_bLiveSpectrumMode = false;
                    this.EnableControls(true);
                    this.RefreshGraph();
                    if (this.backgroundWorker.IsBusy)
                    {
                      this.m_LiveCommManager._bufferQueue.Clear();
                      flag = false;
                      continue;
                    }
                    continue;
                  }
                  continue;
                }
                this.m_bLiveSpectrumMode = false;
                this.EnableControls(true);
                this.RefreshGraph();
                if (this.backgroundWorker.IsBusy)
                {
                  this.m_LiveCommManager._bufferQueue.Clear();
                  flag = false;
                  continue;
                }
                continue;
              default:
                continue;
            }
          }
          else
            break;
        }
      }
      BrukerCommWrapper.DataSyncEvent.Set();
    }

    public string AskSaveFile()
    {
      if (this.InvokeRequired)
        return (string) this.Invoke((Delegate) (() => this.AskSaveFile()));
      SaveFileDialog saveFileDialog = new SaveFileDialog();
      saveFileDialog.Filter = "All Files (*.*)|*.*";
      saveFileDialog.RestoreDirectory = true;
      return saveFileDialog.ShowDialog() != DialogResult.OK ? (string) null : saveFileDialog.FileName;
    }

    private bool UpdateResultWithFileName(string remoteFileNameWithPath)
    {
      this.m_bDataFromLiveSpectrum = false;
      string str1 = this.m_PdzViewerOptions2.LiveSpectrumDataFolder + "\\" + Path.GetFileName(remoteFileNameWithPath);
      string str2 = Path.GetFileName(remoteFileNameWithPath);
      string path = this.m_PdzViewerOptions2.LiveSpectrumDataFolder;
      string str3 = string.Format(string.Format("{0}\n", (object) DateTime.Now));
      if (this.IllumSelect != null && !this.IllumSelect.UseDefaultDirectory)
      {
        path = this.IllumSelect.Directory;
        if (!this.IllumSelect.IndexNumberCheck)
          str2 = str2.Remove(0, 5);
        if (!this.IllumSelect.ApplicationNameCheck)
        {
          int startIndex = str2.IndexOf('-');
          int num = str2.IndexOf('.');
          str2 = str2.Remove(startIndex, num - startIndex);
        }
        if (!this.IllumSelect.ApplicationNameCheck || !this.IllumSelect.IndexNumberCheck)
        {
          int startIndex = str2.IndexOf('-');
          if (startIndex != -1)
            str2 = str2.Remove(startIndex, 1);
        }
        if (this.IllumSelect.UserFileName != null && this.IllumSelect.UserFileName != "")
          str2 = this.IllumSelect.ApplicationNameCheck || this.IllumSelect.IndexNumberCheck ? this.IllumSelect.UserFileName + "-" + str2 : this.IllumSelect.UserFileName + str2;
        if (str2 == ".pdz")
          str2 = str3 + str2;
        str1 = path + "\\" + str2;
      }
      if (!str1.ToLower().EndsWith(".pdz"))
        str1 += ".pdz";
      if (!Directory.Exists(path))
        Directory.CreateDirectory(path);
      bool flag1 = false;
      while (File.Exists(str1) && !flag1)
      {
        if (MessageBox.Show(str1 + " exists, overwrite?", "Overwrite?", MessageBoxButtons.YesNo) == DialogResult.No)
        {
          str1 = this.AskSaveFile();
          while (str1 == null)
            str1 = this.AskSaveFile();
          if (!str1.ToLower().EndsWith(".pdz"))
            str1 += ".pdz";
        }
        else
          flag1 = true;
      }
      this.m_PdzViewerOptions2.LiveSpectrumDataFolder = path;
      bool flag2 = false;
      int num1 = 0;
      SpectrumFile spectrumFile = (SpectrumFile) null;
      while (!flag2 && num1 < 5)
      {
        for (int index = 0; !BrukerCommWrapper.DownloadFileFromTitan(remoteFileNameWithPath, str1) && index < 5; ++index)
          Thread.Sleep(100);
        try
        {
          spectrumFile = new SpectrumFile();
          if (spectrumFile.LoadFromFile(str1, (string) null, 0))
            break;
          ++num1;
        }
        catch (Exception ex)
        {
          ++num1;
        }
      }
      if (num1 >= 5)
        return false;
      this.m_FileNameList.Add(new SpectrumFileEntry()
      {
        FileName = str1,
        ShowSpectra = true,
        Color = this.getNextColor(),
        spectrumFile = spectrumFile
      });
      if (this.panelSpectrum.InvokeRequired)
        this.Invoke((Delegate) (() => this.LoadPdzFiles()));
      else
        this.LoadPdzFiles();
      return true;
    }

    private void FillCookedData(ref S1CookedDataWithHeader cookedData, byte[] byteCookedData)
    {
      using (Stream input = (Stream) new MemoryStream(byteCookedData))
      {
        using (BinaryReader binaryReader = new BinaryReader(input))
        {
          cookedData.eVPerChannel = binaryReader.ReadSingle();
          cookedData.sch.FPGA_Ver = binaryReader.ReadByte();
          cookedData.sch.FPGA_SubVer = binaryReader.ReadByte();
          cookedData.sch.iPacket_Len = binaryReader.ReadUInt16();
          cookedData.sch.iTDur = binaryReader.ReadUInt32();
          cookedData.sch.iRaw_Cnts = binaryReader.ReadUInt32();
          cookedData.sch.iValid_Cnts = binaryReader.ReadUInt32();
          cookedData.sch.iValid_CntsRng = binaryReader.ReadUInt32();
          cookedData.sch.iADur = binaryReader.ReadUInt32();
          cookedData.sch.iADead = binaryReader.ReadUInt32();
          cookedData.sch.iAReset = binaryReader.ReadUInt32();
          cookedData.sch.iALive = binaryReader.ReadUInt32();
          cookedData.sch.iService = binaryReader.ReadUInt32();
          cookedData.sch.iReset_Cnt = binaryReader.ReadUInt16();
          cookedData.sch.iPacket_Cnt = binaryReader.ReadUInt16();
          cookedData.sch.Unused = binaryReader.ReadBytes(20);
          cookedData.sch.fXRay_ActualHV = binaryReader.ReadSingle();
          cookedData.sch.fXRay_ActualAC = binaryReader.ReadSingle();
          cookedData.sch.bValidActuals = binaryReader.ReadByte();
          cookedData.sch.XRay_ActualHVDAC = binaryReader.ReadByte();
          cookedData.sch.XRay_ActualACDAC = binaryReader.ReadByte();
          cookedData.sch.Unused2 = binaryReader.ReadByte();
          cookedData.sch.Xilinx_Vars = binaryReader.ReadBytes(46);
          cookedData.sch.Det_Temp = binaryReader.ReadInt16();
          cookedData.sch.Amb_Temp = binaryReader.ReadUInt16();
          cookedData.sch.MCU_Ver = binaryReader.ReadByte();
          cookedData.sch.MCU_SubVer = binaryReader.ReadByte();
          cookedData.sch.iRaw_Cnts_Acc = binaryReader.ReadUInt32();
          cookedData.sch.iValid_Cnts_Acc = binaryReader.ReadUInt32();
          cookedData.sch.iValid_CntsRng_Acc = binaryReader.ReadUInt32();
          cookedData.sch.iReset_Cnt_Acc = binaryReader.ReadUInt32();
          cookedData.sch.fTDur = binaryReader.ReadSingle();
          cookedData.sch.fADur = binaryReader.ReadSingle();
          cookedData.sch.fADead = binaryReader.ReadSingle();
          cookedData.sch.fAReset = binaryReader.ReadSingle();
          cookedData.sch.fALive = binaryReader.ReadSingle();
          cookedData.sch.lVacuum_Acc = binaryReader.ReadUInt32();
          cookedData.sch.lPacket_Cnt = binaryReader.ReadUInt32();
          cookedData.sch.xTubeFilter.bFilterNum = binaryReader.ReadInt32();
          cookedData.sch.xTubeFilter.flLayer = new FILTERLAYER[3];
          for (int index = 0; index < 3; ++index)
          {
            cookedData.sch.xTubeFilter.flLayer[index].bElement = binaryReader.ReadInt16();
            cookedData.sch.xTubeFilter.flLayer[index].sThickness = binaryReader.ReadInt16();
          }
          cookedData.sch.XRay.sngHVADC = binaryReader.ReadSingle();
          cookedData.sch.XRay.sngCurADC = binaryReader.ReadSingle();
          cookedData.sch.XRay.bytVolt = binaryReader.ReadByte();
          cookedData.sch.XRay.bytCurrent = binaryReader.ReadByte();
          cookedData.sch.XRay.bytToggle = binaryReader.ReadByte();
          cookedData.sch.XRay.bytPulseLength = binaryReader.ReadByte();
          cookedData.sch.XRay.bytPulsePeriod = binaryReader.ReadByte();
          cookedData.sch.XRay.bytFilter = binaryReader.ReadByte();
          cookedData.sch.XRay.bytExtActual = binaryReader.ReadByte();
          cookedData.sch.XRay.bytTimes2 = binaryReader.ReadByte();
          cookedData.data = new uint[2048];
          for (int index = 0; index < 2048; ++index)
            cookedData.data[index] = binaryReader.ReadUInt32();
        }
      }
    }

    private void backgroundWorker_DoWork(object sender, DoWorkEventArgs e)
    {
      while (true)
      {
        this.ProcessSpectrumData();
        if (!this.backgroundWorker.CancellationPending)
          Thread.Sleep(1);
        else
          break;
      }
    }

    private void menuResolutionCursor_Click(object sender, EventArgs e)
    {
      this.m_bShowResolutionAtCursor = true;
      this.ShowForm((Form) new SpectrumViewerFWHM(this));
    }

    private void DetermineSpectraPeak(SpectrumInFile spectrum)
    {
      int num1 = 0;
      bool flag = false;
      foreach (int num2 in spectrum.SpectrumData)
      {
        if (this.m_YaxisHeight < num2)
        {
          flag = true;
          this.m_YaxisHeight = num2;
          this.m_ptPeakPoint.X = (float) num1 * 1f;
          this.m_ptPeakPoint.Y = (float) num2 * 1f;
        }
        ++num1;
      }
      if (!flag)
        return;
      this.m_YaxisHeight = (int) ((double) this.m_YaxisHeight * 1.1);
      if (this.m_YaxisHeight <= 1200)
        return;
      this.m_YaxisHeight = (this.m_YaxisHeight / 100 + 1) * 100;
    }

    private void ProcessAndUpdateSpectrum(S1CookedDataWithHeader rawCookedData)
    {
      this.m_bDataFromLiveSpectrum = true;
      if (this.m_bNoDataToDrawError)
      {
        this.LiveSpectraMutex.WaitOne(1);
        this.LiveSpectrum();
        int num = (int) MessageBox.Show("The instrument is not transmitting spectral data.");
        Thread.Sleep(5000);
        this.LiveSpectraMutex.ReleaseMutex();
      }
      this.m_bNoDataToDrawError = false;
      this.m_SpectrumFile = new SpectrumFile();
      this.m_SpectrumFile.LoadFromLiveData(rawCookedData);
      int realStart = this.spectrumStartBin(this.m_SpectrumFile.SerialString);
      this.m_SpectrumCount = 1;
      this.m_MultiSpectrumDataList.Clear();
      using (IEnumerator<SpectrumInFile> enumerator = this.m_SpectrumFile.GetEnumerator())
      {
        if (enumerator.MoveNext())
        {
          SpectrumInFile current = enumerator.Current;
          this.m_MultiSpectrumDataList.Add(new MultiSpectrumData()
          {
            SpectrumData = (object) current.SpectrumData,
            BackgroundData = (object) this.computeBackground(current.SpectrumData, realStart)
          });
          this.m_YaxisHeight = 0;
          this.DetermineSpectraPeak(current);
        }
      }
      this.RefreshOverlaySpectra(false);
      this.RefreshGraph();
    }

    private void setIlluminationToolStripMenuItem1_Click(object sender, EventArgs e)
    {
      if (this.IllumSelect == null)
      {
        this.IllumSelect = new IlluminationSelector(this.m_IDF, this);
        this.ShowForm((Form) this.IllumSelect);
      }
      else
        this.IllumSelect.Show();
    }

    private void cmbSpectrumFiles_MouseMove(object sender, MouseEventArgs e)
    {
      if ((e.Button & MouseButtons.Left) != MouseButtons.Left || !(this.dragBoxFromMouseDown != Rectangle.Empty) || this.dragBoxFromMouseDown.Contains(e.X, e.Y))
        return;
      this.OpenSpectrumReview();
    }

    private void OpenSpectrumReview()
    {
      this.cmbSpectrumFiles.Enabled = false;
      SpectrumReview formToShow = new SpectrumReview(this);
      formToShow.Show();
      formToShow.SetDesktopLocation(this.panelGraph_DragX, this.panelGraph_DragY);
      this.ShowForm((Form) formToShow);
    }

    private void cmbSpectrumFiles_MouseDown(object sender, MouseEventArgs e)
    {
      Size dragSize = SystemInformation.DragSize;
      this.dragBoxFromMouseDown = new Rectangle(new Point(e.X - dragSize.Width / 2, e.Y - dragSize.Height / 2), dragSize);
    }

    private void cmbSpectrumFiles_MouseUp(object sender, MouseEventArgs e) => this.dragBoxFromMouseDown = Rectangle.Empty;

    private void panelGraph_DragOver(object sender, DragEventArgs e)
    {
      this.panelGraph_DragX = e.X;
      this.panelGraph_DragY = e.Y;
      if (!e.Data.GetDataPresent(DataFormats.FileDrop))
        return;
      e.Effect = DragDropEffects.Copy;
    }

    public float GetDetectorTemp()
    {
      float detectorTemp = 0.0f;
      if (this.m_SpectrumFile != null)
        detectorTemp = this.m_SpectrumFile.SpectrumFileInfo[0].DetectorTempInC;
      return detectorTemp;
    }

    public float GetAmbientTemp()
    {
      float ambientTemp = 0.0f;
      if (this.m_SpectrumFile != null)
        ambientTemp = this.m_SpectrumFile.SpectrumFileInfo[0].AmbientTempInF;
      return ambientTemp;
    }

    private void SpectrumReviewMenuItem_Click(object sender, EventArgs e) => this.OpenSpectrumReview();

    private void OverlaySpectraDialog()
    {
      bool overlaySpectraEnable = Settings.Default.OverlaySpectraEnable;
      string overlaySpectraFile = Settings.Default.OverlaySpectraFile;
      int overlaySpectraPhase = (int) Settings.Default.OverlaySpectraPhase;
      this.m_bNewOverlayFile = false;
      this.m_bNewOverlayPhase = false;
      SpectrumViewerOverlaySpectra viewerOverlaySpectra = new SpectrumViewerOverlaySpectra();
      int num = (int) viewerOverlaySpectra.ShowDialog();
      if (viewerOverlaySpectra.DialogResult == DialogResult.OK)
      {
        if (overlaySpectraFile != Settings.Default.OverlaySpectraFile)
        {
          this.m_bNewOverlayFile = true;
          this.m_bNewOverlayPhase = true;
        }
        if (overlaySpectraPhase != (int) Settings.Default.OverlaySpectraPhase)
          this.m_bNewOverlayPhase = true;
        this.RefreshOverlaySpectra(overlaySpectraEnable);
      }
      this.enableOverlayToolStripMenuItem.Checked = Settings.Default.OverlaySpectraEnable;
    }

    private bool CheckOverlayFile()
    {
      bool flag = true;
      if (!File.Exists(Settings.Default.OverlaySpectraFile))
      {
        int num = (int) MessageBox.Show("Can't find the file overlay file " + Settings.Default.OverlaySpectraFile + ".");
        flag = false;
      }
      return flag;
    }

    private void RefreshOverlaySpectra(bool bOverLaySpectraWasEnabled)
    {
      bool flag = false;
      if (bOverLaySpectraWasEnabled && !Settings.Default.OverlaySpectraEnable || this.m_bNewOverlayFile && this.m_SFOverlaySpectrumFile != null)
      {
        if (this.m_MultiSpectrumDataList.Count > 0)
          this.m_MultiSpectrumDataList.RemoveAt(this.m_MultiSpectrumDataList.Count - 1);
        flag = true;
      }
      try
      {
        if (Settings.Default.OverlaySpectraEnable)
        {
          if (!bOverLaySpectraWasEnabled)
            flag = true;
          if (this.m_bNewOverlayFile)
          {
            if (!this.CheckOverlayFile())
              throw new FileNotFoundException();
            this.m_SFOverlaySpectrumFile = new SpectrumFile();
            this.m_SFOverlaySpectrumFile.LoadFromFile(Settings.Default.OverlaySpectraFile, (string) null, 0);
            this.m_bNewOverlayFile = false;
            this.m_bNewOverlayPhase = true;
          }
          if (this.m_bNewOverlayPhase && this.m_SFOverlaySpectrumFile != null)
          {
            int realStart = this.spectrumStartBin(this.m_SFOverlaySpectrumFile.SerialString);
            int num1 = 1;
            this.m_bNewOverlayPhase = false;
            this.m_MSDOverlaySpectra = new MultiSpectrumData();
            foreach (SpectrumInFile spectrumInFile in this.m_SFOverlaySpectrumFile)
            {
              if (spectrumInFile.SpectrumData.Length == 0)
              {
                int num2 = (int) MessageBox.Show("There is no spectra data in " + Settings.Default.OverlaySpectraFile + ".");
                throw new FileNotFoundException();
              }
              this.m_MSDOverlaySpectra.SpectrumData = (object) spectrumInFile.SpectrumData;
              this.m_MSDOverlaySpectra.BackgroundData = (object) this.computeBackground(spectrumInFile.SpectrumData, realStart);
              this.m_MSDOverlaySpectra.FileIndex = this.m_MultiSpectrumDataList.Count<MultiSpectrumData>();
              this.m_MSDOverlaySpectra.SpectraIndex = num1 - 1;
              this.m_SIFOverlaySpectrumInFile = spectrumInFile;
              if (num1 != (int) Settings.Default.OverlaySpectraPhase)
                ++num1;
              else
                break;
            }
            flag = true;
          }
          this.m_MultiSpectrumDataList.Add(this.m_MSDOverlaySpectra);
          if (this.m_SIFOverlaySpectrumInFile != null)
            this.DetermineSpectraPeak(this.m_SIFOverlaySpectrumInFile);
        }
        if (!flag || this.m_bDataFromLiveSpectrum)
          return;
        this.m_bDoRefresh = true;
        this.panelGraph.Refresh();
      }
      catch (FileNotFoundException ex)
      {
        Settings.Default.OverlaySpectraEnable = false;
        Settings.Default.OverlaySpectraFile = (string) null;
        this.enableOverlayToolStripMenuItem.Checked = false;
      }
    }

    private void enableOverlayToolStripMenuItem_Click(object sender, EventArgs e)
    {
      bool bOverLaySpectraWasEnabled = this.enableOverlayToolStripMenuItem.Checked = Settings.Default.OverlaySpectraEnable;
      this.enableOverlayToolStripMenuItem.Checked = !this.enableOverlayToolStripMenuItem.Checked;
      Settings.Default.OverlaySpectraEnable = this.enableOverlayToolStripMenuItem.Checked;
      this.RefreshOverlaySpectra(bOverLaySpectraWasEnabled);
      this.enableOverlayToolStripMenuItem.Checked = Settings.Default.OverlaySpectraEnable;
    }

    private void overlaySpectraToolStripMenuItem_Click(object sender, EventArgs e) => this.OverlaySpectraDialog();

    private void menuShowBackground_Click(object sender, EventArgs e)
    {
      Settings.Default.ShowBackground = this.menuShowBackground.Checked;
      this.RefreshGraph();
    }

    private void menuShowOneSpectrum_Click(object sender, EventArgs e)
    {
      Settings.Default.ShowOneSpectrum = this.menuShowOneSpectrum.Checked;
      if (!Settings.Default.ShowOneSpectrum)
      {
        if (SpectrumViewer.m_ActiveForms.Count == 0)
        {
          this.oneOnly = -1;
        }
        else
        {
          bool flag = false;
          foreach (Form activeForm in SpectrumViewer.m_ActiveForms)
          {
            if (activeForm is SpectrumReview)
              flag = true;
          }
          if (!flag)
            this.oneOnly = -1;
        }
      }
      else
        this.oneOnly = this.cmbSpectrumFiles.SelectedIndex;
      this.RefreshGraph();
    }

    public double GetKeVPerChannel()
    {
      double keVperChannel = 0.0;
      if (this.m_SpectrumFile != null)
        keVperChannel = this.m_SpectrumFile.SpectrumFileInfo[0].EVPerChannel;
      return keVperChannel;
    }

    private void menuRegionOfInterest_Click(object sender, EventArgs e)
    {
      if (this.ROIForm == null)
        return;
      this.ShowForm((Form) this.ROIForm);
    }

    private void menuRenameROI_Click(object sender, EventArgs e)
    {
      if (this.ROIForm == null)
        return;
      this.ROIForm.RenameROI(this.m_ROIRightClickIndex);
    }

    private void menuDeleteROI_Click(object sender, EventArgs e)
    {
      if (this.ROIForm == null)
        return;
      this.ROIForm.DeleteROI(this.m_ROIRightClickIndex);
    }

    private void menuChangeROIBounds_Click(object sender, EventArgs e)
    {
      if (this.ROIForm == null)
        return;
      this.ROIForm.ChangeBounds(this.m_ROIRightClickIndex);
    }

    private int[] computeBackground(int[] spectrumData, int realStart) => this.peakStrip(this.smooth(spectrumData, realStart), realStart);

    private int[] smooth(int[] spectrumData, int realStart)
    {
      int index1 = spectrumData.Length - 1;
      int[] numArray = new int[spectrumData.Length];
      for (int index2 = 0; index2 < realStart; ++index2)
        numArray[index2] = 0;
      for (int index3 = realStart + 1; index3 < index1; ++index3)
        numArray[index3] = (spectrumData[index3 - 1] + spectrumData[index3] * 2 + spectrumData[index3 + 1] + 2) / 4;
      numArray[realStart] = spectrumData[realStart];
      numArray[index1] = spectrumData[index1];
      return numArray;
    }

    private int[] peakStrip(int[] spectrumData, int realStart) => this.average(this.average(this.cutPeaks(this.cutPeaks(this.cutPeaks(spectrumData, realStart, 5), realStart, 5), realStart, 4), realStart, 8), realStart, 8);

    private int[] cutPeaks(int[] inData, int realStart, int halfWidth)
    {
      int[] numArray = new int[inData.Length];
      int num1 = realStart + halfWidth;
      int num2 = inData.Length - halfWidth;
      for (int index = 0; index < realStart; ++index)
        numArray[index] = inData[index];
      for (int index = num1; index < num2; ++index)
        numArray[index] = this.minChanRange(inData, index - halfWidth, index + halfWidth);
      for (int index = realStart; index < num1; ++index)
        numArray[index] = this.minChanRange(inData, realStart, index + halfWidth);
      for (int index = num2; index < inData.Length; ++index)
        numArray[index] = this.minChanRange(inData, index - halfWidth, inData.Length - 1);
      return numArray;
    }

    private int minChanRange(int[] inData, int firstChan, int lastChan)
    {
      int num = inData[lastChan];
      for (int index = firstChan; index < lastChan; ++index)
      {
        if (inData[index] < num)
          num = inData[index];
      }
      return num;
    }

    private int[] average(int[] inData, int realStart, int halfWidth)
    {
      int[] numArray = new int[inData.Length];
      for (int index = 0; index < realStart; ++index)
        numArray[index] = inData[index];
      for (int index1 = realStart; index1 < inData.Length; ++index1)
      {
        int num1 = index1 - halfWidth;
        int num2 = index1 + halfWidth;
        if (num1 < realStart)
          num1 = realStart;
        if (num2 >= inData.Length)
          num2 = inData.Length - 1;
        int num3 = 0;
        int num4 = 0;
        for (int index2 = num1; index2 <= num2; ++index2)
        {
          num3 += inData[index2];
          ++num4;
        }
        numArray[index1] = (num3 + num4 / 2) / num4;
      }
      return numArray;
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
      ComponentResourceManager componentResourceManager = new ComponentResourceManager(typeof (SpectrumViewer));
      this.contextMenu = new ContextMenuStrip(this.components);
      this.menuReset = new ToolStripMenuItem();
      this.menuUnZoom = new ToolStripMenuItem();
      this.toolStripSeparator2 = new ToolStripSeparator();
      this.menuNormalize = new ToolStripMenuItem();
      this.toolStripSeparator8 = new ToolStripSeparator();
      this.menuAddLabel = new ToolStripMenuItem();
      this.enableOverlayToolStripMenuItem = new ToolStripMenuItem();
      this.toolStripSeparator11 = new ToolStripSeparator();
      this.menuRenameROI = new ToolStripMenuItem();
      this.menuDeleteROI = new ToolStripMenuItem();
      this.menuChangeROIBounds = new ToolStripMenuItem();
      this.openFileDialog = new OpenFileDialog();
      this.backgroundWorker = new BackgroundWorker();
      this.folderBrowserDialog = new FolderBrowserDialog();
      this.saveFileDialog = new SaveFileDialog();
      this.panelSpectrum = new DoubleBufferPanel(this.components);
      this.panelGraph = new DoubleBufferPanel(this.components);
      this.panelAxisX = new DoubleBufferPanel(this.components);
      this.panelAxisY = new DoubleBufferPanel(this.components);
      this.printDialog = new PrintDialog();
      this.printDocument = new PrintDocument();
      this.menuOptions = new ToolStripDropDownButton();
      this.menuFileSelector = new ToolStripMenuItem();
      this.toolStripSeparator4 = new ToolStripSeparator();
      this.menuSaveAsPdz = new ToolStripMenuItem();
      this.toolStripSeparator5 = new ToolStripSeparator();
      this.menuAtomicTable = new ToolStripMenuItem();
      this.menuCursorInfo = new ToolStripMenuItem();
      this.menuSpectrumInfo = new ToolStripMenuItem();
      this.menuRegionOfInterest = new ToolStripMenuItem();
      this.menuResults = new ToolStripMenuItem();
      this.SpectrumReviewMenuItem = new ToolStripMenuItem();
      this.overlaySpectraToolStripMenuItem = new ToolStripMenuItem();
      this.menuImages = new ToolStripMenuItem();
      this.menuShowReportGenerator = new ToolStripMenuItem();
      this.menuResolutionFWHM = new ToolStripMenuItem();
      this.menuResolutionCursor = new ToolStripMenuItem();
      this.toolStripSeparator1 = new ToolStripSeparator();
      this.menuSettings = new ToolStripMenuItem();
      this.menuXraySettings = new ToolStripMenuItem();
      this.menuPrint = new ToolStripMenuItem();
      this.toolStripSeparator3 = new ToolStripSeparator();
      this.menuSetIllumination = new ToolStripMenuItem();
      this.menuLiveSpectrum = new ToolStripMenuItem();
      this.menuShowBackground = new ToolStripMenuItem();
      this.menuShowOneSpectrum = new ToolStripMenuItem();
      this.lineLiveSpectrum = new ToolStripSeparator();
      this.menuExit = new ToolStripMenuItem();
      this.menuEdit = new ToolStripDropDownButton();
      this.menuCopy = new ToolStripMenuItem();
      this.toolStripSeparator6 = new ToolStripSeparator();
      this.lblSpectrumList = new ToolStripLabel();
      this.cmbSpectrumFiles = new ToolStripFontComboBox();
      this.toolStripSeparator7 = new ToolStripSeparator();
      this.windowsMenu = new ToolStripDropDownButton();
      this.menuCascade = new ToolStripMenuItem();
      this.menuCloseAll = new ToolStripMenuItem();
      this.picLiveSpectrum = new ToolStripButton();
      this.toolStrip = new ToolStrip();
      this.toolStripSeparator9 = new ToolStripSeparator();
      this.PerChartBtn = new ToolStripButton();
      this.CurInfoBtn = new ToolStripButton();
      this.toolStripSeparator10 = new ToolStripSeparator();
      this.selectOverlaySpectrumToolStripMenuItem = new ToolStripMenuItem();
      this.contextMenu.SuspendLayout();
      this.panelSpectrum.SuspendLayout();
      this.toolStrip.SuspendLayout();
      this.SuspendLayout();
      this.contextMenu.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.contextMenu.Items.AddRange(new ToolStripItem[11]
      {
        (ToolStripItem) this.menuReset,
        (ToolStripItem) this.menuUnZoom,
        (ToolStripItem) this.toolStripSeparator2,
        (ToolStripItem) this.menuNormalize,
        (ToolStripItem) this.toolStripSeparator8,
        (ToolStripItem) this.menuAddLabel,
        (ToolStripItem) this.enableOverlayToolStripMenuItem,
        (ToolStripItem) this.toolStripSeparator11,
        (ToolStripItem) this.menuRenameROI,
        (ToolStripItem) this.menuDeleteROI,
        (ToolStripItem) this.menuChangeROIBounds
      });
      this.contextMenu.Name = "contextMenu";
      this.contextMenu.Size = new Size(199, 198);
      this.contextMenu.Opening += new CancelEventHandler(this.contextMenu_Opening);
      this.menuReset.Name = "menuReset";
      this.menuReset.Size = new Size(198, 22);
      this.menuReset.Text = "Reset";
      this.menuReset.Click += new EventHandler(this.menuReset_Click);
      this.menuUnZoom.Name = "menuUnZoom";
      this.menuUnZoom.ShortcutKeys = Keys.Z | Keys.Control;
      this.menuUnZoom.Size = new Size(198, 22);
      this.menuUnZoom.Text = "UnZoom";
      this.menuUnZoom.Click += new EventHandler(this.menuUnZoom_Click);
      this.toolStripSeparator2.Name = "toolStripSeparator2";
      this.toolStripSeparator2.Size = new Size(195, 6);
      this.menuNormalize.Name = "menuNormalize";
      this.menuNormalize.Size = new Size(198, 22);
      this.menuNormalize.Text = "Normalize";
      this.menuNormalize.Click += new EventHandler(this.menuNormalize_Click);
      this.toolStripSeparator8.Name = "toolStripSeparator8";
      this.toolStripSeparator8.Size = new Size(195, 6);
      this.menuAddLabel.Name = "menuAddLabel";
      this.menuAddLabel.Size = new Size(198, 22);
      this.menuAddLabel.Text = "Add Label";
      this.menuAddLabel.Click += new EventHandler(this.menuAddLabel_Click);
      this.enableOverlayToolStripMenuItem.Checked = true;
      this.enableOverlayToolStripMenuItem.CheckState = CheckState.Checked;
      this.enableOverlayToolStripMenuItem.Name = "enableOverlayToolStripMenuItem";
      this.enableOverlayToolStripMenuItem.Size = new Size(198, 22);
      this.enableOverlayToolStripMenuItem.Text = "Enable Overlay";
      this.enableOverlayToolStripMenuItem.Click += new EventHandler(this.enableOverlayToolStripMenuItem_Click);
      this.toolStripSeparator11.Name = "toolStripSeparator11";
      this.toolStripSeparator11.Size = new Size(195, 6);
      this.menuRenameROI.Name = "menuRenameROI";
      this.menuRenameROI.Size = new Size(198, 22);
      this.menuRenameROI.Text = "Rename ROI";
      this.menuRenameROI.Click += new EventHandler(this.menuRenameROI_Click);
      this.menuDeleteROI.Name = "menuDeleteROI";
      this.menuDeleteROI.Size = new Size(198, 22);
      this.menuDeleteROI.Text = "Delete ROI";
      this.menuDeleteROI.Click += new EventHandler(this.menuDeleteROI_Click);
      this.menuChangeROIBounds.Name = "menuChangeROIBounds";
      this.menuChangeROIBounds.Size = new Size(198, 22);
      this.menuChangeROIBounds.Text = "Change ROI Bounds";
      this.menuChangeROIBounds.Click += new EventHandler(this.menuChangeROIBounds_Click);
      this.openFileDialog.CheckPathExists = false;
      this.backgroundWorker.WorkerSupportsCancellation = true;
      this.backgroundWorker.DoWork += new DoWorkEventHandler(this.backgroundWorker_DoWork);
      this.panelSpectrum.BackColor = Color.White;
      this.panelSpectrum.BorderStyle = BorderStyle.FixedSingle;
      this.panelSpectrum.Controls.Add((Control) this.panelGraph);
      this.panelSpectrum.Controls.Add((Control) this.panelAxisX);
      this.panelSpectrum.Controls.Add((Control) this.panelAxisY);
      this.panelSpectrum.Dock = DockStyle.Fill;
      this.panelSpectrum.Location = new Point(0, 31);
      this.panelSpectrum.Name = "panelSpectrum";
      this.panelSpectrum.Size = new Size(1193, 648);
      this.panelSpectrum.TabIndex = 7;
      this.panelGraph.BackColor = Color.White;
      this.panelGraph.ContextMenuStrip = this.contextMenu;
      this.panelGraph.Dock = DockStyle.Fill;
      this.panelGraph.Location = new Point(63, 0);
      this.panelGraph.Name = "panelGraph";
      this.panelGraph.Size = new Size(1128, 587);
      this.panelGraph.TabIndex = 2;
      this.panelGraph.Click += new EventHandler(this.panelGraph_Click);
      this.panelGraph.DragOver += new DragEventHandler(this.panelGraph_DragOver);
      this.panelGraph.Paint += new PaintEventHandler(this.panelGraph_Paint);
      this.panelGraph.MouseDown += new MouseEventHandler(this.panelGraph_MouseDown);
      this.panelGraph.MouseMove += new MouseEventHandler(this.panelGraph_MouseMove);
      this.panelGraph.MouseUp += new MouseEventHandler(this.panelGraph_MouseUp);
      this.panelGraph.Resize += new EventHandler(this.panelGraph_Resize);
      this.panelAxisX.BackColor = Color.White;
      this.panelAxisX.Dock = DockStyle.Bottom;
      this.panelAxisX.Location = new Point(63, 587);
      this.panelAxisX.Name = "panelAxisX";
      this.panelAxisX.Size = new Size(1128, 59);
      this.panelAxisX.TabIndex = 1;
      this.panelAxisX.Paint += new PaintEventHandler(this.panelAxisX_Paint);
      this.panelAxisX.MouseDown += new MouseEventHandler(this.panelAxisX_MouseDown);
      this.panelAxisX.MouseMove += new MouseEventHandler(this.panelAxisX_MouseMove);
      this.panelAxisX.MouseUp += new MouseEventHandler(this.panelAxisX_MouseUp);
      this.panelAxisX.Resize += new EventHandler(this.panelAxisX_Resize);
      this.panelAxisY.BackColor = Color.White;
      this.panelAxisY.Dock = DockStyle.Left;
      this.panelAxisY.Location = new Point(0, 0);
      this.panelAxisY.Name = "panelAxisY";
      this.panelAxisY.Size = new Size(63, 646);
      this.panelAxisY.TabIndex = 0;
      this.panelAxisY.Paint += new PaintEventHandler(this.panelAxisY_Paint);
      this.panelAxisY.MouseDown += new MouseEventHandler(this.panelAxisY_MouseDown);
      this.panelAxisY.MouseMove += new MouseEventHandler(this.panelAxisY_MouseMove);
      this.panelAxisY.MouseUp += new MouseEventHandler(this.panelAxisY_MouseUp);
      this.panelAxisY.Resize += new EventHandler(this.panelAxisY_Resize);
      this.printDialog.Document = this.printDocument;
      this.printDialog.UseEXDialog = true;
      this.printDocument.DocumentName = "Spectrum Document";
      this.printDocument.PrintPage += new PrintPageEventHandler(this.printDocument_PrintPage);
      this.menuOptions.DisplayStyle = ToolStripItemDisplayStyle.Text;
      this.menuOptions.DropDownItems.AddRange(new ToolStripItem[26]
      {
        (ToolStripItem) this.menuFileSelector,
        (ToolStripItem) this.toolStripSeparator4,
        (ToolStripItem) this.menuSaveAsPdz,
        (ToolStripItem) this.toolStripSeparator5,
        (ToolStripItem) this.menuAtomicTable,
        (ToolStripItem) this.menuCursorInfo,
        (ToolStripItem) this.menuSpectrumInfo,
        (ToolStripItem) this.menuRegionOfInterest,
        (ToolStripItem) this.menuResults,
        (ToolStripItem) this.SpectrumReviewMenuItem,
        (ToolStripItem) this.overlaySpectraToolStripMenuItem,
        (ToolStripItem) this.menuShowOneSpectrum,
        (ToolStripItem) this.menuShowBackground,
        (ToolStripItem) this.menuImages,
        (ToolStripItem) this.menuShowReportGenerator,
        (ToolStripItem) this.menuResolutionFWHM,
        (ToolStripItem) this.menuResolutionCursor,
        (ToolStripItem) this.toolStripSeparator1,
        (ToolStripItem) this.menuSettings,
        (ToolStripItem) this.menuXraySettings,
        (ToolStripItem) this.menuPrint,
        (ToolStripItem) this.toolStripSeparator3,
        (ToolStripItem) this.menuSetIllumination,
        (ToolStripItem) this.menuLiveSpectrum,
        (ToolStripItem) this.lineLiveSpectrum,
        (ToolStripItem) this.menuExit
      });
      this.menuOptions.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.menuOptions.ImageTransparentColor = Color.Magenta;
      this.menuOptions.Name = "menuOptions";
      this.menuOptions.Size = new Size(67, 28);
      this.menuOptions.Text = "Options";
      this.menuOptions.DropDownOpening += new EventHandler(this.menuOptions_DropDownOpening);
      this.menuFileSelector.Name = "menuFileSelector";
      this.menuFileSelector.Size = new Size(247, 22);
      this.menuFileSelector.Text = "File Selector";
      this.menuFileSelector.Click += new EventHandler(this.menuFileSelector_Click);
      this.toolStripSeparator4.Name = "toolStripSeparator4";
      this.toolStripSeparator4.Size = new Size(244, 6);
      this.menuSaveAsPdz.Enabled = false;
      this.menuSaveAsPdz.Name = "menuSaveAsPdz";
      this.menuSaveAsPdz.Size = new Size(247, 22);
      this.menuSaveAsPdz.Text = "&Save As Pdz(s)...";
      this.menuSaveAsPdz.Click += new EventHandler(this.menuSaveAsPdz_Click);
      this.toolStripSeparator5.Name = "toolStripSeparator5";
      this.toolStripSeparator5.Size = new Size(244, 6);
      this.menuAtomicTable.Name = "menuAtomicTable";
      this.menuAtomicTable.Size = new Size(247, 22);
      this.menuAtomicTable.Text = "Periodic Table";
      this.menuAtomicTable.Click += new EventHandler(this.menuAtomicTable_Click);
      this.menuCursorInfo.Name = "menuCursorInfo";
      this.menuCursorInfo.Size = new Size(247, 22);
      this.menuCursorInfo.Text = "Cursor Info";
      this.menuCursorInfo.Click += new EventHandler(this.menuCursorInfo_Click);
      this.menuSpectrumInfo.Name = "menuSpectrumInfo";
      this.menuSpectrumInfo.Size = new Size(247, 22);
      this.menuSpectrumInfo.Text = "Spectrum Info";
      this.menuSpectrumInfo.Click += new EventHandler(this.menuSpectrumInfo_Click);
      this.menuRegionOfInterest.Name = "menuRegionOfInterest";
      this.menuRegionOfInterest.Size = new Size(247, 22);
      this.menuRegionOfInterest.Text = "Region Of Interest";
      this.menuRegionOfInterest.Click += new EventHandler(this.menuRegionOfInterest_Click);
      this.menuResults.Name = "menuResults";
      this.menuResults.Size = new Size(247, 22);
      this.menuResults.Text = "Results";
      this.menuResults.Click += new EventHandler(this.menuResults_Click);
      this.SpectrumReviewMenuItem.Name = "SpectrumReviewMenuItem";
      this.SpectrumReviewMenuItem.Size = new Size(247, 22);
      this.SpectrumReviewMenuItem.Text = "Spectrum Review";
      this.SpectrumReviewMenuItem.Click += new EventHandler(this.SpectrumReviewMenuItem_Click);
      this.overlaySpectraToolStripMenuItem.Name = "overlaySpectraToolStripMenuItem";
      this.overlaySpectraToolStripMenuItem.Size = new Size(247, 22);
      this.overlaySpectraToolStripMenuItem.Text = "Overlay Spectrum";
      this.overlaySpectraToolStripMenuItem.Click += new EventHandler(this.overlaySpectraToolStripMenuItem_Click);
      this.menuImages.Name = "menuImages";
      this.menuImages.Size = new Size(247, 22);
      this.menuImages.Text = "Image Gallery";
      this.menuImages.Click += new EventHandler(this.menuImages_Click);
      this.menuShowReportGenerator.Name = "menuShowReportGenerator";
      this.menuShowReportGenerator.Size = new Size(247, 22);
      this.menuShowReportGenerator.Text = "Show In Report Generator";
      this.menuShowReportGenerator.Click += new EventHandler(this.menuShowReportGenerator_Click);
      this.menuResolutionFWHM.Name = "menuResolutionFWHM";
      this.menuResolutionFWHM.Size = new Size(247, 22);
      this.menuResolutionFWHM.Text = "Resolution (FWHM) Mn";
      this.menuResolutionFWHM.Click += new EventHandler(this.menuResolutionFWHM_Click);
      this.menuResolutionCursor.Name = "menuResolutionCursor";
      this.menuResolutionCursor.Size = new Size(247, 22);
      this.menuResolutionCursor.Text = "Resolution (FWHM) at cursor";
      this.menuResolutionCursor.Click += new EventHandler(this.menuResolutionCursor_Click);
      this.toolStripSeparator1.Name = "toolStripSeparator1";
      this.toolStripSeparator1.Size = new Size(244, 6);
      this.menuSettings.Name = "menuSettings";
      this.menuSettings.Size = new Size(247, 22);
      this.menuSettings.Text = "General Options";
      this.menuSettings.Click += new EventHandler(this.menuSettings_Click);
      this.menuXraySettings.Name = "menuXraySettings";
      this.menuXraySettings.Size = new Size(247, 22);
      this.menuXraySettings.Text = "Xray Settings";
      this.menuXraySettings.Visible = false;
      this.menuXraySettings.Click += new EventHandler(this.menuXraySettings_Click);
      this.menuPrint.Name = "menuPrint";
      this.menuPrint.Size = new Size(247, 22);
      this.menuPrint.Text = "&Print...";
      this.menuPrint.Click += new EventHandler(this.menuPrint_Click);
      this.toolStripSeparator3.Name = "toolStripSeparator3";
      this.toolStripSeparator3.Size = new Size(244, 6);
      this.menuSetIllumination.Name = "menuSetIllumination";
      this.menuSetIllumination.ShortcutKeys = Keys.F7 | Keys.Alt;
      this.menuSetIllumination.Size = new Size(247, 22);
      this.menuSetIllumination.Text = "Set Illumination";
      this.menuSetIllumination.Click += new EventHandler(this.setIlluminationToolStripMenuItem1_Click);
      this.menuLiveSpectrum.Name = "menuLiveSpectrum";
      this.menuLiveSpectrum.ShortcutKeys = Keys.F6;
      this.menuLiveSpectrum.Size = new Size(247, 22);
      this.menuLiveSpectrum.Text = "Start Live Spectrum";
      this.menuLiveSpectrum.Click += new EventHandler(this.menuLiveSpectrum_Click);
      this.menuShowBackground.CheckOnClick = true;
      this.menuShowBackground.Name = "menuShowBackground";
      this.menuShowBackground.Size = new Size(247, 22);
      this.menuShowBackground.Text = "Show Background";
      this.menuShowBackground.Click += new EventHandler(this.menuShowBackground_Click);
      this.menuShowOneSpectrum.CheckOnClick = true;
      this.menuShowOneSpectrum.Name = "menuShowOneSpectrum";
      this.menuShowOneSpectrum.Size = new Size(247, 22);
      this.menuShowOneSpectrum.Text = "Show One Spectrum";
      this.menuShowOneSpectrum.Click += new EventHandler(this.menuShowOneSpectrum_Click);
      this.lineLiveSpectrum.Name = "lineLiveSpectrum";
      this.lineLiveSpectrum.Size = new Size(244, 6);
      this.menuExit.Name = "menuExit";
      this.menuExit.Size = new Size(247, 22);
      this.menuExit.Text = "&Exit";
      this.menuExit.Click += new EventHandler(this.menuExit_Click);
      this.menuEdit.DisplayStyle = ToolStripItemDisplayStyle.Text;
      this.menuEdit.DropDownItems.AddRange(new ToolStripItem[1]
      {
        (ToolStripItem) this.menuCopy
      });
      this.menuEdit.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.menuEdit.Image = (Image) componentResourceManager.GetObject("menuEdit.Image");
      this.menuEdit.ImageTransparentColor = Color.Magenta;
      this.menuEdit.Name = "menuEdit";
      this.menuEdit.Size = new Size(44, 28);
      this.menuEdit.Text = "&Edit";
      this.menuCopy.Name = "menuCopy";
      this.menuCopy.ShortcutKeys = Keys.C | Keys.Control;
      this.menuCopy.Size = new Size(151, 22);
      this.menuCopy.Text = "&Copy";
      this.menuCopy.Click += new EventHandler(this.menuCopy_Click);
      this.toolStripSeparator6.Name = "toolStripSeparator6";
      this.toolStripSeparator6.Size = new Size(6, 31);
      this.lblSpectrumList.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.lblSpectrumList.Name = "lblSpectrumList";
      this.lblSpectrumList.Size = new Size(108, 28);
      this.lblSpectrumList.Text = "Active Spectrum:";
      this.lblSpectrumList.Click += new EventHandler(this.lblSpectrumList_Click);
      this.cmbSpectrumFiles.DropDownStyle = ComboBoxStyle.DropDownList;
      this.cmbSpectrumFiles.DropDownWidth = 200;
      this.cmbSpectrumFiles.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.cmbSpectrumFiles.Name = "cmbSpectrumFiles";
      this.cmbSpectrumFiles.Size = new Size(200, 31);
      this.cmbSpectrumFiles.SelectedIndexChanged += new EventHandler(this.cmbSpectrumFiles_SelectedIndexChanged);
      this.cmbSpectrumFiles.MouseDown += new MouseEventHandler(this.cmbSpectrumFiles_MouseDown);
      this.cmbSpectrumFiles.MouseMove += new MouseEventHandler(this.cmbSpectrumFiles_MouseMove);
      this.cmbSpectrumFiles.MouseUp += new MouseEventHandler(this.cmbSpectrumFiles_MouseUp);
      this.toolStripSeparator7.Name = "toolStripSeparator7";
      this.toolStripSeparator7.Size = new Size(6, 31);
      this.windowsMenu.DropDownItems.AddRange(new ToolStripItem[2]
      {
        (ToolStripItem) this.menuCascade,
        (ToolStripItem) this.menuCloseAll
      });
      this.windowsMenu.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.windowsMenu.Name = "windowsMenu";
      this.windowsMenu.Size = new Size(76, 28);
      this.windowsMenu.Text = "&Windows";
      this.menuCascade.Name = "menuCascade";
      this.menuCascade.Size = new Size(131, 22);
      this.menuCascade.Text = "&Cascade";
      this.menuCascade.Click += new EventHandler(this.menuCascade_Click);
      this.menuCloseAll.Name = "menuCloseAll";
      this.menuCloseAll.Size = new Size(131, 22);
      this.menuCloseAll.Text = "C&lose All";
      this.menuCloseAll.Click += new EventHandler(this.menuCloseAll_Click);
      this.picLiveSpectrum.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.picLiveSpectrum.Image = (Image) Resources.Circle_Green;
      this.picLiveSpectrum.ImageTransparentColor = Color.Magenta;
      this.picLiveSpectrum.Name = "picLiveSpectrum";
      this.picLiveSpectrum.Size = new Size(143, 28);
      this.picLiveSpectrum.Text = "Start Live Spectrum";
      this.picLiveSpectrum.Visible = false;
      this.toolStrip.Items.AddRange(new ToolStripItem[11]
      {
        (ToolStripItem) this.menuOptions,
        (ToolStripItem) this.menuEdit,
        (ToolStripItem) this.toolStripSeparator6,
        (ToolStripItem) this.lblSpectrumList,
        (ToolStripItem) this.cmbSpectrumFiles,
        (ToolStripItem) this.toolStripSeparator7,
        (ToolStripItem) this.windowsMenu,
        (ToolStripItem) this.picLiveSpectrum,
        (ToolStripItem) this.toolStripSeparator9,
        (ToolStripItem) this.PerChartBtn,
        (ToolStripItem) this.CurInfoBtn
      });
      this.toolStrip.Location = new Point(0, 0);
      this.toolStrip.Name = "toolStrip";
      this.toolStrip.Size = new Size(1193, 31);
      this.toolStrip.TabIndex = 0;
      this.toolStrip.Text = "toolStrip1";
      this.toolStripSeparator9.Name = "toolStripSeparator9";
      this.toolStripSeparator9.Size = new Size(6, 31);
      this.PerChartBtn.DisplayStyle = ToolStripItemDisplayStyle.Image;
      this.PerChartBtn.Image = (Image) componentResourceManager.GetObject("PerChartBtn.Image");
      this.PerChartBtn.ImageScaling = ToolStripItemImageScaling.None;
      this.PerChartBtn.ImageTransparentColor = Color.Magenta;
      this.PerChartBtn.Name = "PerChartBtn";
      this.PerChartBtn.Size = new Size(44, 28);
      this.PerChartBtn.Click += new EventHandler(this.menuAtomicTable_Click);
      this.CurInfoBtn.Image = (Image) componentResourceManager.GetObject("CurInfoBtn.Image");
      this.CurInfoBtn.ImageTransparentColor = Color.Magenta;
      this.CurInfoBtn.Name = "CurInfoBtn";
      this.CurInfoBtn.Size = new Size(62, 28);
      this.CurInfoBtn.Text = "Cursor";
      this.CurInfoBtn.Click += new EventHandler(this.menuCursorInfo_Click);
      this.toolStripSeparator10.Name = "toolStripSeparator10";
      this.toolStripSeparator10.Size = new Size(221, 6);
      this.selectOverlaySpectrumToolStripMenuItem.Name = "selectOverlaySpectrumToolStripMenuItem";
      this.selectOverlaySpectrumToolStripMenuItem.Size = new Size(32, 19);
      this.AutoScaleDimensions = new SizeF(8f, 16f);
      this.AutoScaleMode = AutoScaleMode.Font;
      this.ClientSize = new Size(1193, 679);
      this.Controls.Add((Control) this.panelSpectrum);
      this.Controls.Add((Control) this.toolStrip);
      this.DoubleBuffered = true;
      this.Font = new Font("Microsoft Sans Serif", 9.75f, FontStyle.Regular, GraphicsUnit.Point, (byte) 0);
      this.KeyPreview = true;
      this.Margin = new Padding(3, 4, 3, 4);
      this.Name = nameof (SpectrumViewer);
      this.ShowIcon = false;
      this.StartPosition = FormStartPosition.CenterScreen;
      this.Text = "Spectrum Viewer";
      this.WindowState = FormWindowState.Maximized;
      this.FormClosing += new FormClosingEventHandler(this.PdzViewer_FormClosing);
      this.Load += new EventHandler(this.PdzViewer_Load);
      this.Shown += new EventHandler(this.SpectrumViewer_Shown);
      this.Resize += new EventHandler(this.SpectrumViewer_Resize);
      this.contextMenu.ResumeLayout(false);
      this.panelSpectrum.ResumeLayout(false);
      this.toolStrip.ResumeLayout(false);
      this.toolStrip.PerformLayout();
      this.ResumeLayout(false);
      this.PerformLayout();
    }

    internal class Disposer : Component
    {
      private Action<bool> dispose_;

      internal Disposer(Action<bool> disposeCallback) => this.dispose_ = disposeCallback;

      protected override void Dispose(bool disposing)
      {
        base.Dispose(disposing);
        this.dispose_(disposing);
      }
    }

    private struct XAxisInfo
    {
      public float start;
      public float width;
      public int cursor;

      public XAxisInfo(float startStep, float visibleWidth, int cursorPos)
      {
        this.start = startStep;
        this.width = visibleWidth;
        this.cursor = cursorPos;
      }
    }
  }
}
