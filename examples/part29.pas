program br_cont;
    var i: integer;
begin
    for i := 0 to 10 do
        begin
            if i < 2 then
                continue;
            if i > 5 then
                break;
            writeln(i);
        end
end.