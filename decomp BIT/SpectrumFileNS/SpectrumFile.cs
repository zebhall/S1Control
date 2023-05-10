// Decompiled with JetBrains decompiler
// Type: BrukerAXS.Handheld.SpectrumFileNS.SpectrumFile
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using S1Sync;
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.IO;
using System.Text;
using System.Windows.Forms;

namespace BrukerAXS.Handheld.SpectrumFileNS
{
  [TypeConverter(typeof (SpectrumFileConverter))]
  public class SpectrumFile : IEnumerable<SpectrumInFile>, IEnumerable
  {
    private string _fileName;
    private string _instrumentID;
    private SpectrumFile.FileType _fileType;
    private int _numberOfSpectra;
    private short m_siNumChannels;
    private int _fileVersion;
    private uint _InstrumentType;
    private string _sampleID;
    private int _tubeTargetElement;
    private double _anodeTakeOffAngle;
    private double _sampleIncidenceAngle;
    private double _beThicknessInMicroMeters;
    private double _sampleTakeOffAngle;
    private float _sampleRunTime;
    private float _liveTimeAKAElapstedTime;
    private string _serialString;
    private string _collimSize;
    private string _nosetemp;
    private string _nosepress;
    private Dictionary<string, object> _miscProperties;
    private SpectrumInFile[] _spectra;
    private List<SpectrumResultRow> m_SpectrumResults = new List<SpectrumResultRow>();
    private List<Image> m_SpectrumImages = new List<Image>();

    public SpectrumInFile this[int index]
    {
      get
      {
        if (index >= this._spectra.Length)
          throw new ArgumentOutOfRangeException(string.Format("Attempt to access non-existant spectra loaded from file {0}, index {1}", (object) this._fileName, (object) index));
        return this._spectra[index];
      }
    }

    public IEnumerator<SpectrumInFile> GetEnumerator()
    {
      SpectrumInFile[] spectrumInFileArray = this._spectra;
      for (int index = 0; index < spectrumInFileArray.Length; ++index)
        yield return spectrumInFileArray[index];
      spectrumInFileArray = (SpectrumInFile[]) null;
    }

    IEnumerator IEnumerable.GetEnumerator() => (IEnumerator) this.GetEnumerator();

    public SpectrumFile()
    {
      this._miscProperties = new Dictionary<string, object>();
      this.PassFailString = "None";
      this.StdMultiplier = 1;
    }

    [Category("SpectrumFileInfo")]
    public SpectrumFile.FileType Type => this._fileType;

    [Category("SpectrumFileInfo")]
    public int FileVersion => this._fileVersion;

    [Category("SpectrumFileInfo")]
    public string SampleID => this._sampleID;

    [Category("SpectrumFileInfo")]
    public int NumSpectra => this._numberOfSpectra;

    [Category("SpectrumFileInfo")]
    public string BuildNumber => this._instrumentID;

    [Category("SpectrumFileInfo")]
    public int TubeTargetElement
    {
      get => this._tubeTargetElement;
      set => this._tubeTargetElement = value;
    }

    [Category("SpectrumFileInfo")]
    public string SerialString
    {
      get => this._serialString;
      set => this._serialString = value;
    }

    [Category("SpectrumFileInfo")]
    public double AnodeTakeOffAngle => this._anodeTakeOffAngle;

    [Category("SpectrumFileInfo")]
    public double IncidenceAngle => this._sampleIncidenceAngle;

    [Category("SpectrumFileInfo")]
    public string CollimSize => this._collimSize;

    [Category("SpectrumFileInfo")]
    public string NoseTemperature => this._nosetemp;

    [Category("SpectrumFileInfo")]
    public string NosePressure => this._nosepress;

    [Category("SpectrumFileInfo")]
    public double BeThickInMicroMeters => this._beThicknessInMicroMeters;

    [Category("SpectrumFileInfo")]
    public double TakeOffAngle => this._sampleTakeOffAngle;

    [Category("SpectrumFileInfo")]
    public float RunTime => this._sampleRunTime;

    [Category("SpectrumFileInfo")]
    public SpectrumInFile[] SpectrumFileInfo => this._spectra;

    [Category("SpectrumFileInfo")]
    public string FileName => this._fileName;

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public List<SpectrumResultRow> SpectrumResults => this.m_SpectrumResults;

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public List<Image> SpectrumImages => this.m_SpectrumImages;

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public AnaliticalType AnaliticalType { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public ModeType Mode { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string CalPkgPartNum { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public List<string> AlloyList { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string PDZLibraryName { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string PassFailString { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string PdzInfoName { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string PdzInfoId { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string PdzInfoField1 { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string PdzInfoField2 { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string ApplicationName { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string AssayNumberList { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public DateTime AcquisitionDateTime => this.SpectrumFileInfo[0].AcquisitionDateTime;

    public uint InstrumentType => this._InstrumentType;

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public bool HasGPS { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public bool IsGpsValid { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public double Latitude { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public double Longitude { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public float Altitude { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public List<string> AlloyMatchQualityList { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public int StdMultiplier { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public string ActiveCalName { get; set; }

    [Category("SpectrumFileInfo")]
    [Browsable(false)]
    public CoatingInfoClass CoatingInfo { get; set; }

    public int ElapsedTime()
    {
      int num = 0;
      string sKey = "packetCnt (PDZ)";
      for (int index = 0; index < this._numberOfSpectra; ++index)
      {
        object obj;
        this._spectra[index].Get_miscProperties(sKey, out obj);
        num += Convert.ToInt32(obj);
      }
      return num;
    }

    public float LiveAKAElapsedTime() => this._liveTimeAKAElapstedTime;

    public float TotalLiveTime()
    {
      float num = 0.0f;
      foreach (SpectrumInFile spectrumInFile in this.SpectrumFileInfo)
        num += spectrumInFile.PacketCnt;
      try
      {
        object obj;
        this.SpectrumFileInfo[this.SpectrumFileInfo.Length - 1]._miscProperties.TryGetValue("liveTime (PDZ)", out obj);
        if ((double) (float) obj > 0.5)
          num = (float) obj;
      }
      catch (Exception ex)
      {
      }
      return num;
    }

    public bool LoadFromFile(string fileName, string sampleID, int tubeTargetElement)
    {
      if (!File.Exists(fileName))
      {
        int num = (int) MessageBox.Show("Can't find the file " + fileName + ".");
        return false;
      }
      this._fileName = fileName;
      this._sampleID = sampleID;
      this._tubeTargetElement = tubeTargetElement;
      this._anodeTakeOffAngle = 53.0;
      this._sampleIncidenceAngle = 45.0;
      this._sampleTakeOffAngle = 65.0;
      this._beThicknessInMicroMeters = 75.0;
      switch (Path.GetExtension(fileName).ToLower().TrimEnd())
      {
        case ".pdz":
          this._fileType = SpectrumFile.FileType.Pdz;
          break;
        case ".ssd":
          this._fileType = SpectrumFile.FileType.Ssd;
          break;
        case ".dpp":
          this._fileType = SpectrumFile.FileType.Dpp;
          break;
        default:
          throw new FormatException(string.Format("Attempt to load from file '{0}' that is neither pdz nor ssd", (object) fileName));
      }
      using (FileStream fileStream = new FileStream(fileName, FileMode.Open, FileAccess.Read, FileShare.Read))
      {
        using (BinaryReader fr = new BinaryReader((Stream) fileStream, Encoding.ASCII))
        {
          switch (this._fileType)
          {
            case SpectrumFile.FileType.Pdz:
              this.LoadFromPdzFile(fileStream, fr, fileName);
              break;
            case SpectrumFile.FileType.Dpp:
              this.LoadFromDppFile(fr);
              break;
          }
          fr.Close();
        }
        fileStream.Close();
      }
      if (this._numberOfSpectra > 0 && this._spectra[0].EVPerChannel < 0.001)
      {
        if (this._InstrumentType != 2U)
        {
          int num = (int) MessageBox.Show("The evPerChannel is zero in " + fileName + ", defaulting to 20.");
        }
        for (int index = 0; index < this._numberOfSpectra; ++index)
        {
          if (this._spectra[index].EVPerChannel < 0.001)
            this._spectra[index].EVPerChannel = 20.0;
        }
      }
      return true;
    }

    public static SpectrumFile operator +(SpectrumFile lhs, SpectrumFile rhs)
    {
      if (lhs._numberOfSpectra + rhs._numberOfSpectra > 2)
        throw new InvalidOperationException(string.Format("Attempt to combine spectra from file {0} and file {1} which already have {2} and {3} spectra", (object) lhs._fileName, (object) rhs._fileName, (object) lhs._numberOfSpectra, (object) rhs._numberOfSpectra));
      if (lhs._serialString != rhs._serialString)
        throw new InvalidOperationException(string.Format("Attempt to combine spectra from file {0} and file {1} which have different serial numbers: {2} and {3}", (object) lhs._fileName, (object) rhs._fileName, (object) lhs._serialString, (object) rhs._serialString));
      SpectrumFile spectrumFile = new SpectrumFile();
      if (!string.IsNullOrEmpty(lhs._fileName))
      {
        spectrumFile._fileName = lhs._fileName;
        spectrumFile._fileType = lhs._fileType;
        spectrumFile._fileVersion = lhs._fileVersion;
        spectrumFile._sampleID = lhs._sampleID;
        spectrumFile._tubeTargetElement = lhs._tubeTargetElement;
        spectrumFile._anodeTakeOffAngle = lhs._anodeTakeOffAngle;
        spectrumFile._sampleIncidenceAngle = lhs._sampleIncidenceAngle;
        spectrumFile._beThicknessInMicroMeters = lhs._beThicknessInMicroMeters;
        spectrumFile._sampleTakeOffAngle = lhs._sampleTakeOffAngle;
        spectrumFile._serialString = lhs._serialString;
      }
      else
      {
        spectrumFile._fileName = rhs._fileName;
        spectrumFile._fileType = rhs._fileType;
        spectrumFile._fileVersion = rhs._fileVersion;
        spectrumFile._sampleID = rhs._sampleID;
        spectrumFile._tubeTargetElement = rhs._tubeTargetElement;
        spectrumFile._anodeTakeOffAngle = rhs._anodeTakeOffAngle;
        spectrumFile._sampleIncidenceAngle = rhs._sampleIncidenceAngle;
        spectrumFile._beThicknessInMicroMeters = rhs._beThicknessInMicroMeters;
        spectrumFile._sampleTakeOffAngle = rhs._sampleTakeOffAngle;
        spectrumFile._serialString = rhs._serialString;
      }
      spectrumFile._numberOfSpectra = lhs._numberOfSpectra + rhs._numberOfSpectra;
      spectrumFile._sampleRunTime = lhs._sampleRunTime + rhs._sampleRunTime;
      foreach (string key in lhs._miscProperties.Keys)
        spectrumFile._miscProperties.Add(key, lhs._miscProperties[key]);
      foreach (string key in rhs._miscProperties.Keys)
      {
        if (!spectrumFile._miscProperties.ContainsKey(key))
          spectrumFile._miscProperties.Add(key, rhs._miscProperties[key]);
      }
      spectrumFile._spectra = new SpectrumInFile[spectrumFile._numberOfSpectra];
      int num = 0;
      foreach (SpectrumInFile spectrum in lhs._spectra)
        spectrumFile._spectra[num++] = spectrum;
      foreach (SpectrumInFile spectrum in rhs._spectra)
        spectrumFile._spectra[num++] = spectrum;
      return spectrumFile;
    }

    public void LoadFromLiveData(S1CookedDataWithHeader rawCookedData)
    {
      this._numberOfSpectra = 1;
      this._spectra = new SpectrumInFile[this._numberOfSpectra];
      this._spectra[0] = new SpectrumInFile((string) null, this);
      this._spectra[0].LoadFromLiveData(rawCookedData);
    }

    public void WriteToPDZFile(string fileName)
    {
      using (FileStream output = new FileStream(fileName, FileMode.Create, FileAccess.Write, FileShare.None))
      {
        using (BinaryWriter fw = new BinaryWriter((Stream) output, Encoding.ASCII))
        {
          if (this._fileType == SpectrumFile.FileType.Pdz)
            this.WriteMiscProperty(fw, "FileVersionByte (PDZ)");
          else
            fw.Write((byte) 1);
          fw.Write((byte) this._numberOfSpectra);
          short num = (short) this._fileVersion;
          if (this._fileType != SpectrumFile.FileType.Pdz)
            num = (short) 23;
          fw.Write(num);
          this.WriteMiscProperty(fw, "MaxCh (PDZ)");
          this._spectra[0].WriteToPDZFileFirst(fw);
          if (this._numberOfSpectra > 1)
          {
            for (int index = 1; index < this._numberOfSpectra; ++index)
              this._spectra[index].WriteToPDZFileSecond(fw);
          }
          this.WritePDZAveragingData(fw);
          fw.Close();
        }
        output.Close();
      }
    }

    public void WriteCookedDataToPDZFile(string fileName)
    {
      using (FileStream output = new FileStream(fileName, FileMode.Create, FileAccess.Write, FileShare.None))
      {
        using (BinaryWriter binaryWriter = new BinaryWriter((Stream) output, Encoding.ASCII))
          binaryWriter.Close();
        output.Close();
      }
    }

    public string ToText(bool includeSpectraData)
    {
      StringBuilder sb = new StringBuilder();
      sb.AppendLine(string.Format("fileName:{0}:", (object) this._fileName));
      sb.AppendLine(string.Format("fileType:{0}", (object) this._fileType));
      sb.AppendLine(string.Format("numberOfSpectra:{0}", (object) this._numberOfSpectra));
      sb.AppendLine(string.Format("fileVersion:{0}", (object) this._fileVersion));
      sb.AppendLine(string.Format("sampleID:{0}", (object) this._sampleID));
      sb.AppendLine(string.Format("serialNumber:{0}", (object) this._serialString));
      sb.AppendLine(string.Format("tubeTargetElement:{0}", (object) this._tubeTargetElement));
      sb.AppendLine(string.Format("anodeTakeOffAngle:{0}", (object) this._anodeTakeOffAngle));
      sb.AppendLine(string.Format("sampleIncidenceAngle:{0}", (object) this._sampleIncidenceAngle));
      sb.AppendLine(string.Format("sampleRunTime (seconds):{0}", (object) this._sampleRunTime));
      sb.AppendLine(string.Format("beThicknessInMicroMeters:{0}", (object) this._beThicknessInMicroMeters));
      sb.AppendLine(string.Format("sampleTakeOffAngle:{0}", (object) this._sampleTakeOffAngle));
      foreach (string key in this._miscProperties.Keys)
      {
        object miscProperty = this._miscProperties[key];
        if (miscProperty is byte[])
          sb.AppendLine(string.Format("{0}:byte array length {1}", (object) key, (object) (miscProperty as byte[]).Length));
        else
          sb.AppendLine(string.Format("{0}:{1}", (object) key, miscProperty));
      }
      sb.AppendLine("Spectrum #1 --------------------");
      this._spectra[0].ToText(sb, includeSpectraData);
      if (this._numberOfSpectra > 1)
      {
        for (int index = 1; index < this._numberOfSpectra; ++index)
        {
          sb.AppendLine(string.Format("Spectrum #{0} --------------------", (object) (index + 1)));
          this._spectra[index].ToText(sb, includeSpectraData);
        }
      }
      return sb.ToString();
    }

    public string ToDPPText(bool includeSpectraData)
    {
      StringBuilder stringBuilder = new StringBuilder();
      stringBuilder.AppendLine(string.Format("fileName:{0}:", (object) this._fileName));
      int num1 = 1;
      foreach (SpectrumInFile spectrum in this._spectra)
      {
        stringBuilder.AppendLine(string.Format("Packet {0} ------------------------------------", (object) num1++));
        StringBuilder sb = stringBuilder;
        int num2 = includeSpectraData ? 1 : 0;
        int num3 = num1 == 2 ? 1 : 0;
        spectrum.ToDPPText(sb, num2 != 0, num3 != 0);
      }
      return stringBuilder.ToString();
    }

    public static void WriteCharField(BinaryWriter fw, string toWrite, int fieldLength)
    {
      if (toWrite.Length > fieldLength)
        throw new ArgumentOutOfRangeException(string.Format("Attempt to write {0} to SSD Header field of size {1}", (object) toWrite, (object) fieldLength));
      fw.Write(toWrite.ToCharArray());
      for (int index = toWrite.Length + 1; index <= fieldLength; ++index)
        fw.Write((byte) 0);
    }

    public SpectrumFile CreateNewFileFromSpectrum(int index)
    {
      if (index >= this._numberOfSpectra)
        throw new ArgumentOutOfRangeException("index larger than number of spectra");
      SpectrumFile fileFromSpectrum = new SpectrumFile();
      fileFromSpectrum._fileName = "";
      fileFromSpectrum._fileType = this._fileType;
      fileFromSpectrum._numberOfSpectra = 1;
      fileFromSpectrum._fileVersion = this._fileVersion;
      fileFromSpectrum._sampleID = this._sampleID;
      fileFromSpectrum._tubeTargetElement = this._tubeTargetElement;
      fileFromSpectrum._anodeTakeOffAngle = this._anodeTakeOffAngle;
      fileFromSpectrum._sampleIncidenceAngle = this._sampleIncidenceAngle;
      fileFromSpectrum._beThicknessInMicroMeters = this._beThicknessInMicroMeters;
      fileFromSpectrum._sampleTakeOffAngle = this._sampleTakeOffAngle;
      fileFromSpectrum._sampleRunTime = this._spectra[index].LiveTime;
      fileFromSpectrum._serialString = this._serialString;
      fileFromSpectrum._miscProperties = this._miscProperties;
      fileFromSpectrum._spectra = new SpectrumInFile[1];
      fileFromSpectrum._spectra[0] = this._spectra[index];
      return fileFromSpectrum;
    }

    public void RemoveSpectrum(int index)
    {
      if (index >= this._numberOfSpectra)
        throw new ArgumentOutOfRangeException("index larger than number of spectra");
      int index1 = this._numberOfSpectra - 1;
      this._sampleRunTime -= this._spectra[index].LiveTime;
      if (index != index1)
      {
        for (int index2 = index; index2 < index1 - 1; ++index2)
          this._spectra[index2] = this._spectra[index2 + 1];
      }
      this._spectra[index1] = (SpectrumInFile) null;
      --this._numberOfSpectra;
    }

    private void LoadFromPdzFile(FileStream fs, BinaryReader fr, string filename)
    {
      this.m_SpectrumResults.Clear();
      this.m_SpectrumImages.Clear();
      switch ((ushort) fr.PeekChar())
      {
        case 25:
        case 63:
          fs.Close();
          fr.Close();
          this.LoadPdzFile25(filename);
          break;
        default:
          this.LoadPdzFile24(fr);
          break;
      }
    }

    private void LoadPdzFile25(string fileName)
    {
      this.AlloyList = new List<string>();
      this.AlloyMatchQualityList = new List<string>();
      using (FileStream input = new FileStream(fileName, FileMode.Open, FileAccess.Read, FileShare.Read))
      {
        using (BinaryReader fr = new BinaryReader((Stream) input, Encoding.Unicode))
        {
          this._fileVersion = (int) (ushort) fr.ReadInt16();
          this._miscProperties.Add("FileVersionByte (PDZ)", (object) this._fileVersion);
          int num1 = (int) fr.ReadUInt32();
          string str = new string(fr.ReadChars(5));
          this._InstrumentType = fr.ReadUInt32();
          this._sampleRunTime = 0.0f;
          this.m_SpectrumResults.Clear();
          this.AssayNumberList = "";
          while (fr.BaseStream.Length > fr.BaseStream.Position)
          {
            ushort num2 = (ushort) fr.ReadInt16();
            uint num3 = fr.ReadUInt32();
            switch (num2)
            {
              case 1:
                this.ReadRecordType1Ver25(fr);
                continue;
              case 2:
                this.ReadRecordType2Ver25(fr);
                continue;
              case 3:
                this.ReadRecordType3Ver25(fr);
                continue;
              case 4:
                this.ReadRecordType4Ver25(fr);
                continue;
              case 5:
                this.ReadRecordType5Ver25(fr);
                continue;
              case 6:
                this.ReadRecordType6Ver25(fr);
                continue;
              case 7:
                this.ReadRecordType7Ver25(fr);
                continue;
              case 8:
                this.ReadRecordType8Ver25(fr);
                continue;
              case 9:
                this.ReadRecordType9Ver25(fr);
                continue;
              case 10:
                this.ReadRecordType10Ver25(fr);
                continue;
              case 11:
                this.ReadRecordType11Ver25(fr);
                continue;
              case 12:
                this.ReadRecordType12Ver25(fr);
                continue;
              case 137:
                this.ReadRecordType137Ver25(fr);
                continue;
              case 138:
                this.ReadRecordType138Ver25(fr);
                continue;
              case 139:
                this.ReadRecordType139Ver25(fr);
                continue;
              case 900:
                this.ReadRecordType900Ver25(fr);
                continue;
              case 1001:
                this.ReadRecordType1001Ver25(fr);
                continue;
              case 1002:
                this.ReadRecordType1002Ver25(fr);
                continue;
              case 1003:
                this.ReadRecordType1003Ver25(fr);
                continue;
              case 1004:
                this.ReadRecordType1004Ver25(fr);
                continue;
              default:
                fr.BaseStream.Position += (long) num3;
                continue;
            }
          }
          this.FillMissingSpectrumInFileData();
          if (!(this.AssayNumberList != ""))
            return;
          this._spectra[0].SetDefaultSpectra();
        }
      }
    }

    public void ReadRecordType1Ver25(BinaryReader fr)
    {
      this._serialString = this.ReadLengthAndString(fr);
      this._instrumentID = this.ReadLengthAndString(fr);
      this._tubeTargetElement = (int) fr.ReadByte();
      this._anodeTakeOffAngle = (double) fr.ReadByte();
      this._sampleIncidenceAngle = (double) fr.ReadByte();
      this._sampleTakeOffAngle = (double) fr.ReadByte();
      this._beThicknessInMicroMeters = (double) fr.ReadInt16();
      this.ReadLengthAndString(fr);
      this.ReadLengthAndString(fr);
      this._collimSize = fr.ReadByte().ToString() + " / ";
      this._collimSize += fr.ReadByte().ToString();
      this.ReadLengthAndString(fr);
      uint num = fr.ReadUInt32();
      for (uint index = 0; index < num; ++index)
      {
        switch (fr.ReadUInt16())
        {
          case 1:
            this.ReadLengthAndString(fr);
            break;
          case 2:
            this.ReadLengthAndString(fr);
            break;
          case 3:
            this.ReadLengthAndString(fr);
            break;
          case 4:
            this.ReadLengthAndString(fr);
            break;
          case 5:
            this.ReadLengthAndString(fr);
            break;
          case 6:
            this.ReadLengthAndString(fr);
            break;
          case 7:
            this.ReadLengthAndString(fr);
            break;
          case 8:
            this.ReadLengthAndString(fr);
            break;
          default:
            this.ReadLengthAndString(fr);
            break;
        }
      }
    }

    public void ReadRecordType2Ver25(BinaryReader fr)
    {
      this._numberOfSpectra = (int) fr.ReadUInt32();
      if (this._numberOfSpectra < 1)
        this._numberOfSpectra = 1;
      this._spectra = new SpectrumInFile[this._numberOfSpectra];
      for (int index = 0; index < this._numberOfSpectra; ++index)
        this._spectra[index] = new SpectrumInFile(this._sampleID, this);
      int num1 = (int) fr.ReadUInt32();
      int num2 = (int) fr.ReadUInt32();
      int num3 = (int) fr.ReadUInt32();
      int num4 = (int) fr.ReadUInt32();
      double num5 = (double) fr.ReadSingle();
      double num6 = (double) fr.ReadSingle();
      double num7 = (double) fr.ReadSingle();
      double num8 = (double) fr.ReadSingle();
      double num9 = (double) fr.ReadSingle();
      this._liveTimeAKAElapstedTime = fr.ReadSingle();
      foreach (SpectrumInFile spectrum in this._spectra)
      {
        spectrum._miscProperties.Add("liveTime (PDZ)", (object) this._liveTimeAKAElapstedTime);
        spectrum.InstrumentID = this._instrumentID;
      }
      this.ApplicationName = this.ReadLengthAndString(fr);
      string str = this.ReadLengthAndString(fr);
      str = this.ReadLengthAndString(fr);
    }

    public void ReadRecordType3Ver25(BinaryReader fr)
    {
      SpectrumInFile.GainControlAlgorithms controlAlgorithms = SpectrumInFile.GainControlAlgorithms.None;
      uint index = fr.ReadUInt32();
      this._spectra[(int) index].RawCounts = (int) fr.ReadUInt32();
      this._spectra[(int) index].ValidCounts = (int) fr.ReadUInt32();
      int num1 = (int) fr.ReadUInt32();
      int num2 = (int) fr.ReadUInt32();
      this._spectra[(int) index].AcquisitionTime = fr.ReadSingle();
      this._spectra[(int) index].TDur = fr.ReadSingle();
      this._spectra[(int) index].DeadTime = fr.ReadSingle();
      this._spectra[(int) index].ResetTime = fr.ReadSingle();
      this._spectra[(int) index].LiveTime = fr.ReadSingle();
      this._spectra[(int) index].XrayVoltage = (double) fr.ReadSingle();
      float num3 = fr.ReadSingle();
      this._spectra[(int) index]._miscProperties.Add("xrayFilCur (PDZ)", (object) num3);
      this._spectra[(int) index].XrayCurrent = (double) num3;
      this._spectra[(int) index].FilterLayer1Element = (int) fr.ReadInt16();
      this._spectra[(int) index].FilterLayer1Thickness = (int) fr.ReadInt16();
      this._spectra[(int) index].FilterLayer2Element = (int) fr.ReadInt16();
      this._spectra[(int) index].FilterLayer2Thickness = (int) fr.ReadInt16();
      this._spectra[(int) index].FilterLayer3Element = (int) fr.ReadInt16();
      this._spectra[(int) index].FilterLayer3Thickness = (int) fr.ReadInt16();
      this._spectra[(int) index].FilterNumber = (int) fr.ReadInt16();
      float num4 = fr.ReadSingle();
      this._spectra[(int) index].DetectorTempInC = num4;
      float num5 = fr.ReadSingle();
      this._spectra[(int) index].AmbientTempInF = num5;
      int num6 = fr.ReadInt32();
      this._spectra[(int) index]._miscProperties.Add("vacuum (PDZ)", (object) num6);
      this._spectra[(int) index].EVPerChannel = (double) fr.ReadSingle();
      switch (fr.ReadInt16())
      {
        case 0:
          controlAlgorithms = SpectrumInFile.GainControlAlgorithms.None;
          break;
        case 1:
          controlAlgorithms = SpectrumInFile.GainControlAlgorithms.ClassicTurbo;
          break;
        case 2:
          controlAlgorithms = SpectrumInFile.GainControlAlgorithms.VassiliNextGen;
          break;
      }
      this._spectra[(int) index].GainControlAlgorithm = controlAlgorithms;
      this._spectra[(int) index].StartingChannel = (double) fr.ReadSingle();
      this._spectra[(int) index].StartingKeV = -this._spectra[(int) index].StartingChannel;
      int year = (int) fr.ReadInt16();
      int month = (int) fr.ReadInt16();
      int num7 = (int) fr.ReadInt16();
      this._spectra[(int) index]._miscProperties.Add("assayDateTimeDayOfWeek (PDZ)", (object) num7);
      int day = (int) fr.ReadInt16();
      int hour = (int) fr.ReadInt16();
      int minute = (int) fr.ReadInt16();
      int second = (int) fr.ReadInt16();
      int millisecond = (int) fr.ReadInt16();
      DateTime dateTime = new DateTime(year, month, day, hour, minute, second, millisecond);
      this._spectra[(int) index].AcquisitionDateTime = dateTime;
      this._spectra[(int) index].ActiveTime = this._spectra[(int) index].LiveTime + this._spectra[(int) index].DeadTime;
      this._spectra[(int) index].PacketTime = this._spectra[(int) index].ActiveTime + this._spectra[(int) index].ResetTime;
      this._spectra[(int) index].PacketCnt = this._spectra[(int) index].AcquisitionTime;
      this._spectra[(int) index].ElapsedPhaseClockTime = (int) (float) Math.Truncate(1.0640000104904175 * (double) this._spectra[(int) index].PacketTime + 0.5);
      this._spectra[(int) index].CommunicationTime = (float) this._spectra[(int) index].ElapsedPhaseClockTime - this._spectra[(int) index].PacketTime;
      this._nosepress = fr.ReadSingle().ToString("0.#");
      this.m_siNumChannels = fr.ReadInt16();
      this._spectra[(int) index].NumberOfChannels = (int) this.m_siNumChannels;
      if (index == 0U)
        this._miscProperties.Add("MaxCh (PDZ)", (object) this.m_siNumChannels);
      this._spectra[(int) index]._miscProperties.Add("channelLong (PDZ)", (object) this.m_siNumChannels);
      this._nosetemp = string.Format("{0:F1}", (object) fr.ReadInt16());
      short num8 = fr.ReadInt16();
      this.ReadLengthAndString(fr);
      num8 = fr.ReadInt16();
      this._spectra[(int) index].ReadLongSpectrumData(fr);
    }

    public void ReadRecordType4Ver25(BinaryReader fr)
    {
      byte[] numArray1 = new byte[20];
      byte[] numArray2 = new byte[58];
      ulong[] numArray3 = new ulong[(int) this.m_siNumChannels];
      uint index1 = fr.ReadUInt32();
      byte num1 = fr.ReadByte();
      this._spectra[(int) index1]._miscProperties.Add("xilinxVer (PDZ)", (object) num1);
      byte num2 = fr.ReadByte();
      this._spectra[(int) index1]._miscProperties.Add("xilinxSubVer (PDZ)", (object) num2);
      ushort num3 = (ushort) fr.ReadInt16();
      this._spectra[(int) index1]._miscProperties.Add("packetLen (PDZ)", (object) num3);
      ulong num4 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("tDur (PDZ)", (object) num4);
      ulong num5 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("rawCnts (PDZ)", (object) num5);
      ulong num6 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("validCnts (PDZ)", (object) num6);
      ulong num7 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("validCntsRng (PDZ)", (object) num7);
      ulong num8 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("aDur (PDZ)", (object) num8);
      ulong num9 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("aDead (PDZ)", (object) num9);
      ulong num10 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("aReset (PDZ)", (object) num10);
      ulong num11 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("aLive (PDZ)", (object) num11);
      ulong num12 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("service (PDZ)", (object) num12);
      ushort num13 = fr.ReadUInt16();
      this._spectra[(int) index1]._miscProperties.Add("resetCnt (PDZ)", (object) num13);
      ushort num14 = fr.ReadUInt16();
      this._spectra[(int) index1].PacketCnt = (float) num14;
      this._spectra[(int) index1]._miscProperties.Add("packetCnt (PDZ)", (object) num14);
      for (int index2 = 0; index2 < 20; ++index2)
        numArray1[index2] = fr.ReadByte();
      for (int index3 = 0; index3 < 58; ++index3)
        numArray2[index3] = fr.ReadByte();
      int num15 = (int) fr.ReadInt16();
      fr.ReadUInt16();
      byte num16 = fr.ReadByte();
      this._spectra[(int) index1]._miscProperties.Add("picVer (PDZ)", (object) num16);
      byte num17 = fr.ReadByte();
      this._spectra[(int) index1]._miscProperties.Add("picSubVer (PDZ)", (object) num17);
      ulong num18 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1].RawCounts = (int) num18;
      ulong num19 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1].ValidCounts = (int) num19;
      ulong num20 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("validCntsRngAcc (PDZ)", (object) num20);
      ulong num21 = (ulong) fr.ReadUInt32();
      this._spectra[(int) index1]._miscProperties.Add("resetCntAcc (PDZ)", (object) num21);
      float num22 = fr.ReadSingle();
      this._spectra[(int) index1]._miscProperties.Add("ftDur (PDZ)", (object) num22);
      float num23 = fr.ReadSingle();
      this._spectra[(int) index1].AcquisitionTime = num23;
      float num24 = fr.ReadSingle();
      this._spectra[(int) index1].DeadTime = num24;
      float num25 = fr.ReadSingle();
      this._spectra[(int) index1].ResetTime = num25;
      float num26 = fr.ReadSingle();
      this._spectra[(int) index1].LiveTime = num26;
      this._spectra[(int) index1].ActiveTime = this._spectra[(int) index1].LiveTime + this._spectra[(int) index1].DeadTime;
      this._spectra[(int) index1].PacketTime = this._spectra[(int) index1].ActiveTime + this._spectra[(int) index1].ResetTime;
      this._spectra[(int) index1].CommunicationTime = this._spectra[(int) index1].PacketTime - this._spectra[(int) index1].AcquisitionTime;
      this._sampleRunTime += this._spectra[(int) index1].LiveTime;
      this._spectra[(int) index1].CountsPerSecond = (double) this._spectra[(int) index1].ActiveTime <= 0.1 ? (float) this._spectra[(int) index1].RawCounts : (float) this._spectra[(int) index1].RawCounts / this._spectra[(int) index1].ActiveTime;
      for (int index4 = 0; index4 < (int) this.m_siNumChannels; ++index4)
      {
        numArray3[index4] = (ulong) fr.ReadUInt32();
        if (numArray3[index4] != 0UL)
          ;
      }
    }

    public void ReadRecordType5Ver25(BinaryReader fr)
    {
      this.Mode = (ModeType) fr.ReadUInt32();
      this.AnaliticalType = (AnaliticalType) fr.ReadUInt32();
      int num1 = (int) fr.ReadInt16();
      int num2 = (int) fr.ReadInt16();
      int num3 = (int) fr.ReadUInt16();
      this.ReadLengthAndString(fr);
      this.ReadLengthAndString(fr);
      this.CalPkgPartNum = this.ReadLengthAndString(fr);
      this.ReadLengthAndString(fr);
    }

    public void ReadRecordType6Ver25(BinaryReader fr)
    {
      SpectrumResultRow spectrumResultRow = new SpectrumResultRow();
      string str = this.ReadLengthAndString(fr);
      spectrumResultRow.m_strElementName = spectrumResultRow.m_strCompoundName = str;
      uint num1 = fr.ReadUInt32();
      spectrumResultRow.m_bAtomicNumber = (byte) num1;
      spectrumResultRow.m_bUnits = fr.ReadByte();
      float num2 = fr.ReadSingle();
      spectrumResultRow.m_fResult = num2;
      float num3 = fr.ReadSingle();
      spectrumResultRow.m_fTypeStdResult = num3;
      float num4 = fr.ReadSingle();
      spectrumResultRow.m_fError = num4;
      float num5 = fr.ReadSingle();
      spectrumResultRow.m_fMinRange = num5;
      float num6 = fr.ReadSingle();
      spectrumResultRow.m_fMaxRange = num6;
      spectrumResultRow.m_bTrampResidual = fr.ReadInt16() != (short) 0;
      spectrumResultRow.m_bNominal = fr.ReadInt16() != (short) 0;
      this.m_SpectrumResults.Add(spectrumResultRow);
    }

    public void ReadRecordType7Ver25(BinaryReader fr)
    {
      string str1 = this.ReadLengthAndString(fr);
      float num1 = fr.ReadSingle();
      if (str1 != "")
      {
        this.AlloyList.Add(str1);
        this.AlloyMatchQualityList.Add(num1.ToString("N"));
      }
      string str2 = this.ReadLengthAndString(fr);
      num1 = fr.ReadSingle();
      if (str2 != "")
      {
        this.AlloyList.Add(str2);
        this.AlloyMatchQualityList.Add(num1.ToString("N"));
      }
      string str3 = this.ReadLengthAndString(fr);
      num1 = fr.ReadSingle();
      if (str3 != "")
      {
        this.AlloyList.Add(str3);
        this.AlloyMatchQualityList.Add(num1.ToString("N"));
      }
      num1 = fr.ReadSingle();
      int num2 = (int) fr.ReadInt16();
      int num3 = (int) fr.ReadInt16();
      uint num4 = (uint) fr.ReadUInt16();
      for (int index = 0; (long) index < (long) num4; ++index)
      {
        string str4 = this.ReadLengthAndString(fr);
        if (index == 0)
          this.PDZLibraryName = str4;
        this.ReadLengthAndString(fr);
      }
    }

    public void ReadRecordType8Ver25(BinaryReader fr)
    {
      switch (fr.ReadUInt16())
      {
        case 0:
          this.PassFailString = "None";
          break;
        case 1:
          this.PassFailString = "Fail";
          break;
        case 2:
          this.PassFailString = "Pass";
          break;
        case 3:
          this.PassFailString = "Inconclusive";
          break;
        default:
          this.PassFailString = "Inconclusive";
          break;
      }
      this.ReadLengthAndString(fr);
      this.ReadLengthAndString(fr);
    }

    public void ReadRecordType9Ver25(BinaryReader fr)
    {
      if (this.PdzInfoName != null)
        this.PdzInfoName.Remove(0);
      if (this.PdzInfoId != null)
        this.PdzInfoId.Remove(0);
      short num = fr.ReadInt16();
      for (short index = 0; (int) index < (int) num; ++index)
      {
        string str1 = this.ReadLengthAndString(fr);
        string str2 = this.ReadLengthAndString(fr);
        this.PdzInfoName += str1;
        this.PdzInfoId += str2;
        if ((int) index < (int) num)
        {
          this.PdzInfoName += "::";
          this.PdzInfoId += "::";
        }
      }
    }

    public void ReadRecordType10Ver25(BinaryReader fr)
    {
      uint length = fr.ReadUInt32();
      StringBuilder stringBuilder = new StringBuilder();
      uint[] numArray = new uint[(int) length];
      for (uint index = 0; index < length; ++index)
      {
        numArray[(int) index] = fr.ReadUInt32();
        stringBuilder.Append(numArray.ToString());
      }
      this.AssayNumberList = stringBuilder.ToString();
    }

    public void ReadRecordType11Ver25(BinaryReader fr)
    {
      ushort index1 = fr.ReadUInt16();
      ushort num = fr.ReadUInt16();
      for (ushort index2 = 0; (int) index2 < (int) num; ++index2)
      {
        ushort iElement = fr.ReadUInt16();
        this._spectra[(int) index1].SetFilterLayerElementFromPDZ((int) iElement);
      }
      for (ushort index3 = 0; (int) index3 < (int) num; ++index3)
      {
        uint iThickness = fr.ReadUInt32();
        this._spectra[(int) index1].SetFilterLayerThicknessFromPDZ((int) iThickness);
      }
    }

    public void ReadRecordType12Ver25(BinaryReader fr)
    {
      CoatingInfoClass coatingInfoClass = new CoatingInfoClass();
      int num1 = (int) fr.ReadInt16();
      coatingInfoClass.AreaDensity = fr.ReadSingle();
      coatingInfoClass.Density = fr.ReadSingle();
      coatingInfoClass.Thickness = fr.ReadSingle();
      coatingInfoClass.AD_deviation = fr.ReadSingle();
      coatingInfoClass.T_deviation = fr.ReadSingle();
      coatingInfoClass.SatRatio = fr.ReadSingle();
      coatingInfoClass.AD_Inf = fr.ReadSingle();
      coatingInfoClass.T_Inf = fr.ReadSingle();
      coatingInfoClass.LayerIndex = fr.ReadInt32();
      short num2 = fr.ReadInt16();
      coatingInfoClass.bInfThick = ((int) num2 >> 8 & (int) byte.MaxValue) == 1;
      coatingInfoClass.FullyDefined = ((int) num2 & (int) byte.MaxValue) == 1;
      this.CoatingInfo = coatingInfoClass;
    }

    public void ReadRecordType137Ver25(BinaryReader fr)
    {
      uint num1 = fr.ReadUInt32();
      for (int index = 0; (long) index < (long) num1; ++index)
      {
        uint count = fr.ReadUInt32();
        byte[] buffer = fr.ReadBytes((int) count);
        Image image;
        using (MemoryStream memoryStream = new MemoryStream())
        {
          memoryStream.Write(buffer, 0, buffer.Length);
          image = Image.FromStream((Stream) memoryStream);
        }
        this.m_SpectrumImages.Add(image);
        int num2 = (int) fr.ReadUInt32();
        int num3 = (int) fr.ReadUInt32();
        this.ReadLengthAndString(fr);
      }
    }

    public void ReadRecordType138Ver25(BinaryReader fr)
    {
      this.HasGPS = true;
      this.IsGpsValid = fr.ReadInt32() != 0;
      this.Latitude = fr.ReadDouble();
      this.Longitude = fr.ReadDouble();
      this.Altitude = fr.ReadSingle();
    }

    public void ReadRecordType139Ver25(BinaryReader fr)
    {
      this.StdMultiplier = fr.ReadInt32();
      this.ActiveCalName = this.ReadLengthAndString(fr);
      this._sampleID = this.ReadLengthAndString(fr);
    }

    public void ReadRecordType900Ver25(BinaryReader fr) => this.ReadLengthAndString(fr);

    public void ReadRecordType1001Ver25(BinaryReader fr)
    {
      if (this._spectra == null)
      {
        this._spectra = new SpectrumInFile[1];
        for (int index = 0; index < 1; ++index)
          this._spectra[index] = new SpectrumInFile(this._sampleID, this);
      }
      int num1 = (int) fr.ReadUInt16();
      int num2 = (int) fr.ReadUInt16();
      uint count1 = fr.ReadUInt32();
      this.PDZLibraryName = new string(fr.ReadChars((int) count1));
      int year = (int) fr.ReadInt16();
      int month = (int) fr.ReadInt16();
      int num3 = (int) fr.ReadInt16();
      int day = (int) fr.ReadInt16();
      int hour = (int) fr.ReadInt16();
      int minute = (int) fr.ReadInt16();
      int second = (int) fr.ReadInt16();
      int millisecond = (int) fr.ReadInt16();
      this._spectra[0].AcquisitionDateTime = new DateTime(year, month, day, hour, minute, second, millisecond);
      uint count2 = fr.ReadUInt32();
      string str1 = new string(fr.ReadChars((int) count2));
      short num4 = fr.ReadInt16();
      for (short index = 0; (int) index < (int) num4; ++index)
      {
        SpectrumResultRow spectrumResultRow = new SpectrumResultRow();
        string str2 = new string(fr.ReadChars(2));
        spectrumResultRow.m_strElementName = str2;
        spectrumResultRow.m_strCompoundName = str2;
        spectrumResultRow.m_bAtomicNumber = (byte) 0;
        float num5 = fr.ReadSingle();
        spectrumResultRow.m_fResult = num5;
        spectrumResultRow.m_fTypeStdResult = num5;
        fr.ReadSingle();
        float num6 = fr.ReadSingle();
        spectrumResultRow.m_fError = num6;
        float num7 = fr.ReadSingle();
        spectrumResultRow.m_fMaxRange = num7;
        float num8 = fr.ReadSingle();
        spectrumResultRow.m_fMinRange = num8;
        spectrumResultRow.m_bUnits = (byte) 0;
        this.m_SpectrumResults.Add(spectrumResultRow);
      }
    }

    public void ReadRecordType1002Ver25(BinaryReader fr)
    {
      ushort num1 = fr.ReadUInt16();
      for (ushort index = 0; (int) index < (int) num1; ++index)
      {
        string str = this.ReadLengthAndString(fr);
        float num2 = fr.ReadSingle();
        this.AlloyList.Add(str);
        this.AlloyMatchQualityList.Add(num2.ToString("N"));
      }
      fr.ReadSingle();
      ushort num3 = fr.ReadUInt16();
      for (ushort index = 0; (int) index < (int) num3; ++index)
      {
        string str = this.ReadLengthAndString(fr);
        if (index == (ushort) 0)
          this.PDZLibraryName = str;
        this.ReadLengthAndString(fr);
      }
    }

    public void ReadRecordType1003Ver25(BinaryReader fr)
    {
      this._instrumentID = this.ReadLengthAndString(fr);
      string str = this.ReadLengthAndString(fr);
      int num1 = (int) fr.ReadUInt32();
      int num2 = (int) fr.ReadInt16();
      int num3 = (int) fr.ReadInt16();
      int num4 = (int) fr.ReadInt16();
      int num5 = (int) fr.ReadInt16();
      int num6 = (int) fr.ReadInt16();
      int num7 = (int) fr.ReadInt16();
      int num8 = (int) fr.ReadInt16();
      int num9 = (int) fr.ReadInt16();
      str = this.ReadLengthAndString(fr);
    }

    public void ReadRecordType1004Ver25(BinaryReader fr)
    {
      fr.ReadInt64();
      string str = this.ReadLengthAndString(fr);
      str = this.ReadLengthAndString(fr);
      int num1 = (int) fr.ReadInt16();
      int num2 = (int) fr.ReadInt16();
      int num3 = (int) fr.ReadInt16();
      int num4 = (int) fr.ReadInt16();
      int num5 = (int) fr.ReadInt16();
      int num6 = (int) fr.ReadInt16();
      int num7 = (int) fr.ReadInt16();
      int num8 = (int) fr.ReadInt16();
      str = this.ReadLengthAndString(fr);
      short num9 = fr.ReadInt16();
      for (short index = 0; (int) index < (int) num9; ++index)
      {
        this.PdzInfoName += this.ReadLengthAndString(fr);
        this.PdzInfoId += this.ReadLengthAndString(fr);
        if ((int) index < (int) num9)
        {
          this.PdzInfoName += "::";
          this.PdzInfoId += "::";
        }
      }
      int num10 = this._spectra[0].NumberOfChannels = fr.ReadInt32();
      int length = num10 != 0 ? num10 / 2 : 2048;
      this._spectra[0].SpectrumData = new int[length];
      for (int index = 0; index < length; ++index)
      {
        float num11 = fr.ReadSingle();
        float num12 = fr.ReadSingle();
        if (index == 0)
        {
          this._spectra[0].StartingChannel = (double) num11;
          this._spectra[0].StartingKeV = -this._spectra[0].StartingChannel;
        }
        this._spectra[0].SpectrumData[index] = (int) (uint) num12;
      }
    }

    public string ReadLengthAndString(BinaryReader fr)
    {
      uint count = fr.ReadUInt32();
      return new string(fr.ReadChars((int) count));
    }

    private void FillMissingSpectrumInFileData()
    {
      foreach (SpectrumInFile spectrum in this._spectra)
      {
        spectrum._miscProperties.Add("centriod range[0] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("centriod range[1] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("compton range[0] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("compton range[1] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("rayCompRange[0] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("rayCompRange[1] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("accumulate (PDZ)", (object) -1);
        spectrum._miscProperties.Add("lBeta (PDZ)", (object) -1);
        spectrum._miscProperties.Add("inteR (PDZ)", (object) -1);
        spectrum._miscProperties.Add("gainShift (PDZ)", (object) -1);
        spectrum._miscProperties.Add("specMultiplier (PDZ)", (object) -1);
        spectrum._miscProperties.Add("ktiXrayTube (PDZ)", (object) -1);
        spectrum._miscProperties.Add("xrayTube (PDZ)", (object) -1);
        spectrum._miscProperties.Add("advHeader (PDZ)", (object) -1);
        spectrum._miscProperties.Add("systemFlags (PDZ)", (object) -1);
        spectrum._miscProperties.Add("comptonStarteV (PDZ)", (object) -1);
        spectrum._miscProperties.Add("comptonEndeV (PDZ)", (object) -1);
        spectrum._miscProperties.Add("percentShift (PDZ)", (object) -1);
        spectrum._miscProperties.Add("AgKCentroid[0] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("AgKCentroid[1] (PDZ)", (object) -1);
        spectrum._miscProperties.Add("centroidMinCount (PDZ)", (object) -1);
        spectrum._miscProperties.Add("maxPk (PDZ)", (object) -1);
        spectrum._miscProperties.Add("byteVolt (PDZ)", (object) -1);
        spectrum._miscProperties.Add("byteCurrent (PDZ)", (object) -1);
        spectrum._miscProperties.Add("byteToggle (PDZ)", (object) -1);
        spectrum.PulseLength = -1;
        spectrum.PulsePeriod = -1;
        spectrum._miscProperties.Add("byteExtActual (PDZ)", (object) -1);
        spectrum._miscProperties.Add("byteTimes2 (PDZ)", (object) -1);
        spectrum._miscProperties.Add("eVChInte (PDZ)", (object) -1);
        spectrum._miscProperties.Add("averagingData (PDZ)", (object) -1);
      }
    }

    private void LoadPdzFile24(BinaryReader fr)
    {
      fr.BaseStream.Position = 0L;
      this.AssayNumberList = "";
      int num = (int) fr.ReadByte();
      this._numberOfSpectra = (int) fr.ReadByte();
      this._fileVersion = (int) fr.ReadInt16();
      if (this._numberOfSpectra < 1 || this._numberOfSpectra > 3 || this._fileVersion < 23)
        throw new FormatException(string.Format("Pdz file {0} invalid: numSpectra {1}, version {2}", (object) this._fileName, (object) this._numberOfSpectra, (object) this._fileVersion));
      this._miscProperties.Add("MaxCh (PDZ)", (object) fr.ReadInt16());
      this._spectra = new SpectrumInFile[this._numberOfSpectra];
      for (int index = 0; index < this._numberOfSpectra; ++index)
        this._spectra[index] = new SpectrumInFile(this._sampleID, this);
      this._spectra[0].LoadFromFilePDZFirst(fr);
      if (this._numberOfSpectra > 1)
      {
        for (int index = 1; index < this._numberOfSpectra; ++index)
          this._spectra[index].LoadFromFilePDZSecond(this._spectra[0], fr);
      }
      if (this._fileVersion >= 23 && fr.BaseStream.Length > fr.BaseStream.Position)
      {
        this.ReadPDZAveragingData(fr);
        this._serialString = this._spectra[0].SerialNumber;
        this._sampleRunTime = 0.0f;
        foreach (SpectrumInFile spectrum in this._spectra)
          this._sampleRunTime += spectrum.LiveTime;
        this.ConstructResultAndImageTableFromByteArray();
      }
      if (!(this.AssayNumberList != ""))
        return;
      this._spectra[0].SetDefaultSpectra();
    }

    private void ConstructResultAndImageTableFromByteArray()
    {
      if (!this._miscProperties.ContainsKey("averagingData (PDZ)"))
        return;
      using (Stream input = (Stream) new MemoryStream(this._miscProperties["averagingData (PDZ)"] as byte[]))
      {
        using (BinaryReader binaryReader = new BinaryReader(input))
        {
          uint num1 = binaryReader.ReadUInt32();
          uint num2 = binaryReader.ReadUInt32();
          this.Mode = (ModeType) num1;
          this.AnaliticalType = (AnaliticalType) num2;
          byte num3 = binaryReader.ReadByte();
          this.AlloyList = new List<string>();
          this.AlloyMatchQualityList = new List<string>();
          for (int index = 0; index < (int) num3; ++index)
          {
            uint count = binaryReader.ReadUInt32();
            this.AlloyList.Add(Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count)).Trim(' ').Replace("\0", string.Empty));
            this.AlloyMatchQualityList.Add(binaryReader.ReadSingle().ToString("N"));
          }
          byte num4 = binaryReader.ReadByte();
          for (int index = 0; index < (int) num4; ++index)
          {
            SpectrumResultRow spectrumResultRow = new SpectrumResultRow();
            spectrumResultRow.m_bAtomicNumber = binaryReader.ReadByte();
            uint count = binaryReader.ReadUInt32();
            spectrumResultRow.m_strCompoundName = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count)).Trim(' ').Replace("\0", string.Empty);
            spectrumResultRow.m_strElementName = spectrumResultRow.m_strCompoundName;
            spectrumResultRow.m_bUnits = binaryReader.ReadByte();
            spectrumResultRow.m_fTypeStdResult = spectrumResultRow.m_fResult = binaryReader.ReadSingle();
            spectrumResultRow.m_fError = binaryReader.ReadSingle();
            byte[] numArray1 = new byte[4]
            {
              (byte) 78,
              (byte) 79,
              (byte) 77,
              (byte) 73
            };
            spectrumResultRow.m_bNominal = false;
            spectrumResultRow.m_bTrampResidual = false;
            if ((double) spectrumResultRow.m_fError == (double) BitConverter.ToSingle(numArray1, 0))
            {
              spectrumResultRow.m_bNominal = true;
              spectrumResultRow.m_bTrampResidual = false;
              spectrumResultRow.m_fError = -1f;
            }
            spectrumResultRow.m_fMaxRange = binaryReader.ReadSingle();
            spectrumResultRow.m_fMinRange = binaryReader.ReadSingle();
            byte[] numArray2 = new byte[4]
            {
              (byte) 84,
              (byte) 82,
              (byte) 65,
              (byte) 77
            };
            if ((double) spectrumResultRow.m_fMinRange == (double) BitConverter.ToSingle(numArray2, 0))
            {
              spectrumResultRow.m_bNominal = false;
              spectrumResultRow.m_bTrampResidual = true;
              spectrumResultRow.m_fMinRange = -1f;
            }
            this.m_SpectrumResults.Add(spectrumResultRow);
          }
          try
          {
            uint count1 = binaryReader.ReadUInt32();
            this.PDZLibraryName = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count1)).Trim(' ').Replace("\0", string.Empty);
            uint count2 = binaryReader.ReadUInt32();
            this.PassFailString = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count2)).Trim(' ').Replace("\0", string.Empty);
            uint count3 = binaryReader.ReadUInt32();
            this.PdzInfoName = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count3)).Trim(' ').Replace("\0", string.Empty);
            uint count4 = binaryReader.ReadUInt32();
            this.PdzInfoId = Encoding.Unicode.GetString(binaryReader.ReadBytes((int) count4)).Trim(' ').Replace("\0", string.Empty);
            uint count5 = binaryReader.ReadUInt32();
            this.PdzInfoField1 = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count5)).Trim(' ').Replace("\0", string.Empty);
            uint count6 = binaryReader.ReadUInt32();
            this.PdzInfoField2 = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count6)).Trim(' ').Replace("\0", string.Empty);
            uint count7 = binaryReader.ReadUInt32();
            this.ApplicationName = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count7)).Trim(' ').Replace("\0", string.Empty);
            uint count8 = binaryReader.ReadUInt32();
            this.AssayNumberList = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count8)).Trim(' ').Replace("\0", string.Empty);
            int num5 = (int) binaryReader.ReadInt16();
            uint num6 = binaryReader.ReadUInt32();
            if (num5 == 137 && num6 > 0U)
            {
              uint num7 = binaryReader.ReadUInt32();
              for (int index = 0; (long) index < (long) num7; ++index)
              {
                uint count9 = binaryReader.ReadUInt32();
                byte[] buffer = binaryReader.ReadBytes((int) count9);
                Image image;
                using (MemoryStream memoryStream = new MemoryStream())
                {
                  memoryStream.Write(buffer, 0, buffer.Length);
                  image = Image.FromStream((Stream) memoryStream);
                }
                this.m_SpectrumImages.Add(image);
                int num8 = (int) binaryReader.ReadUInt32();
                int num9 = (int) binaryReader.ReadUInt32();
                uint count10 = binaryReader.ReadUInt32();
                if (count10 > 0U)
                  Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count10)).Trim(' ').Replace("\0", string.Empty);
              }
            }
            int num10 = (int) binaryReader.ReadInt16();
            uint num11 = binaryReader.ReadUInt32();
            this.HasGPS = false;
            this.IsGpsValid = false;
            if (num10 == 138 && num11 > 0U)
            {
              this.HasGPS = true;
              this.IsGpsValid = binaryReader.ReadInt32() == 1;
              this.Latitude = binaryReader.ReadDouble();
              this.Longitude = binaryReader.ReadDouble();
              this.Altitude = binaryReader.ReadSingle();
            }
            int num12 = (int) binaryReader.ReadInt16();
            uint num13 = binaryReader.ReadUInt32();
            if (num12 == 139 && num13 > 0U)
            {
              this.StdMultiplier = binaryReader.ReadInt32();
              if (this.StdMultiplier > 5 || this.StdMultiplier < 1)
                this.StdMultiplier = (int) (ushort) this.StdMultiplier;
              uint count11 = binaryReader.ReadUInt32();
              this.ActiveCalName = "";
              if (count11 > 0U)
                this.ActiveCalName = Encoding.ASCII.GetString(binaryReader.ReadBytes((int) count11)).Trim(' ').Replace("\0", string.Empty);
            }
            else if (this.Mode == ModeType.METAL_ANALYZE)
              this.StdMultiplier = 2;
            else if (this.Mode == ModeType.ROHS_ANALYZE)
              this.StdMultiplier = 3;
          }
          catch (Exception ex)
          {
          }
          binaryReader.Close();
        }
        input.Close();
      }
    }

    private void LoadFromDppFile(BinaryReader fr)
    {
      List<SpectrumInFile> spectrumInFileList = new List<SpectrumInFile>();
      SpectrumInFile firstSpectrum = new SpectrumInFile(this._sampleID, this);
      firstSpectrum.LoadFromDppFile(fr, (SpectrumInFile) null);
      spectrumInFileList.Add(firstSpectrum);
      while (fr.PeekChar() != -1)
      {
        SpectrumInFile spectrumInFile = new SpectrumInFile(this._sampleID, this);
        spectrumInFile.LoadFromDppFile(fr, firstSpectrum);
        spectrumInFileList.Add(spectrumInFile);
      }
      this._numberOfSpectra = spectrumInFileList.Count;
      this._spectra = spectrumInFileList.ToArray();
      this._serialString = "???";
    }

    private void ReadMiscStringProperty(BinaryReader fr, string name, int size) => this._miscProperties.Add(name, (object) new string(fr.ReadChars(size)).Trim(new char[1]));

    private void WriteMiscProperty(BinaryWriter fw, string name)
    {
      object miscProperty = this._miscProperties[name];
      switch (miscProperty)
      {
        case byte num1:
          fw.Write(num1);
          break;
        case byte[] _:
          fw.Write((byte[]) miscProperty);
          break;
        case short num2:
          fw.Write(num2);
          break;
        case ushort num3:
          fw.Write(num3);
          break;
        case int num4:
          fw.Write(num4);
          break;
        case uint num5:
          fw.Write(num5);
          break;
        case float num6:
          fw.Write(num6);
          break;
        case double num7:
          fw.Write(num7);
          break;
        default:
          throw new FormatException("misc property of unsupported type - " + name);
      }
    }

    private void WriteMiscStringProperty(BinaryWriter fw, string name, int size) => SpectrumFile.WriteCharField(fw, this._miscProperties[name] as string, size);

    private void ReadPDZAveragingData(BinaryReader fr)
    {
      long position = fr.BaseStream.Position;
      long length = fr.BaseStream.Length;
      if (position == length)
        return;
      int count = (int) (length - position);
      this._miscProperties.Add("averagingData (PDZ)", (object) fr.ReadBytes(count));
    }

    private void WritePDZAveragingData(BinaryWriter fw)
    {
      if (!this._miscProperties.ContainsKey("averagingData (PDZ)"))
        return;
      this.WriteMiscProperty(fw, "averagingData (PDZ)");
    }

    public enum FileType
    {
      None,
      Pdz,
      Ssd,
      Dpp,
    }
  }
}
