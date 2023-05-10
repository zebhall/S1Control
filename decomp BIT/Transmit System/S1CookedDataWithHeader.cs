// Decompiled with JetBrains decompiler
// Type: S1Sync.S1CookedDataWithHeader
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using System.Runtime.InteropServices;

namespace S1Sync
{
  public struct S1CookedDataWithHeader
  {
    public float eVPerChannel;
    public s1_cooked_head sch;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 2048)]
    public uint[] data;

    public void Initialize()
    {
      this.sch = new s1_cooked_head();
      this.data = new uint[2048];
    }
  }
}
