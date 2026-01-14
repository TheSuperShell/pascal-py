program arr;
    const PI = 3.14;
    type angles = 0..361;
    var a: array[angles] of real;
        i: angles;
begin
    for i := 0 to 361 do
        a[i] := i / 360 * PI;
    writeln(a)
end.