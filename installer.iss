[Setup]
AppName=TaskFlow
AppVersion=1.0
DefaultDirName={autopf}\TaskFlow
DefaultGroupName=TaskFlow
UninstallDisplayIcon={app}\TaskFlow.exe
Compression=lzma
SolidCompression=yes
OutputDir=userdocs:\TaskFlowInstaller
OutputBaseFilename=TaskFlowSetup

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Source points to your PyInstaller dist/TaskFlow folder
Source: "dist\TaskFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TaskFlow"; Filename: "{app}\TaskFlow.exe"
Name: "{autodesktop}\TaskFlow"; Filename: "{app}\TaskFlow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TaskFlow.exe"; Description: "{cm:LaunchProgram,TaskFlow}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up the app folder on uninstall
Type: filesandordirs; Name: "{app}"

[Code]
// Optional: Ask user if they want to wipe their database on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataPath := ExpandConstant('{userlocalappdata}\TaskFlow');
    if DirExists(DataPath) then
    begin
      if MsgBox('Do you want to completely remove your TaskFlow database and local task data?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(DataPath, True, True, True);
      end;
    end;
  end;
end;