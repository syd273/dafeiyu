# 一键熄屏：关闭显示器，按任意键/动鼠标即亮
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MonitorOff {
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
}
"@
[void][MonitorOff]::SendMessage([IntPtr]0xffff, 0x0112, [IntPtr]0xF170, [IntPtr]2)