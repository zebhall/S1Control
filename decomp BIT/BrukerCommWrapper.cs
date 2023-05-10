// Decompiled with JetBrains decompiler
// Type: S1Sync.BrukerCommWrapper
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using BrukerCommunication;
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace S1Sync
{
  public static class BrukerCommWrapper
  {
    public static CommunicationManager CommManager;
    public static ManualResetEvent CharCountEvent;
    public static ManualResetEvent CarriageReturnEvent;
    public static ManualResetEvent DataSyncEvent;
    public static BrukerDeviceName BrukerDeviceName;

    public static void SetEvents(
      ManualResetEvent charEvent,
      ManualResetEvent carriageEvent,
      ManualResetEvent dataEvent)
    {
      BrukerCommWrapper.CharCountEvent = charEvent;
      BrukerCommWrapper.CarriageReturnEvent = carriageEvent;
      BrukerCommWrapper.DataSyncEvent = dataEvent;
    }

    public static string SendOmapCommand(string strCmd) => BrukerCommWrapper.SendOmapCommand("BrukerCommandFile.CMD", strCmd, 4);

    public static string SendOmapCommand(string strCmd, int bytesToRead) => BrukerCommWrapper.SendOmapCommand("BrukerCommandFile.CMD", strCmd, bytesToRead);

    public static string SendOmapCommand(string strFileName, string strCmd) => BrukerCommWrapper.SendOmapCommand(strFileName, strCmd, 4);

    public static string SendOmapCommand(string strFileName, string strCmd, int bytesToRead)
    {
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, strFileName, bytesToRead);
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, strCmd, bytesToRead);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, bytesToRead);
      return comm;
    }

    public static string SendOmapCommand(
      string strCmd,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 4, CommunicationManager.TimeoutType.CariageReturn, 5000);
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, strCmd, bytesToRead, timeoutType, timeout);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CariageReturn, 5000);
      return comm;
    }

    public static string SendOmapMessageToComm(
      CommunicationManager.OmapMessageType dataType,
      string data,
      int bytesToRead)
    {
      return BrukerCommWrapper.SendOmapMessageToComm(dataType, data, bytesToRead, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
    }

    public static string SendOmapMessageToComm(
      CommunicationManager.OmapMessageType dataType,
      string data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType)
    {
      return BrukerCommWrapper.SendOmapMessageToComm(dataType, data, bytesToRead, timeoutType, 3000);
    }

    public static string SendOmapMessageToComm(
      CommunicationManager.OmapMessageType dataType,
      string data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.CommManager.SendMessageToOmap(dataType, data);
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      if (bytesToRead == 0)
        bytesToRead = BrukerCommWrapper.CommManager.BufferAvailableSize;
      return BrukerCommWrapper.CommManager.ReadAvailable(bytesToRead);
    }

    public static string SendOmapMessageToComm(
      CommunicationManager.OmapMessageType dataType,
      byte[] data,
      int bytesToRead)
    {
      return BrukerCommWrapper.SendOmapMessageToComm(dataType, data, bytesToRead, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
    }

    public static string SendOmapMessageToComm(
      CommunicationManager.OmapMessageType dataType,
      byte[] data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType)
    {
      return BrukerCommWrapper.SendOmapMessageToComm(dataType, data, bytesToRead, timeoutType, 3000);
    }

    public static string SendOmapMessageToComm(
      CommunicationManager.OmapMessageType dataType,
      byte[] data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.CommManager.SendMessageToOmap(dataType, data);
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      if (bytesToRead == 0)
        bytesToRead = BrukerCommWrapper.CommManager.BufferAvailableSize;
      return BrukerCommWrapper.CommManager.ReadAvailable(bytesToRead);
    }

    public static byte[] SendOmapMessageToCommEx(
      CommunicationManager.OmapMessageType cmdType,
      string data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.CommManager.SendMessageToOmap(cmdType, data);
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      if (bytesToRead == 0)
        bytesToRead = BrukerCommWrapper.CommManager.BufferAvailableSize;
      return BrukerCommWrapper.CommManager.ReadBytesAvailable(bytesToRead);
    }

    public static byte[] SendOmapMessageToCommEx(
      CommunicationManager.OmapMessageType cmdType,
      string data,
      int bytesToRead)
    {
      return BrukerCommWrapper.SendOmapMessageToCommEx(cmdType, data, bytesToRead, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
    }

    public static byte[] SendOmapMessageToCommEx(
      CommunicationManager.OmapMessageType cmdType,
      string data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType)
    {
      return BrukerCommWrapper.SendOmapMessageToCommEx(cmdType, data, bytesToRead, timeoutType, 3000);
    }

    public static byte[] SendOmapMessageToCommEx(
      CommunicationManager.OmapMessageType cmdType,
      byte[] data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.CommManager.SendMessageToOmap(cmdType, data);
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      if (bytesToRead == 0)
        bytesToRead = BrukerCommWrapper.CommManager.BufferAvailableSize;
      return BrukerCommWrapper.CommManager.ReadBytesAvailable(bytesToRead);
    }

    public static byte[] SendOmapMessageToCommEx(
      CommunicationManager.OmapMessageType cmdType,
      byte[] data,
      int bytesToRead)
    {
      return BrukerCommWrapper.SendOmapMessageToCommEx(cmdType, data, bytesToRead, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
    }

    public static byte[] SendOmapMessageToCommEx(
      CommunicationManager.OmapMessageType cmdType,
      byte[] data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType)
    {
      return BrukerCommWrapper.SendOmapMessageToCommEx(cmdType, data, bytesToRead, timeoutType, 3000);
    }

    public static string WaitAndReadFromComm(
      CommunicationManager.TimeoutType timeoutType,
      int bytesToRead,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      return BrukerCommWrapper.CommManager.GetChars(bytesToRead);
    }

    private static bool WaitForFutureEvent(
      CommunicationManager.TimeoutType timeoutType,
      int charCount,
      int timeout)
    {
      bool flag = false;
      switch (timeoutType)
      {
        case CommunicationManager.TimeoutType.CharCount:
          flag = BrukerCommWrapper.CharCountEvent.WaitOne(timeout);
          BrukerCommWrapper.CharCountEvent.Reset();
          break;
        case CommunicationManager.TimeoutType.CariageReturn:
          flag = BrukerCommWrapper.CarriageReturnEvent.WaitOne(timeout);
          BrukerCommWrapper.CarriageReturnEvent.Reset();
          break;
        case CommunicationManager.TimeoutType.CharCountOrCariageReturn:
          int num = WaitHandle.WaitAny(new WaitHandle[2]
          {
            (WaitHandle) BrukerCommWrapper.CarriageReturnEvent,
            (WaitHandle) BrukerCommWrapper.CharCountEvent
          }, timeout);
          flag = num == 0 || num == 1;
          BrukerCommWrapper.CarriageReturnEvent.Reset();
          BrukerCommWrapper.CharCountEvent.Reset();
          break;
        case CommunicationManager.TimeoutType.CharCountAndCariageReturn:
          flag = WaitHandle.WaitAll(new WaitHandle[2]
          {
            (WaitHandle) BrukerCommWrapper.CarriageReturnEvent,
            (WaitHandle) BrukerCommWrapper.CharCountEvent
          }, timeout);
          BrukerCommWrapper.CarriageReturnEvent.Reset();
          BrukerCommWrapper.CharCountEvent.Reset();
          break;
      }
      return flag;
    }

    private static bool LookForPastEvent(
      CommunicationManager.TimeoutType timeoutType,
      int charCount,
      int timeout)
    {
      bool flag = false;
      if (timeoutType == CommunicationManager.TimeoutType.CharCount && charCount <= BrukerCommWrapper.CommManager.BufferAvailableSize)
        flag = true;
      else if (timeoutType == CommunicationManager.TimeoutType.CariageReturn && BrukerCommWrapper.CommManager._comBuffer != null && BrukerCommWrapper.CommManager._comBuffer.Length != 0 && Array.IndexOf<byte>(BrukerCommWrapper.CommManager._comBuffer, (byte) 13) >= 0)
        flag = true;
      else if (timeoutType == CommunicationManager.TimeoutType.CharCountOrCariageReturn && BrukerCommWrapper.CommManager._comBuffer != null && BrukerCommWrapper.CommManager._comBuffer.Length != 0 && (charCount <= BrukerCommWrapper.CommManager.BufferAvailableSize || Array.IndexOf<byte>(BrukerCommWrapper.CommManager._comBuffer, (byte) 13) >= 0))
        flag = true;
      else if (timeoutType == CommunicationManager.TimeoutType.CharCountAndCariageReturn && BrukerCommWrapper.CommManager._comBuffer != null && BrukerCommWrapper.CommManager._comBuffer.Length != 0 && charCount <= BrukerCommWrapper.CommManager.BufferAvailableSize && Array.IndexOf<byte>(BrukerCommWrapper.CommManager._comBuffer, (byte) 13) >= 0)
        flag = true;
      return flag;
    }

    public static bool WaitForEvent(
      CommunicationManager.TimeoutType timeoutType,
      int charCount,
      int timeout)
    {
      if (BrukerCommWrapper.LookForPastEvent(timeoutType, charCount, timeout))
        return true;
      BrukerCommWrapper.CommManager.ExpectedCharCount = charCount;
      return BrukerCommWrapper.WaitForFutureEvent(timeoutType, charCount, timeout);
    }

    public static string SendOmapMessageToComm(
      string data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.CommManager.WriteData(data, 0);
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      if (bytesToRead == 0)
        bytesToRead = BrukerCommWrapper.CommManager.BufferAvailableSize;
      return BrukerCommWrapper.CommManager.ReadAvailable(bytesToRead);
    }

    public static byte[] SendOmapMessageToComm(
      byte[] data,
      int bytesToRead,
      CommunicationManager.TimeoutType timeoutType,
      int timeout)
    {
      BrukerCommWrapper.CommManager.ExpectedCharCount = bytesToRead;
      BrukerCommWrapper.CommManager.WriteData(data, 0);
      BrukerCommWrapper.WaitForFutureEvent(timeoutType, bytesToRead, timeout);
      if (bytesToRead == 0)
        bytesToRead = BrukerCommWrapper.CommManager.BufferAvailableSize;
      return BrukerCommWrapper.CommManager.ReadBytesAvailable(bytesToRead);
    }

    public static bool DownloadFileFromTitan(string remoteFileName, string localFileName)
    {
      bool flag = false;
      byte[] numArray = (byte[]) null;
      byte[] commEx1 = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenRead, remoteFileName, 0, CommunicationManager.TimeoutType.CariageReturn, 1000);
      if (commEx1.Length > 5)
      {
        string str = BrukerCommWrapper.CommManager.ByteArrayToStr(commEx1);
        long int64 = Convert.ToInt64(str.Substring(4, str.Length - 5));
        long num1 = 0;
        int num2 = (int) Convert.ToByte(13);
        try
        {
          using (FileStream output = File.Open(localFileName, FileMode.Create, FileAccess.Write, FileShare.ReadWrite))
          {
            using (BinaryWriter binaryWriter = new BinaryWriter((Stream) output))
            {
              int num3;
              for (; num1 < int64; num1 += (long) num3)
              {
                num3 = BrukerCommWrapper.CommManager.DownloadBlockSize;
                if (num1 + (long) BrukerCommWrapper.CommManager.DownloadBlockSize > int64)
                  num3 = (int) (int64 - num1);
                int bytesToRead = 8 + num3.ToString().Length + num3;
                byte[] commEx2 = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileRead, num3.ToString(), bytesToRead, CommunicationManager.TimeoutType.CharCount);
                int num4 = 6 + num3.ToString().Length + 1;
                int num5 = (int) commEx2[num4 - 1];
                int num6 = (int) BrukerCommWrapper.CommManager.CRCModulo256(commEx2, num4 + 1);
                binaryWriter.Write(commEx2, num4 + 1, commEx2.Length - num4 - 1);
              }
              binaryWriter.Flush();
              binaryWriter.Close();
            }
            output.Close();
          }
          flag = true;
        }
        catch (Exception ex)
        {
          flag = false;
        }
      }
      numArray = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCount, 3000);
      return flag;
    }

    public static string GetUpdateFileFromZip(string zipFileName, string fileName)
    {
      string updateFileFromZip = "";
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "UncompressFile " + zipFileName + ";" + fileName, 4, CommunicationManager.TimeoutType.CharCount, 2000);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      if (comm.Contains("!FW"))
      {
        updateFileFromZip = Path.GetTempPath() + "\\" + fileName;
        if (File.Exists(updateFileFromZip))
        {
          File.Delete(updateFileFromZip);
          int num = 0;
          while (File.Exists(updateFileFromZip))
          {
            updateFileFromZip = updateFileFromZip + "." + num++.ToString();
            File.Delete(updateFileFromZip);
          }
        }
        BrukerCommWrapper.DownloadFileFromTitan("\\Temp\\" + fileName, updateFileFromZip);
      }
      return updateFileFromZip;
    }

    public static bool IsTempMonRunning()
    {
      bool flag = false;
      byte[] data = new byte[4];
      byte[] numArray = new byte[2];
      data[0] = Convert.ToByte(':');
      data[1] = Convert.ToByte('5');
      data[2] = Convert.ToByte('2');
      data[3] = Convert.ToByte(31);
      byte[] comm = BrukerCommWrapper.SendOmapMessageToComm(data, 2, CommunicationManager.TimeoutType.CharCount, 100);
      if (comm.Length >= 2 && comm[0] == (byte) 139 && comm[1] == (byte) 98)
        flag = true;
      return flag;
    }

    public static bool StopTempMonRunning()
    {
      bool flag = false;
      byte[] msg = new byte[5];
      byte[] data = new byte[4];
      byte[] numArray = new byte[2];
      msg[0] = Convert.ToByte(':');
      msg[1] = Convert.ToByte('5');
      msg[2] = Convert.ToByte('1');
      msg[3] = Convert.ToByte(31);
      msg[4] = Convert.ToByte(194);
      BrukerCommWrapper.CommManager.WriteData(msg, 0);
      Thread.Sleep(200);
      BrukerCommWrapper.CommManager.ReadAvailable();
      data[0] = Convert.ToByte(':');
      data[1] = Convert.ToByte('5');
      data[2] = Convert.ToByte('2');
      data[3] = Convert.ToByte(31);
      byte[] comm = BrukerCommWrapper.SendOmapMessageToComm(data, 2, CommunicationManager.TimeoutType.CharCount, 100);
      if (comm.Length == 2 && comm[0] == (byte) 194 && comm[1] == (byte) 98)
        flag = true;
      return flag;
    }

    public static SYSTEM_POWER_STATUS_EX2 GetBatteryLife()
    {
      SYSTEM_POWER_STATUS_EX2 batteryLife = new SYSTEM_POWER_STATUS_EX2(true);
      if (BrukerCommWrapper.CommManager.IsOpen())
      {
        BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
        byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, nameof (GetBatteryLife), 58, CommunicationManager.TimeoutType.CharCount, 3000);
        BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
        if (commEx.Length == 58)
        {
          byte[] numArray = new byte[53];
          Array.Copy((Array) commEx, 4, (Array) numArray, 0, 53);
          using (MemoryStream input = new MemoryStream(numArray))
          {
            using (BinaryReader binaryReader = new BinaryReader((Stream) input))
            {
              batteryLife.ACLineStatus = binaryReader.ReadByte();
              batteryLife.BatteryFlag = binaryReader.ReadByte();
              batteryLife.BatteryLifePercent = binaryReader.ReadByte();
              batteryLife.Reserved1 = binaryReader.ReadByte();
              batteryLife.BatteryLifeTime = binaryReader.ReadUInt32();
              batteryLife.BatteryFullLifeTime = binaryReader.ReadUInt32();
              batteryLife.Reserved2 = binaryReader.ReadByte();
              batteryLife.BackupBatteryFlag = binaryReader.ReadByte();
              batteryLife.BackupBatteryLifePercent = binaryReader.ReadByte();
              batteryLife.Reserved3 = binaryReader.ReadByte();
              batteryLife.BackupBatteryLifeTime = binaryReader.ReadUInt32();
              batteryLife.BackupBatteryFullLifeTime = binaryReader.ReadUInt32();
              batteryLife.BatteryVoltage = binaryReader.ReadUInt32();
              batteryLife.BatteryCurrent = binaryReader.ReadUInt32();
              batteryLife.BatteryAverageCurrent = binaryReader.ReadUInt32();
              batteryLife.BatteryAverageInterval = binaryReader.ReadUInt32();
              batteryLife.BatterymAHourConsumed = binaryReader.ReadUInt32();
              batteryLife.BatteryTemperature = binaryReader.ReadUInt32();
              batteryLife.BackupBatteryVoltage = binaryReader.ReadUInt32();
              batteryLife.BatteryChemistry = binaryReader.ReadByte();
            }
          }
        }
      }
      return batteryLife;
    }

    public static string ParseOutput(string str)
    {
      string output = "";
      if (str.Length > 5)
        output = str.Substring(4, str.Length - 5);
      return output;
    }

    public static BRKR_UUP_STATUS GetUupStatus()
    {
      BRKR_UUP_STATUS uupStatus = new BRKR_UUP_STATUS((byte) 0, (byte) 0);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, nameof (GetUupStatus), 7, CommunicationManager.TimeoutType.CharCount, 1000);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      if (commEx.Length == 7)
        uupStatus = new BRKR_UUP_STATUS(commEx[4], commEx[5]);
      return uupStatus;
    }

    public static BRKR_SUP_STATUS GetSupStatus()
    {
      BRKR_SUP_STATUS supStatus = new BRKR_SUP_STATUS((byte) 0, (byte) 0, (byte) 0);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, nameof (GetSupStatus), 8, CommunicationManager.TimeoutType.CharCount, 1000);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      if (commEx.Length == 8)
        supStatus = new BRKR_SUP_STATUS(commEx[4], commEx[5], commEx[6]);
      return supStatus;
    }

    public static XRAY_TABLE GetXboxStatus()
    {
      XRAY_TABLE xboxStatus = new XRAY_TABLE();
      xboxStatus.Initialize();
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 4, CommunicationManager.TimeoutType.CharCount, 1000);
      byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, nameof (GetXboxStatus), 182, CommunicationManager.TimeoutType.CharCount, 10000);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      if (commEx.Length >= 182)
      {
        byte[] numArray = new byte[177];
        Array.Copy((Array) commEx, 4, (Array) numArray, 0, 177);
        using (MemoryStream input = new MemoryStream(numArray))
        {
          using (BinaryReader binaryReader = new BinaryReader((Stream) input))
          {
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_sVoltADC[index] = binaryReader.ReadUInt16();
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_bVoltDAC[index] = binaryReader.ReadByte();
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_sCurrADC[index] = binaryReader.ReadUInt16();
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_bCurrDAC[index] = binaryReader.ReadByte();
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_bPulseLen[index] = binaryReader.ReadByte();
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_bFilter[index] = binaryReader.ReadByte();
            for (int index = 0; index < 7; ++index)
              xboxStatus.m_blCurScalar[index] = binaryReader.ReadByte();
            xboxStatus.m_bPulseL = binaryReader.ReadByte();
            xboxStatus.m_bPulseW = binaryReader.ReadByte();
            xboxStatus.m_bActVolt = binaryReader.ReadByte();
            xboxStatus.m_bActCurr = binaryReader.ReadByte();
            xboxStatus.m_bCurFilter = binaryReader.ReadByte();
            xboxStatus.m_sFltSensorDAC = binaryReader.ReadUInt16();
            xboxStatus.m_sLightPipeDAC = binaryReader.ReadUInt16();
            xboxStatus.m_Version_1 = binaryReader.ReadByte();
            xboxStatus.m_Version_2 = binaryReader.ReadByte();
            xboxStatus.m_Version_3 = binaryReader.ReadByte();
            xboxStatus.m_Mode = binaryReader.ReadByte();
            xboxStatus.m_AnodeZ = binaryReader.ReadByte();
            xboxStatus.m_fBeThickness = binaryReader.ReadSingle();
            xboxStatus.m_Incidence = binaryReader.ReadSingle();
            xboxStatus.m_TakeOff = binaryReader.ReadSingle();
            for (int index1 = 0; index1 < 5; ++index1)
            {
              xboxStatus.m_Filter[index1].bFilterNum = (int) binaryReader.ReadByte();
              for (int index2 = 0; index2 < 3; ++index2)
              {
                xboxStatus.m_Filter[index1].flLayer[index2].bElement = (short) binaryReader.ReadByte();
                xboxStatus.m_Filter[index1].flLayer[index2].sThickness = binaryReader.ReadInt16();
              }
            }
            for (int index = 0; index < 5; ++index)
              xboxStatus.m_bFilterGaps[index] = binaryReader.ReadByte();
            xboxStatus.m_Actuals.HV_ADC = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.HVG_DAC = binaryReader.ReadByte();
            xboxStatus.m_Actuals.HVG_Current = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.FC_ADC = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.FG_DAC = binaryReader.ReadByte();
            xboxStatus.m_Actuals.FG_Current = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.InputVoltage = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.InputCurrent = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.Pulselen = binaryReader.ReadByte();
            xboxStatus.m_Actuals.Filter = binaryReader.ReadByte();
            xboxStatus.m_Actuals.FilterError = binaryReader.ReadByte();
            xboxStatus.m_Actuals.Temperature = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.Flux = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.Mod_Anode = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.Mod_Cathode = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.IRLED = binaryReader.ReadInt16();
            xboxStatus.m_Actuals.ActiveVolt = binaryReader.ReadByte();
            xboxStatus.m_Actuals.ActiveCurr = binaryReader.ReadByte();
            xboxStatus.m_Actuals.Valid = binaryReader.ReadInt32();
            binaryReader.Close();
          }
          input.Close();
        }
      }
      return xboxStatus;
    }

    public static DPP_TABLE GetDppStatus()
    {
      DPP_TABLE dppStatus = new DPP_TABLE();
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000);
      byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, nameof (GetDppStatus), 69, CommunicationManager.TimeoutType.CharCount, 2000);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 32);
      if (commEx.Length == 69)
      {
        byte[] destinationArray = new byte[64];
        Array.Copy((Array) commEx, 4, (Array) destinationArray, 0, 64);
        GCHandle gcHandle = GCHandle.Alloc((object) destinationArray, GCHandleType.Pinned);
        dppStatus = (DPP_TABLE) Marshal.PtrToStructure(gcHandle.AddrOfPinnedObject(), typeof (DPP_TABLE));
        gcHandle.Free();
      }
      return dppStatus;
    }

    public static BRKR_WIN32_FIND_DATA_EXT GetFileStatus(string fileName)
    {
      BRKR_WIN32_FIND_DATA_EXT fileStatus = new BRKR_WIN32_FIND_DATA_EXT();
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
      byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, "GetFileStatus " + fileName, 33, CommunicationManager.TimeoutType.CharCount, 5000);
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
      if (commEx.Length == 33)
      {
        byte[] destinationArray = new byte[28];
        Array.Copy((Array) commEx, 4, (Array) destinationArray, 0, 28);
        GCHandle gcHandle = GCHandle.Alloc((object) destinationArray, GCHandleType.Pinned);
        fileStatus = (BRKR_WIN32_FIND_DATA_EXT) Marshal.PtrToStructure(gcHandle.AddrOfPinnedObject(), typeof (BRKR_WIN32_FIND_DATA_EXT));
        gcHandle.Free();
      }
      return fileStatus;
    }

    public static BRKR_WIN32_FIND_DATAA ByteArrayToFileData(byte[] byteArray)
    {
      BRKR_WIN32_FIND_DATA_HEAD wiN32FindDataHead = new BRKR_WIN32_FIND_DATA_HEAD();
      byte[] destinationArray = new byte[40];
      byte[] numArray = new byte[260];
      Array.Copy((Array) byteArray, 0, (Array) destinationArray, 0, 40);
      Array.Copy((Array) byteArray, 40, (Array) numArray, 0, 260);
      IntPtr num = Marshal.AllocHGlobal(byteArray.Length);
      Marshal.Copy(byteArray, 0, num, byteArray.Length);
      BRKR_WIN32_FIND_DATA_HEAD structure = (BRKR_WIN32_FIND_DATA_HEAD) Marshal.PtrToStructure(num, typeof (BRKR_WIN32_FIND_DATA_HEAD));
      Marshal.FreeHGlobal(num);
      return new BRKR_WIN32_FIND_DATAA()
      {
        fData = structure,
        cFileName = Encoding.ASCII.GetString(numArray, 0, Array.IndexOf<byte>(numArray, (byte) 0))
      };
    }

    public static void CreateDirectory(DirectoryInfo dirInfo)
    {
      if (dirInfo.Parent != null && !dirInfo.Exists)
        BrukerCommWrapper.CreateDirectory(dirInfo.Parent);
      if (dirInfo.Exists)
        return;
      dirInfo.Create();
    }

    public static List<string> GetRecursiveFileList(string folderName)
    {
      List<string> recursiveFileList = new List<string>();
      int num = 5;
      do
        ;
      while (--num > 0 && BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCount, 3000).Length <= 5);
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "GetRecursiveFileList " + folderName, 5, CommunicationManager.TimeoutType.CharCount, 5000);
      StringBuilder stringBuilder = new StringBuilder();
      if (comm.StartsWith("!FW") && comm.Length == 5)
      {
        while (BrukerCommWrapper.WaitForEvent(CommunicationManager.TimeoutType.CharCount, 1, 1000))
          stringBuilder.Append(BrukerCommWrapper.CommManager.ReadAvailable());
      }
      if (BrukerCommWrapper.CommManager.BufferAvailableSize > 0)
        stringBuilder.Append(BrukerCommWrapper.CommManager.ReadAvailable());
      string str1 = stringBuilder.ToString();
      char[] chArray = new char[1]{ Convert.ToChar(13) };
      foreach (string str2 in str1.Split(chArray))
      {
        if (str2.Length > 0)
          recursiveFileList.Add(str2);
      }
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CariageReturn, 3000);
      return recursiveFileList;
    }

    public static List<string> GetFileList(string folderName)
    {
      List<string> fileList = new List<string>();
      int num = 5;
      do
        ;
      while (--num > 0 && BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCount, 3000).Length <= 5);
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, "GetOnlyFileList " + folderName, 4, CommunicationManager.TimeoutType.CharCount, 5000);
      StringBuilder stringBuilder = new StringBuilder();
      if (comm.StartsWith("!FW") && comm.Length == 4)
      {
        while (BrukerCommWrapper.WaitForEvent(CommunicationManager.TimeoutType.CharCount, 1, 1000))
          stringBuilder.Append(BrukerCommWrapper.CommManager.ReadAvailable());
      }
      if (BrukerCommWrapper.CommManager.BufferAvailableSize > 0)
        stringBuilder.Append(BrukerCommWrapper.CommManager.ReadAvailable());
      stringBuilder.Replace(Convert.ToChar(13), Convert.ToChar(0));
      string str1 = stringBuilder.ToString();
      char[] chArray = new char[1]{ ';' };
      foreach (string str2 in str1.Split(chArray))
      {
        if (str2.Length > 0)
          fileList.Add(str2);
      }
      BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CariageReturn, 3000);
      return fileList;
    }

    private static void SplitByteArray(
      byte[] source,
      out byte[] first,
      out byte[] second,
      int lengthOfFirst)
    {
      first = new byte[lengthOfFirst];
      second = new byte[source.Length - lengthOfFirst];
      Array.Copy((Array) source, 0, (Array) first, 0, lengthOfFirst);
      Array.Copy((Array) source, lengthOfFirst, (Array) second, 0, source.Length - lengthOfFirst);
    }

    public static string GetCalibrationList()
    {
      BrukerCommWrapper.DataSyncEvent.Reset();
      string calibrationList = BrukerCommWrapper.SendOmapCommand(nameof (GetCalibrationList));
      BrukerCommWrapper.DataSyncEvent.Set();
      return calibrationList;
    }

    public static int BlockSizeAnalyzer(string fileName, int nUploadBlockSize)
    {
      int num = nUploadBlockSize;
      bool flag;
      do
      {
        flag = true;
        try
        {
          using (BinaryReader binaryReader = new BinaryReader((Stream) File.Open(fileName, FileMode.Open, FileAccess.Read, FileShare.Read)))
          {
            long length = (long) (int) binaryReader.BaseStream.Length;
            int count;
            for (long index = 0; index < length; index += (long) count)
            {
              count = num;
              if (index + (long) num > length)
                count = (int) (length - index);
              byte[] byteArray = binaryReader.ReadBytes(count);
              if (BrukerCommWrapper.CommManager.CRCModulo256(byteArray, 0) == (byte) 13)
              {
                binaryReader.Close();
                --num;
                if (num == 0)
                  return MessageBox.Show("You are trying to copy a CORRUPTED file (" + fileName + "). Do you want to copy anyway?", "Upload", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes ? nUploadBlockSize : 0;
                flag = false;
                break;
              }
            }
            binaryReader.Close();
          }
        }
        catch (Exception ex)
        {
          num = 0;
          flag = true;
        }
      }
      while (!flag);
      return num;
    }

    public static void UploadFileOnTitan(string sourceFile, string destFile)
    {
      ASCIIEncoding asciiEncoding = new ASCIIEncoding();
      string str = sourceFile;
      string data1 = destFile;
      int num1 = BrukerCommWrapper.BlockSizeAnalyzer(str, BrukerCommWrapper.CommManager.UploadBlockSize);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, data1, 5, CommunicationManager.TimeoutType.CharCount, 1000);
      using (BinaryReader binaryReader = new BinaryReader((Stream) File.Open(str, FileMode.Open, FileAccess.Read, FileShare.Read)))
      {
        long length = (long) (int) binaryReader.BaseStream.Length;
        long num2 = 0;
        while (num2 < length)
        {
          int count = num1;
          if (num2 + (long) num1 > length)
            count = (int) (length - num2);
          byte[] data2 = binaryReader.ReadBytes(count);
          num2 += (long) count;
          bool flag = true;
          for (int index = 0; index < 10; ++index)
          {
            byte[] commEx = BrukerCommWrapper.SendOmapMessageToCommEx(CommunicationManager.OmapMessageType.FileWrite, data2, 4, CommunicationManager.TimeoutType.CharCount, 1000);
            if (asciiEncoding.GetString(commEx).StartsWith("!FW"))
            {
              flag = false;
              break;
            }
          }
          if (flag)
            break;
        }
        binaryReader.Close();
      }
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 4, CommunicationManager.TimeoutType.CariageReturn, 1000);
    }

    public static void DeleteFileFromTitan(string strFileName)
    {
      int num = 5;
      string str = "DeleteFile ";
      do
        ;
      while (--num > 0 && BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.OpenWrite, "BrukerCommandFile.CMD", 6, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 1000).Length <= 5);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileWrite, str + strFileName, 4, CommunicationManager.TimeoutType.CharCount, 5000);
      BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.FileClose, (string) null, 3, CommunicationManager.TimeoutType.CharCountOrCariageReturn, 3000);
    }

    public static bool StartTrigger(string cmdline, bool displayError = true)
    {
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.Custom, "$TS" + cmdline, 0, CommunicationManager.TimeoutType.CariageReturn, 3000);
      if (comm.StartsWith("!TS"))
        return true;
      if (comm.Contains("parse"))
      {
        int num1 = (int) MessageBox.Show("TITAN/Tracer: Parse error in Live Spectrum Start string");
      }
      else if (displayError)
      {
        int num2 = (int) MessageBox.Show("TITAN/Tracer: Cannot start Live Spectrum.\nUnexpected or no response received from the instrument: " + comm + ".\nAm I Armed?");
      }
      return false;
    }

    public static int ReadRemID()
    {
      string comm = BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.Custom, "$ID", 0, CommunicationManager.TimeoutType.CariageReturn, 3000);
      return comm.StartsWith("!ID ") ? Convert.ToInt32(comm.Substring(4)) : -1;
    }

    public static bool StopTrigger() => BrukerCommWrapper.SendOmapMessageToComm(CommunicationManager.OmapMessageType.Custom, "$TE", 0, CommunicationManager.TimeoutType.CariageReturn, 3000).StartsWith("!TE");

    public static string GetInstrumentSerialNo()
    {
      BrukerCommWrapper.DataSyncEvent.Reset();
      string instrumentSerialNo = BrukerCommWrapper.SendOmapCommand("GetSerialNumber", 1024, CommunicationManager.TimeoutType.CariageReturn, 1000);
      if (instrumentSerialNo.Length > 5)
        instrumentSerialNo = instrumentSerialNo.Substring(4, instrumentSerialNo.Length - 5);
      BrukerCommWrapper.DataSyncEvent.Set();
      return instrumentSerialNo;
    }

    public static bool IsSerialNumberAlreadySet()
    {
      BrukerCommWrapper.DataSyncEvent.Reset();
      string str = BrukerCommWrapper.SendOmapCommand(nameof (IsSerialNumberAlreadySet), 1024, CommunicationManager.TimeoutType.CariageReturn, 1000);
      if (str.Length > 5)
        str = str.Substring(4, str.Length - 5);
      BrukerCommWrapper.DataSyncEvent.Set();
      return str.Equals("1");
    }

    public static bool SetSerialNumber(string newSerialNo)
    {
      BrukerCommWrapper.DataSyncEvent.Reset();
      string str = BrukerCommWrapper.SendOmapCommand("SetSerialNumber " + newSerialNo);
      BrukerCommWrapper.DataSyncEvent.Set();
      return str.StartsWith("!FW");
    }

    public static string GetBuildNumber()
    {
      BrukerCommWrapper.DataSyncEvent.Reset();
      string buildNumber = BrukerCommWrapper.SendOmapCommand(nameof (GetBuildNumber), 1024, CommunicationManager.TimeoutType.CariageReturn, 1000);
      if (buildNumber.Length > 5)
        buildNumber = buildNumber.Substring(4, buildNumber.Length - 5);
      BrukerCommWrapper.DataSyncEvent.Set();
      return buildNumber;
    }
  }
}
