; Inno Setup script for CodeMerger
; This script is used by the GitHub Action to build the installer.

#define MyAppName "CodeMerger"
#define MyAppPublisher "M Nugteren/2Shine"
#define MyAppURL "https://github.com/DrSiemer/codemerger"
#define MyAppExeName "CodeMerger.exe"
#define MyAppSetupName "CodeMerger_Setup"

[Setup]
AppId={{C06CFB28-1B8E-4B3B-A107-5A5C9FC92CA1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename={#MyAppSetupName}
OutputDir=.\dist-installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=assets\install.ico
UninstallDisplayIcon={app}\uninstall.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "checkforupdates"; Description: "Enable automatic update checks"; GroupDescription: "Updates:"
Name: "addcontextmenu"; Description: "Add 'Open in CodeMerger' to folder context menu"; GroupDescription: "Integration:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\uninstall.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commonprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\uninstall.ico"

[Registry]
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: dword; ValueName: "AutomaticUpdates"; ValueData: "{code:GetCheckForUpdatesValue}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}"; ValueType: string; ValueName: ""; ValueData: "Open in CodeMerger"; Flags: uninsdeletekey; Tasks: addcontextmenu
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName},0"; Tasks: addcontextmenu
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: addcontextmenu

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
const
  AppGuid = '{C06CFB28-1B8E-4B3B-A107-5A5C9FC92CA1}';

var
  g_DeleteConfigData: Boolean;

// --- Helper Function for Writing Values ---
function GetCheckForUpdatesValue(Param: String): String;
begin
  if WizardIsTaskSelected('checkforupdates') then
    Result := '1'
  else
    Result := '0';
end;

// --- Split string helper ---
function SplitString(const S, Delimiter: string): TArrayOfString;
var
  P: Integer;
  Temp: string;
begin
  SetArrayLength(Result, 0);
  Temp := S;
  repeat
    P := Pos(Delimiter, Temp);
    if P > 0 then
    begin
      SetArrayLength(Result, GetArrayLength(Result)+1);
      Result[GetArrayLength(Result)-1] := Copy(Temp, 1, P-1);
      Temp := Copy(Temp, P + Length(Delimiter), MaxInt);
    end
    else
    begin
      SetArrayLength(Result, GetArrayLength(Result)+1);
      Result[GetArrayLength(Result)-1] := Temp;
      Temp := '';
    end;
  until Temp = '';
end;

// --- Compare versions (returns -1,0,1) ---
function VersionCompare(V1, V2: String): Integer;
var
  Parts1, Parts2: TArrayOfString;
  I, N1, N2, Count1, Count2, Count: Integer;
begin
  Parts1 := SplitString(V1, '.');
  Parts2 := SplitString(V2, '.');
  Count1 := GetArrayLength(Parts1);
  Count2 := GetArrayLength(Parts2);
  if Count1 > Count2 then Count := Count1 else Count := Count2;

  for I := 0 to Count-1 do
  begin
    if I < Count1 then N1 := StrToIntDef(Parts1[I],0) else N1 := 0;
    if I < Count2 then N2 := StrToIntDef(Parts2[I],0) else N2 := 0;

    if N1 < N2 then begin Result := -1; exit; end
    else if N1 > N2 then begin Result := 1; exit; end;
  end;
  Result := 0;
end;

// --- Detect installed version ---
function GetInstalledVersion(): String;
var
  S: String;
begin
  Result := '';
  if RegQueryStringValue(HKLM,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1',
    'DisplayVersion', S) then
  begin
    Result := S;
    exit;
  end;

  if RegQueryStringValue(HKLM,
    'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1',
    'DisplayVersion', S) then
  begin
    Result := S;
  end;
end;

// --- Check if app is running ---
function IsAppRunning(const FileName: string): Boolean;
var
  FSWbemLocator: Variant;
  FWMIService: Variant;
  FWbemObjectSet: Variant;
begin
  Result := False;
  try
    FSWbemLocator := CreateOleObject('WbemScripting.SWbemLocator');
    FWMIService := FSWbemLocator.ConnectServer('.', 'root\cimv2', '', '');
    FWbemObjectSet := FWMIService.ExecQuery('SELECT Name FROM Win32_Process WHERE Name = "' + FileName + '"');
    Result := (FWbemObjectSet.Count > 0);
  except
    // Ignore WMI errors
  end;
end;

// --- Installer initialization ---
function InitializeSetup(): Boolean;
var
  InstalledVer, NewVer: String;
  Compare: Integer;
  Msg: String;
begin
  NewVer := ExpandConstant('{#MyAppVersion}');

  // Strip the leading 'v' if it exists (for Github Action)
  if (Length(NewVer) > 0) and (NewVer[1] = 'v') then
    Delete(NewVer, 1, 1);

  Log('Installer version (cleaned): ' + NewVer);
  InstalledVer := GetInstalledVersion();
  if InstalledVer <> '' then
    Log('Detected installed version: ' + InstalledVer)
  else
    Log('No installed version found.');

  if InstalledVer <> '' then
  begin
    Compare := VersionCompare(NewVer, InstalledVer);
    if Compare <= 0 then
    begin
      if Compare = 0 then
        Msg := 'You are about to install the same version (v' + InstalledVer + '). Proceed?'
      else // Compare < 0
        Msg := 'You are about to install an older version (v' + NewVer + ' < v' + InstalledVer + '). Proceed?';

      if MsgBox(Msg, mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
        exit;
      end;
    end;
  end;

  if IsAppRunning('{#MyAppExeName}') then
  begin
    MsgBox('CodeMerger is currently running. Please close all instances before proceeding.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// --- Wizard initialization ---
procedure InitializeWizard();
var
  Value: Cardinal;
  UpdatesEnabled: Boolean;
  ContextMenuEnabled: Boolean;
  I: Integer;
begin
  WizardForm.Caption := ExpandConstant('{#MyAppName} v{#MyAppVersion} Setup');
  WizardForm.BringToFront;
  if not RegQueryDwordValue(HKLM, 'Software\CodeMerger', 'AutomaticUpdates', Value) then
    UpdatesEnabled := True
  else
    UpdatesEnabled := (Value = 1);

  ContextMenuEnabled := RegKeyExists(HKLM, 'Software\Classes\Directory\shell\{#MyAppName}');

  for I := 0 to WizardForm.TasksList.Items.Count - 1 do
  begin
    if WizardForm.TasksList.Name[I] = 'checkforupdates' then
      WizardForm.TasksList.Checked[I] := UpdatesEnabled;
    if WizardForm.TasksList.Name[I] = 'addcontextmenu' then
      WizardForm.TasksList.Checked[I] := ContextMenuEnabled;
  end;
end;

// --- Uninstall steps ---
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigDir: string;
  HKCUKey, HKLMKey, ShellKey: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    if MsgBox('Do you want to remove all your CodeMerger settings and project data?', mbConfirmation, MB_YESNO) = IDYES then
      g_DeleteConfigData := True
    else
      g_DeleteConfigData := False;
  end;

  if CurUninstallStep = usPostUninstall then
  begin
    // Delete per-user config data
    if g_DeleteConfigData then
    begin
      ConfigDir := ExpandConstant('{userappdata}\CodeMerger');
      if DirExists(ConfigDir) then
        DelTree(ConfigDir, True, True, True);

      HKCUKey := 'Software\CodeMerger';
      if RegKeyExists(HKCU, HKCUKey) then
        RegDeleteKeyIncludingSubkeys(HKCU, HKCUKey);
    end;

    // Delete system-wide HKLM keys safely
    HKLMKey := 'Software\CodeMerger';
    if RegKeyExists(HKLM, HKLMKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, HKLMKey);

    ShellKey := 'Software\Classes\Directory\shell\CodeMerger';
    if RegKeyExists(HKLM, ShellKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, ShellKey);

    // Delete uninstall information
    HKLMKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1';
    if RegKeyExists(HKLM, HKLMKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, HKLMKey);

    HKLMKey := 'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\' + AppGuid + '_is1';
    if RegKeyExists(HKLM, HKLMKey) then
      RegDeleteKeyIncludingSubkeys(HKLM, HKLMKey);
  end;
end;