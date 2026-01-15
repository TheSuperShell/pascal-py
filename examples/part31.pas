program incorrect_func;
    var a: integer = 5;
    procedure sum(out b: integer);
    begin
        b:= 10;
    end;
begin
    sum(a);
    writeln(a);
end.