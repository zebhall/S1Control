// Decompiled with JetBrains decompiler
// Type: S1Sync.s1_cooked_struct
// Assembly: S1Sync, Version=1.9.0.146, Culture=neutral, PublicKeyToken=null
// MVID: AEE7AF75-B376-4601-A89E-A23B75544DB1
// Assembly location: C:\Program Files (x86)\Bruker\Bruker Toolbox\Bruker Instrument Tools.exe

using System.Runtime.InteropServices;

namespace S1Sync
{
  public struct s1_cooked_struct
  {
    public s1_cooked_head head;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 8192)]
    public float[] fData;

    public void Initialize() => this.fData = new float[8192];
  }
}
