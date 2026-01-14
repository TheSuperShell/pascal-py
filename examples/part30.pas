program arr;
    const PI = 3.14;
    type angles = 0..361;
        radians = array[angles] of real;
    var a: radians;
        i: angles;
begin
    for i := 0 to 361 do
        a[i] := i / 360 * PI;
    writeln(a)
end.