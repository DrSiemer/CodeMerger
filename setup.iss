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
; Override the default name+version format, and just use the name
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
; Use a custom icon for the installer itself
SetupIconFile=assets\install.ico
; Set the icon for the uninstaller in Add/Remove Programs
UninstallDisplayIcon={app}\uninstall.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "checkforupdates"; Description: "Enable automatic update checks"; GroupDescription: "Updates:"; Flags: checkedonce
Name: "addcontextmenu"; Description: "Add 'Open in CodeMerger' to folder context menu"; GroupDescription: "Integration:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Bundle the uninstall icon with the application files
Source: "assets\uninstall.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Add an uninstaller shortcut to the Start Menu folder
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\uninstall.ico"

[Registry]
Root: HKCR; Subkey: "Directory\shell\{#MyAppName}"; ValueType: string; ValueName: ""; ValueData: "Open in CodeMerger"; Flags: uninsdeletekey; Tasks: addcontextmenu
Root: HKCR; Subkey: "Directory\shell\{#MyAppName}"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#MyAppExeName},0"; Tasks: addcontextmenu
Root: HKCR; Subkey: "Directory\shell\{#MyAppName}\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: addcontextmenu

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  g_DeleteConfigData: Boolean; // Global variable for the uninstaller's choice

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
    // Handle exceptions if WMI is not available
  end;
end;

function InitializeSetup(): Boolean;
begin
  if IsAppRunning('{#MyAppExeName}') then
  begin
    MsgBox('CodeMerger is currently running. Please close all instances of the application before proceeding with the installation.', mbError, MB_OK);
    Result := False;
  end
  else
  begin
    Result := True;
  end;
end;

// --- INSTALLER LOGIC ---
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigDir: string;
  ConfigPath: string;
  ConfigJson: TStringList;
  UpdateCheckValue: string;
begin
  // This code runs after all files are installed
  if CurStep = ssPostInstall then
  begin
    // Determine the path for the config file
    ConfigDir := ExpandConstant('{userappdata}\CodeMerger');
    ConfigPath := ConfigDir + '\config.json';

    // Only create a default config file if one doesn't already exist.
    // This preserves user settings during an upgrade or reinstall.
    if not FileExists(ConfigPath) then
    begin
      // Ensure the configuration directory exists
      if not DirExists(ConfigDir) then
      begin
        CreateDir(ConfigDir);
      end;

      // Set the value based on the user's selection in the installer
      if WizardIsTaskSelected('checkforupdates') then
      begin
        UpdateCheckValue := 'true';
      end
      else
      begin
        UpdateCheckValue := 'false';
      end;

      // Create a minimal JSON file. The application will populate the rest of the
      // settings on its first run, respecting this user choice.
      ConfigJson := TStringList.Create;
      try
        ConfigJson.Add('{');
        ConfigJson.Add('  "check_for_updates": ' + UpdateCheckValue);
        ConfigJson.Add('}');
        ConfigJson.SaveToFile(ConfigPath);
      finally
        ConfigJson.Free;
      end;
    end;
  end;
end;

// --- UNINSTALLER LOGIC ---
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigDir: string;
begin
  // This step runs right after the user confirms the uninstallation,
  // but before any files are deleted. This is the correct time to ask.
  if CurUninstallStep = usUninstall then
  begin
    if MsgBox('Do you want to remove all your CodeMerger settings and project data?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      g_DeleteConfigData := True;
    end else
    begin
      g_DeleteConfigData := False;
    end;
  end;

  // This runs after the main application files have been uninstalled
  if CurUninstallStep = usPostUninstall then
  begin
    // Check if the user agreed to delete their data
    if g_DeleteConfigData then
    begin
      ConfigDir := ExpandConstant('{userappdata}\CodeMerger');
      // Delete the entire CodeMerger folder from AppData
      DelTree(ConfigDir, True, True, True);
    end;
  end;
end;