program factorial;
    function factorial(num: integer): integer;
    begin
        if num <= 1 then
            exit(1);
        exit(num * factorial(num - 1));
    end;
    var i: integer;
begin
    for i := 0 to 11 do
        writeln(i, '! = ', factorial(i));
end.