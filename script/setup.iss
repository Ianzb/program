﻿; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "zb小程序"
#define MyAppVersion "5.2.1"
#define MyAppPublisher "Ianzb"
#define MyAppURL "https://ianzb.github.io/"
#define MyAppExeName "zbProgram.exe"
#define MyAppAssocName MyAppName + "插件"
#define MyAppAssocExt ".zbaddon"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{EDBF158C-3195-4DCE-8CD3-9E34AC69267C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:\Program Files\zbProgram
ChangesAssociations=yes
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=D:\Code\program\LICENSE
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=D:\Code\打包\zbProgram
OutputBaseFilename=zbProgram_setup
SetupIconFile=D:\Code\program\program\source\img\program.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式";  Flags: unchecked
Name: "startupicon"; Description: "开机自启动"; Flags: unchecked

[Files]
Source: "D:\Code\打包\zbProgram\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Code\打包\zbProgram\source\*"; DestDir: "{app}\source"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: {#MyAppName}; ValueData: "{app}\{#MyAppExeName} startup"; Flags: uninsdeletevalue; Tasks: startupicon

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent




[Code]
procedure ExitProcess(exitCode:integer);
  external 'ExitProcess@kernel32.dll stdcall';
// 自定义函数，判断软件是否运行，参数为需要判断的软件的exe名称
function KDetectSoft(strExeName: String;mode:String): Boolean;
// 变量定义
var ErrorCode: Integer;
var bRes: Boolean;
var strFileContent: AnsiString;
var strTmpPath: String;  // 临时目录
var strTmpFile: String;  // 临时文件，保存查找软件数据结果
var strCmdFind: String;  // 查找软件命令
var strCmdKill: String;  // 终止软件命令
var strTip: String;  // 终止软件提示语
begin
  strTmpPath := GetTempDir();
  strTmpFile := Format('%sfindSoftRes.txt', [strTmpPath]);
  strCmdFind := Format('/c tasklist /nh|find /c /i "%s" > "%s"', [strExeName, strTmpFile]);
  strCmdKill := Format('/c taskkill /f /t /im %s', [strExeName]);
  strTip := Format('%s程序检测到将%s的软件正在运行！'#13''#13'点击"确定"终止软件后继续操作，否则点击"取消"。', [mode,mode]);
  //ShellExec('open', ExpandConstant('{cmd}'), '/c taskkill /f /t /im {#MyAppExeName}', '', SW_HIDE, ewNoWait, ErrorCode);
  //bRes := ShellExec('open', ExpandConstant('{cmd}'), '/c tasklist /nh|find /c /i "{#MyAppExeName}" > 0.txt', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  bRes := ShellExec('open', ExpandConstant('{cmd}'), strCmdFind, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  if bRes then begin
      bRes := LoadStringFromFile(strTmpFile, strFileContent);
      strFileContent := Trim(strFileContent);
      if bRes then begin
         if StrToInt(strFileContent) > 0 then begin
            if MsgBox(ExpandConstant(strTip), mbConfirmation, MB_OKCANCEL) = IDOK then begin
             // 终止程序
             ShellExec('open', ExpandConstant('{cmd}'), strCmdKill, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
             Result:= true;// 继续安装
            end else begin
             ExitProcess(0)
            end;
         end else begin
            //MsgBox('软件没在运行', mbInformation, MB_OK);
            Result:= true;
            Exit;
         end;
      end;
  end;
  Result :=true;
end;

// 开始页下一步时判断软件是否运行
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := KDetectSoft('{#MyAppExeName}','安装');
end;

// 卸载时关闭软件
function InitializeUninstall(): Boolean;
begin
  Result := KDetectSoft('{#MyAppExeName}','卸载');
end;
