Program recurse;
    var res: integer;
    function recursive(num: integer): integer;
    begin
        if (num <= 0) then
            exit(num);
        exit(recursive(num - 1));
    end;
begin
    res := recursive(10);
end.