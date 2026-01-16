program pr;
    type
        arr_range = 0..10;
        a = array[arr_range] of real;
    function avg(vals: a): real;
    var i: integer;
    var size: integer = 0;
    begin
        result := 0;
        for i in arr_range do
            begin
                size := size + 1;
                result := result + vals[i];
            end;
        result := result / size;
    end;
    var some_values: a;
        i: integer;
begin
    for i in arr_range do
        some_values[i] := i;
    writeln(avg(some_values));
end.