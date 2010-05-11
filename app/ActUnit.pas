unit ActUnit;

interface

procedure CheckActCode;
procedure CheckDemoCode;
procedure CheckAnnualCode;
function AnnualCode(Product: integer): string;

implementation

uses General, Windows, IniFiles, Registry, SysUtils, ActUser, Controls, Dialogs,
  MessFile,ClipBrd,DateUtils;

const SysFileName = '`n_6-73d+iiq';
      SysFileOffset = 608;
      CalcFileName = '`fih+juj';
      Iclass = 'Iclass';
      Left = 'Left';

var Registry: TRegistry;
    f1: file;
    RegID,FileID,CompId,ActCode: string;
    CalcSec: integer;
    fPath,cPath: string;
    WindowsDir,SystemDir: array[0..200] of char;
    WindowsDirs,SystemDirS: string;
    s1: array[1..2048] of char;

function sisCode(s: string): string;
var loop: integer;
begin
  for loop:= 1 to length(s) do
    s[loop]:= chr(ord(s[loop]) - loop MOD 2 * 3 + (loop - 1) MOD 2 * 5);
  sisCode := s;
end;

function sisUndoCode(s: string): string;
var loop: integer;
begin
  for loop:= 1 to length(s) do
    s[loop]:= chr(ord(s[loop]) + loop MOD 2 * 3 - (loop - 1) MOD 2 * 5);
  sisUndoCode := s;
end;

function sisCompId(s: string; sec: integer): string;
var d1,d2,d3,n1,n2,n3,n4,n5: integer;
begin
  d1 := StrToInt(copy(s,1,1));
  d2 := StrToInt(copy(s,6,1));
  n1 := StrToInt(copy(s,2,2));
  n2 := StrToInt(copy(s,4,2));
  n3 := StrToInt(copy(s,1,2));
  n4 := StrToInt(copy(s,5,2));
  n5 := n1*n2 + n1*100 + n2 + n3*n4*100 + sec*100;
  n5 := n5 MOD 1000000;
  d3 := abs(5 + d1 - d2) MOD 10;
  sisCompId := IntToStr(d3) + PadVal(n5,6,'0');
end;

function sisACode(pCompId,pSerial: string): string;
var n1,n2,n3,aBase,m1,m2,m3,m4: integer;
    a,s,ms: string;
begin  {already checked that both pCompId and pSerial are 7 numeric chars}
  n1 := StrToInt(copy(pCompId,3,3));
  n2 := StrToInt(copy(pSerial,5,3));
  n3 := (n1 + n2) MOD 1000;
  aBase := Random(1000);
  a := PadVal(aBase,3,'0');
  s := PadVal(aBase + n3,4,'0');
  m1 := StrToInt(copy(pCompId,1,2));
  m2 := StrToInt(copy(pCompId,6,2));
  m3 := StrToInt(copy(pSerial,1,3));
  m4 := StrToInt(copy(pSerial,4,4));
  ms := PadVal((m1*m2 + m3 + m4) MOD 1000,3,'0');
  sisACode := ms + s[3] + a[1] + a[2] + s[4] + a[3] + s[2] + s[1];
end;

function InvalidNum(s: string; n: integer): boolean;
var loop: integer;
begin
  Result := true;
  if length(s) <> n then exit;
  for loop := 1 to length(s) do
    if not(s[loop] in numeric) then exit;
  Result := false;
end;

function sisACodeValid(pCompId,pSerial,b: string): boolean;
var Temp,a,s: string;
    n1,n2: integer;
begin
  Result := false;
  if InvalidNum(pCompId,7) then exit;
  if InvalidNum(pSerial,7) then exit;
  if InvalidNum(b,10) then exit;
  Temp := sisACode(pCompId,pSerial);
  if copy(Temp,1,3) <> copy(b,1,3) then exit;
  a := b[5] + b[6] + b[8];
  s := b[10] + b[9] + b[4] + b[7];
  n1 := StrToInt(copy(pCompId,3,3));
  n2 := StrToInt(copy(pSerial,5,3));
  if ((n1 + n2) MOD 1000) <> (StrToInt(s) - StrToInt(a)) then exit;
  Result := true;
end;

procedure SetCurrent;
var loop: integer;
begin
  GetWindowsDirectory(WindowsDir,200);
  WindowsDirS := WindowsDir;
  WindowsDirS := IncludeTrailingPathDelimiter(WindowsDirS);
  GetSystemDirectory(SystemDir,200);
  SystemDirS := SystemDir;
  SystemDirS := IncludeTrailingPathDelimiter(SystemDirS);
  fPath := SystemDirS + sisUndoCode(SysFileName);
  FileId := '';
  if FileExists(fPath) then
  begin
    AssignFile(f1,fPath);
    Reset(f1,1);
    BlockRead(f1,s1,2048);
    CloseFile(f1);
    for loop := 0 to 5 do FileId := FileId + s1[SysFileOffset + loop];
  end;
  cPath := WindowsDirS + sisUndoCode(CalcFileName);
  if FileExists(cPath) then CalcSec := GetSec(cPath)
  else begin
    cPath := SystemDirS + sisUndoCode(CalcFileName);
    if FileExists(cPath) then CalcSec := GetSec(cPath) else CalcSec := 0;
  end;
end;

function Fails(Condition: boolean): boolean;
begin
  Result := Condition;
  if Result then FatalError(ReinstallSoftware);
end;

function FailsOn(Condition: boolean; ErrMessage: string): boolean;
begin
  Result := Condition;
  IniFile.WriteString('Serial','Serial',ActivateForm.SerialEdit.Text);  {save serial number}
  if Result then
  begin
    ShowMessage(ErrMessage);
    ProgramCorrupt := true;
  end;
end;

procedure CheckActCode;
var iCompId,iSerial: string;
begin
  Registry := TRegistry.Create(KEY_READ);  {changed 16/2/05}
  with Registry do
  begin
    RootKey := HKEY_LOCAL_MACHINE;
    if KeyExists('\Software\Iclass') then
    begin
      OpenKey('\Software\Iclass',false);
      RegID := ReadString(Left);
    end
    else begin
      RootKey := HKEY_CURRENT_USER;
      OpenKey('\Software\Iclass',false);
      RegID := ReadString(Left);
    end
  end;
  SetCurrent;
  if Fails(RegId <> sisUndoCode(FileId)) then exit;
  if Fails(InvalidNum(RegId,6)) then exit;
  CompId := sisCompId(RegId,CalcSec);
  iCompId := IniFile.ReadString('Serial','CompId','');
  if (iCompId <> '') and Fails(CompId <> iCompId) then exit;
  iSerial := IniFile.ReadString('Serial','Serial','');
  ActCode := IniFile.ReadString('Serial','ActCode','');
{$IFDEF StandAlone}
  if (iSerial <> '') and Fails(copy(iSerial,1,2) <> '99') then exit;
  if not sisACodeValid(iCompId,iSerial,ActCode) then
    FatalError(mInvalidActivationCode);
{$ELSE}
  if (iSerial <> '') and Fails(iSerial[1] <> ProgSerialStart) then exit;
  if (ActCode <> '') then
  begin
    if Fails(not sisACodeValid(iCompId,iSerial,ActCode)) then;  {else normal entry}
  end
  else with ActivateForm do
  begin
    IniFile.WriteString('Serial','CompId',CompId);
    IdString.Caption := CompId;
    SerialEdit.Text := iSerial;
{    ActCodeEdit.Text := sisACode(CompId,'2000000');}
    if FailsOn(ShowModal = mrCancel,mActivationCancelled) then exit;
    if FailsOn(InvalidNum(SerialEdit.Text,7),mInvalidSerial) then exit;
    if FailsOn(InvalidNum(ActCodeEdit.Text,10),mInvalidActivationCode) then exit;
    if FailsOn(SerialEdit.Text[1] <> ProgSerialStart,mInvalidSerial) then exit;
    if FailsOn(not sisACodeValid(CompId,SerialEdit.Text,ActCodeEdit.Text),
      mInvalidActivationCode) then exit;
    IniFile.WriteString('Serial','ActCode',ActCodeEdit.Text);
  end;
{$ENDIF}
  Registry.Free;
end;

procedure CheckDemoCode;
begin
  Registry := TRegistry.Create(KEY_READ);
  with Registry do
  begin
    RootKey := HKEY_LOCAL_MACHINE;
    if KeyExists('\Software\Iclass') then
    begin
      OpenKey('\Software\Iclass',false);
      RegID := ReadString(Left);
    end
    else begin
      RootKey := HKEY_CURRENT_USER;
      OpenKey('\Software\Iclass',false);
      RegID := ReadString(Left);
    end
  end;
  SetCurrent;
  if Fails(RegID <> sisUndoCode(FileId)) then exit;
  if Fails(InvalidNum(RegID,6)) then exit;
  CompId := sisCompId(RegID,CalcSec);
  if Fails(ParamStr(1) <> 'd@' + CompId) then exit;
  Registry.Free;
end;

procedure CheckAnnualCode;
var s: string;
    Hash: char;
    n,m: integer;
begin
  Registry := TRegistry.Create(KEY_READ);
  with Registry do
  begin
    RootKey := HKEY_LOCAL_MACHINE;
    if KeyExists('\Software\Iclass') then
    begin
      OpenKey('\Software\Iclass',false);
      RegID := ReadString(Left);
    end
    else begin
      RootKey := HKEY_CURRENT_USER;
      OpenKey('\Software\Iclass',false);
      RegID := ReadString(Left);
    end
  end;
  SetCurrent;
  if Fails(RegID <> sisUndoCode(FileId)) then exit;
  if Fails(InvalidNum(RegID,6)) then exit;
  CompId := sisCompId(RegID,CalcSec);
  s := ParamStr(1);
  if Fails(length(s) < 20) then exit;
  Hash := s[length(s)];
  delete(s,length(s),1);
  if Fails(Hash <> NewCalcHash(s)) then exit;
  s := sisUndoCode(s);
  if Fails(copy(s,6,7) <> CompId) then exit;
  if Fails(s[18] <> IntToStr((StrToInt(s[1]) + StrToInt(ProgSerialStart)) MOD 10)[1]) then
    exit;      {wrong product}
  n := StrToInt(copy(s,19,3));
  if IniFile.ReadBool('Settings','Secure2',true) then
    if Fails(n <> StrToIntDef(Clipboard.AsText,-1)) then exit;
  n := StrToInt(copy(s,22,length(s) - 21)) - n;
  m := MinuteOfTheYear(Now);
  m := m - n;
  if Fails((m < 0) or (m > 3)) then exit;
  Registry.Free;
end;

function AnnualCode(Product: integer): string;
var s: string;
    n,m: integer;
begin
  s := ActCode;
  Insert(CompId,s,6);
  s := s + IntToStr((StrToInt(s[1]) + Product) MOD 10);
  n := Random(1000);
  Clipboard.AsText := IntToStr(n);
  m := MinuteOfTheYear(Now);
  s := s + PadVal(n,3,'0') + IntToStr(n + m);
  s := sisCode(s);
  Result := s + NewCalcHash(s);
end;

end.
