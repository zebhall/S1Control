// Decompiled with JetBrains decompiler
// Type: S1Sync.s1_cooked_head
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using System.Runtime.InteropServices;

namespace S1Sync
{
  public struct s1_cooked_head
  {
    public byte FPGA_Ver;
    public byte FPGA_SubVer;
    public ushort iPacket_Len;
    public uint iTDur;
    public uint iRaw_Cnts;
    public uint iValid_Cnts;
    public uint iValid_CntsRng;
    public uint iADur;
    public uint iADead;
    public uint iAReset;
    public uint iALive;
    public uint iService;
    public ushort iReset_Cnt;
    public ushort iPacket_Cnt;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 20)]
    public byte[] Unused;
    public float fXRay_ActualHV;
    public float fXRay_ActualAC;
    public byte bValidActuals;
    public byte XRay_ActualHVDAC;
    public byte XRay_ActualACDAC;
    public byte Unused2;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 46)]
    public byte[] Xilinx_Vars;
    public short Det_Temp;
    public ushort Amb_Temp;
    public byte MCU_Ver;
    public byte MCU_SubVer;
    public uint iRaw_Cnts_Acc;
    public uint iValid_Cnts_Acc;
    public uint iValid_CntsRng_Acc;
    public uint iReset_Cnt_Acc;
    public float fTDur;
    public float fADur;
    public float fADead;
    public float fAReset;
    public float fALive;
    public uint lVacuum_Acc;
    public uint lPacket_Cnt;
    public S1FILTER xTubeFilter;
    public XRAY XRay;

    public void Initialize()
    {
      this.Unused = new byte[20];
      this.Xilinx_Vars = new byte[46];
      this.xTubeFilter = new S1FILTER();
      this.XRay = new XRAY();
    }
  }
}
