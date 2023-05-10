// Decompiled with JetBrains decompiler
// Type: S1Sync.S1RawHead
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using System.Runtime.InteropServices;

namespace S1Sync
{
  public struct S1RawHead
  {
    public byte Xilinx_Ver;
    public byte Xilinx_SubVer;
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
    public uint iReset_Cnt;
    public uint iPacket_Cnt;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 20)]
    public byte[] Unused;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 58)]
    public byte[] Xilinx_Vars;
    public short Det_Temp;
    public ushort Amb_Temp;
    public byte PIC_Ver;
    public byte PIC_SubVer;

    public void Initialize()
    {
      this.Unused = new byte[20];
      this.Xilinx_Vars = new byte[58];
    }
  }
}
