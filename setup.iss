; Inno Setup script for CodeMerger
; This script is used by the GitHub Action to build the installer.

#define MyAppName "CodeMerger"
#define MyAppVersion "1.0.0" ; This will be replaced by the build process
#define MyAppPublisher "Your Name/Company"
#define MyAppURL "https://github.com/DrSiemer/codemerger"
#define MyAppExeName "CodeMerger.exe"
#define MyAppSetupName "CodeMerger_Setup"

[Setup]
AppId={{C6E2D2F0-2E3F-4B8A-9A0D-1B2C3D4E5F6A}}
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
Name: "checkforupdates"; Description: "Enable automatic update checks"; GroupDescription: "Updates:"; Flags: checkedonce; Check: IsCheckForUpdatesEnabled
Name: "addcontextmenu"; Description: "Add 'Open in CodeMerger' to folder context menu"; GroupDescription: "Integration:"; Flags: checkedonce; Check: IsContextMenuEnabled

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\uninstall.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commonprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\uninstall.ico"

[Registry]
; Write the installer choices to HKEY_LOCAL_MACHINE, the correct place for system-wide defaults.
Root: HKLM; Subkey: "Software\{#MyAppName}"; ValueType: dword; ValueName: "AutomaticUpdates"; ValueData: "{code:GetCheckForUpdatesValue}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}"; ValueType: string; ValueName: ""; ValueData: "Open in CodeMerger"; Flags: uninsdeletekey; Tasks: addcontextmenu
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName},0"; Tasks: addcontextmenu
Root: HKLM; Subkey: "Software\Classes\Directory\shell\{#MyAppName}\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: addcontextmenu

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  g_DeleteConfigData: Boolean;

// --- Check Functions to Read Current State from HKLM ---

function IsCheckForUpdatesEnabled(): Boolean;
var
  Value: Cardinal;
begin
  // Reads the system-wide default from HKLM.
  // If the value doesn't exist, default to True (checked), respecting 'checkedonce'.
  if not RegQueryDwordValue(HKLM, 'Software\CodeMerger', 'AutomaticUpdates', Value) then
    Result := True
  else
    Result := (Value = 1);
end;

function IsContextMenuEnabled(): Boolean;
begin
  // Checks if the system-wide context menu key exists in HKLM.
  Result := RegKeyExists(HKLM, 'Software\Classes\Directory\shell\{#MyAppName}');
end;

// --- Helper Function for Writing Values ---

function GetCheckForUpdatesValue(Param: String): String;
begin
  if WizardIsTaskSelected('checkforupdates') then
    Result := '1'
  else
    Result := '0';
end;

// --- Standard Installer/Uninstaller Logic ---

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
    FWbemObjectSet := FSWbemLocator.ExecQuery('SELECT Name FROM Win32_Process WHERE Name = "' + FileName + '"');
    Result := (FWbemObjectSet.Count > 0);
  except
    // Handle exceptions if WMI is not available
  end;
end;

function InitializeSetup(): Boolean;
begin
  if IsAppRunning('{#MyAppExeName}') then
  begin
    MsgBox('CodeMerger is currently running. Please close all instances before proceeding.', mbError, MB_OK);
    Result := False;
  end
  else
  begin
    Result := True;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigDir: string;
  AppRegistryKey: string;
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
    if g_DeleteConfigData then
    begin
      ConfigDir := ExpandConstant('{userappdata}\CodeMerger');
      DelTree(ConfigDir, True, True, True);

      AppRegistryKey := 'Software\CodeMerger';
      if RegKeyExists(HKCU, AppRegistryKey) then
        RegDeleteKeyIncludingSubkeys(HKCU, AppRegistryKey);
    end;
  end;
end;